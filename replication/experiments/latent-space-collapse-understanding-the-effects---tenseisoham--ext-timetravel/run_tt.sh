#!/usr/bin/env bash
# R-7 time-travel: date-frozen resolution via uv --exclude-newer. Usage: run_tt.sh <YYYY-MM-DD> <tag>
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D=$1; TAG=$2; V="$HERE/.venv_$TAG"; L="$HERE/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
echo "== $(date -Is) TIMETRAVEL $TAG exclude-newer=$D start" | tee -a "$L"
if [ ! -x "$V/bin/python" ]; then
  uv venv -q "$V" --python 3.11
  uv pip install -q --python "$V/bin/python" --exclude-newer "$D" torch transformers datasets scikit-learn matplotlib tqdm accelerate jupyter nbconvert ipykernel pot transformer-lens scipy 2>&1 | tail -3 | tee -a "$L"
fi
"$V/bin/python" -c "import torch,transformers,datasets;print('RESOLVED torch',torch.__version__,'transformers',transformers.__version__,'datasets',datasets.__version__,'cuda',torch.cuda.is_available())" | tee -a "$L"
( nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 30 > "$HERE/vram_$TAG.log" 2>/dev/null & echo $! > "$HERE/.vram.pid" )
t0=$(date +%s); rc=0
for nb in finetune-sentiment-gpt2small logit-lens-analysis post-finetune-gpt2small; do
  ( cd "$HERE/src" && timeout 45m "$V/bin/python" -m jupyter nbconvert --to notebook --execute --allow-errors $nb.ipynb --output "../executed_${TAG}_$nb.ipynb" --ExecutePreprocessor.timeout=-1 ) >> "$L" 2>&1 || rc=$?
  echo "== $(date -Is) TIMETRAVEL $TAG notebook $nb exit $rc" | tee -a "$L"
done
kill "$(cat "$HERE/.vram.pid")" 2>/dev/null
echo "== $(date -Is) TIMETRAVEL $TAG RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
