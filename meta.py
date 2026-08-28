#!/usr/bin/env python3
"""
meta.py -- the warrant for corpus-analysis.md.

Recomputes every [MEASURED] number in corpus-analysis.md and emits them as data, so the prose can be
checked mechanically instead of by eye (test_numbers.py does the checking).

Usage
  python3 meta.py                     text report to stdout + numbers.json beside this file
  python3 meta.py --json PATH         write numbers.json somewhere else
  python3 meta.py --quiet             numbers.json only, no report
  python3 meta.py --no-json           report only (the pre-2026-08-25 behaviour)
  python3 meta.py --src DIR           corpora live under DIR instead of $HOME
  python3 meta.py --src-union PATH    rebuild the AF/LW side from union.json (NNCO still from --src)
  python3 meta.py --show-matches K    print K random matches per instrument pattern, with context
  python3 meta.py --api-spotcheck     re-query the LessWrong GraphQL API for the karma-field check
                                      and refresh api_spotcheck.json

Inputs (read-only; nothing under them is written or modified):
  <src>/alignment-forum-scrape/projects.json                          253 records
  <src>/scrape-lesswrong/lesswrong_empirical_ai_safety_projects.json  637 records
  <src>/neel-nandas-chris-olah/manifest.json                          101 records
  plus the three source readme.md files, for file sizes and recommendation counts.

Conventions
  * Every proportion carries a Wilson 95% interval; every median carries a bootstrap 95%
    interval (1000 resamples, seed 0). A rate without an interval is a bug.
  * If you disagree with a claim in readme.md, modify this script, not the prose.
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import os
import random
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The scrape window as declared by the source readmes (LW's title is the explicit one).
# Period lengths are measured against this window, not against first/last post, because the
# window is what bounds each pipeline's opportunity to collect.
WINDOW = ("2024-08-25", "2026-08-25")
PERIODS = ["2024H2", "2025H1", "2025H2", "2026H1", "2026H2"]

POST_ID = re.compile(r"/posts/([A-Za-z0-9]+)/")
GH = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")

# AF's readme presents 7 normalised project_type rows over 17 raw labels and does not ship the
# mapping (readme.md O8). This is that mapping. reproduces_af_table() checks it against the
# published table; if the check fails, the mapping is wrong, not the table.
PROJECT_TYPE_MAP = {
    "interpretability": "interpretability",
    "steering": "interpretability",
    "interpretability-replication": "interpretability",
    "evals": "evals",
    "CoT-faithfulness": "evals",
    "CoT-monitoring": "evals",
    "unlearning/evals": "evals",
    "benchmark/evals": "evals",
    "training-experiment": "training-experiment",
    "red-teaming": "red-teaming",
    "adversarial-robustness": "red-teaming",
    "benchmark": "benchmark",
    "AI-control-experiment": "benchmark",
    "model-organisms": "model-organisms",
    "model-organism": "model-organisms",
    "dataset": "dataset",
    "dataset-construction": "dataset",
}
AF_README_TABLE = {  # the published §1.2 table, for verification
    "interpretability": 91, "evals": 60, "training-experiment": 59, "red-teaming": 22,
    "benchmark": 11, "model-organisms": 8, "dataset": 2,
}

# ------------------------------------------------------------------ instruments
# One instrument, applied identically to every corpus. Divergence from the source readmes'
# numbers is an instrument effect, not a population effect -- and this instrument is not
# validated either: see readme.md 1.3c and prompts.md P4. --show-matches exists so that the
# false-positive rate can be eyeballed before any of these rates is quoted.
RIGOR = {
    "seeds_loose":  r"\b(random seed|seeds?\b|across \d+ seeds|seed variance)\b",
    "seeds_strict": r"\b(random seeds?|\d+ seeds|seed variance|across seeds|per-seed|seed-to-seed)\b",
    "errorbar":     r"\b(error bars?|confidence intervals?|standard error|95% ci|stderr|s\.e\.m)\b|±",
    "sig_test":     r"\b(p\s*[<=]\s*0?\.\d|p-value|t-test|mann-whitney|bootstrap|chi-squared|wilcoxon)\b",
    "n_equals":     r"\bn\s*=\s*\d+",
    "ablation":     r"\bablat",
    "baseline":     r"\bbaselines?\b",
    "prereg":       r"\b(pre-?regist)",
    "heldout":      r"\b(held[- ]out|test split|validation set)\b",
    "arxiv":        r"arxiv\.org",
    "limitations":  r"\b(limitations?|caveats?)\b",
    "neg_result":   r"\b(negative results?|did not (?:work|replicate)|failed to (?:find|replicate)|no (?:significant )?effect)\b",
    "multi_model":  r"\b(across (?:several|multiple|\d+) models|model families)\b",
}
TOPIC = {
    "SAE":          r"\b(sparse autoencoder|SAEs?\b|dictionary learning|crosscoder)",
    "agents":       r"\b(agentic|agent scaffold|tool[- ]use|multi[- ]turn agent|AI agents?)\b",
    "reward_hack":  r"\b(reward hack|specification gaming|reward tamper)",
    "cot_monitor":  r"\b(chain[- ]of[- ]thought monitor|CoT monitor|monitorab|CoT faithful|faithfulness of (?:the )?chain)",
    "eval_aware":   r"\b(eval(?:uation)?[- ]aware|knows it(?:'|’)s being (?:tested|evaluated)|sandbagg|situational awareness)",
    "probes":       r"\b(linear probe|probing classifier|probe accuracy)",
    "emergent_mis": r"\b(emergent misalignment)",
    "align_fake":   r"\b(alignment fak)",
    "unlearning":   r"\bunlearn",
    "steering":     r"\b(steering vector|activation steering|activation addition)",
}
# Diagnostics for readme.md 1.3c: the narrow reading of "seeds", and a crude construct-validity
# check on multi_model (AF's published 18.2% was "multiple models OR SCALES", a wider construct
# than the regex above measures).
DIAG = {
    "seeds_random_only": r"\brandom seeds?\b",
}
MODEL_FAMILY = re.compile(
    r"\b(gpt-?[45o]|claude|gemma|llama|qwen|mistral|deepseek|pythia|gemini|o[13]-?(?:mini)?|kimi|phi-?\d)\b",
    re.I)
MODEL_FAMILY_LOWER = re.compile(MODEL_FAMILY.pattern)

SOURCE_CLAIMS = {  # printed for comparison; read off the source readmes, not computed here
    "af.seeds_variance": 5.9, "af.stat_test_or_interval": 19.4, "af.limitations": 43.9,
    "af.arxiv": 84.2, "af.negative": 9.9, "af.multi_model": 18.2,
    "lw.seeds": 17, "lw.errorbar": 16, "lw.n_equals": 13, "lw.prereg": 2,
    "lw.ablation": 24, "lw.baseline": 52, "lw.heldout": 20, "lw.arxiv": 72,
}


# ---------------------------------------------------------------------- numbers
class Numbers(dict):
    """Flat dotted-key store. Refuses silent overwrites so a copy-paste key clash is loud."""

    def set(self, key, value):
        if key in self and self[key] != value:
            raise KeyError(f"duplicate numbers.json key with a different value: {key}")
        self[key] = value
        return value

    def rate(self, key, k, n):
        """Emit a percentage plus its Wilson interval and the counts behind it."""
        self.set(f"{key}.k", k)
        self.set(f"{key}.n", n)
        p = self.set(f"{key}.pct", pct(k, n))
        self.set(f"{key}.ci95", wilson(k, n))
        return p

    def median(self, key, xs):
        m = self.set(f"{key}.median", round(st.median(xs), 1) if xs else None)
        self.set(f"{key}.median_ci95", boot_median_ci(xs))
        self.set(f"{key}.n", len(xs))
        return m


def pct(k, n):
    return round(100.0 * k / n, 1) if n else None


def fmt0(k, n):
    """Percent to 0dp from the exact ratio. Never format numbers.json's 1dp value to 0dp --
    that double-rounds (8.54 -> 8.5 -> 8, when the answer is 9)."""
    return f"{100.0 * k / n:.0f}%" if n else "-"


def wilson(k, n, z=1.96):
    """95% Wilson interval for a proportion, as [lo_pct, hi_pct]."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * max(0.0, centre - half), 1), round(100 * min(1.0, centre + half), 1)]


