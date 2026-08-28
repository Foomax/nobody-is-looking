#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D=${1:-2025-02-16}; V="$HERE/.venv"; L="$HERE/run.log"; S="$HERE/interpretability"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
echo "== $(date -Is) TIMETRAVEL exclude-newer=$D start (checkout dir renamed to interpretability/)" | tee -a "$L"
if [ ! -x "$V/bin/python" ]; then
  uv venv -q "$V" --python 3.11
  uv pip install -q --python "$V/bin/python" --exclude-newer "$D" -r "$S/requirements.txt" "transformer-lens==2.0.0" "jaxtyping==0.2.29" typeguard "transformers<5" datasets scikit-learn plotly ipywidgets einops "setuptools<81" 2>&1 | tail -3 | tee -a "$L"
fi
"$V/bin/python" -c "import torch,transformer_lens,transformers;print('RESOLVED torch',torch.__version__,'transformer-lens',transformer_lens.__version__,'transformers',transformers.__version__,'cuda',torch.cuda.is_available())" | tee -a "$L"
( nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 30 > "$HERE/vram.log" 2>/dev/null & echo $! > "$HERE/.vram.pid" )
t0=$(date +%s); ( cd "$S" && PYTHONPATH="$S:$S/training_probes" timeout 75m "$V/bin/python" prove_circuits_last_flipped_repl.py ) >> "$L" 2>&1; rc=$?
kill "$(cat "$HERE/.vram.pid")" 2>/dev/null
echo "== $(date -Is) TIMETRAVEL RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
