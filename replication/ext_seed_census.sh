#!/usr/bin/env bash
# GPU run 1 of the new direction: seed-variance census. One card, sequential. Logs per ext folder.
set -uo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; cd "$R"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
SEEDS="0 1 2 3 4"
log() { echo "== $(date -Is) $*" | tee -a "$R/ext_seed_census.log"; }
run_nb() { # kind extdir nbtimeout_min
  kind=$1; d=$2; tmo=$3; L="$d/run.log"; : > "$d/results.jsonl"
  log "PREP $d"; ./tree_prep.sh "$d"
  uv pip install -q --python "$d/.venv/bin/python" jupyter nbconvert ipykernel matplotlib scipy $( [ $kind = ioi ] && echo transformer-lens ) 2>&1 | tail -1
  for s in $SEEDS; do
    python3 ext_seed_nb.py $kind "$d/src" $s | tee -a "$L"
    log "RUN $kind seed=$s"; t0=$(date +%s)
    ( cd "$d/src" && timeout ${tmo}m ../.venv/bin/python -m jupyter nbconvert --to notebook --execute --allow-errors seed${s}_repl.ipynb --output ../executed_seed${s}.ipynb --ExecutePreprocessor.timeout=-1 ) >> "$L" 2>&1
    rc=$?; python3 - "$d/executed_seed${s}.ipynb" >> "$d/results.jsonl" <<'EOF'
import json,sys
nb=json.load(open(sys.argv[1]))
for c in nb['cells']:
    for o in c.get('outputs',[]):
        t=''.join(o.get('text',[])) if o.get('output_type')=='stream' else ''
        for line in t.splitlines():
            if line.startswith('SEEDJSON '): print(line[9:])
EOF
    log "EXIT $kind seed=$s rc=$rc after $(( ($(date +%s)-t0)/60 )) min"
  done
}
run_phus() {
  d="$R/experiments/can-we-teach-a-model-to-encode-a-semantic-featur--phusroyal--ext-seeds"; L="$d/run.log"; : > "$d/results.jsonl"
  for s in $SEEDS; do
    log "RUN phusroyal seed=$s"; t0=$(date +%s)
    ( cd "$d/src" && uv sync -q && timeout 20m uv run python -m src.predefined_manifold run --device cuda --seed $s --run-id seed$s ) >> "$L" 2>&1
    rc=$?; python3 - "$d/src/.artifacts/predefined_manifold/runs/seed$s/metrics.json" $s >> "$d/results.jsonl" <<'EOF'
import json,sys
try: m=json.load(open(sys.argv[1]))
except Exception as e: print(json.dumps({'seed':int(sys.argv[2]),'error':str(e)})); sys.exit()
out={'seed':int(sys.argv[2])}
for g,v in m['geometries'].items():
    mm=v['metrics']; out[g]={k:mm[k] for k in ('linear_probe_auc','causal_target_delta','geometry_probe_auc','complement_probe_auc')}; out[g]['passed']=v['passed']
print(json.dumps(out))
EOF
    log "EXIT phusroyal seed=$s rc=$rc after $(( ($(date +%s)-t0)/60 )) min"
  done
}
log "START seed census (nvidia: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader))"
run_nb ioi "$R/experiments/gpt-2-s-ioi-behavior-is-defined-where-the-paper---fractalmachinist--ext-seeds" 15
run_phus
run_nb matryoshka "$R/experiments/matryoshka-sparse-autoencoders--noanabeshima--ext-seeds" 25
log "DONE seed census"
