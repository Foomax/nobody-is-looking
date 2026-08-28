#!/usr/bin/env bash
# R-6: second-family arm. Usage: run_family.sh <hf_model_id> <tag>
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; V="$HERE/../adding-noise-to-a-sandbagging-model-can-reveal-i--lovkush-a--ext-epoch/.venv_tf453"; L="$HERE/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false MODEL=$1 TAG=$2
echo "== $(date -Is) FAMILY $TAG model=$MODEL start ($("$V/bin/python" -c 'import torch,transformers;print(torch.__version__,transformers.__version__)'))" | tee -a "$L"
( nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 30 > "$HERE/vram_$TAG.log" 2>/dev/null & echo $! > "$HERE/.vram.pid" )
t0=$(date +%s); ( cd "$HERE/src/experiments" && timeout 130m "$V/bin/python" exp07_family.py ) >> "$L" 2>&1; rc=$?
kill "$(cat "$HERE/.vram.pid")" 2>/dev/null
echo "== $(date -Is) FAMILY $TAG RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
