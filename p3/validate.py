#!/usr/bin/env python3
"""
validate.py -- schema-check the extraction output before any synthesis runs.

prompts.md P3 phase 1 ends with "validate before phase 2". This is that gate. It reports what is
missing, what is malformed, and the field distributions that reveal a lazy extractor (all-false
design flags, every claim_type "positive", phenomenon labels used exactly once).

Usage:  python3 p3/validate.py            # summary
        python3 p3/validate.py --missing  # just the ids still to do, one per line
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLAIMS = os.path.join(HERE, "claims")
UNION = os.path.join(os.path.dirname(HERE), "union.json")

REQUIRED = ["post_id", "primary_claim", "claim_type", "phenomenon", "models", "n_model_families",
            "effect", "design", "depends_on", "contradicts_or_qualifies", "stated_future_work",
            "limitations_stated", "reproducible_in_principle", "extractor_confidence", "quote"]
CLAIM_TYPES = {"positive", "negative", "null", "replication", "method", "benchmark", "dataset"}
REPRO = {"code+data", "code", "neither"}
CONF = {"high", "medium", "low"}
UNCERT = {"seeds", "ci", "se", "none"}


def load():
    want = set(json.load(open(UNION))["records"])
    got, bad = {}, []
    for fn in os.listdir(CLAIMS) if os.path.isdir(CLAIMS) else []:
        if not fn.endswith(".json"):
            continue
        pid = fn[:-5]
        try:
            got[pid] = json.load(open(os.path.join(CLAIMS, fn)))
        except Exception as e:
            bad.append((pid, f"unparseable: {e}"))
    return want, got, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--missing", action="store_true")
    a = ap.parse_args()
    want, got, bad = load()
    missing = sorted(want - set(got))
    if a.missing:
        print("\n".join(missing))
        return 0

    print(f"claims written : {len(got)}/{len(want)}   missing {len(missing)}   unparseable {len(bad)}")
    for pid, err in bad[:10]:
        print(f"  BAD {pid}: {err}")

    errs = collections.Counter()
    for pid, c in got.items():
        for k in REQUIRED:
            if k not in c:
                errs[f"missing field: {k}"] += 1
        if c.get("claim_type") not in CLAIM_TYPES:
            errs[f"bad claim_type: {c.get('claim_type')}"] += 1
        if c.get("reproducible_in_principle") not in REPRO:
            errs[f"bad reproducible: {c.get('reproducible_in_principle')}"] += 1
        if c.get("extractor_confidence") not in CONF:
            errs[f"bad confidence: {c.get('extractor_confidence')}"] += 1
        if isinstance(c.get("effect"), dict) and c["effect"].get("uncertainty_reported") not in UNCERT:
            errs[f"bad uncertainty: {c['effect'].get('uncertainty_reported')}"] += 1
        if c.get("post_id") != pid:
            errs["post_id does not match filename"] += 1
        for lf in ["models", "depends_on", "stated_future_work", "limitations_stated",
                   "contradicts_or_qualifies"]:
            if not isinstance(c.get(lf), list):
                errs[f"not a list: {lf}"] += 1
    print(f"\nschema errors: {sum(errs.values())}")
    for k, v in errs.most_common(15):
        print(f"  {v:>4}  {k}")

    if not got:
        return 1
    ct = collections.Counter(c.get("claim_type") for c in got.values())
    print(f"\nclaim_type: {dict(ct.most_common())}")
    conf = collections.Counter(c.get("extractor_confidence") for c in got.values())
    print(f"extractor_confidence: {dict(conf.most_common())}")
    rep = collections.Counter(c.get("reproducible_in_principle") for c in got.values())
    print(f"reproducible_in_principle: {dict(rep.most_common())}")
    unc = collections.Counter(c["effect"].get("uncertainty_reported")
                              for c in got.values() if isinstance(c.get("effect"), dict))
    print(f"uncertainty_reported: {dict(unc.most_common())}")
    for f in ["baseline", "ablation", "held_out", "prereg", "human_eval"]:
        n = sum(1 for c in got.values() if isinstance(c.get("design"), dict) and c["design"].get(f))
        print(f"design.{f:10} true in {n:>4}/{len(got)} ({100*n/len(got):.1f}%)")
    seeds = [c["design"].get("seeds_n") for c in got.values()
             if isinstance(c.get("design"), dict) and c["design"].get("seeds_n")]
    print(f"design.seeds_n     given in {len(seeds)}/{len(got)}")
    stubs = sum(1 for c in got.values() if c.get("primary_claim") == "STUB")
    print(f"STUB posts: {stubs}")

    ph = collections.Counter(c.get("phenomenon") for c in got.values())
    seed = set(json.load(open(os.path.join(HERE, "phenomenon_seed.json"))))
    print(f"\nphenomenon: {len(ph)} distinct over {len(got)} claims; "
          f"{sum(1 for p in ph if p in seed)} are seed labels; "
          f"{sum(1 for v in ph.values() if v == 1)} used exactly once")
    print("top 20:", ph.most_common(20))
    novel = [(p, n) for p, n in ph.most_common() if p not in seed]
    print(f"\n{len(novel)} invented labels; most common 25:")
    for p, n in novel[:25]:
        print(f"  {n:>3}  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
