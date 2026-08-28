#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; V="$HERE/.venv"; L="$HERE/run.log"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
echo "== $(date -Is) ARTIFACT start" | tee -a "$L"
if [ ! -x "$V/bin/python" ]; then
  uv venv -q "$V" --python 3.11
  uv pip install -q --python "$V/bin/python" --exclude-newer 2026-02-18 "torch==2.9.0" "sae-lens==6.18.0" "transformer-lens==2.16.1" "transformers==4.57.1" "numpy==1.26.4" plotly pandas scikit-learn jupyter nbconvert ipykernel matplotlib kaleido 2>&1 | tail -3 | tee -a "$L"
fi
"$V/bin/python" -c "import torch,transformer_lens,sae_lens,transformers;print('RESOLVED torch',torch.__version__,'sae-lens',sae_lens.__version__,'transformer-lens',transformer_lens.__version__,'transformers',transformers.__version__)" | tee -a "$L"
echo "== $(date -Is) ENV FIX: populate ~/.cache/sae_lens/blocks.{6,8,10,11}.hook_resid_pre from release gpt2-small-res-jb (uncommitted artifact the notebook loads from disk)" | tee -a "$L"
"$V/bin/python" - <<'EOF' 2>&1 | tail -8 | tee -a "$L"
from pathlib import Path
from sae_lens import SAE
base = Path.home()/".cache"/"sae_lens"
for L in (6, 8, 10, 11):
    sid = f"blocks.{L}.hook_resid_pre"; out = base/sid
    if (out/"cfg.json").exists(): print("cached", sid); continue
    r = SAE.from_pretrained("gpt2-small-res-jb", sid)
    sae = r[0] if isinstance(r, tuple) else r
    out.mkdir(parents=True, exist_ok=True); sae.save_model(str(out)); print("saved", sid, sorted(p.name for p in out.iterdir()))
EOF
t0=$(date +%s); ( cd "$HERE/src" && timeout 75m "$V/bin/python" -m jupyter nbconvert --to notebook --execute --allow-errors notebooks/phase_2_semantics_vs_ideas_v2.ipynb --output "$HERE/executed.ipynb" --ExecutePreprocessor.timeout=-1 ) >> "$L" 2>&1; rc=$?
echo "== $(date -Is) ARTIFACT RUN-EXIT $rc after $(( ($(date +%s)-t0)/60 )) min" | tee -a "$L"
