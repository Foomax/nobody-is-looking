#!/usr/bin/env python3
"""Write ledger.json for an extension-class experiment folder (schema-compatible; excluded from the rate by ledger.py).
Usage: ext_ledger.py <ext_dir> --observed "..." --notes "..." [--minutes N] [--seeds N] [--runs true|false]"""
import os, sys
sys.path = [p for p in sys.path if os.path.abspath(p or ".") != os.path.dirname(os.path.abspath(__file__))]  # replication/select.py shadows stdlib select
import argparse, datetime as dt, json, subprocess
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--observed", required=True); ap.add_argument("--notes", default="")
ap.add_argument("--minutes", type=float, default=0); ap.add_argument("--seeds", type=int, default=None); ap.add_argument("--runs", default="true")
ap.add_argument("--fix", action="append", default=[]); ap.add_argument("--artifact", action="append", default=[])
a = ap.parse_args(); d = a.dir.rstrip("/"); s = json.load(open(os.path.join(d, "spec.json")))
gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
e = {"post_id": s["post_id"], "repo": s["repo"], "head_sha": s["head_sha"], "attempted_at": dt.date.today().isoformat(), "machine": gpu,
     "experiment_class": "extension", "extension_kind": s["extension"]["kind"], "parent_slug": s.get("parent_slug"),
     "what_varies": s["extension"]["what_varies"], "installs": True, "runs": a.runs == "true", "claim_located": a.runs == "true",
     "claim_reproduced": None, "claimed_value": s.get("target_value"), "observed_value": a.observed, "delta": None,
     "tolerance_used": "n/a (extension: not a replication)", "blocking_reason": "none" if a.runs == "true" else "runtime",
     "env_fixes": a.fix, "wallclock_minutes": a.minutes, "peak_vram_gb": None, "seeds_run": a.seeds, "notes": a.notes,
     "artifact_paths": a.artifact or ["run.log", "results.jsonl"]}
json.dump(e, open(os.path.join(d, "ledger.json"), "w"), indent=1); print("wrote", os.path.join(d, "ledger.json"))
