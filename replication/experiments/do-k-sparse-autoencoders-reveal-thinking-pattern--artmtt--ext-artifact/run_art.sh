#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; L="$HERE/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
echo "== $(date -Is) ARTIFACT start (relaunch via script): repl.ipynb = author cells 0-24 + re-enabled generation (32 prompts, seed 0) + aggregation" | tee -a "$L"
t0=$(date +%s); ( cd "$HERE/src" && timeout 90m "$HERE/.venv/bin/python" -m jupyter nbconvert --to notebook --execute --allow-errors repl.ipynb --output "$HERE/executed.ipynb" --ExecutePreprocessor.timeout=-1 ) >> "$L" 2>&1; rc=$?
echo "== $(date -Is) ARTIFACT RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
