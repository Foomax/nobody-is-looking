#!/usr/bin/env python3
"""
analyze.py -- cross-cutting meta-analysis of the joined corpus.

Complements the two analyses that already exist:
  meta.py        -> readme.md          : how the corpora were COLLECTED
  p3/findings.py -> p3/findings.md     : what the posts CLAIM
this script     -> results.md          : themes, difference patterns, and OUTLIERS across
                                         the axes neither of the above used --
                                         LessWrong's human-assigned `tags` (180 distinct,
                                         previously unused), the model landscape, the
                                         dependency graph, author structure, and
                                         multi-axis outlier detection.

Reuses p3/findings.py's loader so the denominators are identical (728 substantive projects).
Every number printed is emitted to analysis_numbers.json.

Usage: python3 analyze.py [--quiet]
"""
import argparse, collections, json, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "p3"))
import findings as F  # noqa: E402

POSITIVE = {"positive", "benchmark", "method", "dataset"}
NEGATIVE = {"negative", "null"}


def wilson(k, n):
    return F.wilson(k, n)


def pct(k, n):
    return F.pct(k, n)


def boot_median_ci(xs, resamples=1000, seed=0):
    import random
    xs = sorted(xs)
    if len(xs) < 3:
        return None
    r = random.Random(seed)
    m = sorted(st.median(r.choices(xs, k=len(xs))) for _ in range(resamples))
    return [round(m[int(0.025 * resamples)], 1), round(m[int(0.975 * resamples)], 1)]


class N(dict):
    def set(self, k, v):
        self[k] = v
        return v

    def rate(self, k, a, b):
        self.set(f"{k}.k", a); self.set(f"{k}.n", b)
        p = self.set(f"{k}.pct", pct(a, b)); self.set(f"{k}.ci95", wilson(a, b))
        return p