def boot_median_ci(xs, resamples=1000, seed=0):
    """Percentile bootstrap 95% interval for a median.

    `xs` is sorted first: the median does not depend on input order, so its interval must not
    either. Without this the same corpus produces different intervals depending on whether the
    records arrived from the raw JSONs or from union.json.
    """
    if not xs:
        return None
    xs = sorted(xs)
    rng = random.Random(seed)
    n = len(xs)
    meds = sorted(st.median(rng.choices(xs, k=n)) for _ in range(resamples))
    return [round(meds[int(0.025 * resamples)], 1), round(meds[int(0.975 * resamples) - 1], 1)]


def h(s):
    return hashlib.md5((s or "").encode()).hexdigest()


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def repo(url):
    """Normalised owner/name, lowercased, for cross-corpus repo identity."""
    if not url:
        return None
    m = GH.search(url)
    if not m:
        return None
    return f"{m.group(1)}/{m.group(2)}".lower().removesuffix(".git")


def half(d):
    return f"{d[:4]}H{1 if int(d[5:7]) <= 6 else 2}"


def period_days(period, window=WINDOW):
    """Days of the scrape window that fall inside a half-year. 2024H2 and 2026H2 are partial."""
    y = int(period[:4])
    lo = dt.date(y, 1, 1) if period.endswith("H1") else dt.date(y, 7, 1)
    hi = dt.date(y, 6, 30) if period.endswith("H1") else dt.date(y, 12, 31)
    w0 = dt.date.fromisoformat(window[0])
    w1 = dt.date.fromisoformat(window[1])
    lo, hi = max(lo, w0), min(hi, w1)
    return (hi - lo).days + 1 if hi >= lo else 0


def authors_of(rec):
    return [a.strip() for a in re.split(r",\s*", rec.get("author") or "") if a.strip()]


# ------------------------------------------------------------------------ load
def src_paths(src):
    return {
        "AF": os.path.join(src, "alignment-forum-scrape", "projects.json"),
        "LW": os.path.join(src, "scrape-lesswrong", "lesswrong_empirical_ai_safety_projects.json"),
        "NNCO": os.path.join(src, "neel-nandas-chris-olah", "manifest.json"),
        "AF_README": os.path.join(src, "alignment-forum-scrape", "readme.md"),
        "LW_README": os.path.join(src, "scrape-lesswrong", "readme.md"),
        "NNCO_README": os.path.join(src, "neel-nandas-chris-olah", "readme.md"),
        "NNCO_README_PRIOR": os.path.join(src, "neel-nandas-chris-olah", "readme.chatgpt.md"),
    }


def load_raw(paths):
    AF = json.load(open(paths["AF"]))
    LW = json.load(open(paths["LW"]))
    NN = json.load(open(paths["NNCO"]))
    for r in AF:
        m = POST_ID.search(r["url"] or "")
        r["_pid"] = m.group(1) if m else None
    for r in LW:
        r["_pid"] = r["_id"]
    return AF, LW, NN


def load_from_union(union_path, paths):
    """Rebuild AF-shaped and LW-shaped record lists from union.json.

    Exists so that `--src-union` can prove union.json is a faithful superset: the numbers it
    produces must match the ones produced from the two raw JSONs, key for key.
    """
    doc = json.load(open(union_path))
    recs = doc["records"]
    AF, LW = [], []
    for pid, r in recs.items():
        if r["in_af"]:
            a = r["af"]
            AF.append({
                "_pid": pid, "date": r["date"], "title": a["title"], "author": a["author"],
                "github-link": a["github_link"],
                "github-readme": (a.get("github_readme_alt") if a.get("github_readme_alt") is not None
                                  else (r["github-readme"] if a["github_readme_present"] else None)),
                "article-content": r["article-content"], "url": a["url"],
                "project_type": a["project_type_raw"], "article_file": a["article_file"],
                "additional_github_links": a["additional_github_links"],
                "karma": a["karma"], "word_count": a["word_count"],
            })
        if r["in_lw"]:
            l = r["lw"]
            LW.append({
                "_pid": pid, "_id": pid, "date": r["date"], "title": l["title"],
                "author": l["author"], "github-link": l["github_link"],
                "github-readme": r["github-readme"] if l["github_readme_present"] else None,
                "article-content": r["article-content"], "url": l["url"],
                "topic": l["topic"], "confidence": l["confidence"], "tags": l["tags"],
                "file": l["file"], "github_readme_status": l["github_readme_status"],
                "karma": l["karma"], "word_count": l["word_count"],
            })
    AF.sort(key=lambda r: (r["date"], r["_pid"]))
    LW.sort(key=lambda r: (r["date"], r["_pid"]))
    NN = json.load(open(paths["NNCO"]))
    return AF, LW, NN


# ------------------------------------------------------------------- the corpus
class Corpus:
    """The join, plus every per-record derived value, computed exactly once."""

    def __init__(self, AF, LW, NN):
        self.AF, self.LW, self.NN = AF, LW, NN
        self.AFP = {r["_pid"]: r for r in AF}
        self.LWP = {r["_pid"]: r for r in LW}
        self.BOTH = set(self.AFP) & set(self.LWP)
        self.AFONLY = set(self.AFP) - set(self.LWP)
        self.LWONLY = set(self.LWP) - set(self.AFP)
        # LW record wins on collision (superset schema); AF fills the gaps.
        self.UNION = {}
        for r in LW:
            self.UNION[r["_pid"]] = dict(r, _src="LW")
        for r in AF:
            self.UNION.setdefault(r["_pid"], dict(r, _src="AF"))
        self.V = list(self.UNION.values())

        # One pass over every body: markers, topics, model families, GitHub mentions.
        # Bodies are lowercased once and the patterns compiled without re.I -- case-insensitive
        # matching is the single most expensive thing this script does. Every pattern in RIGOR,
        # TOPIC and DIAG is lowercase-safe (no uppercase escapes, no case-sensitive classes);
        # test_numbers.py pins the resulting rates so a pattern that stops being safe is caught.
        self.rigor_rx = {k: re.compile(p.lower()) for k, p in RIGOR.items()}
        self.topic_rx = {k: re.compile(p.lower()) for k, p in TOPIC.items()}
        self.diag_rx = {k: re.compile(p.lower()) for k, p in DIAG.items()}
        self.flags = {}
        self.gh_mentions = {}
        for pid, r in self.UNION.items():
            body = r["article-content"] or ""
            low = body.lower()
            f = {}
            for k, rx in self.rigor_rx.items():
                f[k] = rx.search(low) is not None
            for k, rx in self.topic_rx.items():
                f[k] = rx.search(low) is not None
            for k, rx in self.diag_rx.items():
                f[k] = rx.search(low) is not None
            fams = {m.group(0)[:4] for m in MODEL_FAMILY_LOWER.finditer(low)}
            f["_families"] = len(fams)
            self.flags[pid] = f
            self.gh_mentions[pid] = {f"{o}/{n}".lower() for o, n in GH.findall(body)}

    # -- strata ---------------------------------------------------------------
    def stratum(self, name):
        if name == "AF-only":
            return [self.AFP[p] for p in sorted(self.AFONLY)]
        if name == "shared":
            return [self.AFP[p] for p in sorted(self.BOTH)]
        if name == "LW-only":
            return [self.LWP[p] for p in sorted(self.LWONLY)]
        if name == "AF all":
            return self.AF
        if name == "LW all":
            return self.LW
        if name == "in AF":
            return self.AF
        if name == "not in AF":
            return [self.LWP[p] for p in sorted(self.LWONLY)]
        if name == "UNION":
            return self.V
        raise KeyError(name)

    def prevalence(self, records, key):
        n = len(records)
        k = sum(1 for r in records if self.flags[r["_pid"]][key])
        return k, n


