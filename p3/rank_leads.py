#!/usr/bin/env python3
"""
rank_leads.py -- the ranking half of R9 (orphaned-lead mining).

Consumes p3/leads/themed_*.json (written by the 6 clustering agents) and ranks themes by the
number of INDEPENDENT posts proposing them. readme.md R9: "the same lead proposed independently
by three abandoned projects is the signal, not a duplicate."

The six agents themed their chunks independently, so the same idea can arrive under slightly
different strings. `THEME_ALIASES` below is the cross-chunk merge map; it is deliberately small
and conservative, and `--show-unmerged` prints the full theme list so it can be extended by hand.

Usage:  python3 p3/rank_leads.py [--show-unmerged]
Writes: p3/leads_ranked.json, and appends lead.* keys to p3/findings_numbers.json
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

THEME_ALIASES = {
    "scale up to larger models": "scale to larger models",
    "scale to larger/frontier models": "scale to larger models",
    "test on larger models": "scale to larger models",
    "extend to new domains": "extend to new domains/tasks",
    "extend to other tasks": "extend to new domains/tasks",
    "extend to more tasks/domains": "extend to new domains/tasks",
    "ablate design choices": "ablation of design choices",
    "ablation of hyperparameters": "ablation of design choices",
    "investigate the mechanism": "investigate underlying mechanism",
    "understand underlying mechanism": "investigate underlying mechanism",
    "mechanistic follow-up": "investigate underlying mechanism",
    "replicate prior findings": "replicate or validate prior findings",
    "validate on real data": "replicate or validate prior findings",
    "improve monitoring methods": "improve detection/monitoring methods",
    "improve detection methods": "improve detection/monitoring methods",
    "build eval suite": "build benchmark or eval suite",
    "build a benchmark": "build benchmark or eval suite",
    "more realistic settings": "make experiments more realistic",
    "increase realism": "make experiments more realistic",
    "test generalisation of an effect": "test generalization of an effect",
    "cross-model transfer": "cross-model transfer of representations",
    # cross-chunk merges, added after inspecting the first four returned chunks
    "test on other model families": "test on more model families",
    "test across model families": "test on more model families",
    "test on broader task/domain set": "extend to new domains/tasks",
    "extend to broader domains": "extend to new domains/tasks",
    "study why phenomenon occurs": "investigate underlying mechanism",
    "mechanistic interpretability investigation": "investigate underlying mechanism",
    "understand mechanism behind effect": "investigate underlying mechanism",
    "run parameter/ablation sweep": "ablation of design choices",
    "hyperparameter sweep": "ablation of design choices",
    "tune method hyperparameters": "ablation of design choices",
    "generalize to more realistic settings": "make experiments more realistic",
    "more realistic experimental setup": "make experiments more realistic",
    "expand benchmark/dataset coverage": "build benchmark or eval suite",
    "expand evaluation to more settings": "extend to new domains/tasks",
    "untried algorithmic variant": "explore alternative training methods",
    "try alternative method variant": "explore alternative training methods",
    # cross-chunk merges from chunk 4's vocabulary
    "characterize mechanism/property": "investigate underlying mechanism",
    "explain cause of observed phenomenon": "investigate underlying mechanism",
    "test alternative techniques": "explore alternative training methods",
    "test generalization to other settings": "test generalization of an effect",
    "generalize to other task types": "extend to new domains/tasks",
    "ablate design choice": "ablation of design choices",
    "improve benchmark realism": "make experiments more realistic",
    "develop mitigation techniques": "detection and mitigation countermeasures",
    "test robustness to adversarial attacks": "robustness to adversarial attack",
    "build realistic model organisms": "build more realistic model organisms",
    "model organism development": "build more realistic model organisms",
    "extend to new task domains": "extend to new domains/tasks",
    "test on larger/more capable models": "scale to larger models",
    # cross-chunk merges from chunk 6's vocabulary
    "replicate finding on larger models": "scale to larger models",
    "replicate finding across model families": "test on more model families",
    "test in more naturalistic/real-world settings": "make experiments more realistic",
    "test robustness across scenario variations": "test generalization of an effect",
    "characterize conditions for generalization": "test generalization of an effect",
    "test cross-domain generalization": "test generalization of an effect",
    "test cross-model generalization": "test on more model families",
    "extend to more model families": "test on more model families",
    "test on more realistic model organisms": "build more realistic model organisms",
    "develop automated detection/auditing tooling": "improve detection/monitoring methods",
    "detect internal state via probes/interpretability": "improve detection/monitoring methods",
    "test sae architecture variant": "sae architecture variant",
    "increase dataset/question-set size for power": "build benchmark or eval suite",
}


def norm(t):
    t = re.sub(r"\s+", " ", (t or "").strip().lower())
    return THEME_ALIASES.get(t, t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-unmerged", action="store_true")
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(os.path.join(HERE, "leads"))
                   if re.fullmatch(r"themed_\d+\.json", f))
    if not files:
        print("no themed_*.json yet -- the clustering agents have not returned", file=sys.stderr)
        return 1
    rows = []
    for f in files:
        rows += json.load(open(os.path.join(HERE, "leads", f)))
    fw = {c["idx"]: c for c in json.load(open(os.path.join(HERE, "future_work.json")))
          if "idx" in c} or None
    raw = json.load(open(os.path.join(HERE, "future_work.json")))
    for i, c in enumerate(raw):
        c.setdefault("idx", i)
    byidx = {c["idx"]: c for c in raw}

    U = json.load(open(os.path.join(ROOT, "union.json")))["records"]
    themes = collections.defaultdict(lambda: {"posts": set(), "leads": [], "scope": collections.Counter(),
                                              "kind": collections.Counter(), "repos": set()})
    for r in rows:
        t = norm(r.get("theme"))
        if not t:
            continue
        src = byidx.get(r["idx"], {})
        pid = r.get("post_id") or src.get("post_id")
        e = themes[t]
        e["posts"].add(pid)
        e["leads"].append({"post_id": pid, "date": src.get("date"), "lead": src.get("lead")})
        e["scope"][r.get("scope")] += 1
        e["kind"][r.get("kind")] += 1
        if src.get("repo"):
            e["repos"].add(src["repo"])

    ranked = []
    for t, e in themes.items():
        posts = sorted(p for p in e["posts"] if p)
        authors = {(U[p]["authors"] or [None])[0] for p in posts if p in U}
        ranked.append({
            "theme": t,
            "n_leads": len(e["leads"]),
            "n_posts": len(posts),
            "n_distinct_first_authors": len(authors - {None}),
            "n_posts_with_code": len(e["repos"]),
            "scope": e["scope"].most_common(1)[0][0] if e["scope"] else None,
            "kind": e["kind"].most_common(1)[0][0] if e["kind"] else None,
            "last_proposed": max((l["date"] for l in e["leads"] if l["date"]), default=None),
            "example_leads": [l["lead"] for l in e["leads"][:3]],
            "post_ids": posts[:25],
        })
    # Rank by independent authors first: the same idea from many people is the signal.
    ranked.sort(key=lambda r: (-r["n_distinct_first_authors"], -r["n_posts"], -r["n_leads"]))
    json.dump(ranked, open(os.path.join(HERE, "leads_ranked.json"), "w"), indent=1)

    nf = os.path.join(HERE, "findings_numbers.json")
    N = json.load(open(nf)) if os.path.exists(nf) else {}
    N["lead.chunks_returned"] = len(files)
    N["lead.rows_themed"] = len(rows)
    N["lead.distinct_themes"] = len(ranked)
    N["lead.themes_1_author"] = sum(1 for r in ranked if r["n_distinct_first_authors"] <= 1)
    N["lead.themes_3plus_authors"] = sum(1 for r in ranked if r["n_distinct_first_authors"] >= 3)
    json.dump(dict(sorted(N.items())), open(nf, "w"), indent=1)

    print(f"{len(files)}/6 chunks, {len(rows)} leads themed, {len(ranked)} distinct themes "
          f"after alias merge")
    print(f"themes proposed by >=3 distinct first authors: {N['lead.themes_3plus_authors']}")
    print(f"\n{'theme':46}{'auth':>5}{'posts':>6}{'leads':>6}{'code':>5}  kind")
    for r in ranked[:30]:
        print(f"{r['theme'][:45]:46}{r['n_distinct_first_authors']:>5}{r['n_posts']:>6}"
              f"{r['n_leads']:>6}{r['n_posts_with_code']:>5}  {r['kind']}")
    if a.show_unmerged:
        print("\nall themes (extend THEME_ALIASES from this list):")
        for r in ranked:
            print(f"  {r['n_posts']:>4}  {r['theme']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
