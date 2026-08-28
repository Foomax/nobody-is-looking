#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D=${1:-2026-08-15}; V="$HERE/.venv"; L="$HERE/run.log"; S="$HERE/src"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false MPLBACKEND=Agg
echo "== $(date -Is) TIMETRAVEL exclude-newer=$D start" | tee -a "$L"
if [ ! -x "$V/bin/python" ]; then
  uv venv -q "$V" --python 3.11
  uv pip install -q --python "$V/bin/python" --exclude-newer "$D" torch numpy matplotlib tqdm scipy pandas 2>&1 | tail -3 | tee -a "$L"
fi
"$V/bin/python" -c "import torch,numpy,matplotlib;print('RESOLVED torch',torch.__version__,'numpy',numpy.__version__,'matplotlib',matplotlib.__version__,'cuda',torch.cuda.is_available())" 2>&1 | tail -1 | tee -a "$L"
( nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 30 > "$HERE/vram.log" 2>/dev/null & echo $! > "$HERE/.vram.pid" )
t0=$(date +%s); ( cd "$S" && timeout 30m "$V/bin/python" -m synth.run h1 && timeout 30m "$V/bin/python" -m synth.run h2 ) >> "$L" 2>&1; rc=$?
kill "$(cat "$HERE/.vram.pid")" 2>/dev/null
echo "== $(date -Is) TIMETRAVEL RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