def reproduces_af_table(AF):
    got = collections.Counter(PROJECT_TYPE_MAP[r["project_type"]] for r in AF)
    return dict(got) == AF_README_TABLE, dict(got)


# ------------------------------------------------------------------- api check
API_SPOTCHECK_FILE = os.path.join(HERE, "api_spotcheck.json")
SPOTCHECK_PID = "umYzsh7SGHHKsRCaA"


def api_spotcheck(pid=SPOTCHECK_PID, timeout=20):
    """Ask LessWrong for baseScore vs afBaseScore on one shared post.

    readme.md O1b turns on the difference between the two: the AF readme documents its `karma`
    field as "AF baseScore", but AF karma equals LW karma on all 149 shared posts, which is only
    possible if it is the LessWrong baseScore.
    """
    import urllib.request
    q = ('{ post(input:{selector:{_id:"%s"}}) { result { title baseScore afBaseScore af } } }' % pid)
    req = urllib.request.Request(
        "https://www.lesswrong.com/graphql",
        data=json.dumps({"query": q}).encode(),
        headers={"content-type": "application/json", "user-agent": "meta.py spotcheck"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        out = json.load(resp)["data"]["post"]["result"]
    out["_post_id"] = pid
    out["_fetched"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    json.dump(out, open(API_SPOTCHECK_FILE, "w"), indent=2)
    return out


def load_api_spotcheck():
    if os.path.exists(API_SPOTCHECK_FILE):
        return json.load(open(API_SPOTCHECK_FILE))
    return None


# ---------------------------------------------------------------------- report
def build(C, N, paths, out=sys.stdout, show_matches=0):
    """Print the text report and fill N (the numbers store) as it goes."""

    def rule(t):
        print(f"\n{'=' * 78}\n{t}\n{'=' * 78}", file=out)

    AF, LW, NN, V = C.AF, C.LW, C.NN, C.V
    AFP, LWP, BOTH, AFONLY, LWONLY = C.AFP, C.LWP, C.BOTH, C.AFONLY, C.LWONLY
    nb = len(BOTH)

    # ---------------------------------------------------------------- 0 sources
    rule("0  SOURCE ARTIFACTS  (sizes and recommendation counts, for readme.md 1.1 and O10)")
    for key, label in [("AF", "af.json"), ("LW", "lw.json"), ("NNCO", "nnco.manifest"),
                       ("AF_README", "af.readme"), ("LW_README", "lw.readme"),
                       ("NNCO_README", "nnco.readme"), ("NNCO_README_PRIOR", "nnco.readme_prior")]:
        b = os.path.getsize(paths[key])
        N.set(f"sources.{label}.bytes", b)
        N.set(f"sources.{label}.kb", round(b / 1024))
        print(f"  {label:20} {b:>9,} bytes  ({round(b/1024):>3} KB)", file=out)
    readme_kb = sum(N[f"sources.{k}.kb"] for k in
                    ["af.readme", "lw.readme", "nnco.readme", "nnco.readme_prior"])
    N.set("sources.three_readmes_plus_prior.kb", readme_kb)
    print(f"  {'three readmes + prior':20} {readme_kb} KB total", file=out)

    # Recommendation counts: how many R-specs each source readme ships (readme.md O10).
    rec_pat = {
        "af": re.compile(r"^#+\s*R(\d+)\s*[-—]", re.M),
        "lw": re.compile(r"^#+\s*R(\d+)\.", re.M),
        "nnco": re.compile(r"^#+\s*R(\d+\.\d+)\s*[-—]", re.M),
    }
    recs = {}
    for tag, path_key in [("af", "AF_README"), ("lw", "LW_README"), ("nnco", "NNCO_README")]:
        txt = open(paths[path_key]).read()
        found = rec_pat[tag].findall(txt)
        recs[tag] = len(set(found))
        N.set(f"source_recs.{tag}", recs[tag])
    nnco_txt = open(paths["NNCO_README"]).read()
    recs["nnco_tier0"] = len({m for m in re.findall(r"^#+\s*R(0\.\d+)\s*[-—]", nnco_txt, re.M)})
    recs["nnco_tier1"] = len({m for m in re.findall(r"^#+\s*R(1\.\d+)\s*[-—]", nnco_txt, re.M)})
    N.set("source_recs.nnco_tier0", recs["nnco_tier0"])
    N.set("source_recs.nnco_tier1", recs["nnco_tier1"])
    total_recs = N.set("source_recs.total", recs["af"] + recs["lw"] + recs["nnco"])
    print(f"  recommendations shipped: AF {recs['af']}  LW {recs['lw']}  "
          f"NNCO {recs['nnco']} ({recs['nnco_tier0']} tier-0 + {recs['nnco_tier1']} tier-1)  "
          f"total {total_recs}", file=out)

    # ------------------------------------------------------------- 1.1 the join
    rule("1.1  CORPUS SIZES AND THE JOIN")
    N.set("corpus.af.n", len(AF))
    N.set("corpus.lw.n", len(LW))
    N.set("corpus.nnco.n", len(NN))
    N.set("join.shared", nb)
    N.set("join.af_only", len(AFONLY))
    N.set("join.lw_only", len(LWONLY))
    N.set("join.union", len(C.UNION))
    N.set("join.af_only_pct", pct(len(AFONLY), len(AF)))
    N.set("join.lw_only_pct", pct(len(LWONLY), len(LW)))
    N.rate("join.shared_share_of_af", nb, len(AF))
    N.rate("join.shared_share_of_lw", nb, len(LW))
    idfail = sum(1 for r in AF if not r["_pid"])
    N.set("join.af_id_extraction_failures", idfail)
    print(f"AF   {len(AF):>4} records   unique post-ids {len(AFP):>4}   id-extraction failures {idfail}", file=out)
    print(f"LW   {len(LW):>4} records   unique post-ids {len(LWP):>4}", file=out)
    print(f"NNCO {len(NN):>4} records   (different unit: blog documents, no post-ids)", file=out)
    print(f"\nAF n LW (shared post-id) : {nb}", file=out)
    print(f"AF only                  : {len(AFONLY)}   ({N['join.af_only_pct']}% of AF)", file=out)
    print(f"LW only                  : {len(LWONLY)}   ({N['join.lw_only_pct']}% of LW)", file=out)
    print(f"UNION                    : {len(C.UNION)}", file=out)
    aft = {norm_title(r["title"]) for r in AF}
    lwt = {norm_title(r["title"]) for r in LW}
    N.set("join.title_overlap", len(aft & lwt))
    N.set("join.title_and_id_agree", len(aft & lwt) == nb)
    print(f"title-level overlap      : {len(aft & lwt)}  (title join and id join agree exactly: "
          f"{len(aft & lwt) == nb})", file=out)
    dates = sorted(r["date"] for r in V)
    N.set("corpus.union.first_date", dates[0])
    N.set("corpus.union.last_date", dates[-1])
    N.set("corpus.window.start", WINDOW[0])
    N.set("corpus.window.end", WINDOW[1])
    print(f"union date range         : {dates[0]} -> {dates[-1]}   "
          f"(declared scrape window {WINDOW[0]} -> {WINDOW[1]})", file=out)

    # ----------------------------------------------------- 1.4/O1 independence
    rule("1.4/O1  AGREEMENT BETWEEN THE TWO CORPORA ON THE 149 SHARED POSTS")
    print("The two scrapes were built by two separate Opus sessions, one per forum (user, "
          "2026-08-25).\nIdentical body text and karma are expected -- both pull the same posts "
          "from the same\ndatabase. The load-bearing number is repo-adjudication agreement.", file=out)
    ident = {
        "content": sum(1 for p in BOTH if h(AFP[p]["article-content"]) == h(LWP[p]["article-content"])),
        "github_readme": sum(1 for p in BOTH if h(AFP[p]["github-readme"]) == h(LWP[p]["github-readme"])),
        "title": sum(1 for p in BOTH if AFP[p]["title"] == LWP[p]["title"]),
        "author": sum(1 for p in BOTH if AFP[p]["author"] == LWP[p]["author"]),
        "karma": sum(1 for p in BOTH if int(AFP[p]["karma"]) == int(LWP[p]["karma"])),
        "word_count": sum(1 for p in BOTH if int(AFP[p]["word_count"]) == int(LWP[p]["word_count"])),
    }
    for k, v in ident.items():
        N.set(f"o1.identical.{k}", v)
    N.set("o1.shared_n", nb)
    print(f"\nbyte-identical article-content : {ident['content']}/{nb}   [expected under independence]", file=out)
    print(f"byte-identical github-readme   : {ident['github_readme']}/{nb}", file=out)
    print(f"identical title / author       : {ident['title']}/{nb}  /  {ident['author']}/{nb}", file=out)
    print(f"identical karma / word_count   : {ident['karma']}/{nb}  /  {ident['word_count']}/{nb}", file=out)

    agree_repo = agree_none = af_x = lw_x = disagree = 0
    disagreements = []
    for p in sorted(BOTH):
        a, l = repo(AFP[p]["github-link"]), repo(LWP[p]["github-link"])
        if a and l:
            if a == l:
                agree_repo += 1
            else:
                disagree += 1
                disagreements.append((AFP[p]["title"], a, l, p))
        elif a:
            af_x += 1
        elif l:
            lw_x += 1
        else:
            agree_none += 1
    N.set("o1.repo.same", agree_repo)
    N.set("o1.repo.both_null", agree_none)
    N.set("o1.repo.af_only", af_x)
    N.set("o1.repo.lw_only", lw_x)
    N.set("o1.repo.different", disagree)
    N.rate("o1.repo.decision_agreement", agree_repo + agree_none, nb)
    N.rate("o1.repo.identity_agreement_among_both_assigned", agree_repo, agree_repo + disagree)
    print(f"\nrepo adjudication: same repo {agree_repo} | both null {agree_none} | "
          f"AF-only {af_x} | LW-only {lw_x} | different {disagree}", file=out)
    print(f"  decision agreement (assigned vs null, either way) : "
          f"{agree_repo + agree_none}/{nb} = {N['o1.repo.decision_agreement.pct']}% "
          f"CI {N['o1.repo.decision_agreement.ci95']}", file=out)
    print(f"  identity agreement among the {agree_repo + disagree} both-assigned : "
          f"{agree_repo}/{agree_repo + disagree} = "
          f"{N['o1.repo.identity_agreement_among_both_assigned.pct']}% "
          f"CI {N['o1.repo.identity_agreement_among_both_assigned.ci95']}", file=out)
    print("  (Cohen's kappa on the binary has-repo decision is omitted: with "
          f"{af_x + lw_x} one-sided\n   assignments it is 1.0 by construction and measures nothing.)", file=out)
    for t, a, l, p in disagreements:
        N.set("o2.post_id", p)
        N.set("o2.af_repo", a)
        N.set("o2.lw_repo", l)
        print(f"  DISAGREEMENT ({p}): {t[:52]}\n                AF={a}\n                LW={l}", file=out)

    # ------------------------------------------------ 1.4/O1b the karma field
    rule("1.4/O1b  WHICH KARMA IS IN THE AF CORPUS?")
    print(f"AF karma == LW karma on {ident['karma']}/{nb} shared posts. LessWrong's `baseScore` and "
          "the\nAlignment Forum's `afBaseScore` are different numbers, so AF's `karma` field is the "
          "LW\nbaseScore -- not 'AF baseScore at scrape time' as the AF readme's schema states.", file=out)
    spot = load_api_spotcheck()
    if spot:
        N.set("o1b.api.base_score", spot["baseScore"])
        N.set("o1b.api.af_base_score", spot["afBaseScore"])
        N.set("o1b.api.post_id", spot["_post_id"])
        N.set("o1b.stored_karma_af", int(AFP[spot["_post_id"]]["karma"]))
        N.set("o1b.stored_karma_lw", int(LWP[spot["_post_id"]]["karma"]))
        print(f"\nLessWrong GraphQL spot-check on {spot['_post_id']} (fetched {spot['_fetched']}):", file=out)
        print(f"  baseScore {spot['baseScore']}   afBaseScore {spot['afBaseScore']}   "
              f"stored in AF json {N['o1b.stored_karma_af']}   stored in LW json {N['o1b.stored_karma_lw']}", file=out)
    else:
        print("\n  (no api_spotcheck.json; run `python3 meta.py --api-spotcheck` to fetch it)", file=out)

    # ---------------------------------------------------- 1.3b prestige strata
    rule("1.3b  PRESTIGE STRATIFICATION  (AF promotion as the stratifier)")
    print(f"{'stratum':11} {'n':>4} {'med karma':>10} {'karma CI':>14} {'mean karma':>11} "
          f"{'repo%':>7} {'readme%':>8} {'solo%':>6} {'7+auth':>7} {'mean auth':>10} {'med words':>10}", file=out)
    for lbl, key in [("AF-only", "af_only"), ("shared", "shared"), ("LW-only", "lw_only"),
                     ("in AF", "in_af"), ("not in AF", "not_in_af")]:
        rs = C.stratum(lbl)
        k = [int(r["karma"]) for r in rs]
        w = [int(r["word_count"]) for r in rs]
        au = [len(authors_of(r)) for r in rs]
        solo = sum(1 for r in rs if "," not in (r["author"] or ""))
        N.set(f"strata.{key}.n", len(rs))
        N.median(f"strata.{key}.karma", k)
        N.set(f"strata.{key}.karma.mean", round(st.mean(k), 1))
        N.rate(f"strata.{key}.own_repo", sum(1 for r in rs if r["github-link"]), len(rs))
        N.rate(f"strata.{key}.readme", sum(1 for r in rs if r["github-readme"]), len(rs))
        N.rate(f"strata.{key}.solo", solo, len(rs))
        N.set(f"strata.{key}.authors_7plus", sum(1 for a in au if a >= 7))
        N.set(f"strata.{key}.authors.mean", round(st.mean(au), 2))
        N.median(f"strata.{key}.words", w)
        print(f"{lbl:11} {len(rs):>4} {N[f'strata.{key}.karma.median']:>10.1f} "
              f"{str(N[f'strata.{key}.karma.median_ci95']):>14} "
              f"{N[f'strata.{key}.karma.mean']:>11.1f} "
              f"{N[f'strata.{key}.own_repo.pct']:>6.1f}% {N[f'strata.{key}.readme.pct']:>7.1f}% "
              f"{N[f'strata.{key}.solo.pct']:>5.0f}% {N[f'strata.{key}.authors_7plus']:>7} "
              f"{N[f'strata.{key}.authors.mean']:>10.2f} {N[f'strata.{key}.words.median']:>10.0f}", file=out)
    # The contrasts the prose quotes, emitted rather than left for the reader to divide.
    for lbl, a, b in [("in_af_vs_not", "in_af", "not_in_af"),
                      ("af_only_vs_lw_only", "af_only", "lw_only")]:
        N.set(f"contrast.{lbl}.karma_median_ratio",
              round(N[f"strata.{a}.karma.median"] / N[f"strata.{b}.karma.median"], 2))
        N.set(f"contrast.{lbl}.mean_authors_ratio",
              round(N[f"strata.{a}.authors.mean"] / N[f"strata.{b}.authors.mean"], 2))
        N.set(f"contrast.{lbl}.own_repo_pct_diff",
              round(N[f"strata.{a}.own_repo.pct"] - N[f"strata.{b}.own_repo.pct"], 1))
        print(f"\ncontrast {lbl}: karma median x{N[f'contrast.{lbl}.karma_median_ratio']}  "
              f"team size x{N[f'contrast.{lbl}.mean_authors_ratio']}  "
              f"code release {N[f'contrast.{lbl}.own_repo_pct_diff']:+} points", file=out)
    print("\n  'in AF' vs 'not in AF' is the treatment contrast; 'AF-only' vs 'LW-only' is the same\n"
          "  contrast with the shared posts removed from both arms, which selects on LW pipeline\n"
          "  failure and inflates the gap. Report the first as primary.", file=out)

    # --------------------------------------------------- 1.3d coverage in time
    rule("1.3d  AF-IN-LW COVERAGE BY HALF-YEAR  (recall of the LW pipeline against a known in-scope set)")
    ca = collections.Counter(half(AFP[p]["date"]) for p in AFP)
    cl = collections.Counter(half(LWP[p]["date"]) for p in LWP)
    cb = collections.Counter(half(AFP[p]["date"]) for p in BOTH)
    cu = collections.Counter(half(r["date"]) for r in V)
    print(f"{'period':8} {'days':>5} {'AF n':>5} {'LW n':>5} {'shared':>7} {'coverage':>9} "
          f"{'95% CI':>14} {'AF/30d':>7} {'LW/30d':>7} {'UNION/30d':>10}", file=out)
    for p in PERIODS:
        d = N.set(f"period.{p}.days", period_days(p))
        N.set(f"period.{p}.af_n", ca[p])
        N.set(f"period.{p}.lw_n", cl[p])
        N.set(f"period.{p}.shared", cb[p])
        N.set(f"period.{p}.union_n", cu[p])
        N.rate(f"coverage.{p}", cb[p], ca[p])
        af30 = N.set(f"period.{p}.af_per30d", round(30 * ca[p] / d, 1))
        lw30 = N.set(f"period.{p}.lw_per30d", round(30 * cl[p] / d, 1))
        un30 = N.set(f"period.{p}.union_per30d", round(30 * cu[p] / d, 1))
        print(f"{p:8} {d:>5} {ca[p]:>5} {cl[p]:>5} {cb[p]:>7} {fmt0(cb[p], ca[p]):>9} "
              f"{str(N[f'coverage.{p}.ci95']):>14} {af30:>7} {lw30:>7} {un30:>10}", file=out)
    N.rate("coverage.overall", nb, len(AF))
    print(f"\noverall AF captured by LW: {nb}/{len(AF)} = {N['coverage.overall.pct']}% "
          f"CI {N['coverage.overall.ci95']}", file=out)
    print("2024H2 and 2026H2 are PARTIAL periods -- compare the per-30-day columns, not the counts.", file=out)

    af_by_karma = sorted(AFP.values(), key=lambda r: -int(r["karma"]))
    top9_missed = [i + 1 for i, r in enumerate(af_by_karma[:9]) if r["_pid"] in AFONLY]
    N.set("coverage.af_top9_missed_count", len(top9_missed))
    N.set("coverage.af_top9_missed_ranks", top9_missed)
    print(f"\nof AF's own top 9 posts by karma, {len(top9_missed)} are missed by the LW pipeline "
          f"(ranks {top9_missed})", file=out)
    print("AF posts missed by the LW pipeline, top 15 by karma:", file=out)
    missed15 = sorted((AFP[p] for p in AFONLY), key=lambda r: -int(r["karma"]))[:15]
    N.set("coverage.missed_top15_karma", [int(r["karma"]) for r in missed15])
    for r in missed15:
        print(f"  {r['karma']:>4}  {r['date']}  {r['title'][:60]:60} [{r['project_type']}]", file=out)
    N.set("coverage.missed.n", len(AFONLY))
    N.set("coverage.missed.under_1000_words", sum(1 for p in AFONLY if int(AFP[p]["word_count"]) < 1000))
    N.set("coverage.missed.over_100_karma", sum(1 for p in AFONLY if int(AFP[p]["karma"]) > 100))
    N.set("coverage.missed.single_author", sum(1 for p in AFONLY if "," not in AFP[p]["author"]))
    print(f"\n  of the {len(AFONLY)} missed: {N['coverage.missed.under_1000_words']} are <1000 words, "
          f"{N['coverage.missed.over_100_karma']} are >100 karma, "
          f"{N['coverage.missed.single_author']} are single-author", file=out)
    print("  WHICH of LW's three recall gates (43-tag retrieval -> 1,706; regex prefilter -> 909;\n"
          "  LLM inclusion -> 637) dropped each of these is NOT decidable from the shipped data.", file=out)

    # ------------------------------------------- 1.3c one instrument, all strata
    rule("1.3c  ONE INSTRUMENT APPLIED TO EVERY STRATUM  (rigor markers, % of posts)")
    cols = ["AF-only", "shared", "LW-only", "AF all", "LW all", "UNION"]
    colkey = {"AF-only": "af_only", "shared": "shared", "LW-only": "lw_only",
              "AF all": "af_all", "LW all": "lw_all", "UNION": "union"}
    print(f"{'marker':14}" + "".join(f"{c:>9}" for c in cols), file=out)
    for m in RIGOR:
        row = []
        for c in cols:
            k, n = C.prevalence(C.stratum(c), m)
            row.append(N.rate(f"rigor.{colkey[c]}.{m}", k, n))
        print(f"{m:14}" + "".join(f"{x:>9}" for x in row), file=out)
    for m in DIAG:
        k, n = C.prevalence(V, m)
        N.rate(f"rigor.union.{m}", k, n)
        print(f"{m:14}" + f"{N[f'rigor.union.{m}.pct']:>54} (union only; diagnostic)", file=out)
    fam2 = sum(1 for r in V if C.flags[r["_pid"]]["_families"] >= 2)
    fam3 = sum(1 for r in V if C.flags[r["_pid"]]["_families"] >= 3)
    N.rate("rigor.union.model_families_2plus", fam2, len(V))
    N.rate("rigor.union.model_families_3plus", fam3, len(V))
    print(f"{'≥2 families':14}" + f"{N['rigor.union.model_families_2plus.pct']:>54} "
          f"(crude name count; construct-validity check on multi_model)", file=out)
    print(f"{'≥3 families':14}" + f"{N['rigor.union.model_families_3plus.pct']:>54}", file=out)

    print("\nsource-readme claims, and the gap to this instrument on the matching corpus:", file=out)
    gap_rows = [("af", "seeds_variance", "seeds_strict", "af_all"),
                ("af", "limitations", "limitations", "af_all"),
                ("af", "arxiv", "arxiv", "af_all"),
                ("af", "negative", "neg_result", "af_all"),
                ("af", "multi_model", "multi_model", "af_all"),
                ("lw", "seeds", "seeds_loose", "lw_all"),
                ("lw", "errorbar", "errorbar", "lw_all"),
                ("lw", "n_equals", "n_equals", "lw_all"),
                ("lw", "prereg", "prereg", "lw_all"),
                ("lw", "ablation", "ablation", "lw_all"),
                ("lw", "baseline", "baseline", "lw_all"),
                ("lw", "heldout", "heldout", "lw_all"),
                ("lw", "arxiv", "arxiv", "lw_all")]
    print(f"  {'source claim':28}{'claimed':>9}{'ours':>9}{'gap':>8}", file=out)
    for corp, claim, marker, col in gap_rows:
        claimed = SOURCE_CLAIMS[f"{corp}.{claim}"]
        N.set(f"source_claims.{corp}.{claim}", claimed)
        ours = N[f"rigor.{col}.{marker}.pct"]
        gap = N.set(f"instrument_gap.{corp}.{claim}", round(ours - claimed, 1))
        flag = "  <-- >3pt" if abs(gap) > 3 else ""
        print(f"  {corp + ' ' + claim:28}{claimed:>9}{ours:>9}{gap:>8}{flag}", file=out)
    N.set("source_claims.af.stat_test_or_interval", SOURCE_CLAIMS["af.stat_test_or_interval"])

    # -------------------------------------------------------- 1.3e topic trends
    rule("1.3e  TOPIC PREVALENCE BY HALF-YEAR, ONE INSTRUMENT (% of posts in period)")
    for lbl, key, rs in [("UNION", "union", V), ("AF subset", "af", AF), ("LW subset", "lw", LW)]:
        g = collections.defaultdict(list)
        for r in rs:
            g[half(r["date"])].append(r)
        print(f"\n-- {lbl}  n: " + "  ".join(f"{p}={len(g[p])}" for p in PERIODS), file=out)
        print(f"{'topic':14}" + "".join(f"{p:>9}" for p in PERIODS), file=out)
        for t in TOPIC:
            row = []
            for p in PERIODS:
                sub = g[p]
                k = sum(1 for r in sub if C.flags[r["_pid"]][t])
                N.rate(f"topic.{key}.{t}.{p}", k, len(sub))
                row.append(fmt0(k, len(sub)))
            print(f"{t:14}" + "".join(f"{x:>9}" for x in row), file=out)
    print("\n  2026H2 is 56 days of a 184-day period. Do not read a trend off the last column.", file=out)

    # ------------------------------------------------------- 1.3f artifact layer
    rule("1.3f  THE ARTIFACT LAYER AND THE INVISIBLE DEPENDENCY LAYER")
    for lbl, key, rs in [("AF", "af", AF), ("LW", "lw", LW), ("UNION", "union", V)]:
        mention = [r for r in rs if C.gh_mentions[r["_pid"]]]
        null_m = [r for r in mention if not r["github-link"]]
        N.rate(f"artifact.{key}.mentions_github", len(mention), len(rs))
        N.set(f"artifact.{key}.own_repo_assigned", sum(1 for r in rs if r["github-link"]))
        N.rate(f"artifact.{key}.mentions_but_null", len(null_m), len(mention))
        print(f"{lbl:6} n={len(rs):>3}  mention github {len(mention):>3} "
              f"({fmt0(len(mention), len(rs))})  "
              f"assigned own-repo {N[f'artifact.{key}.own_repo_assigned']:>3}  "
              f"mentions-but-null {len(null_m):>3} "
              f"({fmt0(len(null_m), len(mention))} of mentioners discarded)", file=out)

    ra = collections.Counter(filter(None, (repo(r["github-link"]) for r in AF)))
    rl = collections.Counter(filter(None, (repo(r["github-link"]) for r in LW)))
    # Own-project repos counted over the UNION, one vote per post. The pre-2026-08-25 version of
    # this script summed the two per-corpus counters, which double-counted the 149 shared posts.
    ru = collections.Counter(filter(None, (repo(r["github-link"]) for r in V)))
    N.set("repos.af_distinct", len(ra))
    N.set("repos.lw_distinct", len(rl))
    N.set("repos.shared_distinct", len(set(ra) & set(rl)))
    N.set("repos.union_of_sets", len(set(ra) | set(rl)))
    N.set("repos.union_distinct", len(ru))
    N.set("repos.claimed_by_gt1", sum(1 for v in ru.values() if v > 1))
    N.set("repos.claimed_by_gt2", sum(1 for v in ru.values() if v > 2))
    print(f"\ndistinct own-project repos: AF {len(ra)}  LW {len(rl)}  shared {len(set(ra)&set(rl))}  "
          f"|AF u LW| {len(set(ra)|set(rl))}  counted over the union {len(ru)}", file=out)
    print(f"  (the two differ by {len(set(ra)|set(rl)) - len(ru)}: the O2 post carries a different "
          f"repo in each corpus)", file=out)
    print(f"repos claimed by >1 union post: {N['repos.claimed_by_gt1']}   by >2: {N['repos.claimed_by_gt2']}", file=out)
    for k, c in sorted(((k, c) for k, c in ru.items() if c > 1), key=lambda x: (-x[1], x[0])):
        print(f"    {c}  {k}", file=out)

    cited = collections.Counter()
    for r in V:
        for k in C.gh_mentions[r["_pid"]]:
            cited[k] += 1
    own = set(ru)
    print("\nmost-cited repos across the union (distinct posts citing; * = never an own-project repo):", file=out)
    top_cited = cited.most_common(18)
    N.set("repos.most_cited", [[k, c, k not in own] for k, c in top_cited])
    for k, c in top_cited:
        print(f"  {c:>3}  {k}{'' if k in own else '  *'}", file=out)
    top7 = top_cited[:7]
    N.set("repos.top7_never_own", sum(1 for k, _ in top7 if k not in own))
    print(f"  of the top 7 most-cited, {N['repos.top7_never_own']} are never an own-project repo", file=out)

    # ---------------------------------------------------------- 1.4/O3 NNCO frame
    rule("1.4/O3  THE NNCO SAMPLING FRAME AGAINST THE OTHER TWO CORPORA")
    N.set("nnco.records", len(NN))
    N.set("nnco.technical", sum(1 for r in NN if r["technical"]))
    by_auth = collections.Counter(r["author"] for r in NN)
    tech_by_auth = collections.Counter(r["author"] for r in NN if r["technical"])
    for a, c in by_auth.items():
        N.set(f"nnco.records_by_author.{a.replace(' ', '_').lower()}", c)
    for a, c in tech_by_auth.items():
        N.set(f"nnco.technical_by_author.{a.replace(' ', '_').lower()}", c)
    print(f"NNCO records {len(NN)}  technical {N['nnco.technical']}", file=out)
    print("by author:", dict(by_auth), file=out)
    print("technical by author:", dict(tech_by_auth), file=out)
    print("domains:", dict(collections.Counter(
        re.sub(r"^https?://", "", r["url"]).split("/")[0] for r in NN)), file=out)
    nn_words = N.set("nnco.technical_words.nanda",
                     sum(int(r["words"]) for r in NN if r["author"] == "Neel Nanda" and r["technical"]))
    ol_words = N.set("nnco.technical_words.olah",
                     sum(int(r["words"]) for r in NN if r["author"] == "Chris Olah" and r["technical"]))
    print(f"technical words (manifest `words` field): Nanda {nn_words:,}  Olah {ol_words:,}", file=out)
    print("  NOTE: the NNCO readme's Fact 2 table reports 81,162 / 45,247 from analysis/features.json,\n"
          "  which counts post-processed text. Different instrument, same corpus.", file=out)

    nanda = [r for r in V if "neel nanda" in (r["author"] or "").lower()]
    N.set("nanda.union_posts", len(nanda))
    N.set("nanda.union_words", sum(int(r["word_count"]) for r in nanda))
    N.set("nanda.union_first_date", min(r["date"] for r in nanda))
    N.set("nanda.union_last_date", max(r["date"] for r in nanda))
    N.set("nanda.union_first_author", sum(1 for r in nanda if authors_of(r) and authors_of(r)[0] == "Neel Nanda"))
    N.set("nanda.union_with_repo", sum(1 for r in nanda if r["github-link"]))
    tot = nn_words + N["nanda.union_words"]
    N.rate("nanda.nnco_capture_of_technical_words", nn_words, tot)
    print(f"\nNeel Nanda in AF u LW : {len(nanda)} posts, {N['nanda.union_words']:,} words, "
          f"{N['nanda.union_first_date']} -> {N['nanda.union_last_date']}", file=out)
    print(f"  as first author     : {N['nanda.union_first_author']}", file=out)
    print(f"  with own repo       : {N['nanda.union_with_repo']}", file=out)
    print(f"  NNCO captures {fmt0(nn_words, tot)} of the technical "
          f"words attributed to him across both collections", file=out)
    un_titles = {norm_title(r["title"]) for r in V}
    N.set("nnco.titles_also_in_union", sum(1 for r in NN if norm_title(r["title"]) in un_titles))
    N.set("nnco.records_hosted_on_forums", sum(
        1 for r in NN if "lesswrong" in r["url"] or "alignmentforum" in r["url"]))
    print(f"  NNCO titles also present in AF u LW: {N['nnco.titles_also_in_union']}", file=out)
    print(f"  NNCO records hosted on lesswrong/alignmentforum: {N['nnco.records_hosted_on_forums']}", file=out)

    # ------------------------------------------------------------ 1.2 union shape
    rule("1.2  UNION AGGREGATES")
    allA, firstA = collections.Counter(), collections.Counter()
    for r in V:
        parts = authors_of(r)
        if parts:
            firstA[parts[0]] += 1
        allA.update(parts)
    ks = [int(r["karma"]) for r in V]
    ws = [int(r["word_count"]) for r in V]
    N.set("union.posts", len(V))
    N.set("union.words", sum(ws))
    N.set("union.words_millions", round(sum(ws) / 1e6, 2))
    N.median("union.words", ws)
    N.median("union.karma", ks)
    N.set("union.karma.mean", round(st.mean(ks), 1))
    N.set("union.karma.min", min(ks))
    N.set("union.karma.max", max(ks))
    N.rate("union.own_repo", sum(1 for r in V if r["github-link"]), len(V))
    N.set("union.with_readme", sum(1 for r in V if r["github-readme"]))
    N.set("union.distinct_authors", len(allA))
    N.set("union.distinct_first_authors", len(firstA))
    N.rate("union.single_author", sum(1 for r in V if "," not in (r["author"] or "")), len(V))
    N.rate("union.authors_appearing_once", sum(1 for c in allA.values() if c == 1), len(allA))
    N.rate("union.first_authors_appearing_once", sum(1 for c in firstA.values() if c == 1), len(firstA))
    N.set("union.author_slots", sum(allA.values()))
    N.rate("union.top20_author_share", sum(c for _, c in allA.most_common(20)), sum(allA.values()))
    print(f"posts {len(V)}  words {sum(ws):,}  median words {N['union.words.median']:.0f} "
          f"CI {N['union.words.median_ci95']}", file=out)
    print(f"karma median {N['union.karma.median']:.0f} CI {N['union.karma.median_ci95']}  "
          f"mean {N['union.karma.mean']}  min {min(ks)}  max {max(ks)}", file=out)
    print(f"with own repo {N['union.own_repo.k']} ({N['union.own_repo.pct']}%, CI "
          f"{N['union.own_repo.ci95']})  with README {N['union.with_readme']}", file=out)
    print(f"distinct authors {len(allA)}  distinct first authors {len(firstA)}  "
          f"single-author posts {N['union.single_author.k']} "
          f"({fmt0(N['union.single_author.k'], len(V))})", file=out)
    print(f"authors appearing exactly once {N['union.authors_appearing_once.k']} "
          f"({fmt0(N['union.authors_appearing_once.k'], len(allA))})   first authors appearing once "
          f"{fmt0(N['union.first_authors_appearing_once.k'], len(firstA))}", file=out)
    print(f"top-20 authors hold "
          f"{fmt0(N['union.top20_author_share.k'], N['union.top20_author_share.n'])} of "
          f"{sum(allA.values())} author-slots", file=out)
    N.set("union.top_authors", [[a, c] for a, c in allA.most_common(15)])
    print("top 15 by author-slots:", allA.most_common(15), file=out)
    second = allA.most_common(2)[1][1]
    N.set("union.top_author_lead_ratio", round(allA.most_common(1)[0][1] / second, 2))

    print("\ntop 12 union posts by karma:", file=out)
    top12 = sorted(V, key=lambda r: -int(r["karma"]))[:12]
    tags12 = []
    for r in top12:
        tag = "AF+LW" if r["_pid"] in BOTH else r["_src"]
        tags12.append(tag)
        print(f"  {r['karma']:>4} {r['date']} [{tag:>5}] repo={'Y' if r['github-link'] else 'n'} "
              f"{r['title'][:60]}", file=out)
    N.set("o6.top12.shared", tags12.count("AF+LW"))
    N.set("o6.top12.af_only", tags12.count("AF"))
    N.set("o6.top12.lw_only", tags12.count("LW"))
    N.set("o6.union_max_karma", int(top12[0]["karma"]))
    N.set("union.top12_karma", [int(r["karma"]) for r in top12])
    print(f"  of the top 12: {tags12.count('AF+LW')} shared, {tags12.count('AF')} AF-only, "
          f"{tags12.count('LW')} LW-only", file=out)

    # ------------------------------------------------------- 1.4/O8-O9 label hygiene
    rule("1.4/O8-O9  LABEL HYGIENE")
    raw = collections.Counter(r["project_type"] for r in AF)
    N.set("o8.raw_labels", len(raw))
    N.set("o8.normalised_rows", len(set(PROJECT_TYPE_MAP.values())))
    ok, got = reproduces_af_table(AF)
    N.set("o8.mapping_reproduces_af_readme_table", ok)
    print(f"AF project_type: {len(raw)} raw labels in the JSON, "
          f"{len(set(PROJECT_TYPE_MAP.values()))} normalised rows in the AF readme table", file=out)
    for k, c in raw.most_common():
        print(f"  {c:>3}  {k:32} -> {PROJECT_TYPE_MAP[k]}", file=out)
    print(f"\nshipped mapping reproduces the AF readme's published table exactly: {ok}", file=out)
    for k in sorted(got):
        N.set(f"o8.normalised.{k}", got[k])
        print(f"  {k:22} {got[k]:>4}   (AF readme: {AF_README_TABLE[k]})", file=out)

    conf = collections.Counter(r["confidence"] for r in LW)
    for k, c in conf.items():
        N.set(f"o9.lw_confidence.{k}", c)
    print("\nLW confidence:", dict(conf), file=out)
    cx = collections.Counter((r["confidence"], r["_pid"] in BOTH) for r in LW)
    N.set("o9.shared_high", cx[("high", True)])
    N.set("o9.shared_medium", cx[("medium", True)])
    N.set("o9.shared_low", cx[("low", True)])
    N.set("o9.dropped_by_high_filter", cx[("medium", True)] + cx[("low", True)])
    print("LW confidence x in-AF:", dict(cx), file=out)
    print(f"  filtering LW on confidence=high discards {N['o9.dropped_by_high_filter']} posts that "
          f"AF promoted", file=out)
    rs_status = collections.Counter(r["github_readme_status"] for r in LW)
    for k, c in rs_status.items():
        N.set(f"o9.lw_readme_status.{k.replace('-', '_')}", c)
    print("LW github_readme_status:", dict(rs_status), file=out)
    N.set("o9.lw_distinct_tags", len({t for r in LW for t in (r["tags"] or [])}))
    N.set("o9.lw_posts_without_tags", sum(1 for r in LW if not r["tags"]))
    print(f"LW tags: {N['o9.lw_distinct_tags']} distinct, "
          f"{N['o9.lw_posts_without_tags']} posts carry none "
          f"(the field exists and is unused by every analysis so far)", file=out)
    N.set("af.additional_github_links_nonempty",
          sum(1 for r in AF if r["additional_github_links"]))
    print(f"AF additional_github_links non-empty: {N['af.additional_github_links_nonempty']}", file=out)

    # ------------------------------------------------------- 1.4/O7 near-duplicates
    rule("1.4/O7  NEAR-DUPLICATE POSTS IN THE UNION")
    dups = near_duplicates(V)
    N.set("o7.pairs", len(dups))
    for j, d1, d2, t1, t2, p1, p2 in dups:
        print(f"   jaccard {j}  {d1} / {d2}\n     {t1[:60]}\n     {t2[:60]}", file=out)
    print(f"  total near-duplicate pairs (same first author, Jaccard >= 0.6): {len(dups)}", file=out)
    N.set("o7.exact_title_pairs", sum(1 for d in dups if d[0] == 1.0))

    # ------------------------------------------------------------- 1.4/O10 meta layer
    rule("1.4/O10  THE META LAYER")
    print(f"three source readmes + the retracted predecessor: {readme_kb} KB over "
          f"{N['union.words']:,} words of primary text", file=out)
    print(f"research specs proposed by the three sources: {total_recs} "
          f"(AF {recs['af']}, LW {recs['lw']}, NNCO {recs['nnco']})", file=out)
    print("executable artifacts shipped alongside them: NNCO's analysis/audit.py, and this script.", file=out)
    print("HOW MANY OF THOSE SPECS HAVE BEEN EXECUTED IS NOT MEASURED HERE -- it is a judgment\n"
          "from reading the three directories, and readme.md tiers it [INFERRED].", file=out)

    if show_matches:
        rule(f"INSTRUMENT INSPECTION  ({show_matches} random matches per pattern, seed 0)")
        show_instrument(C, show_matches, out)
    return N


def near_duplicates(V, threshold=0.6):
    def toks(t):
        return {w for w in re.findall(r"[a-z]+", (t or "").lower()) if len(w) > 4}

    index = collections.defaultdict(list)
    for r in V:
        for w in toks(r["title"]):
            index[w].append(r)
    seen, dups = set(), []
    for w, rs in index.items():
        if len(rs) > 12:
            continue
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = rs[i], rs[j]
                key = tuple(sorted((a["_pid"], b["_pid"])))
                if key in seen:
                    continue
                seen.add(key)
                ta, tb = toks(a["title"]), toks(b["title"])
                if not (ta | tb):
                    continue
                jac = len(ta & tb) / len(ta | tb)
                if jac >= threshold and a["author"].split(",")[0] == b["author"].split(",")[0]:
                    lo, hi = sorted([a, b], key=lambda r: r["date"])
                    dups.append((round(jac, 2), lo["date"], hi["date"], lo["title"], hi["title"],
                                 lo["_pid"], hi["_pid"]))
    return sorted(dups, reverse=True)


def show_instrument(C, k, out=sys.stdout):
    """Print k random matches with context for every pattern, so false positives are visible."""
    rng = random.Random(0)
    for label, patterns in [("RIGOR", RIGOR), ("TOPIC", TOPIC), ("DIAG", DIAG)]:
        for name, pat in patterns.items():
            rx = re.compile(pat, re.I)
            hits = []
            for r in C.V:
                body = r["article-content"] or ""
                for m in rx.finditer(body):
                    ctx = body[max(0, m.start() - 55):m.end() + 55].replace("\n", " ")
                    hits.append(ctx)
            print(f"\n== {label}.{name}: {len(hits)} raw hits in "
                  f"{sum(1 for r in C.V if C.flags[r['_pid']][name])} posts", file=out)
            for s in rng.sample(hits, min(k, len(hits))):
                print(f"   ...{s}...", file=out)


# ------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.expanduser("~"),
                    help="directory containing the three corpus directories (default: $HOME)")
    ap.add_argument("--src-union", default=None,
                    help="rebuild the AF/LW side from this union.json instead of the raw JSONs")
    ap.add_argument("--json", default=os.path.join(HERE, "numbers.json"),
                    help="where to write the numbers (default: numbers.json beside this script)")
    ap.add_argument("--no-json", action="store_true", help="do not write numbers.json")
    ap.add_argument("--quiet", action="store_true", help="suppress the text report")
    ap.add_argument("--show-matches", type=int, default=0, metavar="K",
                    help="print K random matches per instrument pattern")
    ap.add_argument("--api-spotcheck", action="store_true",
                    help="re-query the LessWrong GraphQL API and refresh api_spotcheck.json")
    a = ap.parse_args(argv)

    paths = src_paths(a.src)
    if a.api_spotcheck:
        try:
            got = api_spotcheck()
            print(f"api_spotcheck.json refreshed: baseScore {got['baseScore']} "
                  f"afBaseScore {got['afBaseScore']}", file=sys.stderr)
        except Exception as e:  # network is not guaranteed; the cached file stays authoritative
            print(f"api spotcheck failed ({e}); keeping any cached api_spotcheck.json", file=sys.stderr)

    if a.src_union:
        AF, LW, NN = load_from_union(a.src_union, paths)
    else:
        AF, LW, NN = load_raw(paths)
    C = Corpus(AF, LW, NN)
    N = Numbers()
    out = open(os.devnull, "w") if a.quiet else sys.stdout
    build(C, N, paths, out=out, show_matches=a.show_matches)
    if not a.no_json:
        with open(a.json, "w") as fh:
            json.dump(dict(sorted(N.items())), fh, indent=1, sort_keys=True)
        print(f"\nwrote {len(N)} keys to {a.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