def two_proportion_z(k1, n1, k2, n2):
    """Unpooled-CI-friendly z for a difference of proportions. Reported, never used as a gate."""
    if not n1 or not n2:
        return None
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return round((p1 - p2) / se, 2) if se else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    out = open(os.devnull, "w") if a.quiet else sys.stdout
    n = N()

    def rule(t):
        print(f"\n{'=' * 78}\n{t}\n{'=' * 78}", file=out)

    U, C = F.load()
    D = F.dedup(C)
    S = {k: c for k, c in D.items() if c.get("primary_claim") != "STUB"}
    # attach union-side fields the P3 loader does not carry
    for pid, c in S.items():
        u = U[pid]
        c["_tags"] = (u["lw"] or {}).get("tags") or []
        c["_authors"] = u["authors"]
        c["_wc"] = u["word_count"]
        c["_lw_conf"] = (u["lw"] or {}).get("confidence")
        c["_lw_topic"] = (u["lw"] or {}).get("topic")
        c["_af_type"] = (u["af"] or {}).get("project_type_norm")
    n.set("base.union", len(U)); n.set("base.projects", len(D)); n.set("base.substantive", len(S))
    print(f"union {len(U)}  projects {len(D)}  substantive {len(S)}", file=out)

    def sign(c):
        t = c.get("claim_type")
        if t in NEGATIVE:
            return "neg"
        if t in POSITIVE or t == "replication":
            return "pos"
        return "other"

    # ================================================================ 1  THEMES (tags)
    rule("1  THEMES -- LessWrong human-assigned tags (previously unused axis)")
    tagged = [c for c in S.values() if c["_tags"]]
    n.rate("tags.coverage", len(tagged), len(S))
    tc = collections.Counter(t for c in tagged for t in c["_tags"])
    n.set("tags.distinct", len(tc))
    n.set("tags.median_per_post", st.median([len(c["_tags"]) for c in tagged]))
    print(f"tagged {len(tagged)}/{len(S)}  distinct tags {len(tc)}  "
          f"median tags/post {n['tags.median_per_post']}", file=out)
    # long tail
    n.set("tags.used_once", sum(1 for v in tc.values() if v == 1))
    top10 = tc.most_common(10)
    n.set("tags.top10_share_pct", pct(sum(v for _, v in top10), sum(tc.values())))
    print(f"tags used once: {n['tags.used_once']}   top-10 tags cover "
          f"{n['tags.top10_share_pct']}% of all tag assignments", file=out)

    # per-tag profile (>= 10 posts)
    print(f"\n{'tag':38s} {'n':>4} {'neg%':>6} {'code%':>6} {'base%':>6} {'medK':>5} {'medWC':>6} {'nFam':>5}", file=out)
    tag_rows = []
    for t, k in tc.most_common():
        if k < 10:
            continue
        g = [c for c in tagged if t in c["_tags"]]
        neg = sum(1 for c in g if sign(c) == "neg")
        code = sum(1 for c in g if c.get("reproducible_in_principle") in ("code", "code+data"))
        base = sum(1 for c in g if F.design(c, "baseline"))
        row = dict(tag=t, n=len(g),
                   neg_pct=pct(neg, len(g)), neg_ci=wilson(neg, len(g)),
                   code_pct=pct(code, len(g)), baseline_pct=pct(base, len(g)),
                   median_karma=st.median([c["_karma"] for c in g]),
                   median_wc=st.median([c["_wc"] for c in g]),
                   median_families=st.median([c.get("n_model_families") or 0 for c in g]))
        tag_rows.append(row)
        print(f"{t[:38]:38s} {row['n']:4d} {row['neg_pct']:6.1f} {row['code_pct']:6.1f} "
              f"{row['baseline_pct']:6.1f} {row['median_karma']:5.0f} {row['median_wc']:6.0f} "
              f"{row['median_families']:5.1f}", file=out)
    n.set("tags.profiles", tag_rows)

    # tag co-occurrence: lift over independence, for pairs seen >= 5 times
    pairs = collections.Counter()
    for c in tagged:
        ts = sorted(set(c["_tags"]))
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                pairs[(ts[i], ts[j])] += 1
    T = len(tagged)
    lifts = []
    for (x, y), k in pairs.items():
        if k < 5 or tc[x] < 10 or tc[y] < 10:
            continue
        exp = tc[x] * tc[y] / T
        lifts.append((round(k / exp, 2), k, x, y))
    lifts.sort(reverse=True)
    n.set("tags.top_lift_pairs", [dict(lift=l, n=k, a=x, b=y) for l, k, x, y in lifts[:12]])
    print("\nstrongest tag pairs (observed/expected, n>=5):", file=out)
    for l, k, x, y in lifts[:12]:
        print(f"  x{l:<5.2f} n={k:<3d} {x}  +  {y}", file=out)

    # tag vs phenomenon: do the two independent labellers agree on structure?
    rule("1b  TAG (human) vs PHENOMENON (LLM) -- two independent label systems")
    ph = collections.Counter(c["_phenomenon"] for c in S.values())
    n.set("phenomena.distinct", len(ph))
    n.set("phenomena.singletons", sum(1 for v in ph.values() if v == 1))
    n.rate("phenomena.singleton_posts", sum(v for v in ph.values() if v == 1), len(S))
    print(f"phenomena {len(ph)} (singletons {n['phenomena.singletons']}) vs tags {len(tc)} "
          f"(used-once {n['tags.used_once']})", file=out)
    # purity: for the biggest tags, how concentrated are the phenomena inside?
    print(f"\n{'tag':38s} {'n':>4} {'distinct phen':>13} {'top phen share%':>15}", file=out)
    purity = []
    for t, k in tc.most_common(12):
        g = [c for c in tagged if t in c["_tags"]]
        p = collections.Counter(c["_phenomenon"] for c in g)
        share = pct(p.most_common(1)[0][1], len(g))
        purity.append(dict(tag=t, n=len(g), distinct_phenomena=len(p), top_share_pct=share,
                           top_phenomenon=p.most_common(1)[0][0]))
        print(f"{t[:38]:38s} {len(g):4d} {len(p):13d} {share:15.1f}", file=out)
    n.set("tags.purity", purity)

    # ================================================================ 2  MODEL LANDSCAPE
    rule("2  MODEL LANDSCAPE -- what the field actually runs on")
    fam = collections.Counter()
    openw = collections.Counter()
    for c in S.values():
        ms = c.get("models") or []
        fams = set()
        for m in ms:
            f = (m.get("family") or "").strip()
            if not f:
                continue
            fams.add(f)
            openw[bool(m.get("open_weight"))] += 1
        fam.update(fams)
    n.set("models.distinct_families", len(fam))
    n.set("models.top20", [dict(family=f, posts=k, pct=pct(k, len(S))) for f, k in fam.most_common(20)])
    print(f"{len(fam)} distinct families named. Top 20 by posts studying them:", file=out)
    for f, k in fam.most_common(20):
        print(f"  {k:4d}  {pct(k,len(S)):5.1f}%  {f}", file=out)
    # open-weight share, per post (a post counts as open if ANY model it studies is open)
    any_open = sum(1 for c in S.values() if any(m.get("open_weight") for m in (c.get("models") or [])))
    all_open = sum(1 for c in S.values() if (c.get("models") or []) and
                   all(m.get("open_weight") for m in c["models"]))
    no_model = sum(1 for c in S.values() if not (c.get("models") or []))
    n.rate("models.any_open", any_open, len(S))
    n.rate("models.all_open", all_open, len(S))
    n.rate("models.none_named", no_model, len(S))
    print(f"\nposts with >=1 open-weight model {any_open} ({n['models.any_open.pct']}%)  "
          f"all-open {all_open} ({n['models.all_open.pct']}%)  no model named {no_model}", file=out)
    # monoculture
    nf = [c.get("n_model_families") or 0 for c in S.values()]
    one = sum(1 for x in nf if x == 1)
    n.rate("models.single_family", one, len(S))
    n.set("models.median_families", st.median(nf))
    n.set("models.median_families_ci95", boot_median_ci(nf))
    print(f"single-family posts {one} ({n['models.single_family.pct']}%)  "
          f"median families {n['models.median_families']} {n['models.median_families_ci95']}", file=out)

    # drift over time
    print(f"\n{'period':8s} {'n':>4} {'anyOpen%':>9} {'medFam':>7} {'neg%':>6} {'code%':>6} {'base%':>6}", file=out)
    periods = sorted({c["_period"] for c in S.values()})
    per_rows = []
    for p in periods:
        g = [c for c in S.values() if c["_period"] == p]
        ao = sum(1 for c in g if any(m.get("open_weight") for m in (c.get("models") or [])))
        neg = sum(1 for c in g if sign(c) == "neg")
        code = sum(1 for c in g if c.get("reproducible_in_principle") in ("code", "code+data"))
        base = sum(1 for c in g if F.design(c, "baseline"))
        row = dict(period=p, n=len(g), any_open_pct=pct(ao, len(g)),
                   any_open_ci=wilson(ao, len(g)),
                   median_families=st.median([c.get("n_model_families") or 0 for c in g]),
                   neg_pct=pct(neg, len(g)), code_pct=pct(code, len(g)),
                   baseline_pct=pct(base, len(g)))
        per_rows.append(row)
        print(f"{p:8s} {len(g):4d} {row['any_open_pct']:9.1f} {row['median_families']:7.1f} "
              f"{row['neg_pct']:6.1f} {row['code_pct']:6.1f} {row['baseline_pct']:6.1f}", file=out)
    n.set("periods", per_rows)

    # ================================================================ 3  DIFFERENCE PATTERNS
    rule("3  PATTERNS IN THE DIFFERENCES -- paired contrasts")
    def contrast(key, label, pred):
        A = [c for c in S.values() if pred(c)]
        B = [c for c in S.values() if not pred(c)]
        if not A or not B:
            return
        def prof(g):
            return dict(
                n=len(g),
                neg=sum(1 for c in g if sign(c) == "neg"),
                code=sum(1 for c in g if c.get("reproducible_in_principle") in ("code", "code+data")),
                base=sum(1 for c in g if F.design(c, "baseline")),
                abl=sum(1 for c in g if F.design(c, "ablation")),
                seeds=sum(1 for c in g if (c.get("design") or {}).get("seeds_n")),
                unc=sum(1 for c in g if F.uncertainty(c) not in (None, "none")),
                contra=sum(1 for c in g if c.get("contradicts_or_qualifies")),
                lim=st.median([len(c.get("limitations_stated") or []) for c in g]),
                karma=st.median([c["_karma"] for c in g]),
                wc=st.median([c["_wc"] for c in g]),
                fam=st.median([c.get("n_model_families") or 0 for c in g]),
            )
        pa, pb = prof(A), prof(B)
        row = dict(label=label, n_a=pa["n"], n_b=pb["n"])
        print(f"\n-- {label}:  {pa['n']} vs {pb['n']}", file=out)
        print(f"   {'marker':14s} {'group A':>16} {'group B':>16} {'z':>6}", file=out)
        for m in ("neg", "code", "base", "abl", "seeds", "unc", "contra"):
            za = two_proportion_z(pa[m], pa["n"], pb[m], pb["n"])
            row[m] = dict(a_pct=pct(pa[m], pa["n"]), a_ci=wilson(pa[m], pa["n"]),
                          b_pct=pct(pb[m], pb["n"]), b_ci=wilson(pb[m], pb["n"]), z=za)
            print(f"   {m:14s} {pct(pa[m],pa['n']):7.1f}% {str(wilson(pa[m],pa['n'])):>8} "
                  f"{pct(pb[m],pb['n']):7.1f}% {str(wilson(pb[m],pb['n'])):>8} {za if za is not None else 0:6.2f}", file=out)
        for m in ("lim", "karma", "wc", "fam"):
            row["median_" + m] = [pa[m], pb[m]]
            print(f"   median {m:8s} {pa[m]:15.1f} {pb[m]:16.1f}", file=out)
        n.set(f"contrast.{key}", row)

    contrast("af", "in Alignment Forum vs LessWrong-only", lambda c: c["_in_af"])
    contrast("mats", "MATS-tagged vs not", lambda c: "MATS Program" in c["_tags"])
    contrast("solo", "solo author vs team", lambda c: len(c["_authors"]) == 1)
    contrast("code", "ships code vs not",
             lambda c: c.get("reproducible_in_principle") in ("code", "code+data"))
    kmed = st.median([c["_karma"] for c in S.values()])
    contrast("karma", f"karma above median ({kmed:.0f}) vs at/below", lambda c: c["_karma"] > kmed)
    wmed = st.median([c["_wc"] for c in S.values()])
    contrast("length", f"longer than median ({wmed:.0f} words) vs not", lambda c: c["_wc"] > wmed)
    contrast("interp", "Interpretability-tagged vs not",
             lambda c: "Interpretability (ML & AI)" in c["_tags"])
    contrast("evalctl", "AI Control / Evaluations-tagged vs not",
             lambda c: bool({"AI Control", "AI Evaluations"} & set(c["_tags"])))
    contrast("open", "studies an open-weight model vs not",
             lambda c: any(m.get("open_weight") for m in (c.get("models") or [])))

    # ================================================================ 4  DEPENDENCY GRAPH
    rule("4  DEPENDENCY GRAPH -- what the field builds on")
    dep = collections.Counter()
    kind = collections.Counter()
    for c in S.values():
        for d in set(c.get("depends_on") or []):
            dep[d] += 1
            kind["arxiv" if d.lower().startswith("arxiv") else
                 "repo" if "/" in d else "other"] += 1
    n.set("deps.distinct", len(dep))
    n.set("deps.total_edges", sum(dep.values()))
    for k, v in kind.items():
        n.rate(f"deps.kind.{k}", v, sum(kind.values()))
    nodep = sum(1 for c in S.values() if not (c.get("depends_on") or []))
    n.rate("deps.posts_with_none", nodep, len(S))
    n.set("deps.indeg1_pct", pct(sum(1 for v in dep.values() if v == 1), len(dep)))
    print(f"{len(dep)} distinct dependencies, {sum(dep.values())} edges; "
          f"{n['deps.indeg1_pct']}% cited exactly once", file=out)
    print(f"kinds: {dict(kind)}   posts declaring no dependency: {nodep} "
          f"({n['deps.posts_with_none.pct']}%)", file=out)
    n.set("deps.top25", [dict(dep=d, in_degree=k,
                              kind=("arxiv" if d.lower().startswith("arxiv") else
                                    "repo" if "/" in d else "other"))
                         for d, k in dep.most_common(25)])
    print("\ntop 25 by in-degree:", file=out)
    for d, k in dep.most_common(25):
        print(f"  {k:3d}  {d}", file=out)
    # concentration
    tot = sum(dep.values())
    cum = 0
    for i, (_, k) in enumerate(dep.most_common(), 1):
        cum += k
        if cum >= tot * 0.5:
            n.set("deps.n_for_half_of_edges", i)
            break
    print(f"\n{n['deps.n_for_half_of_edges']} dependencies carry half of all "
          f"{tot} edges (of {len(dep)})", file=out)

    # ================================================================ 5  AUTHORS
    rule("5  AUTHOR STRUCTURE")
    first = collections.Counter(c["_authors"][0] for c in S.values() if c["_authors"])
    allau = collections.Counter(a for c in S.values() for a in c["_authors"])
    n.set("authors.distinct", len(allau))
    n.set("authors.distinct_first", len(first))
    n.rate("authors.one_post_only", sum(1 for v in first.values() if v == 1), len(first))
    n.set("authors.top_first", [dict(author=a, posts=k) for a, k in first.most_common(10)])
    n.set("authors.top_any", [dict(author=a, posts=k, first_author_posts=first.get(a, 0))
                              for a, k in allau.most_common(15)])
    print(f"{len(allau)} distinct authors, {len(first)} distinct first authors; "
          f"{n['authors.one_post_only.pct']}% of first authors appear exactly once", file=out)
    print("\nmost prolific by any-authorship (first-author count in brackets):", file=out)
    for a, k in allau.most_common(15):
        print(f"  {k:3d} [{first.get(a,0):2d}]  {a}", file=out)
    # gini on first-authorship
    vals = sorted(first.values())
    m = len(vals); s = sum(vals)
    gini = (2 * sum((i + 1) * v for i, v in enumerate(vals)) / (m * s)) - (m + 1) / m
    n.set("authors.first_author_gini", round(gini, 3))
    print(f"\nGini of first-authorship counts: {gini:.3f}", file=out)

    # ================================================================ 6  OUTLIERS
    rule("6  OUTLIERS")
    def top(key, label, fn, k=8, reverse=True):
        rows = sorted(S.values(), key=fn, reverse=reverse)[:k]
        recs = [dict(post_id=c["post_id"], title=c["_title"][:80], value=fn(c),
                     first_author=c["_first_author"], date=c["_date"],
                     phenomenon=c["_phenomenon"]) for c in rows]
        n.set(f"outliers.{key}", recs)
        print(f"\n-- {label}", file=out)
        for r in recs:
            print(f"   {str(r['value']):>7}  {r['date']}  {r['title'][:64]:64s}  {r['first_author']}", file=out)

    top("karma", "highest karma", lambda c: c["_karma"])
    top("words", "longest", lambda c: c["_wc"])
    top("families", "widest model sweep (n_model_families)", lambda c: c.get("n_model_families") or 0)
    top("deps", "most dependencies declared", lambda c: len(c.get("depends_on") or []))
    top("limitations", "most limitations stated", lambda c: len(c.get("limitations_stated") or []))
    top("future", "most future work proposed", lambda c: len(c.get("stated_future_work") or []))
    top("contra", "most prior work contradicted/qualified",
        lambda c: len(c.get("contradicts_or_qualifies") or []))

    # structural outliers
    print("\n-- structural", file=out)
    # (a) high karma, no code
    hi = sorted([c for c in S.values()
                 if c.get("reproducible_in_principle") == "neither"],
                key=lambda c: -c["_karma"])[:8]
    n.set("outliers.high_karma_no_code", [dict(post_id=c["post_id"], title=c["_title"][:80],
                                               karma=c["_karma"], first_author=c["_first_author"])
                                          for c in hi])
    print(f"   highest-karma posts with neither code nor data:", file=out)
    for c in hi:
        print(f"     {c['_karma']:4d}  {c['_title'][:70]}", file=out)
    # (b) lone dissenter: only negative post in a phenomenon that is otherwise all positive
    byp = collections.defaultdict(list)
    for c in S.values():
        byp[c["_phenomenon"]].append(c)
    lone = []
    for p, g in byp.items():
        if len(g) < 4:
            continue
        negs = [c for c in g if sign(c) == "neg"]
        if len(negs) == 1:
            c = negs[0]
            lone.append(dict(phenomenon=p, n=len(g), post_id=c["post_id"],
                             title=c["_title"][:80], karma=c["_karma"],
                             first_author=c["_first_author"], date=c["_date"],
                             claim=(c.get("primary_claim") or "")[:220]))
    lone.sort(key=lambda r: -r["n"])
    n.set("outliers.lone_dissenter", lone[:12])
    print(f"\n   lone negative result in an otherwise-positive phenomenon (n>=4): {len(lone)}", file=out)
    for r in lone[:12]:
        print(f"     [{r['n']:2d}] {r['phenomenon'][:38]:38s} k={r['karma']:4d}  {r['title'][:50]}", file=out)
    # (c) rigor outliers: all five design flags
    def dscore(c):
        d = c.get("design") or {}
        return sum(bool(d.get(f)) for f in ("baseline", "ablation", "held_out", "prereg", "human_eval")) \
            + (1 if d.get("seeds_n") else 0)
    ds = collections.Counter(dscore(c) for c in S.values())
    n.set("design.score_hist", {str(k): v for k, v in sorted(ds.items())})
    n.set("design.median_score", st.median([dscore(c) for c in S.values()]))
    print(f"\n   design-marker score histogram (0-6): {dict(sorted(ds.items()))}", file=out)
    topd = sorted(S.values(), key=lambda c: (-dscore(c), -c["_karma"]))[:8]
    n.set("outliers.most_rigorous", [dict(post_id=c["post_id"], title=c["_title"][:80],
                                          score=dscore(c), karma=c["_karma"],
                                          first_author=c["_first_author"]) for c in topd])
    print(f"   highest design-marker scores:", file=out)
    for c in topd:
        print(f"     {dscore(c)}/6  k={c['_karma']:4d}  {c['_title'][:60]}", file=out)
    n.rate("design.zero_markers", ds.get(0, 0), len(S))
    n.rate("design.five_plus", sum(v for k, v in ds.items() if k >= 5), len(S))

    # (d) composite unusualness: mean percentile distance from the median across axes
    axes = {
        "karma": lambda c: c["_karma"],
        "wc": lambda c: c["_wc"],
        "families": lambda c: c.get("n_model_families") or 0,
        "deps": lambda c: len(c.get("depends_on") or []),
        "limitations": lambda c: len(c.get("limitations_stated") or []),
        "future": lambda c: len(c.get("stated_future_work") or []),
        "design": dscore,
        "team": lambda c: len(c["_authors"]),
    }
    ids = list(S)
    ranks = {}
    for ax, fn in axes.items():
        vals = sorted((fn(S[i]), i) for i in ids)
        for r, (_, i) in enumerate(vals):
            ranks.setdefault(i, {})[ax] = r / (len(ids) - 1)
    comp = []
    for i in ids:
        d = st.mean(abs(v - 0.5) for v in ranks[i].values())
        comp.append((round(d, 4), i))
    comp.sort(key=lambda x: -x[0])
    n.set("outliers.composite", [dict(post_id=i, score=d, title=S[i]["_title"][:80],
                                      first_author=S[i]["_first_author"], date=S[i]["_date"],
                                      phenomenon=S[i]["_phenomenon"],
                                      axes={k: round(v, 2) for k, v in ranks[i].items()})
                                 for d, i in comp[:12]])
    print(f"\n   composite unusualness (mean |percentile - 0.5| over 8 axes), top 12:", file=out)
    for d, i in comp[:12]:
        print(f"     {d:.3f}  {S[i]['_title'][:60]:60s}  {S[i]['_first_author']}", file=out)
    n.set("outliers.composite_median", round(st.median([d for d, _ in comp]), 4))
    # most median post
    n.set("outliers.most_typical", [dict(post_id=i, score=d, title=S[i]["_title"][:80],
                                         phenomenon=S[i]["_phenomenon"])
                                    for d, i in comp[-5:]])

    # (e) tag-level outlier: tags whose negative rate is far from the corpus rate
    corpus_neg = sum(1 for c in S.values() if sign(c) == "neg")
    n.rate("corpus.negative", corpus_neg, len(S))
    devs = []
    for row in tag_rows:
        devs.append((abs(row["neg_pct"] - n["corpus.negative.pct"]), row))
    devs.sort(key=lambda x: -x[0])
    n.set("outliers.tag_negativity", [dict(tag=r["tag"], n=r["n"], neg_pct=r["neg_pct"],
                                           ci=r["neg_ci"]) for _, r in devs[:8]])
    print(f"\n   corpus negative rate {n['corpus.negative.pct']}% "
          f"{n['corpus.negative.ci95']}; tags furthest from it:", file=out)
    for _, r in devs[:8]:
        print(f"     {r['neg_pct']:5.1f}% {str(r['neg_ci']):>12}  n={r['n']:3d}  {r['tag']}", file=out)


    # ================================================================ 7  ATTENTION vs REPRODUCIBILITY
    rule("7  ATTENTION vs REPRODUCIBILITY -- the corpus's sharpest inverse pattern")
    def spearman(xs, ys):
        def rank(v):
            order = sorted(range(len(v)), key=lambda i: v[i])
            r = [0.0] * len(v); i = 0
            while i < len(order):
                j = i
                while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                    j += 1
                avg = (i + j) / 2 + 1
                for k in range(i, j + 1):
                    r[order[k]] = avg
                i = j + 1
            return r
        rx, ry = rank(xs), rank(ys)
        mx, my = st.mean(rx), st.mean(ry)
        num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
        den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
        return round(num / den, 3) if den else None

    ks = [c["_karma"] for c in S.values()]
    cs = [1 if c.get("reproducible_in_principle") in ("code", "code+data") else 0 for c in S.values()]
    n.set("attention.spearman_karma_code", spearman(ks, cs))
    print(f"Spearman(karma, ships-code) = {n['attention.spearman_karma_code']}  n={len(ks)}", file=out)

    order = sorted(S.values(), key=lambda c: c["_karma"])
    dec_rows = []
    print(f"\n{'decile':7s} {'karma range':>16} {'n':>4} {'code%':>18} {'neg%':>6} {'base%':>6} {'medFam':>7}", file=out)
    for d in range(10):
        g = order[d * len(order) // 10:(d + 1) * len(order) // 10]
        code = sum(1 for c in g if c.get("reproducible_in_principle") in ("code", "code+data"))
        neg = sum(1 for c in g if sign(c) == "neg")
        base = sum(1 for c in g if F.design(c, "baseline"))
        row = dict(decile=d + 1, karma_lo=g[0]["_karma"], karma_hi=g[-1]["_karma"], n=len(g),
                   code_pct=pct(code, len(g)), code_ci=wilson(code, len(g)),
                   neg_pct=pct(neg, len(g)), baseline_pct=pct(base, len(g)),
                   median_families=st.median([c.get("n_model_families") or 0 for c in g]))
        dec_rows.append(row)
        print(f"{d+1:<7d} {str(row['karma_lo'])+'-'+str(row['karma_hi']):>16} {len(g):4d} "
              f"{row['code_pct']:6.1f} {str(row['code_ci']):>11} {row['neg_pct']:6.1f} "
              f"{row['baseline_pct']:6.1f} {row['median_families']:7.1f}", file=out)
    n.set("attention.karma_deciles", dec_rows)

    # stratify: is it an age or a venue artifact?
    print("\nstratified code%% (top karma quartile vs bottom), within strata:", file=out)
    q = sorted([c["_karma"] for c in S.values()])
    q1, q3 = q[len(q) // 4], q[3 * len(q) // 4]
    strat = []
    def stratum(name, g):
        hi = [c for c in g if c["_karma"] >= q3]
        lo = [c for c in g if c["_karma"] <= q1]
        if len(hi) < 15 or len(lo) < 15:
            return
        ch = sum(1 for c in hi if c.get("reproducible_in_principle") in ("code", "code+data"))
        cl = sum(1 for c in lo if c.get("reproducible_in_principle") in ("code", "code+data"))
        r = dict(stratum=name, hi_n=len(hi), hi_code_pct=pct(ch, len(hi)), hi_ci=wilson(ch, len(hi)),
                 lo_n=len(lo), lo_code_pct=pct(cl, len(lo)), lo_ci=wilson(cl, len(lo)),
                 z=two_proportion_z(ch, len(hi), cl, len(lo)))
        strat.append(r)
        print(f"   {name:26s} hi {r['hi_code_pct']:5.1f}% (n={len(hi):3d})  "
              f"lo {r['lo_code_pct']:5.1f}% (n={len(lo):3d})  z={r['z']}", file=out)
    stratum("all", list(S.values()))
    for p in periods:
        stratum(f"period {p}", [c for c in S.values() if c["_period"] == p])
    stratum("in AF", [c for c in S.values() if c["_in_af"]])
    stratum("LW-only", [c for c in S.values() if not c["_in_af"]])
    stratum("solo author", [c for c in S.values() if len(c["_authors"]) == 1])
    stratum("team", [c for c in S.values() if len(c["_authors"]) > 1])
    stratum("interpretability", [c for c in S.values() if "Interpretability (ML & AI)" in c["_tags"]])
    n.set("attention.strata", strat)
    n.set("attention.karma_q1", q1); n.set("attention.karma_q3", q3)


    # mediation: model access
    print("\nkarma quintile x model access (the mediator):", file=out)
    print(f"   {'q':2s} {'anyOpen%':>9} {'code%':>7} {'code|open':>18} {'code|closed':>18}", file=out)
    o5 = sorted(S.values(), key=lambda c: c["_karma"])
    med_rows = []
    def isopen(c):
        return any(m.get("open_weight") for m in (c.get("models") or []))
    def ships(c):
        return c.get("reproducible_in_principle") in ("code", "code+data")
    for d in range(5):
        g = o5[d * len(o5) // 5:(d + 1) * len(o5) // 5]
        op = [c for c in g if isopen(c)]; cl = [c for c in g if not isopen(c)]
        r = dict(quintile=d + 1, n=len(g), any_open_pct=pct(len(op), len(g)),
                 code_pct=pct(sum(map(ships, g)), len(g)),
                 code_given_open_pct=pct(sum(map(ships, op)), len(op)), n_open=len(op),
                 code_given_open_ci=wilson(sum(map(ships, op)), len(op)),
                 code_given_closed_pct=pct(sum(map(ships, cl)), len(cl)), n_closed=len(cl),
                 code_given_closed_ci=wilson(sum(map(ships, cl)), len(cl)))
        med_rows.append(r)
        print(f"   {d+1:<2d} {r['any_open_pct']:9.1f} {r['code_pct']:7.1f} "
              f"{r['code_given_open_pct']:8.1f} (n={len(op):3d}) "
              f"{r['code_given_closed_pct']:8.1f} (n={len(cl):3d})", file=out)
    n.set("attention.mediation_quintiles", med_rows)
    for name, grp in (("open", [c for c in S.values() if isopen(c)]),
                      ("closed", [c for c in S.values() if not isopen(c)])):
        g = sorted(grp, key=lambda c: c["_karma"])
        hi, lo = g[3 * len(g) // 4:], g[:len(g) // 4]
        kh, kl = sum(map(ships, hi)), sum(map(ships, lo))
        n.set(f"attention.within_{name}", dict(hi_n=len(hi), hi_code_pct=pct(kh, len(hi)),
                                               hi_ci=wilson(kh, len(hi)), lo_n=len(lo),
                                               lo_code_pct=pct(kl, len(lo)), lo_ci=wilson(kl, len(lo)),
                                               z=two_proportion_z(kh, len(hi), kl, len(lo))))
        print(f"   within {name}-model posts: top-karma quartile code "
              f"{pct(kh,len(hi))}% vs bottom {pct(kl,len(lo))}%  "
              f"z={n[f'attention.within_{name}']['z']}", file=out)

    json.dump(n, open(os.path.join(HERE, "analysis_numbers.json"), "w"), indent=1, sort_keys=True)
    print(f"\nwrote analysis_numbers.json ({len(n)} keys)", file=sys.stderr)


if __name__ == "__main__":
    main()
