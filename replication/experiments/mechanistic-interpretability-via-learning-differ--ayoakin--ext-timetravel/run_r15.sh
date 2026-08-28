#!/usr/bin/env bash
cd "$(dirname "$0")"; HERE=$PWD; L="$HERE/run.log"; LP="$HERE/src/subteams/LLMProbing"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false MPLBACKEND=Agg
uv pip install -q --python .venv/bin/python --exclude-newer 2025-05-22 seaborn >> "$L" 2>&1
echo "== $(date -Is) R15 start: repl_r2.ipynb (author pipeline, local paths, 800 samples)" >> "$L"
t0=$(date +%s); ( cd "$LP" && PYTHONPATH="$LP" timeout 240m "$HERE/.venv/bin/python" -m jupyter nbconvert --to notebook --execute --allow-errors notebooks/repl_r2.ipynb --output "$HERE/executed.ipynb" --ExecutePreprocessor.timeout=-1 ) >> "$L" 2>&1; rc=$?
echo "== $(date -Is) R15 RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" >> "$L"
