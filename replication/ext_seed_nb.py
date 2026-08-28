#!/usr/bin/env python3
"""Make a seeded copy of a reproduced row's notebook for the seed-variance extension.
Usage: ext_seed_nb.py ioi|matryoshka <src_dir> <seed> -> writes <src_dir>/seed<seed>_repl.ipynb
Only the seed changes. Cells that only draw figures or install packages are dropped; a final cell
prints one 'SEEDJSON {...}' line with the headline statistics the parent VERDICT used."""
import json, sys, copy
kind, src, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])

def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s}

if kind == "ioi":
    nb = json.load(open(f"{src}/experiments.ipynb"))
    cs = [c for c in nb["cells"] if c["cell_type"] == "code"]
    # cell 0 = %pip install + %matplotlib widget (network + widget canvas) -> inline backend
    cells = [code("%matplotlib inline\n"), cs[1], code(f"SEED = {seed}  # seed-variance extension: the only change\nprint('SEED', SEED)\n")]
    cells += cs[2:11]  # model load, SIZE, checks, sampler, sweep, sanity, diffs, plot+stats, tests
    cells.append(code(
        "import json as _j\n"
        "print('SEEDJSON', _j.dumps({'seed': SEED, 'n': int(ctrl.size), 'mean_drop': float(diff.mean()),\n"
        "  'std_drop': float(diff.std(ddof=1)), 't': float(t_stat), 'p': float(p_t), 'cohen_d': float(cohen_d),\n"
        "  'control_accuracy': float(control_accuracy), 'test_accuracy': float(test_accuracy),\n"
        "  'frac_test_below_control': float(frac_below)}))\n"))
elif kind == "matryoshka":
    nb = json.load(open(f"{src}/train_saes_on_toy_repl.ipynb"))
    cs = [c for c in nb["cells"] if c["cell_type"] == "code"]
    cells = [cs[0], cs[1], code(f"SEED = {seed}  # seed-variance extension: the only change\nimport torch, numpy as np\ntorch.manual_seed(SEED); np.random.seed(SEED); torch.cuda.manual_seed_all(SEED)\nprint('SEED', SEED)\n")]
    cells += cs[2:6]  # true_feats+dataset, perm helper, training loop, cosine matrices (drops figure export)
    cells.append(code(
        "import json as _j\n"
        "def _stats(C):\n"
        "    C = C.detach().cpu(); d = C.diag(); off = (C - torch.diag(d)).abs().max().item()\n"
        "    return {'diag_min': d.min().item(), 'diag_mean': d.mean().item(), 'max_offdiag': off,\n"
        "            'n_absorbed_lt085': int((d < 0.85).sum()), 'n_absorbed_lt080': int((d < 0.80).sum()),\n"
        "            'n_latents': int(d.numel()), 'diag': [round(x, 3) for x in d.tolist()]}\n"
        "print('SEEDJSON', _j.dumps({'seed': SEED, 'vanilla': _stats(vanilla_cosine), 'matryoshka': _stats(matryoshka_cosine)}))\n"))
else:
    sys.exit("kind?")
nb = copy.deepcopy(nb); nb["cells"] = cells
json.dump(nb, open(f"{src}/seed{seed}_repl.ipynb", "w"), indent=1)
print(f"wrote {src}/seed{seed}_repl.ipynb ({len(cells)} cells)")
