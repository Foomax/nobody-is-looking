#!/usr/bin/env bash
# R-4: 10 more phusroyal seeds (5-14) to pin the sphere_shell seed-fragility rate. Same folder, same env, same CLI; only --seed.
set -uo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; d="$R/experiments/can-we-teach-a-model-to-encode-a-semantic-featur--phusroyal--ext-seeds"; L="$d/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
for s in 5 6 7 8 9 10 11 12 13 14; do
  echo "== $(date -Is) RUN phusroyal seed=$s" | tee -a "$R/ext_seed_census.log"; t0=$(date +%s)
  ( cd "$d/src" && timeout 20m uv run python -m src.predefined_manifold run --device cuda --seed $s --run-id seed$s ) >> "$L" 2>&1; rc=$?
  python3 - "$d/src/.artifacts/predefined_manifold/runs/seed$s/metrics.json" $s >> "$d/results.jsonl" <<'EOF'
import json,sys
try: m=json.load(open(sys.argv[1]))
except Exception as e: print(json.dumps({'seed':int(sys.argv[2]),'error':str(e)})); sys.exit()
out={'seed':int(sys.argv[2])}
for g,v in m['geometries'].items():
    mm=v['metrics']; out[g]={k:mm[k] for k in ('linear_probe_auc','causal_target_delta','geometry_probe_auc','complement_probe_auc')}; out[g]['passed']=v['passed']
print(json.dumps(out))
EOF
  echo "== $(date -Is) EXIT phusroyal seed=$s rc=$rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$R/ext_seed_census.log"
done
