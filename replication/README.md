# Replication scaffold — one RTX 3090, open-weight models only

This directory turns the 741-post corpus into a queue of experiments an agent can actually re-run
on the hardware in this machine (RTX 3090, 24 GB VRAM, 31 GB RAM, ~150 GB disk, no closed-model
API keys), and records what happened in a ledger that `corpus-analysis.md` R5 specified but nobody built.

## Pipeline

| step | command | writes | status |
|---|---|---|---|
| 1. select | `python3 replication/select.py` | `candidates.json` — 142 posts whose models fit and whose repo + headline number exist | done |
| 2. liveness | (in select's wake) `git ls-remote` over every repo | `liveness.txt` — HEAD sha per repo; 139/139 alive on 2026-08-26 | done |
| 3. inspect | 18 agents, `INSPECT.md` contract | `inspect/result_*.json` — entrypoint, env, VRAM, data, blockers per repo; `inspection_summary.json` tabulates | done — 18/18 batches |
| 4. build specs | `python3 replication/build_specs.py --include-tight` | `experiments/<slug>/spec.json` + `PROMPT.md`, `queue.md` | done — 87 folders |
| 5. run | one Claude Opus session per experiment, `prompts.md` P9 | `experiments/<slug>/ledger.json` + `run.log` | **not started** |
| 6. aggregate | `python3 replication/ledger.py` | `ledger_summary.json`, reproduction rate + failure taxonomy | runs on whatever exists |

## What "replicate" means here

A replication attempt is **successful** when the entrypoint runs to completion on this machine and
produces the post's headline metric within the tolerance in `spec.json`. It is **informative
either way** — R5's point is that the *rate* and the *failure taxonomy* are the finding, not any
one number. The ledger records:

```
installs        did the environment build
runs            did the entrypoint finish without error
claim_located   could the headline number be found in the output
claim_reproduced  is it within tolerance of the post's value
delta           observed − claimed, in the metric's units
blocking_reason one of: env | data | model-access | vram | runtime | code-bug | api-key | unclear-entrypoint | none
```

## Ground rules for the running agent (full text: `prompts.md` P9)

- **Pin the commit** (`head_sha` in the spec). Do not run HEAD-of-main.
- **One venv per experiment**, under `experiments/<slug>/.venv`, built from the repo's own
  requirements. Never install into the base environment.
- **Do not modify the repo's experiment logic.** Environment fixes (a pin, a missing import, a
  path) are fine and are logged; changing what is measured is a different experiment.
- **Do not substitute a closed API** with an open model and call it a replication. If the recipe
  needs GPT-4o as a judge, that is `blocking_reason: api-key`, not a workaround.
- **Time-box.** `spec.json` carries a budget; when it is exceeded, stop, record `runtime`, and
  move on. Repo decay is monotonic; breadth beats depth.
- **Write the ledger even on failure.** A failed attempt with a reason is the point.
- **Never delete anything outside `experiments/<slug>/`.** Never `git push` from a cloned repo.

## Layout

```
replication/
  select.py          candidates from the claims corpus, tiered by VRAM
  candidates.json    output of select.py
  liveness.txt       repo -> HEAD sha
  INSPECT.md         contract for the repo-inspection agents
  inspect/           assign_*.json (input) and result_*.json (output)
  build_specs.py     merges candidates + inspection into experiments/
  queue.md           ranked, human-readable run order
  ledger.py          aggregates experiments/*/ledger.json
  ledger_schema.json what a ledger entry must contain
  env/bootstrap.sh   one-time machine setup (CUDA torch smoke test, HF login check)
  template/          run.sh / report.py copied into each experiment folder
  experiments/<slug>/
    spec.json        everything the runner needs: repo, sha, entrypoint, target, tolerance, budget
    PROMPT.md        the Opus prompt for this experiment (P9 instantiated)
    run.sh           thin wrapper: venv, clone at sha, run entrypoint, capture log
    report.py        parses run.log, writes ledger.json
    ledger.json      written by the run (absent until then)
```

## What the inspection found (142 repos read, 2026-08-26)

These are `[MEASURED]` counts over `inspect/result_*.json` via `inspection_summary.py`, and they
are an object-level finding about the corpus: **of the posts that look replicable from their
claims — open models, code linked, a number to hit — a large share do not ship the experiment
that produced the number.**

| | n | of 142 |
|---|---:|---:|
| fits a 3090 as committed (`yes`) | 82 | 58% |
| fits with a one-line change, usually `torch_dtype=bfloat16` (`tight`/`probably`) | 26 | 18% |
| does not fit (`no`) | 25 | 18% |
| **needs a closed-model API** — 25 of 28 as the *judge that computes the headline metric* | 28 | 20% |
| no identifiable entrypoint for the headline number | 12 | 8% |
| data not obtainable (private Drive, gitignored, withheld "for safety") | 14 | 10% |
| ships any requirements file | 87 | 61% |
| pins versions | 53 | 37% |
| states the compute it used | 56 | 39% |

Recurring failure modes the inspectors reported, each seen in several repos:

- **The metric is an API call.** The GPU work is trivial; the number in the post is a GPT-4o /
  Claude / Gemini rubric score, sometimes hardcoded to one vendor behind an "OpenRouter" alias.
  These are `blocking_reason: api-key` before any code runs. 25 repos.
- **The repo is the library, not the experiment.** A general SAE-training / steering toolkit is
  linked; the sweep or eval that produced the headline table is absent, sometimes as a 0-byte
  placeholder file or a commented-out line. 8–12 repos depending on strictness.
- **The headline number is a literal.** A plotting script with `[0.6038, 0.4234]` typed in; a
  results file committed from the author's own run with no way to regenerate it. Useful as a
  check that the *post* matches the *repo*, useless as a replication. ~20 repos flag this.
- **fp32 by default.** No `torch_dtype` anywhere, so a 7–8B model that fits in bf16 OOMs on
  load. One-line fix, but it means the author never ran it on 24 GB either. 14 repos.
- **The model in the code is not the model in the post.** DPO scripts hardcoding Llama-3-8B
  while the claim is about Qwen-1.8B; a 14-model cross-family claim whose repo contains one
  family. The replication would test a different claim than the one published.
- **Stated compute exceeds the card, honestly.** "One ≥80 GB GPU suffices", "2×3090 TP=2",
  "~55 GB VRAM". 21 repos say so in their own README — the best-documented failures.

`[INFERRED]` The selector's VRAM tiering was the *least* important filter: of 97 T1 candidates,
only 12 turned out not to fit. What removed candidates was the recipe — judges, missing scripts,
missing data — which no amount of parameter-count arithmetic predicts. `corpus-analysis.md` R5's plan to
"clone, install, run" underestimated the share of repos where there is nothing to run.

## Queue quality, stated

`queue.md` lists 87 experiments. Of those: 70 `fits: yes`, 10 `tight`, 7 `probably`; 61 with a
high-confidence entrypoint, 21 medium, **5 low** (flagged in their `PROMPT.md`); 34 minute-class,
38 hour-class, 9 day-class runs; **76 in a contested phenomenon** (`findings.md` §1). Summed run
budgets come to ~260 GPU-hours, so the queue is roughly two weeks of one card, or a long
weekend for the minute-class third.

**55 of 87 targets are compound** (several numbers in one headline) and carry `tolerance:
manual` — the running agent compares components by hand and says so in the ledger. Only 32 have
a scalar target with an automatic tolerance, and for those the tolerance is a stated default,
not something the post justified.
