#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D=${1:-2024-09-20}; V="$HERE/.venv"; L="$HERE/run.log"; S="$HERE/src"
unset CI GITHUB_ACTIONS; export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=online PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
echo "== $(date -Is) TIMETRAVEL exclude-newer=$D start" | tee -a "$L"
if [ ! -x "$V/bin/python" ]; then
  uv venv -q "$V" --python 3.11
  uv pip install -q --python "$V/bin/python" "torch==2.2.2" "torchvision~=0.17.0" --index-url https://download.pytorch.org/whl/cu121 2>&1 | tail -2 | tee -a "$L"
  uv pip install -q --python "$V/bin/python" --exclude-newer "$D" -r "$HERE/req_no_tl.txt" "transformer-lens>=1.14" "einops~=0.7.0" "pydantic~=2.0" "wandb~=0.16.2" "fire~=0.5.0" "jaxtyping~=0.2.25" "python-dotenv~=1.0.1" "zstandard~=0.22.0" "tenacity~=8.2.3" typeguard pandas "setuptools<81" 2>&1 | tail -3 | tee -a "$L"
fi
"$V/bin/python" -c "import torch,transformers,importlib.metadata as m;print('RESOLVED torch',torch.__version__,'transformer-lens',m.version('transformer-lens'),'transformers',transformers.__version__,'cuda',torch.cuda.is_available())" 2>&1 | tail -1 | tee -a "$L"
( nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 30 > "$HERE/vram.log" 2>/dev/null & echo $! > "$HERE/.vram.pid" )
t0=$(date +%s); rc=0
echo "== $(date -Is) ARM A: --layer 6 --direction_type cov_random --subtraction mixture (script hardcodes args.e2e=h9hrelni -> wandb fetch on every path)" | tee -a "$L"
( cd "$S" && PYTHONPATH="$S:$HERE/e2e_sae_src" timeout 40m "$V/bin/python" scripts/sensitive_direction.py --layer 6 --direction_type cov_random --subtraction mixture ) >> "$L" 2>&1 || rc=$?
echo "== $(date -Is) ARM A exit $rc" | tee -a "$L"
echo "== $(date -Is) ARM B: --layer 6 --direction_type real_direction" | tee -a "$L"
( cd "$S" && PYTHONPATH="$S:$HERE/e2e_sae_src" timeout 20m "$V/bin/python" scripts/sensitive_direction.py --layer 6 --direction_type real_direction ) >> "$L" 2>&1 || rcb=$?
echo "== $(date -Is) ARM B exit ${rcb:-0}" | tee -a "$L"
kill "$(cat "$HERE/.vram.pid")" 2>/dev/null
echo "== $(date -Is) TIMETRAVEL RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
