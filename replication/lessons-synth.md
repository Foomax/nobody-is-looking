# lessons-synth (v3) — synthesis of lessons-1 … lessons-25 (2026-08-29)

Supersedes v2. Sources: ~50 h of ledger replication (lessons-1…22), the two hours-class rows
(23–24), and the 15-run variance-decomposition / rot-reversal program (25 + `NEW-DIRECTION.md`).
Part 1 principles · Part 2 phase checklist · **Part 3 the symptom → cause → fix catalogue (the
reusable core)** · Part 4 tiers · Part 5 numbers for this card.

---

## Part 1 — Principles

**P1. Check the system before the science.** Nearly every hour lost was infrastructure wearing an
experiment's mask: a stalled download, a full disk (the `uv` cache alone reached 78 GB), a harness
task killed at startup while the process lived on, a RAM-OOM SIGKILL, a shell that exports `CI`.
When a run fails fast, silently, in a burst, or exits 0 in 0 min, verify disk/RAM/network/process/
invocation before reading the traceback as science.

**P2. The catalogue describes; it does not command.** `spec.json.entrypoint` is a pointer: prose,
a pipeline step, a chain, a notebook, a function library, a script missing its required positional
(two rows), a script that cannot produce the headline at all (the headline lived in a different
notebook). Read and translate every entrypoint; never execute it verbatim.

**P3. Environments are budgets** — time, VRAM, RAM, disk, and *library epochs*. 2024–25 repos
break under 2026 majors; some also break under their own `requirements.txt` (two were unsatisfiable
as a set at publication).

**P4. Fix the environment, never the measurement — on copies, one named `--fix` line each.**
Imports, paths, `PYTHONPATH`, batch size, device, dtype, version pins, resolution dates, Colab stubs,
placeholder logins, submodules, artefact fetches, symlinked/renamed dirs, `unset CI`, unpacking an
unused return value: environment. Prompts, thresholds, dataset slices, metrics, seed counts, model:
a different experiment — and if you run it anyway, it is an **extension**, ledgered as such.

**P5. Install the whole environment at once, in one resolver call.** A pin in an earlier call is
not a constraint on a later one (`accelerate` re-resolved torch 2.3.1 → 2.13; `odeformer` bumped
2.2.0 → 2.4.1). Check the version line before trusting an arm.

**P6. Judge from data, not pixels or prose.** Executed notebooks and saved HTML carry the arrays;
`results/*.json` beats the README; `git log -S` the config to test whether the paper's setting ever
existed; store per-item outputs so two runs can be `diff`ed (35,700 generations byte-identical is
stronger than any statistic).

**P7. Pre-register, honour the rule, disclose the deviation first — and judge the measure the claim
names.** Verify what the notebook actually prints (a catalogued "pairwise distance" was perplexity;
a "0.818 overall" was one cell of a 25,207-cell tensor). Split compound claims; mark unmeasured
halves `UNRESOLVED`.

**P8. A satisfied loss / a green `verify` / a committed graph / a 3-decimal match is not a
reproduction.** A byte-identical recompute of committed artefacts is `recompute`; a 3-decimal match
with the author's seed is `exact-same-seed`; only a match that survives other seeds is
`robust-across-seeds`. State the tier.

**P9. Sequential, observable, resettable, disk-bounded, detached automation.** One GPU job at a
time; one log line per node; a plain-text done-list; delete venvs per run; refuse below the floor;
**detach with `setsid nohup` and watch the log** — harness background tasks can be killed at
startup while the process survives.

**P10. Rank follow-ups by "would this flip the verdict?"** Seeds flipped verdicts (phusroyal
4/15); torch versions did not; `transformers` minor versions changed nothing at all.

**P11. Outward-facing actions are minimal and confirmed.** No forks/PRs/issues/accounts/author
contact; never paste secrets. A W&B login is `model-access`, not a fix.

**P12. Keep two readers in mind.** Ledger row is the deliverable; `human-oversight.md` in plain
language; handoff (state) + lessons (delta) per juncture.

**P13. Don't grind the tail past its information value.** ≤2–3 requeues, then the honest reason.
The build-fail *is* the datum.

**P14. The harness is a deliverable.** Prep/autofix/import-scan/notebook-stub/queue tooling plus
this catalogue; plus, now, `--exclude-newer` freezing and `ext_*` extension runners.

**P15 (new). `env` is an onion; the first exception is the shallowest layer.** Six `env` rows
re-attempted: assert → empty gitlink → notebook path → uncommitted dataset; unsatisfiable lockfile →
uncommitted SAE → uncommitted intermediates → code broken at HEAD. 0/6 first diagnoses named the
terminal cause. Before classifying, peel one more layer: *read the loader*, list the files the script
opens, check `len(data)` against the index range.

**P16 (new). Reconstruct the date, not the versions.** `uv pip install --exclude-newer <post date +
14 d>` resolved three rows in one flag, where hand-pinning had failed twice; version claims in
diagnoses ("removed in ~4.46") were wrong by several minors. Inapplicable to the PyTorch index (no
upload timestamps): pin torch exactly from the CUDA index and freeze the rest.

