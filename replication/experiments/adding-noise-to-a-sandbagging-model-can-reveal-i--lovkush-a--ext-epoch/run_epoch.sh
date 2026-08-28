#!/usr/bin/env bash
# Usage: run_epoch.sh <transformers-version> <tag>   e.g. run_epoch.sh 4.53.3 tf453
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; TV=$1; TAG=$2; V="$HERE/.venv_$TAG"; L="$HERE/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false EPOCH_TAG=$TAG
echo "== $(date -Is) EPOCH $TAG transformers==$TV start" | tee -a "$L"
[ -x "$V/bin/python" ] || { uv venv -q "$V" --python 3.11 && uv pip install -q --python "$V/bin/python" pip "setuptools<81" wheel \
  && uv pip install -q --python "$V/bin/python" "torch==2.6.0" --index-url https://download.pytorch.org/whl/cu124 \
  && uv pip install -q --python "$V/bin/python" -e "$HERE/src" "transformers==$TV" "datasets==5.0.1" accelerate pandas ; }
"$V/bin/python" -c "import torch,transformers,datasets;print('torch',torch.__version__,'transformers',transformers.__version__,'datasets',datasets.__version__)" | tee -a "$L"
( nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 30 > "$HERE/vram_$TAG.log" 2>/dev/null & echo $! > "$HERE/.vram.pid" )
t0=$(date +%s); ( cd "$HERE/src/experiments" && timeout 130m "$V/bin/python" exp07_epoch.py ) >> "$L" 2>&1; rc=$?
kill "$(cat "$HERE/.vram.pid")" 2>/dev/null
echo "== $(date -Is) EPOCH $TAG RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
