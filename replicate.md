# replicate.md — how to re-run everything in this repo

For an LLM. Two kinds of thing are replicable here: **the analyses** (this repo's own scripts, all
CPU, deterministic) and **the 36 + 17 experiment runs** (other people's repos on one GPU). Section 1
is the analyses, §2 the protocol, §3–4 the per-row tables (GitHub link + the specific thing that
will otherwise cost you an hour), §5 the extension experiments, §6 the rules.

Everything below was executed on: **RTX 3090, 24 GB VRAM, 31 GB RAM, driver 580.x, Ubuntu/Pop!_OS,
`uv`, Python 3.11.** Anything hardware-sensitive says so.

---

## 1. The analyses in this repo (CPU, minutes)

```bash
python3 build_union.py            # -> union.json (741 records)   [--verify checks meta.py agrees]
python3 meta.py                   # -> numbers.json (1,336 keys)  ~7 s
python3 analyze.py                # -> analysis_numbers.json      ~10 s
python3 p3/findings.py            # -> p3/findings_numbers.json
python3 test_numbers.py           # fails if readme.md asserts a number no script emits
python3 replication/ledger.py     # -> ledger_summary.json + the extension tally
python3 replication/make_report_table.py   # regenerates META-REPORT.md's numbers
```

Inputs are read-only: `~/alignment-forum-scrape/`, `~/scrape-lesswrong/`, `~/neel-nandas-chris-olah/`.
**Do not re-run the source scrapes** — karma is an age-confounded snapshot and several comparisons
depend on both corpora sharing one.

The only non-deterministic layer is `p3/claims/*.json` (an LLM judge, 30 agents against
`p3/EXTRACT.md`). Re-running it will not give identical labels. It is already committed; treat it
as data, and if you re-extract, report both runs.

---

## 2. Protocol for an experiment row

1. `spec.json` in `replication/experiments/<slug>/` has `repo`, `head_sha`, `entrypoint`,
   `target_value`, `tolerance`, `budget_minutes`. Clone the repo, **check out that SHA**, never
   `git pull`.
2. Build one venv for that experiment. Default recipe:
   `uv venv --python 3.11` → `pip "setuptools<81" wheel` → torch **pinned, from the CUDA index, in
   the same resolver call as everything else** → the repo's requirements → the AST import scan
   (`replication/tree_imports.py`).
3. If the repo is from 2024–25 and anything breaks on an API that "used to exist", do not guess the
   version: **`uv pip install --exclude-newer <post date + 14 days>`**. This resolved three
   otherwise-dead rows in one flag. It does not work on the PyTorch index (no upload timestamps) —
   pin torch exactly there and date-freeze the rest.
4. **Translate the entrypoint; never execute it verbatim.** About a third are prose, a pipeline
   step, a chain, a notebook, a function library, or a command missing its required positional.
5. Environment-only fixes, on copies, each logged. Anything that changes what is measured makes it
   an *extension*, not a replication.
6. Pre-register the pass/fail rule before running. For a stochastic row, pre-register a **rate**
   (fraction of seeds inside the author's tolerance), not a point value.
7. Judge the measure the claim names, from data (`results/*.json`, executed notebooks, plotly
   arrays) — not from prose or PNGs, except for genuinely visual curve-shape claims.

`replication/lessons-synth.md` Part 3 is the symptom → cause → fix table; consult it the moment
anything fails. `replication/HARNESS.md` documents the queue if you want to run many rows unattended.

---

## 3. Rows that reached a measurement (20)

Outcome legend: ✅ exact = recomputed from source and matched · ✅ recompute = re-ran the author's
analysis over their committed artefacts · ⚠️ partial = some components matched · ❌ = located and
genuinely off · ⛔ = blocked by the rules.

| post + repo | run this | target | outcome | what you need to know |
|---|---|---|---|---|
| [post](https://www.lesswrong.com/posts/oSAiKTpQjjKmeeTvT/) · [`ai-forever/data_leakage_detect`](https://github.com/ai-forever/data_leakage_detect) @ `dedaa5e5` | `shift_detection/run_attack.py` | AUC ≈ 98.6% | ✅ exact | Runs clean. `--dataset vl_mia_img_Flickr_2k --attack bag_of_visual_words`. |
| [post](https://www.lesswrong.com/posts/x2ZdCoqAaLedpjDk3/) · [`ameya-bit/quotesbyniche`](https://github.com/ameya-bit/quotesbyniche) @ `135fa893` | `interp/niche_attention_analysis.ipynb` | B5H0 copying score 0.615 vs next-highest head 0.35; OV circuit shows a | ✅ exact | Runs clean (notebook, GPT-2 scale). |
| [post](https://www.lesswrong.com/posts/nnHnNdHLhbrnmEXDr/) · [`coolvision/interp`](https://github.com/coolvision/interp) @ `cfe19a1b` | `LLaMA_jun_4_2025_neurons.ipynb` | non-symmetric, long-tailed distribution with a significant number of n | ✅ exact | No usable requirements file: install plotly, jupyter/nbconvert/ipykernel, transformers, transformer-lens. |
| [post](https://www.lesswrong.com/posts/YGAimivLxycZcqRFR/) · [`cywinski/codi`](https://github.com/cywinski/codi) @ `f0bf2fa0` | `experiments/4_mean_latent_patching_same_vs_diff.py` | model recovers ~20% accuracy (from 55% baseline) when patching in late | ✅ exact | Run `prepare_prompts_json.py` first (README step 1) — script 5 reads its output. Budget ~95 min, not the catalogue's 45. |
| [post](https://www.lesswrong.com/posts/zKyKDre78napvtrEo/) · [`fractalmachinist/ioi`](https://github.com/fractalmachinist/ioi) @ `1571259a` | `experiments.ipynb` | mean drop 0.23, SD 0.84 (n=128 matched pairs), paired t=3.09, p=0.0024 | ✅ exact | No requirements file: install transformer-lens + scipy + the notebook stack. `SIZE="medium"` → n=128. Deterministic **given `SEED`** — see §5, the effect is 30% larger across other seeds. |
| [post](https://www.lesswrong.com/posts/S9xyqRAziRMCcJQmz/) · [`jaehoonlee0829/cross-model-alignment-geometry`](https://github.com/jaehoonlee0829/cross-model-alignment-geometry) @ `bfacecff` | `scripts/run_corrected_permutation_tests.py` | cross-family max debiased CKA ~0.18-0.22 (mean 0.05-0.11) vs within-fa | ✅ exact | `PYTHONPATH=<repo root>` (scripts import `src.*`). Pre-download the 22 GB of models over HTTP with `HF_HUB_DISABLE_XET=1`. ~100 min **per eval** — run control eval C first; D and E were never run. |
| [post](https://www.lesswrong.com/posts/jZfNX4GJPdptxSxt4/) · [`lovkush-a/arena-sandbagging-mi`](https://github.com/lovkush-a/arena-sandbagging-mi) @ `d801cd70` | `experiments/exp07_add_noise_with_batches.py (uses src/eval_model_on_da` | for some seeds, accuracy of the sandbagging-prompted model increases a | ✅ exact | Pin `transformers<5`. `src/src/eval_model_on_dataset.py` never imports `SYSTEM_PROMPT` it uses as a default arg → NameError at import in every commit; add the import. ~1 min per pass, 102 passes. |
| [post](https://www.lesswrong.com/posts/rs2BmwXWJEaEfNr2v/) · [`mild-rgb/qwen-2.5-1.5b-echo_repeat-investigation`](https://github.com/mild-rgb/qwen-2.5-1.5b-echo_repeat-investigation) @ `3c0bf77b` | `2_copy_circuit_survey.ipynb` | head 2 always in top-3 heads across 44 words and both 'repeat'/'echo'  | ✅ exact | Install einops + notebook stack + transformer-lens. Judge the **ablation** ranking (the claim names it), not DLA. |
| [post](https://www.lesswrong.com/posts/WMfSbt7AAcJdHzysB/) · [`mshinkle/activation_plateau_mechanisms`](https://github.com/mshinkle/activation_plateau_mechanisms) @ `4222c3ef` | `full_experiment.sh (runs scripts/interpolate_and_record_activations.py` | freezing MLP block outputs completely eliminates plateaus; freezing at | ✅ exact | Run the `.sh` with `bash -e` and the venv on PATH. Writes ~35 GB of activation tensors — delete after judging. The final Jacobian step OOMs on 24 GB; the headline is already produced by then. |
| [post](https://www.lesswrong.com/posts/zbebxYCqsryPALh8C/) · [`noanabeshima/matryoshka-saes`](https://github.com/noanabeshima/matryoshka-saes) @ `7b80f5fe` | `train_saes_on_toy.ipynb` | Matryoshka SAEs have higher MMC than vanilla SAEs at the same L0 acros | ✅ exact | Notebook copy with `import torch.nn.functional as F` prepended (used, never imported). Toy half only — the TinyStories LM half has no code in the repo. |
| [post](https://www.lesswrong.com/posts/PagGF8roBJmjLunsX/) · [`patrickod32/seq2feature`](https://github.com/patrickod32/seq2feature) @ `f0616acd` | `notebooks/02_evaluate_probe.ipynb` | 0.956 top-5 agreement, 0.90 AUC (seq2feature int8, 5.3MB) vs 0.84/0.75 | ✅ recompute | Rewrite Colab `/content` paths; `--allow-errors` (final cell is a `files.download`). Recompute over the committed probe, not a retrain. |
| [post](https://www.lesswrong.com/posts/zQqGhKPqaCBZZDCge/) · [`peppinob-ol/attribution-graph-probing`](https://github.com/peppinob-ol/attribution-graph-probing) @ `bbff7525` | `scripts/research/graph_subgraph_scores.py` | concept-aligned subgraphs average 0.5394 Replacement and 0.8257 Comple | ✅ recompute | The headline is the **fact variant** (`usa_states_fact_batch`), not the 5-dataset default summary. Read every file in `output/`. |
| [post](https://www.lesswrong.com/posts/ZwEer94AefjdW4933/) · [`phusroyal/phu-bluedot_1st_puzzle`](https://github.com/phusroyal/phu-bluedot_1st_puzzle) @ `27a8be7e` | `src/predefined_manifold (run via `uv run python -m src.predefined_mani` | linear probe AUC falls from 0.9996-0.9998 (ClassOT) to 0.57-0.67 (GFAL | ✅ exact | Use the repo's own command: `uv sync && uv run python -m src.predefined_manifold run --device cuda`. Judge the **GFAL+** variant (what the post reports). Seed-fragile — see §5. |
| [post](https://www.lesswrong.com/posts/aFyir2PaoCHK5prAu/) · [`star2vec/tarcle`](https://github.com/star2vec/tarcle) @ `37831a33` | `tarcle/extract.py (Stage 1, GPU: causal-head identification + FV extra` | margin +0.35 (12 months) and +0.34 (9 months) down to -0.31, -0.46, -0 | ✅ recompute | Do **not** start with `extract.py` (GPU stage-1, needs a positional config). The README's reproduction path is the numpy-only stage-2 chain over committed artefacts: `python -m tarcle.{stage2,floors,measure_corr,margin_split,offset_audit,support_gate}`. Chain with `|| echo FAILED $m`, not `|| break`. Nonzero exits from `stage2`/`floors` are the author's append-only write-guard tripping on an unseeded permutation null — the numbers printed above are valid. |
| [post](https://www.lesswrong.com/posts/jauWv9BEbdCYcRy2d/) · [`vaiyr/probe-necessity`](https://github.com/vaiyr/probe-necessity) @ `31017ee2` | `scripts/run_autopicker_battery.py` | recovers all 17 causal handles that exist and correctly alarms on the  | ✅ recompute | Runs clean; recompute over committed artefacts. |
| [post](https://www.lesswrong.com/posts/523bkuMjSjKjG8jn6/) · [`idostik/llm-typos-interpretability`](https://github.com/idostik/llm-typos-interpretability) @ `4f52a47a` | `llm-typo-experiment.ipynb (per-head ablation loop / logit-difference c` | only the subword merging head (L0H3) showed a significant impact on lo | ⚠️ partial | Stub the `login()` placeholder; `--allow-errors`. The L0H3 mechanism reproduces; the exclusivity sweep dies on transformer-lens arity drift. |
| [post](https://www.lesswrong.com/posts/Eft6ehAcvR8MxFbsR/) · [`jeffreywilliamportfolio/jlens-basin-swaps`](https://github.com/jeffreywilliamportfolio/jlens-basin-swaps) @ `1f68458b` | `reproduce/run_reproduction.py` | paperclip swap 3/3 per batch; doom ablation 3/3; doom string appears 2 | ⛔ hosted API | The reproduction script POSTs to a hosted Neuronpedia API. Not locally reproducible under these rules. |
| [post](https://www.lesswrong.com/posts/JZK2xkedJwA7njKmN/) · [`jordanmccann/polymorphism-is-rotation`](https://github.com/jordanmccann/polymorphism-is-rotation) @ `483a40a9` | `python -m replicate run-fast (replicate/run_fast.py; e.g. polymorphism` | 0.976-0.990 on toy model (vs worst-case -6.56 pre-rotation); 0.85-0.99 | ⚠️ partial | `python -m replicate fetch-artifacts` **then** `run-fast`. Repo `verify` passes 6/6 on Haar statistics that are not the headline; the Pythia post-rotation EV is the headline and comes out 0.2–0.5 vs 0.85–0.99. |
| [post](https://www.lesswrong.com/posts/EXj2bYK2rg8TMrncF/) · [`shivasrightfoot/soo-jailbreak-conceptual-fusion`](https://github.com/shivasrightfoot/soo-jailbreak-conceptual-fusion) @ `c4bf965d` | `02_soo_conceptual_fusion_training.ipynb` | ~20% (base model) to a little under 90% (conceptual fusion, layer 18,  | ⚠️ partial | `sys.modules` stub for `google.colab` **with `__spec__` and `__path__`**; `--allow-errors`. The fusion method reproduces; the ASR percentage needs a separate eval notebook at a different retention setting. |
| [post](https://www.lesswrong.com/posts/nWiwv4GN8aYqpnZKE/) · [`wassname/antipasto`](https://github.com/wassname/antipasto) @ `5e0f8517` | `nbs/train.py gemma1b-24gb (training) + nbs/eval_baseline_prompting.py ` | 31.2±5.3 (AntiPaSTO) vs 13.0 (engineered prompting) vs 4.5 (prompting) | ❌ not reproduced | **The one scientific miss.** Reproduces on Gemma-270M (41.7 vs 38.7), not on 1B (2.0 vs 31.2). `git log -S` shows the paper's 1B config (lr 1e-3, r 128, n_modules 64, 800 pairs) never existed as a default in any commit. Force eval batch ≤8 (fp32 logits over a 262k vocab OOM at 32). `--quick` gives NaN Steer F1 by construction. |
## 4. Rows that never reached a measurement (16), and how to get past each

Eight of these were re-attempted with the environment reconstructed; seven then produced a
measurement and none contradicted its author. The recipes below are what worked.

| post + repo | ledgered as | how to get past it |
|---|---|---|
| [post](https://www.lesswrong.com/posts/nKRvp7LKgjJxbpykq/) · [`artmtt/sae-interpretability-small-reasoning-model`](https://github.com/artmtt/sae-interpretability-small-reasoning-model) @ `50c2b40b` | `data` | **Reversible.** The missing inputs are produced by the repo's own commented-out `create_and_save_model_inferences` cell. Re-enable it on a copy for the first 32 GSM8K prompts (the author's comment says "Finished 31 inferences"), seed the T=0.6 sampling, then run the analysis. 5 min. Shape reproduces; the post's feature ids do not — the post's statistic is not printed by the notebook. |
| [post](https://www.lesswrong.com/posts/dS5dSgwaDQRoWdTuu/) · [`dajale423/error_pathology`](https://github.com/dajale423/error_pathology) @ `a963531e` | `env` | **Not reversible here.** Env resolves (torch 2.2.2+cu121, transformer-lens 1.14, transformers 4.35.2; drop the repo's `transformer-lens==1.10.0` pin — its own git dep needs ≥1.14). `unset CI` or `e2e_sae` demands `GITHUB_WORKSPACE`. Then `sensitive_direction.py` hard-codes `args.e2e="h9hrelni"` and calls `SAETransformer.from_wandb` on **every** path → W&B login. True class: `model-access`. |
| [post](https://www.lesswrong.com/posts/ZB6guMhHH3NEyxA2k/) · [`filyp/sneaky-mamba`](https://github.com/filyp/sneaky-mamba) @ `b44a1d34` | `env` | **Not reversible in 3 tries.** `mamba-ssm`'s `selective_scan_cuda` will not import: prebuilt wheel ABI-mismatches torch (`undefined symbol _ZN3c104cuda…`), and a forced source build still mismatches (nvcc 12.0 vs torch-cuda 12.1, plus later installs bumping torch). If you retry: install/pin torch first, build the kernel last, install nothing after. |
| [post](https://www.lesswrong.com/posts/iDyf7aBdvBp9jnfuY/) · [`ibm/sae-steering`](https://github.com/ibm/sae-steering) @ `f06eeef5` | `env` | **Reversible, four layers deep.** (1) `requirements.txt` is unsatisfiable as a set — the pinned `openai/sparse_autoencoder@4965b94` requires `transformer-lens==1.9.1` while the file pins `2.2.2`; install the file minus that line, then the git dep `--no-deps`. (2) The SAE it loads is uncommitted: fetch `sparse_autoencoder.paths.v5_32k("resid_post_mlp", 9)` (201 MB) to `{path}/gpt.top_k32.f0.pt` (`path=""` in the script). (3) Three `Storage/*.csv` intermediates are uncommitted: regenerate with the repo's own `process_D_ref` / `D_align_scoring`. (4) `timing_tests.py` unpacks 5 values from a `setup()` that returns 4 — broken at the pinned commit; the 5th is unused. Headline is a timing claim: hardware-specific, judge direction only. |
| [post](https://www.lesswrong.com/posts/wezSznWnsMhpRF2QH/) · [`jim-maar/interpretability`](https://github.com/jim-maar/interpretability) @ `73bc8f29` | `env` | **Reversible, four layers deep.** (1) `utils.py` asserts its directory is named `interpretability` — a symlink resolves, so *copy* the checkout into a directory of that name. (2) `othello_world/` is an empty gitlink with no `.gitmodules`: `git ls-tree HEAD othello_world` gives `f23bb56`; clone `likenneth/othello_world` and check that out. (3) `training_utils` lives in `training_probes/` — add it to `PYTHONPATH`. (4) The script indexes games 200…200,200 but the committed data file has 100,000 — the author had a larger uncommitted file; `batches=499` uses everything available. Env: freeze at 2025-02-16 (torch 2.0.1, transformer-lens 2.0.0). |
| [post](https://www.lesswrong.com/posts/f6LoBqSKXFZzMYACN/) · [`tenseisoham/finetuning-mechinterp`](https://github.com/tenseisoham/finetuning-mechinterp) @ `483cc014` | `env` | **Reversible with one flag.** `uv pip install --exclude-newer 2025-03-14` (post date + 14 d) resolves transformers 4.49.0, where `evaluation_strategy` still exists. The catalogued headline "160.87 vs 49,802" is **average perplexity** from `logit-lens-analysis.ipynb`, not a pairwise distance. `post-finetune-gpt2small.ipynb` additionally needs `seaborn`. |
| [post](https://www.lesswrong.com/posts/Qnm6gAFnCPaJsbhSS/) · [`thebuleganteng/interpretability-prototyping`](https://github.com/thebuleganteng/interpretability-prototyping) @ `5ef40554` | `env` | **Reversible — and the ledgered diagnosis was wrong.** The `KeyError: '11-res-jb'` is not a registry rename: the notebook loads four SAEs *from disk* at `~/.cache/sae_lens/blocks.{6,8,10,11}.hook_resid_pre` with a loop that `continue`s silently when a path is missing, and a later cell indexes the empty dict. Populate the cache from the public release `gpt2-small-res-jb` (`SAE.from_pretrained` + `save_model`) at the repo's own pins. CPU-only, 19 min. |
| [post](https://www.lesswrong.com/posts/rwu73dCE3uWjieijK/) · [`uchicago-xlab/superposition-replication`](https://github.com/uchicago-xlab/superposition-replication) @ `d4aa6b7c` | `env` | **Reversible — the failure was the harness's, not the repo's.** A plain venv (torch/numpy/matplotlib) on today's stack runs it in 9 min. The catalogued entrypoint `python -m synth.run` omits its required positional: run `synth.run h1` and `synth.run h2`. |
| [post](https://www.lesswrong.com/posts/rtp6n7Z23uJpEH7od/) · [`ckkissane/sae-dataset-dependence`](https://github.com/ckkissane/sae-dataset-dependence) @ `2c991ba0` | `model-access` | Env fixes (`sae-lens<4`); the SAE is behind a W&B artifact login. Not reproducible under these rules. |
| [post](https://www.lesswrong.com/posts/8zDjhJNoFhMuHB5Kc/) · [`g-w1/gradient-routed-vae`](https://github.com/g-w1/gradient-routed-vae) @ `a644302f` | `runtime` | `vae.py` trains 30 VAEs × 100 epochs + a classifier. ~2 VAEs in 120 min; a 360-min box also timed out. Budget ≥8 h or reduce nothing (scoping would change what is measured). |
| [post](https://www.lesswrong.com/posts/ronAKFdTDE7tiZk2c/) · [`james-sullivan/arithmetictransformer`](https://github.com/james-sullivan/arithmetictransformer) @ `4a10f5e1` | `runtime` | The catalogue entrypoint `EstimateLLC.ipynb` needs `saves/check_point_50/*.pth`, which is uncommitted; the only producer is `GrokkingAdditionMultiplication.ipynb` (~6000 epochs × ~8 ratios). Notebooks are in `src/src/`. Multi-hour by nature — grokking *is* delayed generalisation. |
| [post](https://www.lesswrong.com/posts/wxPvdBwWeaneAsWRB/) · [`mamiglia/deep-dive-l1h5`](https://github.com/mamiglia/deep-dive-l1h5) @ `6c45e47d` | `runtime` | `skew_analysis.py` sweeps the full vocabulary through hooks layer by layer: 2 of 12 layers in 60 min → ~6 h. Pin `sae-lens<6`. Scoping to one head would change what is run. |
| [post](https://www.lesswrong.com/posts/boB3hJiZijxM3J6Ed/) · [`ak47na/top_down_vs_bottom_up_mi`](https://github.com/ak47na/top_down_vs_bottom_up_mi) @ `24b2cb90` | `unclear-entrypoint` | Needs pre-generated completions plus a W&B artifact; early cells reference a stale sibling project. Expected true class: `model-access`. Untried in the reversal series. |
| [post](https://www.lesswrong.com/posts/qdxNsbY5kYNqcgzFb/) · [`ayoakin/mivlde`](https://github.com/ayoakin/mivlde) @ `36046d46` | `unclear-entrypoint` | **Reversible.** The headline is not in the catalogued script (`run_experiment.py` is a function library, and its own `r2_prediction_experiment` probes only the final decoder layer). It is in `subteams/LLMProbing/notebooks/more_layers_r2.ipynb`; `r2_experiment.ipynb` regenerates the inputs (800 samples, seed 42 → ODEFormer activations). Locally: drop the `%pip`/Drive cells, point paths at local dirs, and put **the cloned ODEFormer repo root** on `sys.path` (the sample generator imports `parsers.py`, which the PyPI package does not ship). Freeze at 2025-05-22. ~45 min. Best layer 7 reproduces; Spearman 0.34 vs the claimed 0.75. |
| [post](https://www.lesswrong.com/posts/ifbNtv8QbNBrYFSSv/) · [`sunmoonron/super-weight-circuit-patching`](https://github.com/sunmoonron/super-weight-circuit-patching) @ `dbc14761` | `vram` | `07_compare_patch.py` loads 3× fp32 OLMo-1B state dicts into 31 GB RAM → SIGKILL(137). Switching `DEVICE="cpu"`→`"cuda"` puts the identical computation on the 24 GB card (fp32×3 ≈ 12 GB) — worth retrying that way. |
| [post](https://www.lesswrong.com/posts/aWYQHh2pEFCLYh85C/) · [`syvb/natural_language_autoencoders`](https://github.com/syvb/natural_language_autoencoders) @ `85399df1` | `vram` | `setup_box.sh` pulls six Qwen2.5-7B checkpoints (~90 GB) with the author's token; the sweep loads 7B AV+AR models on an assumed 48 GB card. Out of scope for a 3090. |
---

## 5. The extension experiments (what a reproduction depends on)

These are **not replications** — each changes one declared thing and is ledgered
`experiment_class: "extension"`. Recipes, so they can be redone or extended to other rows:

| experiment | recipe | result |
|---|---|---|
| **Seed variance** (`ext_seed_census.sh`, `ext_seed_nb.py`) | Take a reproduced row, make N seeded copies of the entrypoint changing **only** the seed (a `--seed` flag; or `torch.manual_seed`/`np.random.seed` prepended to an unseeded notebook), run 5, print one JSON line of the headline statistics per seed. | ioi: effect is 30% larger across seeds than the author's seed; phusroyal `sphere_shell`: bimodal, **4/15** seeds inside the claimed range; matryoshka toy: invariant (SD 0.002). |
| **Sampling rate** (`run_rate.sh`) | For a "works for some seeds" claim, run 20 more draws at the informative settings against one baseline and report a rate with a Wilson interval. | Noise-injection sandbagging: reveals capability on **67% [49, 81]** of draws, *collapses* the model on **23% [12, 41]** (n=30). The author's 6/10 and our 9/10 are both ordinary draws. |
| **Library epoch** (`run_epoch.sh`) | Same code, same seeds, one library changed. Store per-item outputs so the arms can be `diff`ed. | `transformers` 4.53.3 vs 4.57.6: **35,700/35,700 generations byte-identical**. torch 2.6 → 2.13: 65% of generated text rewritten, max pass-level swing 6.6 pp, **verdict and seed ranking unchanged** (Spearman 0.90); seed SD / kernel SD = 3.5. |
| **Second family** (`run_family.sh`) | Same prompts/data/grid/seeds, one model swapped. Pre-register a stop-rule for whether the phenomenon exists on the new model at all. | Llama-3.2-1B: the sandbagging *prompt* only half-works (9 pp gap vs 26), so the noise effect is **untestable**, not falsified. The noise grid is model-specific (absolute σ vs weight scale). |
| **Bug injection** (`ext_buginject.sh`) | Run a reproduced row clean and with one realistic injected bug (variable swap, off-by-one layer, config value silently not applied). Hand both outputs to a **blind judge** with the claim and tolerance, labels shuffled. | **7/7 correct.** One bug was caught by the author's own input assertion before any statistic ran. Caveat: bugs were realistic, not sub-tolerance. |
| **Rot reversal** (`run_tt.sh`, `run_art.sh`) | Re-attempt a never-located row with the environment reconstructed at the post date and uncommitted artefacts regenerated by the author's own code. | 8 attempted → 7 measured → 3 exact + 4 partial, 0 scientific misses; 1 credential-gated. |

## 6. The three protocol experiments

Self-contained prompts in `~/prompts/3090/` (also `3090-prompts.md`): cross-model geometry
(`jaehoonlee0829`, a negative result on the Platonic Representation Hypothesis), AntiPaSTO honesty
steering (`wassname`, the one scientific miss), noise-injection sandbagging (`lovkush-a`, now
re-tiered as a 67% rate). Each carries setup, exact commands, the target table, a pre-registered
tolerance, a budget and the ledger call. Paste one into a fresh session; nothing else is needed.

## 7. Rules any continuation inherits

1. Environment-only fixes on replication rows; anything else is an extension and never enters the
   reproduction rate.
2. No hosted-model APIs, even keyless (→ `api-key`). No accounts or logins (→ `model-access`).
   Two rows are blocked this way and stay blocked.
3. No pushes to authors' repos, no issues, no author contact, no new forks. Three forks exist by the
   user's decision.
4. Cap requeues at 2–3, then ledger the honest reason. A clean `env` row is a finding.
5. One GPU job at a time; delete the venv after each run; keep ≥25 GB free (`uv cache clean` — the
   cache reached 78 GB across 14 environments); detach long runs (`setsid nohup`) and watch the log.
6. Report tiers honestly: a 3-decimal match with the author's seed is `exact-same-seed`; a recompute
   over committed artefacts is `recompute`; only ≥5 seeds earns `robust`.