**P17 (new). Uncommitted artefacts are the most common rot, and the author's own code usually
regenerates them.** SAE caches from a public release; pipeline intermediates from the repo's own
functions; a commented-out generation cell; a broken submodule pointer whose upstream still exists.
Regenerating with the author's code is an artefact fetch, not a design change — log it as `--fix`.

**P18 (new). A seed count is a scientific variable, not hygiene.** One in three reproduced training
rows was seed-bimodal; a "for some seeds" claim was a 67% coin with a 23% collapse rate; the first
ten seeds were the least representative ten of thirty. Run ≥5 seeds before tiering above
`exact-same-seed`; report rates with Wilson intervals.

---

## Part 2 — Phase checklist (condensed)

- **Before GPU:** export `HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 WANDB_MODE=disabled
  PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false`; `unset CI`; `df -h /` (floor ≥25 GB; `uv cache
  clean` if the cache is large); pre-download models over HTTP; read the author's committed outputs
  and per-item timing; `git log -S` the config; list the files the entrypoint opens and check each
  exists in the checkout; pre-register the criterion in `run.log` (as a *rate* if seeded).
- **Env:** one resolver call; torch pinned exactly from the CUDA index; everything else
  `--exclude-newer <post date + 14 d>` (or the repo's lockfile if it resolves); `setuptools<81`;
  notebook stack for `.ipynb`; full `tree_imports.py` list; per-package fallback; print the version
  line and read it; delete the venv after the run.
- **Entrypoint translation:** back-ticked command → verbatim; chains via `bash -e`; `.ipynb` →
  nbconvert `--execute --allow-errors` on a *copy*; `pkg/module.py` → `python -m pkg.module`;
  `from src.x` → `PYTHONPATH`; required positionals supplied (`--layer 6`, `h1`); Colab → `/content`
  rewrites + `sys.modules['google.colab']` stub with `__spec__`/`__path__`; Drive paths → local dirs;
  `assert dir.name == X` → a *copy* named `X` (symlinks resolve); missing inputs → prepend the
  author's generator; empty gitlink → clone upstream at the gitlink commit.
- **Run:** detached, one GPU job; time-box from the author's timing; batch ≤8 on 24 GB; watch the
  log with a `Monitor` on `RUN-EXIT`; "EXIT 0 in 0 min" or a burst of instant exits is a red flag.
- **Judge:** the named measure; what the script itself prints; per-item outputs stored for `diff`;
  ordinals → indices; mean/min/fraction for "~90%" claims; ≥5 seeds before `exact`; rates with
  intervals; hosted API → `api-key`; login → `model-access`; partial → `UNRESOLVED` halves; never
  ledger a failure that points at your own invocation or at the harness.
- **Ops:** VERDICT + `report.py`/`ext_ledger.py` → human/machine docs → copy verdict artefacts into
  the row folder → commit `replication/` (+ `prompts2/`) → mirror.

---

## Part 3 — Failure-mode catalogue (symptom → cause → fix)

| symptom (in log) | cause | fix |
|---|---|---|
| silent, no writes/socket for >5 min, GPU idle | xet download stall | `HF_HUB_DISABLE_XET=1`; kill, delete `.incomplete`, HTTP re-download |
| burst of "EXIT in 0s", ENOSPC, lost command output | disk full (venvs + **uv cache** + HF cache) | `uv cache clean`; delete finished venvs; floor ≥25 GB; delete venv per run |
| harness background task "killed" ~20 s after start, process still running | harness task limits (once coincided with disk < floor) | detach (`setsid nohup … &`), watch the log with a Monitor |
| `SIGKILL`/137 on a CPU node | system-RAM OOM (fp32×N model copies) | move to GPU (`DEVICE`), a hardware knob |
| CUDA OOM in `calc_nll`/vmap | 80 GB-era batch on 24 GB | eval batch ≤8; full-residual Jacobian on a large model = `vram` |
| `ModuleNotFoundError` for a normal package | import scanner missed a transitive dep | pre-install; `typeguard`+`jaxtyping` for transformer-lens; per-package fallback |
| `No module named 'src'` / `'training_utils'` / `'parsers'` | wrong CWD, a subdir the author had on the notebook path, or a module from a *cloned* repo (not the pip package) | `PYTHONPATH` += repo root / subdir; clone the upstream repo the author cloned and add its root |
| `NameError: true` / notebook JSON in traceback | runner fed an `.ipynb` to Python | dispatch on extension; nbconvert |
| `TRANSFORMERS_CACHE` import error | removed in transformers 5 | `transformers<5` |
| `datasets` `HfUriError` / `'imdb'` non-namespaced | removed in datasets 4 | `datasets<4` |
| `TrainingArguments(evaluation_strategy=)` TypeError | removed in a later 4.x than diagnosed (still in 4.49) | `--exclude-newer <post date>`; don't guess the version |
| `sae_lens.toolkit` / `sae_lens.sae` missing | moved across sae-lens majors | `sae-lens<6` / `<4` |
| `KeyError: '<sae id>'` two cells after the loader | a silent-skip loader (`continue` on a missing local cache) — an **uncommitted artefact**, not a registry id | populate the cache from the public release (`SAE.from_pretrained` + `save_model`); read the loader first |
| `pkg_resources` missing (wandb) | setuptools ≥81 | `setuptools<81` |
| `params_t` from torch.optim | removed in torch 2.6 | `torch==2.3.1` from cu121 (may re-break transformer-lens) |
| a pinned torch silently becomes the newest torch | a later unconstrained install re-resolved it | pin torch in the same call as everything else; read the version line |
| `--exclude-newer` resolves nothing from the PyTorch index | no upload timestamps there | pin torch exactly, freeze the rest by date |
| `not enough/too many values to unpack` in mech-interp | transformer-lens API arity drift | match the author's transformer-lens version, else `env` |
| `ValueError: expected 5, got 4` unpacking a helper | **code broken at publication** (script written against another helper version) | fix on a copy only if the extra value is unused; class `code-bug at HEAD` |
| requirements.txt unsatisfiable at any date | self-contradictory pins (a git dep pins a different major) | install minus the contradiction; git dep `--no-deps`; class `broken lockfile at publication` |
| `cannot import name Sae from sparsify` | wrong PyPI `sparsify` | `pip install "git+https://github.com/EleutherAI/sparsify.git"` |
| `No module named e2e_sae.scripts` | fork wheel omits `scripts/` | editable clone on `PYTHONPATH` |
| `KeyError: 'GITHUB_WORKSPACE'` | this shell exports `CI` | `unset CI` |
| `google.colab.__spec__ is None` | incomplete stub | `sys.modules` stub with `__spec__`+`__path__` |
| `login("Your hf token")` raises | placeholder secret | stub on a copy; cached token used |
| `FileNotFoundError: <intermediate>.csv/.pt` | an earlier pipeline step / a commented-out cell produces it | prepend the author's generator (`prepare_*.py`, `process_D_ref`, the commented cell) on a copy |
| `IndexError` deep in a data loop after a clean env | committed dataset smaller than the script indexes (author had a larger uncommitted file) | check `len(data)` vs index range; deviation on a copy; ledger partial with n |
| `assert dir.name == "<repo>"` | dir-name assert; symlinks *resolve* | copy the checkout into a dir of that name |
| empty directory where a submodule should be, no `.gitmodules` | broken gitlink | `git ls-tree HEAD <dir>` → clone upstream at that commit |
| `AssertionError: upload X to /content` | Colab upload cell | rewrite `/content` paths |
| nonzero exit with a full table of numbers above it | author's append-only write-guard tripped by an unseeded stochastic field | read the last lines; the computation succeeded (lessons-23) |
| `undefined symbol: _ZN3c104cuda…` | CUDA-extension wheel ABI ≠ installed torch | pin torch first, build the kernel last (`--no-build-isolation`, force-build), install nothing after; 2–3 tries then `env` (lessons-24) |
| exits 0 in 0 min, no output | function library needing uncommitted data | `unclear-entrypoint` — then find the notebook that *does* produce the headline |
| `wandb: api_key not configured` | artefact behind a W&B login, often hard-coded on every path | `model-access`; do not create an account |
| runs, times out, k/N of a loop done | multi-hour work mis-tagged "minutes" | `runtime`; queue overnight at the author's budget |
| entrypoint POSTs to a hosted API | not local inference | `api-key` |
| an "exact" 3-decimal match | same RNG seed as the author | tier `exact-same-seed`; run ≥5 seeds |

---

## Part 4 — Reproduction quality tiers

- **T-exact-same-seed:** matches to stated precision with the author's seed/config (most `exact`
  rows before R-1 are this). Say so.
