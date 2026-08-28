#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D=${1:-2024-11-08}; V="$HERE/.venv"; L="$HERE/run.log"; S="$HERE/src"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
echo "== $(date -Is) TIMETRAVEL exclude-newer=$D start" | tee -a "$L"
if false; then
  uv venv -q "$V" --python 3.11
  uv pip install -q --python "$V/bin/python" --exclude-newer "$D" -r "$S/requirements.txt" "setuptools<81" 2>&1 | tail -3 | tee -a "$L"
fi
"$V/bin/python" -c "import torch,transformer_lens,transformers,sparse_autoencoder;print('RESOLVED torch',torch.__version__,'transformer-lens',__import__("importlib.metadata").metadata.version("transformer-lens"),'transformers',transformers.__version__,'cuda',torch.cuda.is_available())" | tee -a "$L"
t0=$(date +%s)
( cd "$S" && timeout 40m "$V/bin/python" prep_storage.py ) >> "$L" 2>&1; echo "== $(date -Is) prep exit $?" | tee -a "$L"
( cd "$S" && timeout 20m "$V/bin/python" timing_tests_repl.py ) >> "$L" 2>&1; rc=$?
echo "== $(date -Is) TIMETRAVEL RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
