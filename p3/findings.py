#!/usr/bin/env python3
"""
findings.py -- phase 2 of prompts.md P3. Turns p3/claims/*.json into the tables findings.md cites.

Every number in findings.md must come from here, the same contract meta.py has with readme.md.
Emits p3/findings_numbers.json.

Usage:  python3 p3/findings.py            # report to stdout + findings_numbers.json
        python3 p3/findings.py --quiet
"""
import argparse, collections, json, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLAIMS = os.path.join(HERE, "claims")
MAP = os.path.join(HERE, "phenomenon_map.json")
MIN_POSTS = 3


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1)]


def pct(k, n):
    return round(100.0 * k / n, 1) if n else None


class N(dict):
    def set(self, k, v):
        self[k] = v
        return v

    def rate(self, k, a, b):
        self.set(f"{k}.k", a)
        self.set(f"{k}.n", b)
        p = self.set(f"{k}.pct", pct(a, b))
        self.set(f"{k}.ci95", wilson(a, b))
        return p


def load():
    U = json.load(open(os.path.join(ROOT, "union.json")))["records"]
    pmap = json.load(open(MAP)) if os.path.exists(MAP) else {}
    C = {}
    for fn in sorted(os.listdir(CLAIMS)):
        if not fn.endswith(".json"):
            continue
        try:
            c = json.load(open(os.path.join(CLAIMS, fn)))
        except Exception:
            continue
        pid = fn[:-5]
        u = U.get(pid)
        if not u:
            continue
        raw = (c.get("phenomenon") or "").strip()
        c["_phenomenon_raw"] = raw
        c["_phenomenon"] = pmap.get(raw, raw)
        c["_date"] = u["date"]
        c["_period"] = f"{u['date'][:4]}H{1 if int(u['date'][5:7]) <= 6 else 2}"
        c["_in_af"] = u["in_af"]
        c["_karma"] = u["karma_lw"]
        c["_title"] = u["title"]
        c["_first_author"] = (u["authors"] or [None])[0]
        c["_own_repo"] = u["own_repo"]
        c["_dup"] = u["dup_cluster_id"]
        C[pid] = c
    return U, C


def dedup(C):
    """One record per project: collapse dup_cluster_id, keeping the earliest post."""
    seen, out = {}, {}
    for pid, c in C.items():
        k = c["_dup"] or pid
        if k not in seen or c["_date"] < seen[k]["_date"]:
            seen[k] = c
    for k, c in seen.items():
        out[c["post_id"]] = c
    return out


def design(c, f):
    d = c.get("design")
    return bool(d.get(f)) if isinstance(d, dict) else False