- **T-robust-across-seeds / T-rate:** ≥5 seeds; report the fraction inside the author's tolerance
  with a Wilson interval (sandbagging 67% [49, 81]; phusroyal 27% [11, 52]; matryoshka 5/5).
- **T-recompute:** the author's committed artefacts re-analysed and matched; the upstream
  computation not regenerated (vaiyr, peppinob, patrickod, tarcle).
- **T-partial / direction:** some components or the direction only (jordanmccann; jim-maar; ibm;
  ayoakin; artmtt-shape).
- **T-not:** located and genuinely off (AntiPaSTO 1B config drift — the only one).
- **Extension:** any run that changes model/seed set/library epoch/dataset size on purpose; never
  in the rate.

## Part 5 — Numbers for this card (RTX 3090, 24 GB, 31 GB RAM)
AntiPaSTO seed 47 min (270M 33) · Qwen2.5-1.5B GSM8K 350-q pass ~1 min / 15 GB (102 passes ≈ 100
min) · CKA + 500-perm per 1–3B pair ~100 min · GPT-2 small IMDB fine-tune 1.5 epochs ~30 min ·
Othello flipping-circuit proof 499 batches ~74 min · ODEFormer 800-sample regeneration ~40 min ·
quick notebooks 1–3 min once the venv is right · venv prep 3–12 min (torch download ~5 min when
the cache is cold) · torch venv ≈ 5 GB · **uv cache ≈ 5 GB per environment, unbounded** · HF over
HTTP ~6 MB/s · a 30-VAE training (g-w1) > 6 h.
