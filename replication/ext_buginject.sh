#!/usr/bin/env bash
# R-13 bug-injection control: 3 rows x {clean,bug}; outputs -> <ext>/out_{clean,bug}.txt
set -uo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; cd "$R"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
log(){ echo "== $(date -Is) $*" | tee -a "$R/ext_buginject.log"; }
run_row(){ # extdir venv timeout
  d=$1; V=$2; tmo=$3
  for arm in clean bug; do
    log "RUN $(basename $d) $arm"; t0=$(date +%s)
    ( cd "$d/src" && timeout ${tmo}m "$V/bin/python" -m jupyter nbconvert --to notebook --execute --allow-errors $arm.ipynb --output "../executed_$arm.ipynb" --ExecutePreprocessor.timeout=-1 ) >> "$d/run.log" 2>&1; rc=$?
    python3 - "$d/executed_$arm.ipynb" > "$d/out_$arm.txt" <<'EOF'
import json,sys
nb=json.load(open(sys.argv[1]))
for i,c in enumerate(nb['cells']):
    if c['cell_type']!='code': continue
    for o in c.get('outputs',[]):
        if o.get('output_type')=='stream': print(''.join(o['text']),end='')
        elif o.get('output_type')=='error': print('ERROR',o.get('ename'),o.get('evalue','')[:200])
EOF
    log "EXIT $(basename $d) $arm rc=$rc after $(( ($(date +%s)-t0)/60 )) min"
  done
}
E="$R/experiments"
run_row "$E/gpt-2-s-ioi-behavior-is-defined-where-the-paper---fractalmachinist--ext-buginject" "$E/gpt-2-s-ioi-behavior-is-defined-where-the-paper---fractalmachinist--ext-seeds/.venv" 15
MR="$E/investigating-echo-tasks-in-qwen-2-5-1-5b-instru--mild-rgb--ext-buginject"
[ -x "$MR/.venv/bin/python" ] || { log "PREP mild-rgb venv"; ./tree_prep.sh "$MR"; uv pip install -q --python "$MR/.venv/bin/python" jupyter nbconvert ipykernel transformer-lens einops 2>&1 | tail -1; }
run_row "$MR" "$MR/.venv" 20
run_row "$E/matryoshka-sparse-autoencoders--noanabeshima--ext-buginject" "$E/matryoshka-sparse-autoencoders--noanabeshima--ext-seeds/.venv" 25
log "DONE"
