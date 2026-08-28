#!/usr/bin/env python3
"""Aggregate experiments/*/ledger.json into the R5 headline: reproduction rate + failure taxonomy."""
import collections, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ALL = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(HERE, "experiments", "*", "ledger.json")))]
# extension-class rows (seed/family/library-epoch variations of a reproduced row) are a different
# experiment: they are tallied separately and NEVER enter the reproduction rate.
EXT = [e for e in ALL if e.get("experiment_class") == "extension"]
L = [e for e in ALL if e.get("experiment_class") != "extension"]
if not L:
    print("no ledger entries yet"); sys.exit(0)
n = len(L)
inst = sum(1 for e in L if e["installs"]); runs = sum(1 for e in L if e["runs"])
loc = sum(1 for e in L if e["claim_located"]); rep = sum(1 for e in L if e.get("claim_reproduced"))
reasons = collections.Counter(e["blocking_reason"] for e in L)
out = {"attempted": n, "installs": inst, "runs": runs, "claim_located": loc, "claim_reproduced": rep,
       "reproduction_rate_of_attempted": round(rep / n, 3),
       "reproduction_rate_of_located": round(rep / loc, 3) if loc else None,
       "failure_taxonomy": dict(reasons.most_common()),
       "median_wallclock_min": sorted(e["wallclock_minutes"] for e in L)[n // 2],
       "entries": [{k: e[k] for k in ["post_id", "repo", "runs", "claim_reproduced", "blocking_reason", "delta"]} for e in L]}
json.dump(out, open(os.path.join(HERE, "ledger_summary.json"), "w"), indent=1)
print(f"attempted {n}  installs {inst}  runs {runs}  located {loc}  reproduced {rep}  "
      f"-> {out['reproduction_rate_of_attempted']:.0%} of attempted, "
      f"{(rep/loc if loc else 0):.0%} of located")
print("failure taxonomy:", dict(reasons.most_common()))
if EXT:
    print(f"extensions (not in the rate): {len(EXT)} -- " + "; ".join(
        f"{e.get('extension_kind','?')}:{e['repo']}={e.get('observed_value','')[:60]}" for e in EXT))
