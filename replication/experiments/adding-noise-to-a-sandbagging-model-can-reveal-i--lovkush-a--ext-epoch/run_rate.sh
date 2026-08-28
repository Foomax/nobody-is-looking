#!/usr/bin/env bash
# R-5: sandbagging collapse-rate estimate. seeds 10-29 x noise {0.001,0.002}, sandbag prompt only; env = .venv_tf453 (bit-identical to parent).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; V="$HERE/.venv_tf453"; L="$HERE/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false EPOCH_TAG=rate_seeds10_29
echo "== $(date -Is) RATE start ($("$V/bin/python" -c 'import torch,transformers;print(torch.__version__,transformers.__version__)'))" | tee -a "$L"
t0=$(date +%s); ( cd "$HERE/src/experiments" && timeout 90m "$V/bin/python" exp07_rate.py ) >> "$L" 2>&1; rc=$?
echo "== $(date -Is) RATE RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
