#!/usr/bin/env bash
cd "$(dirname "$0")"; L=run.log
echo "== $(date -Is) ENV build (detached) start" >> $L
[ -x .venv/bin/python ] || uv venv -q .venv --python 3.11
uv pip install -q --python .venv/bin/python "torch==2.2.0" --index-url https://download.pytorch.org/whl/cu121 >> $L 2>&1
uv pip install -q --python .venv/bin/python --exclude-newer 2025-05-22 "numpy<2" "sympy==1.11.1" odeformer jupyter nbconvert ipykernel scipy scikit-learn pandas matplotlib "setuptools<81" >> $L 2>&1
.venv/bin/python -c "import torch,numpy,odeformer,importlib.metadata as m;print('RESOLVED torch',torch.__version__,'numpy',numpy.__version__,'odeformer',m.version('odeformer'),'cuda',torch.cuda.is_available())" >> $L 2>&1 || echo "ENV-BUILD-FAILED" >> $L
echo "== $(date -Is) ENV build done" >> $L