def uncertainty(c):
    e = c.get("effect")
    return e.get("uncertainty_reported", "none") if isinstance(e, dict) else "none"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    out = open(os.devnull, "w") if a.quiet else sys.stdout
    U, C = load()
    n = N()

    def rule(t):
        print(f"\n{'=' * 78}\n{t}\n{'=' * 78}", file=out)

    D = dedup(C)
    n.set("claims.extracted", len(C))
    n.set("claims.union_total", len(U))
    n.set("claims.projects_after_dedup", len(D))
    stubs = [c for c in D.values() if c.get("primary_claim") == "STUB"]
    n.set("claims.stubs", len(stubs))
    S = {k: c for k, c in D.items() if c.get("primary_claim") != "STUB"}
    n.set("claims.substantive", len(S))

    rule("2.0  COVERAGE")
    print(f"union posts {len(U)}  claims extracted {len(C)}  after project dedup {len(D)}  "
          f"stubs {len(stubs)}  substantive {len(S)}", file=out)
    conf = collections.Counter(c.get("extractor_confidence") for c in S.values())
    for k, v in conf.most_common():
        n.set(f"claims.confidence.{k}", v)
    print(f"extractor confidence: {dict(conf.most_common())}", file=out)

    # ---------------------------------------------------------------- 1 phenomena
    rule("2.1  PHENOMENON TABLE  (>= 3 substantive posts)")
    byp = collections.defaultdict(list)
    for c in S.values():
        byp[c["_phenomenon"]].append(c)
    big = {p: cs for p, cs in byp.items() if len(cs) >= MIN_POSTS}
    n.set("phenomena.distinct", len(byp))
    n.set("phenomena.with_3plus", len(big))
    n.rate("phenomena.posts_in_3plus", sum(len(v) for v in big.values()), len(S))
    print(f"{len(byp)} distinct phenomena; {len(big)} have >= {MIN_POSTS} posts, covering "
          f"{n['phenomena.posts_in_3plus.k']}/{len(S)} substantive posts "
          f"({n['phenomena.posts_in_3plus.pct']}%)", file=out)
    print(f"\n{'phenomenon':42}{'n':>4}{'auth':>5}{'fam':>4}{'pos':>4}{'neg':>4}{'null':>5}"
          f"{'unc%':>6}{'code%':>6}{'base%':>6}  span", file=out)
    rows = []
    for p, cs in sorted(big.items(), key=lambda x: -len(x[1])):
        key = p.replace(" ", "_").replace("/", "_").lower()
        auth = len({c["_first_author"] for c in cs})
        fams = len({m.get("family") for c in cs for m in (c.get("models") or [])
                    if isinstance(m, dict) and m.get("family")})
        ct = collections.Counter(c.get("claim_type") for c in cs)
        unc = sum(1 for c in cs if uncertainty(c) != "none")
        code = sum(1 for c in cs if c.get("reproducible_in_principle") in ("code", "code+data"))
        base = sum(1 for c in cs if design(c, "baseline"))
        span = (min(c["_date"] for c in cs), max(c["_date"] for c in cs))
        n.set(f"phenomenon.{key}.n", len(cs))
        n.set(f"phenomenon.{key}.first_authors", auth)
        n.set(f"phenomenon.{key}.model_families", fams)
        n.set(f"phenomenon.{key}.positive", ct["positive"])
        n.set(f"phenomenon.{key}.negative", ct["negative"])
        n.set(f"phenomenon.{key}.null", ct["null"])
        n.rate(f"phenomenon.{key}.uncertainty", unc, len(cs))
        n.rate(f"phenomenon.{key}.code", code, len(cs))
        n.rate(f"phenomenon.{key}.baseline", base, len(cs))
        n.set(f"phenomenon.{key}.span", list(span))
        rows.append((p, len(cs), auth, fams, ct["positive"], ct["negative"], ct["null"],
                     pct(unc, len(cs)), pct(code, len(cs)), pct(base, len(cs)), span))
        print(f"{p[:41]:42}{len(cs):>4}{auth:>5}{fams:>4}{ct['positive']:>4}{ct['negative']:>4}"
              f"{ct['null']:>5}{pct(unc,len(cs)):>6}{pct(code,len(cs)):>6}{pct(base,len(cs)):>6}"
              f"  {span[0][:7]}->{span[1][:7]}", file=out)

    # ---------------------------------------------------------------- 2 contested
    rule("2.2  CONTESTED PHENOMENA  (both a positive and a negative/null claim)")
    contested = []
    for p, cs in sorted(byp.items(), key=lambda x: -len(x[1])):
        pos = [c for c in cs if c.get("claim_type") == "positive"]
        neg = [c for c in cs if c.get("claim_type") in ("negative", "null")]
        if pos and neg:
            contested.append((p, pos, neg))
    n.set("contested.count", len(contested))
    n.rate("contested.share_of_3plus", sum(1 for p, _, _ in contested if p in big), len(big))
    print(f"{len(contested)} phenomena carry claims in both directions "
          f"({n['contested.share_of_3plus.k']} of the {len(big)} with >= {MIN_POSTS} posts)", file=out)
    for p, pos, neg in contested[:14]:
        print(f"\n-- {p}   ({len(pos)} positive / {len(neg)} negative-or-null)", file=out)
        for c in (pos[:2] + neg[:2]):
            fam = ",".join(sorted({m.get("family", "?") for m in (c.get("models") or [])
                                   if isinstance(m, dict)}))[:34]
            e = c.get("effect") or {}
            print(f"   [{c.get('claim_type'):10}] {c['_date']} {c.get('primary_claim','')[:88]}"
                  f"\n        models={fam or '-'} | effect={str(e.get('value'))[:40]} "
                  f"| unc={uncertainty(c)} | base={design(c,'baseline')}", file=out)

    # ---------------------------------------------------------------- 3 replication
    rule("2.3  REPLICATION")
    reps = [c for c in S.values() if c.get("claim_type") == "replication"]
    n.rate("replication.share", len(reps), len(S))
    print(f"posts whose primary contribution is a replication: {len(reps)}/{len(S)} "
          f"({n['replication.share.pct']}%) CI {n['replication.share.ci95']}", file=out)
    ctr = collections.Counter()
    for c in S.values():
        for d in (c.get("contradicts_or_qualifies") or []):
            ctr[str(d)[:70]] += 1
    n.rate("posts_qualifying_prior_work", sum(1 for c in S.values()
                                              if c.get("contradicts_or_qualifies")), len(S))
    print(f"posts that say they contradict or qualify prior work: "
          f"{n['posts_qualifying_prior_work.k']} ({n['posts_qualifying_prior_work.pct']}%)", file=out)
    for c in reps[:20]:
        print(f"   {c['_date']} {c['_title'][:66]}", file=out)

    # ---------------------------------------------------------------- 4 dependencies
    rule("2.4  DEPENDENCY GRAPH  (in-degree over depends_on)")
    dep = collections.Counter()
    for c in S.values():
        for d in {str(x).strip().lower() for x in (c.get("depends_on") or []) if x}:
            dep[d] += 1
    own = {(c["_own_repo"] or "").lower() for c in C.values() if c["_own_repo"]}
    n.set("dependencies.distinct", len(dep))
    n.set("dependencies.top20", [[k, v, k not in own] for k, v in dep.most_common(20)])
    print(f"{len(dep)} distinct dependencies named. Top 25 (* = never an own-project repo in the union):",
          file=out)
    for k, v in dep.most_common(25):
        print(f"  {v:>4}  {k[:66]}{'  *' if k not in own else ''}", file=out)
    n.rate("dependencies.top20_share_of_edges", sum(v for _, v in dep.most_common(20)),
           sum(dep.values()))
    print(f"\ntop-20 dependencies carry {n['dependencies.top20_share_of_edges.pct']}% of "
          f"{sum(dep.values())} dependency edges", file=out)
    # readme.md M5/O5 predicts a small tooling substrate carrying the majority of reuse.
    # Test it on repo-shaped dependencies only, separately from paper citations.
    repo_deps = collections.Counter({k: v for k, v in dep.items()
                                     if "/" in k and not k.startswith("arxiv")})
    paper_deps = collections.Counter({k: v for k, v in dep.items() if k.startswith("arxiv")})
    for lbl, cc in [("repo", repo_deps), ("paper", paper_deps)]:
        n.set(f"dependencies.{lbl}.distinct", len(cc))
        n.set(f"dependencies.{lbl}.edges", sum(cc.values()))
        if cc:
            n.rate(f"dependencies.{lbl}.top20_share", sum(v for _, v in cc.most_common(20)),
                   sum(cc.values()))
            n.rate(f"dependencies.{lbl}.top40_share", sum(v for _, v in cc.most_common(40)),
                   sum(cc.values()))
            n.rate(f"dependencies.{lbl}.singletons", sum(1 for v in cc.values() if v == 1), len(cc))
        print(f"  {lbl:6} {len(cc):>5} distinct, {sum(cc.values()):>5} edges, "
              f"top-20 carry {n[f'dependencies.{lbl}.top20_share.pct']}%, "
              f"top-40 carry {n[f'dependencies.{lbl}.top40_share.pct']}%, "
              f"{n[f'dependencies.{lbl}.singletons.pct']}% cited once", file=out)
    print("\n  top 15 REPO dependencies (the tooling substrate readme.md M5 predicts is small):", file=out)
    for k, v in repo_deps.most_common(15):
        print(f"    {v:>3}  {k}{'  *' if k not in own else ''}", file=out)
    n.set("dependencies.repo.top15", [[k, v] for k, v in repo_deps.most_common(15)])

    # ------------------------------------------------------- 5 evidence strength
    rule("2.5  EVIDENCE STRENGTH FROM READ POSTS  vs  THE REGEX INSTRUMENT")
    marks = {
        "baseline":    ("baseline", "rigor.union.baseline.pct"),
        "ablation":    ("ablation", "rigor.union.ablation.pct"),
        "held_out":    ("held_out", "rigor.union.heldout.pct"),
        "prereg":      ("prereg", "rigor.union.prereg.pct"),
    }
    RN = json.load(open(os.path.join(ROOT, "numbers.json")))
    print(f"{'marker':16}{'judge %':>9}{'CI':>15}{'regex %':>9}{'delta':>8}", file=out)
    for label, (field, rk) in marks.items():
        k = sum(1 for c in S.values() if design(c, field))
        j = n.rate(f"judge.{label}", k, len(S))
        r = RN[rk]
        d = n.set(f"judge_vs_regex.{label}", round(j - r, 1))
        print(f"{label:16}{j:>9}{str(n[f'judge.{label}.ci95']):>15}{r:>9}{d:>+8}", file=out)
    kseed = sum(1 for c in S.values() if design(c, "seeds_n"))
    n.rate("judge.seeds_n_given", kseed, len(S))
    n.set("judge_vs_regex.seeds_n_given",
          round(n['judge.seeds_n_given.pct'] - RN['rigor.union.seeds_strict.pct'], 1))
    print(f"{'seeds_n given':16}{n['judge.seeds_n_given.pct']:>9}"
          f"{str(n['judge.seeds_n_given.ci95']):>15}{RN['rigor.union.seeds_strict.pct']:>9}"
          f"{n['judge_vs_regex.seeds_n_given']:>+8}", file=out)
    unc = collections.Counter(uncertainty(c) for c in S.values())
    for k, v in unc.items():
        n.set(f"judge.uncertainty.{k}", v)
    n.rate("judge.any_uncertainty", len(S) - unc["none"], len(S))
    print(f"\nany uncertainty reported on the headline effect: "
          f"{n['judge.any_uncertainty.k']}/{len(S)} = {n['judge.any_uncertainty.pct']}% "
          f"CI {n['judge.any_uncertainty.ci95']}   (regex errorbar: {RN['rigor.union.errorbar.pct']}%)",
          file=out)
    n.set("judge_vs_regex.any_uncertainty",
          round(n["judge.any_uncertainty.pct"] - RN["rigor.union.errorbar.pct"], 1))
    fam = [c.get("n_model_families") or 0 for c in S.values()]
    n.rate("judge.model_families_2plus", sum(1 for x in fam if x >= 2), len(S))
    n.rate("judge.model_families_3plus", sum(1 for x in fam if x >= 3), len(S))
    print(f"tested >=2 model families: {n['judge.model_families_2plus.pct']}% "
          f"CI {n['judge.model_families_2plus.ci95']}   "
          f"(regex multi_model {RN['rigor.union.multi_model.pct']}%, "
          f"crude name-count {RN['rigor.union.model_families_2plus.pct']}%)", file=out)
    n.set("judge_vs_regex.model_families_2plus",
          round(n["judge.model_families_2plus.pct"] - RN["rigor.union.multi_model.pct"], 1))

    # claim type overall + by stratum
    rule("2.6  CLAIM TYPE, AND WHETHER PRESTIGE CHANGES IT")
    ct = collections.Counter(c.get("claim_type") for c in S.values())
    for k, v in ct.items():
        n.rate(f"claim_type.{k}", v, len(S))
    print(f"{'claim_type':14}{'all':>8}{'in AF':>10}{'not in AF':>12}", file=out)
    inaf = [c for c in S.values() if c["_in_af"]]
    notaf = [c for c in S.values() if not c["_in_af"]]
    n.set("strata.in_af.substantive", len(inaf))
    n.set("strata.not_in_af.substantive", len(notaf))
    for k in ["positive", "negative", "null", "replication", "method", "benchmark", "dataset"]:
        a1 = sum(1 for c in inaf if c.get("claim_type") == k)
        b1 = sum(1 for c in notaf if c.get("claim_type") == k)
        n.rate(f"claim_type.in_af.{k}", a1, len(inaf))
        n.rate(f"claim_type.not_in_af.{k}", b1, len(notaf))
        print(f"{k:14}{pct(ct[k],len(S)):>7}%{pct(a1,len(inaf)):>9}%{pct(b1,len(notaf)):>11}%", file=out)
    for lbl, grp, key in [("in AF", inaf, "in_af"), ("not in AF", notaf, "not_in_af")]:
        u2 = sum(1 for c in grp if uncertainty(c) != "none")
        b2 = sum(1 for c in grp if design(c, "baseline"))
        f2 = sum(1 for c in grp if (c.get("n_model_families") or 0) >= 2)
        n.rate(f"judge.{key}.any_uncertainty", u2, len(grp))
        n.rate(f"judge.{key}.baseline", b2, len(grp))
        n.rate(f"judge.{key}.model_families_2plus", f2, len(grp))
        print(f"  {lbl:10} uncertainty {pct(u2,len(grp)):>5}%  baseline {pct(b2,len(grp)):>5}%  "
              f">=2 families {pct(f2,len(grp)):>5}%", file=out)

    # ---------------------------------------------------------------- 7 future work
    rule("2.7  UNEXECUTED FUTURE WORK")
    fw = [(c["post_id"], c["_date"], c["_own_repo"], s)
          for c in S.values() for s in (c.get("stated_future_work") or [])]
    n.set("future_work.items", len(fw))
    n.rate("future_work.posts_with_any", sum(1 for c in S.values()
                                             if c.get("stated_future_work")), len(S))
    print(f"{len(fw)} stated next steps across {n['future_work.posts_with_any.k']} posts "
          f"({n['future_work.posts_with_any.pct']}%)", file=out)
    orph = [c for c in S.values() if c.get("stated_future_work")
            and c.get("reproducible_in_principle") in ("code", "code+data")]
    n.rate("future_work.with_inherited_code", len(orph), len(S))
    print(f"of those, {len(orph)} ship code a successor could inherit "
          f"({n['future_work.with_inherited_code.pct']}%)", file=out)
    json.dump([{"post_id": p, "date": d, "repo": r, "lead": s} for p, d, r, s in fw],
              open(os.path.join(HERE, "future_work.json"), "w"), indent=1)

    # ---------------------------------------------------------------- 8 by period
    rule("2.8  CLAIM TYPE BY PERIOD  (share of substantive posts)")
    per = ["2024H2", "2025H1", "2025H2", "2026H1", "2026H2"]
    g = collections.defaultdict(list)
    for c in S.values():
        g[c["_period"]].append(c)
    print(f"{'':14}" + "".join(f"{p:>9}" for p in per), file=out)
    for k in ["positive", "negative", "null", "replication", "method", "benchmark"]:
        row = []
        for p in per:
            kk = sum(1 for c in g[p] if c.get("claim_type") == k)
            n.rate(f"claim_type_by_period.{k}.{p}", kk, len(g[p]))
            row.append(f"{pct(kk, len(g[p])):.0f}%" if g[p] else "-")
        print(f"{k:14}" + "".join(f"{x:>9}" for x in row), file=out)
    for lbl, fn2 in [("any uncertainty", lambda c: uncertainty(c) != "none"),
                     ("baseline", lambda c: design(c, "baseline")),
                     (">=2 families", lambda c: (c.get("n_model_families") or 0) >= 2)]:
        row = []
        for p in per:
            kk = sum(1 for c in g[p] if fn2(c))
            n.rate(f"rigor_by_period.{lbl.replace(' ', '_').replace('>=', 'ge')}.{p}", kk, len(g[p]))
            row.append(f"{pct(kk, len(g[p])):.0f}%" if g[p] else "-")
        print(f"{lbl:14}" + "".join(f"{x:>9}" for x in row), file=out)
    print(f"{'n':14}" + "".join(f"{len(g[p]):>9}" for p in per), file=out)

    with open(os.path.join(HERE, "findings_numbers.json"), "w") as fh:
        json.dump(dict(sorted(n.items())), fh, indent=1)
    print(f"\nwrote {len(n)} keys to p3/findings_numbers.json", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
