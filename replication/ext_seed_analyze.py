#!/usr/bin/env python3
"""Summarise the seed-variance census (R-1) from the three ext folders' results.jsonl -> ext_seed_census.json + stdout."""
import json, os, statistics as st, glob
HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.join(HERE, "experiments")
def rows(slug):
    p = os.path.join(E, slug, "results.jsonl")
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
def ms(xs):
    xs = [x for x in xs if x is not None]
    return (round(st.mean(xs), 4), round(st.stdev(xs), 4) if len(xs) > 1 else None, round(min(xs), 4), round(max(xs), 4), len(xs))
out = {}
# ---- ioi
r = rows("gpt-2-s-ioi-behavior-is-defined-where-the-paper---fractalmachinist--ext-seeds")
if r:
    d = {k: ms([x[k] for x in r]) for k in ("mean_drop", "std_drop", "t", "p", "cohen_d", "control_accuracy", "test_accuracy")}
    d["per_seed"] = {x["seed"]: {"mean_drop": round(x["mean_drop"], 3), "d": round(x["cohen_d"], 3), "p": float(f"{x['p']:.2g}")} for x in r}
    d["author_seed"] = 0; d["parent_target"] = "mean drop 0.23, SD 0.84, t 3.09, p 0.0024, d 0.27 (n=128)"
    d["all_seeds_p_below_0.01"] = all(x["p"] < 0.01 for x in r)
    d["author_seed_rank_of_effect"] = sorted(r, key=lambda x: x["mean_drop"]).index(next(x for x in r if x["seed"] == 0)) + 1
    out["ioi"] = d
    print("ioi:", json.dumps(d, indent=1))
# ---- phusroyal
r = rows("can-we-teach-a-model-to-encode-a-semantic-featur--phusroyal--ext-seeds")
if r:
    d = {}
    for g in ("sphere_shell", "helix_tube"):
        g_rows = [x for x in r if g in x]
        d[g] = {k: ms([x[g][k] for x in g_rows]) for k in ("linear_probe_auc", "causal_target_delta", "geometry_probe_auc")}
        d[g]["passed_all_checks"] = sum(1 for x in g_rows if x[g]["passed"]); d[g]["n"] = len(g_rows)
        d[g]["per_seed"] = {x["seed"]: {"probe_auc": round(x[g]["linear_probe_auc"], 3), "causal_delta": round(x[g]["causal_target_delta"], 3)} for x in g_rows}
        d[g]["in_target_range"] = sum(1 for x in g_rows if 0.57 <= x[g]["linear_probe_auc"] <= 0.67 and 1.9 <= x[g]["causal_target_delta"] <= 3.5)
    d["parent_target"] = "probe AUC 0.57-0.67 after GFAL; causal delta 1.9-3.5 (stage gfal_plus); parent (seed 1729): sphere 0.589/3.473, helix 0.5685/2.565"
    d["errors"] = [x for x in r if "error" in x]
    out["phusroyal"] = d
    print("phusroyal:", json.dumps(d, indent=1))
# ---- matryoshka
r = rows("matryoshka-sparse-autoencoders--noanabeshima--ext-seeds")
if r:
    d = {}
    for sae in ("vanilla", "matryoshka"):
        d[sae] = {k: ms([x[sae][k] for x in r]) for k in ("diag_min", "diag_mean", "max_offdiag", "n_absorbed_lt085")}
        d[sae]["per_seed_absorbed_lt085"] = {x["seed"]: x[sae]["n_absorbed_lt085"] for x in r}
        d[sae]["per_seed_diag_min"] = {x["seed"]: round(x[sae]["diag_min"], 3) for x in r}
    d["parent_target"] = "vanilla 9/20 absorbed (diag 0.66-0.75), matryoshka 0/20 (diag min 0.923 mean 0.965)"
    d["claim_holds_per_seed"] = {x["seed"]: bool(x["vanilla"]["n_absorbed_lt085"] > x["matryoshka"]["n_absorbed_lt085"]) for x in r}
    out["matryoshka"] = d
    print("matryoshka:", json.dumps(d, indent=1))
json.dump(out, open(os.path.join(HERE, "ext_seed_census.json"), "w"), indent=1)
