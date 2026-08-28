# brainstorm.md — where to take the research next (wild pass, 2026-08-28 06:40)

Written for the next Fable instance. Grounded in `nav.md`'s salient rows, `META-REPORT.md` (N=34),
and the findings in `meta-analysis-blog-post.md` / `results.md`. **Deliberately not limited to the
87-row queue** — the queue was selected for feasibility, which (by `results.md` §7) selects *against*
the results people actually rely on. Ideas are rated:

- **value** — would the result change what we believe (★★★ = could overturn the headline finding)
- **cost** — 3090-hours, or CPU-only
- **class** — `replication` (P9 protocol, env-only fixes) · `extension` (changes model/seed/library —
  a *new* experiment, ledgered separately, never counted in the reproduction rate) · `data-only` ·
  `gated` (needs the user's OK — outward-facing or rule-adjacent)

§3 is the actual run order. Everything above it is the argument.

---

## 0. Three numbers pulled while brainstorming — `[MEASURED, n=34, small]`

Cross-tabs of the 34 ledger rows against `union.json` (`analyze.py`-style, not yet scripted):

| split | located | reproduced |
|---|---|---|
| post dated **before 2025-07** (n=12) | **3/12** | 2/12 |
| post dated **2025-07 or later** (n=22) | **16/22** | 12/22 |
| solo author (n=27) | 17/27 | 12/27 |
| team (n=7) | 2/7 | 2/7 |
| karma ≤ 20 (n=26) | 16/26 | 11/26 |
| karma > 20 (n=8) | 3/8 | 3/8 |

`[INFERRED]` Age is the strongest predictor of *whether the code runs at all* in this sample — a
**rot clock**. The team and karma rows point the same way as `results.md` §3/§7 (openness falls
with team size and attention) but n is too small to say more than "consistent". Every idea in §1
exists to make these three rows big enough to trust.

## 0b. The ledger found three failure classes the literature has no names for

1. **Engineering rot** — code that ran in 2024–25 does not run under 2026 majors (15/34 never ran).
2. **Provenance drift** — the repo's HEAD is no longer the paper's experiment. AntiPaSTO's 1B preset
   never matched the paper (`git log -S` proves it); diffing-toolkit deleted the gemma-2-2b config
   the post used. This is neither rot nor fragility: the artefact and the claim have *diverged*.
3. **Toy→real gap** — the toy component reproduces exactly and the real-model component does not
   (jordanmccann: toy + Haar exact, Pythia EV 0.2–0.5 vs 0.85–0.99; codi recovery ~7% vs 20%).

Naming them is half the contribution; measuring their rates is the other half (§1.5, §2.3).

---

## 1. Turn the failures into measurements

### 1.1 Time-travel environments ★★★ · CPU + minutes GPU · `replication` (second attempt class)
**Seed:** all 15 never-ran rows failed on packaging; 6 are `env`. The headline finding ("rot, not
fragility") is only as strong as our ability to *undo the rot* and see what is underneath.
**Idea:** rebuild each `env` row's venv **as of the post date** — a PyPI index frozen at a cutoff
(`pypi-timemachine` runs a local proxy index with a date cutoff; verify it installs; fall back to
hand-pinning from `pip index versions` + release dates) plus the matching torch CUDA wheel index.
Re-run under the same entrypoint. Ledger as attempt class `env-timetravel`.
**Rows:** dajale423 (2024-09), ibm (2024-10), jim-maar (2025-02), tenseisoham (2025-02),
thebuleganteng (2026-02), uchicago-xlab (2026-08 — if *this* fails at t≈0 it is not rot).
**What changes minds:** if ≥4/6 then run *and* reproduce, the "89% of located" number extends to
the never-located and the finding hardens. If they run and *don't* reproduce, the headline is wrong
and rot was hiding fragility. Either outcome is worth more than any remaining queue row.

### 1.2 The rot half-life ★★ · CPU · `data-only`
Fit `located ~ age_at_attempt` (logistic, Wilson bands) on the ledger; refit as rows land. Report
the age at which P(runs) crosses 50%. From §0 it is somewhere around 12–14 months. Add "repo last
commit before/after post date" as a covariate (the *repo moved on* signal). Script it into
`replication/rot.py` so `META-REPORT.md` can cite it.

### 1.3 The library kill table ★★ · CPU · `data-only`
From every `env_fixes[]` and `lessons-synth` Part 3: count rows broken per library major
(`transformers 5`, `datasets 4`, `sae-lens 6/4`, `torch 2.6`, `setuptools 81`, `mamba-ssm` build).
A one-table result: *"the five version bumps that broke alignment research."* Names names;
publishable on its own.

### 1.4 A rot linter ★★★ · CPU · `data-only`
Static checks, no execution: no lockfile / unpinned majors · `/content` or `google.colab` ·
`wandb.login()` unconditional · file paths referenced but absent from the repo · prose entrypoint ·
notebook-only · `assert dir.name` · external git deps at "not yet stable" commits. Score all 142
candidates; **validate AUC against the 34 ledger rows** (located vs not); then *predict* the 53
untouched rows before running any of them. If AUC > 0.8, the harness has a triage tool and the
field has a badge. Package as `replication/rotlint.py`.

### 1.5 The provenance-drift census ★★ · CPU (+ network) · `data-only`
For each of the 142 candidates: does the pinned SHA post-date the post? Does the repo's default
config still contain the numbers the post states (lr, rank, n, batch — extract from
`p3/claims/*.json` `effect.value` and the post body; `git log -S` each)? Rate of "paper config absent
at HEAD". AntiPaSTO and diffing-toolkit are the two known positives; find the base rate.

---

## 2. Turn the reproductions into stronger science

### 2.1 Seed-variance census ★★★ · ~1 GPU-h · `extension`
**Seed:** 13.7% of posts report a seed count (`results.md` §2); no post scores 6/6 on design markers.
**Idea:** take 5 reproduced minute-class rows (ioi, induction-head, coolvision, mild-rgb, phusroyal —
all deterministic-or-cheap) and run **5 seeds each**, changing nothing else. Report the headline's
SD and *the fraction of seeds that would have fallen outside the author's own tolerance*.
**What changes minds:** this prices what 86% of the field is not reporting. If most headlines are
seed-stable, seed-reporting is a norm problem, not an epistemics problem. If not, `p3/findings.md`
§4's "rigor is rising" is cosmetic.

### 2.2 Second-family campaign ★★★ · 2–3 GPU-h · `extension`
**Seed:** interpretability's median is **1 model family** (`results.md` §1.1); 39% of posts are
single-family. Every reproduction so far confirms a result *on the model it was found on*.
**Idea:** for reproduced rows whose claim is stated generally, re-run on one second family already
in the HF cache: mshinkle plateaus (GPT-2 → Qwen2.5-1.5B), coolvision vocab-alignment
(Llama → Qwen), mild-rgb echo heads (Qwen-1.5B → Llama-3.2-1B), sandbagging-noise
(Qwen2.5-1.5B → Llama-3.2-1B-Instruct / gemma-3-1b-it). Skip ioi (the claim is about GPT-2).
**What changes minds:** converts "reproduces" into "generalises" — or shows the monoculture is
hiding non-generalisation, which would be the corpus's most important negative result.

### 2.3 The environment as an unreported variable ★★★ · ~3 GPU-h · `extension`
**Seed:** the sandbagging row reproduced with a *larger* effect (9/10 seeds vs author 6/10); the
author's seeds 2, 3, 9 collapsed to 8–25% and none of ours did. Our env: `transformers 4.57.6`,
`torch 2.6`; the author's: mid-2025. Library version may be an experimental variable with an effect
size comparable to seed — and *nobody reports it either*.
**Idea:** re-run `exp07` under three library epochs (author-era `transformers~=4.53`, ours 4.57,
and 5.x), 10 seeds each (~1 min/pass → ~100 min per epoch). Decompose variance: seed vs epoch.
**What changes minds:** if epoch variance ≳ seed variance, the field's reproducibility problem is
not "no seeds" but "no environment", and `lessons-synth` P3 becomes a scientific claim, not ops.

### 2.4 Adversarial-environment red team ★★ · 1–2 GPU-h · `extension`
For each reproduced row, vary only what the protocol already permits — dtype (bf16/fp16/fp32),
batch size, attention implementation (`sdpa`/`eager`), device — and record which verdicts flip.
A result that survives every environment-only perturbation is a *different tier* from one that
only reproduces at the author's batch size. Adds a `robustness` field to the ledger.

### 2.5 The 6/6 upgrade — the price of rigor ★★ · 2–4 GPU-h · `extension`
Take one reproduced row and give it every design marker the corpus lacks: pre-register (in-repo,
before running), baseline, ablation, held-out split, 5 seeds, and a human eval (the user, 20
items). Measure the cost in GPU-hours and person-minutes. *"Full rigor on a 3090 costs X"* is a
number nobody has, and it makes the 0/728 finding actionable rather than accusatory.

### 2.6 Cross-row diagnostics: are the field's steering vectors imposters? ★★ · 1 GPU-h · `extension`
**Seed:** tarcle (H36c) shows function vectors can pass every classic check while encoding a
neighbour task. The ledger already holds *other* steering artefacts (AntiPaSTO's adapter,
ak47na's top-down vectors, shivasrightfoot's fusion adapter).
**Idea:** apply tarcle's margin / support-gate diagnostic to those artefacts, wherever a
"neighbour task" can be defined. This is reuse *across ledger rows* — the first time one
reproduced experiment is used to audit another. Wild; may not transfer; try one.

---

## 3. Adjudicate the contested — where the field's uncertainty actually lives

### 3.1 Metric × sign cross-tab for every contested phenomenon ★★★ · CPU, 1 h · `data-only`
**Seed:** 35 of the 50 best-studied phenomena carry claims in both directions. Nobody has asked
whether the two sides *measure the same thing*. `p3/claims/*.json` carries `effect.metric`.
**Idea:** for each contested phenomenon, cross-tab metric family × claim sign. If sign is
predicted by metric (e.g. representation geometry: CKA-users negative, probe-transfer-users
positive), the phenomenon is **not contested — it is a metric disagreement**, and it can be settled
by one battery on one model pair (§3.2). Do this *before* spending GPU on any contested row.

### 3.2 PRH metric battery ★★★ · 3–4 GPU-h (+10–22 GB re-download) · `extension`
On one within-family pair and one cross-family pair from the reproduced cross-model-geometry row,
compute every metric the 22-vs-5 literature uses: debiased CKA, linear CKA, SVCCA, Procrustes EV,
probe transfer, model stitching. One table, one afternoon, and the 22-vs-5 split either collapses
into "which metric" or survives as a real disagreement. Note: the PRH models are no longer in
`~/.cache/huggingface/hub` (26 GB cache, 57 GB free — mind the 25 GB floor).

### 3.3 The crosscoder triangle ★★★ · 4–6 GPU-h · `replication` ×2
**Seed:** `results.md` §8.3 — crosscoder / model diffing is 12-positive-and-one-dissenter
(*What We Learned Trying to Diff Base and Chat Models*, 106 karma, queue row 72). A replication row
also exists (annasoligo tiny-sleepers, 71%, row 51, TinyStories-33M, 6 GB).
**Idea:** run both under the harness. Row 51 first (cheap, self-contained). Row 72 is
`diffing-toolkit` at a SHA whose gemma-2-2b config was deleted — *authoring a config from the
template* is borderline environment-only; do it on a copy, log it as a `--fix`, and say in the
VERDICT that the config is reconstructed. Together they answer whether the lone dissenter is a
flawed challenge or an unanswered one.

### 3.4 Hours-class negatives the meta-report is light on ★★ · 4 GPU-h each · `replication`
Per `handoff-synth` §B3.4, in this order: row 47 `hannahtao` (does compression undo unlearning —
negative, 8 GB, clean), row 44 `dmitry-dereshev` (7B judges own homework — negative, 6 GB),
row 37 `jacobcd52` (weight-sparse circuits unfaithful — negative, 4 GB, repo sprawl), row 48
`sahilraut22` (eval-awareness steering — negative, 18 GB, **needs the Llama-3.1-8B licence and an
external harness with 7 patches**; last). These test whether the 89% holds off the minute-class.

### 3.5 A training-induced sandbagging organism ★★★ · 4–6 GPU-h · `extension` (builds the missing artefact)
**Seed:** `p3/findings.md` §8 — "build more realistic model organisms" is asked for by **19
independent first authors**; the sandbagging (5-vs-6) and alignment-faking posts name
prompt-induced organisms as the reason their results may not hold. The reproduced noise-injection
result (9/10 seeds) is on a *prompted* sandbagger.
**Idea:** LoRA Qwen2.5-1.5B-Instruct into a password-locked / trigger-gated sandbagger on GSM8K
(bad unless the password is present — a published recipe). Then re-run `exp07` unmodified except
for the model path. **Does noise still reveal the hidden capability when the sandbagging was
trained in, not prompted in?** Ship the organism on the HF hub (gated: user decides).
**What changes minds:** either the noise result generalises to the realistic organism — a
safety-relevant positive — or it is a prompt artefact, which the field explicitly suspected.

### 3.6 Replicate the beams, not the queue ★★★ · 4–8 GPU-h · `replication` / `gated`
**Seed:** `results.md` §8.2 — the eight highest-karma posts ship neither code nor data, and three
are top-25 dependencies. The queue *cannot* contain them; the feasibility gate excluded exactly
the results the field builds on.
**Idea:** check the *paper-side* repos (the posts didn't link them; the papers may have — verify
before assuming). **Subliminal learning** is the tractable one: the transfer eval is "what is your
favourite animal", no closed judge, and an in-corpus small-model replication exists (*Subliminal
Learning Across Models*, 58 karma) to compare against. Qwen2.5-1.5B/7B-4bit LoRA on
number-sequence data fits the card. **Emergent misalignment** is blocked as a replication (GPT-4o
judge) — an open-judge *extension* is `gated`. **Alignment faking** needs Claude — `api-key`.
**What changes minds:** a from-scratch reproduction of an in-degree-9 result on a consumer GPU,
or its failure, is worth more than ten queue rows.

---

## 4. Calibrate the instruments — how much of the 89% is the harness being blind?

### 4.1 Bug-injection positive control ★★★ · ~1 GPU-h · `extension`
Take 5 reproduced rows; on a *copy*, inject one change that should flip the verdict (sign flip
in the metric, threshold moved, wrong layer index). Run under the harness with the same judging
procedure. **If the verdict does not flip, the harness cannot detect non-reproduction and the 89%
is inflated.** This is the single cheapest thing that could invalidate the headline. Do it early.

### 4.2 Validate the P3 judge on ledger ground truth ★★ · CPU, 30 min · `data-only`
`p3/claims` says `reproducible_in_principle ∈ {code, code+data, neither}`; the ledger knows
`installs / runs / located` for 34 of those posts. Precision of the judge's "code" label against
"it actually ran". First human-adjacent validation of the P3 instrument; extends P4 for free.

### 4.3 Reproduction prediction log ★★ · CPU + human · `data-only`
Before each new run: three fresh instances (and the user, if present) predict P(runs), P(reproduces)
from the post + README alone. Log; score Brier as rows land. Combine with §1.4's linter as features.
Answers "can a reader tell which results will reproduce?" — a SCORE-style result for LW.

### 4.4 Control baseline: well-maintained repos ★★ · 1 GPU-h · `replication`
Run the harness on the documented example of 5 infrastructure repos (TransformerLens demo,
SAELens tutorial, control-arena quickstart, nnsight, dictionary_learning). If *those* fail at 44%,
the finding is about Python in 2026, not about the field. If they run at ~100%, the 44% is the
field's.

---

## 5. Build the missing shared artefacts

### 5.1 Reproducibility weather station ★★ · minutes/month · `extension`
A monthly cron that re-runs the 14 reproduced rows **unpinned** (latest libraries) and appends to
the ledger. Rot measured *prospectively*, not archaeologically. The harness already supports it.

### 5.2 A standing replication role ★★ · ongoing · `gated`
`results.md` §6: 24 replications, 23 authors — nobody holds the role. A standing session that takes
every new LW empirical post within a week of publication and runs it through the harness gives
the rot curve its **intercept**: do fresh repos run at t=0? Posts nothing; ledgers everything;
human decides what to publish.

### 5.3 The harness as a product · CPU · `data-only`
`HARNESS.md` + `lessons-synth` Part 3 → a package with `rotlint`, `timetravel`, `queue`, `ledger`.
Test on one non-safety ML repo to show it is topic-agnostic. Possibly the largest contribution.

---

## 6. Wild cards

- **R10 on the meta-layer** (`readme.md` §2.2): does *this repository's text* teach eval-awareness?
  Expensive; leave the pointer.
- **LLM-written reconciliation pre-registrations** for the four lone dissenters and the 12-vs-12
  AI-control split: write the design that would settle each, commit it under `p3/prereg/`, run the
  3090-feasible ones (only crosscoder is).
- **Judge-agreement study for `api-key` rows** (`gated`): 20% of code-shipping open-model posts
  compute their headline through a closed judge. Where the post released the judge's outputs,
  measure open-judge (Qwen2.5-7B) agreement with them. *Not* a replication and must never be
  called one — but it converts a hard block into a measured gap. Needs the user's explicit OK.
- **Karma-blind ranking**: `results.md` §7 says attention selects against runnability. Re-rank the
  53 untouched rows by `rotlint` score × value with karma weight = 0, and see if the order changes.

---

## 7. Run order — what to actually queue

Time is the constraint (one card, 57 GB free, 25 GB floor). Parallelise CPU work with GPU work.

### Queue A — GPU, one at a time via `tree_late.txt`
| # | item | § | class | est. | why first |
|---|---|---|---|---|---|
| A0 | judge H36c / H57b when they exit (already queued; H57b needs a `mamba-ssm` CUDA build — one more try, then `env`) | nav | replication | — | live |
| A1 | seed-variance census, 5 rows × 5 seeds | 2.1 | extension | 1 h | cheapest ★★★ |
| A2 | bug-injection positive control, 5 rows | 4.1 | extension | 1 h | could invalidate the headline |
| A3 | crosscoder triangle: row 51, then row 72 | 3.3 | replication | 4–6 h | adjudicates the lone dissenter |
| A4 | time-travel envs for the 6 `env` rows | 1.1 | replication† | CPU + 1 h | converts failures to measurements |
| A5 | second-family campaign, 4 rows | 2.2 | extension | 2–3 h | tests the monoculture |
| A6 | environment-as-variable on sandbagging, 3 epochs × 10 seeds | 2.3 | extension | 3 h | new variable |
| A7 | hours-class negatives: 47 → 44 → 37 → 48 | 3.4 | replication | 4 h each | scale test |
| A8 | training-induced sandbagging organism + noise re-run | 3.5 | extension | 4–6 h | the field asked for it |
| A9 | subliminal learning on open models (verify no closed judge first) | 3.6 | replication | 4–8 h | a load-bearing beam |
| A10 | PRH metric battery (only if §3.1 says the split is metric-shaped) | 3.2 | extension | 4 h + download | settles a contested phenomenon |
| A11 | control baseline on 5 infra repos | 4.4 | replication | 1 h | interprets the 44% |

† attempt class `env-timetravel`; a run that succeeds here is ledgered as `located` with the
time-travel fix logged, and the original `env` reason kept in `notes`.

### Queue B — CPU / data-only, run while the GPU is busy
| # | item | § | est. |
|---|---|---|---|
| B1 | metric × sign cross-tab for contested phenomena | 3.1 | 1 h |
| B2 | rot half-life logistic (`replication/rot.py`) | 1.2 | 30 min |
| B3 | library kill table | 1.3 | 30 min |
| B4 | P3 judge vs ledger truth | 4.2 | 30 min |
| B5 | rot linter + AUC on 34 + predictions for the 53 | 1.4 | 3 h |
| B6 | provenance-drift census over 142 | 1.5 | 2–3 h (network) |
| B7 | prediction log, per new run | 4.3 | 10 min each |
| B8 | karma-blind re-rank of the 53 | 6 | 30 min |

### Queue C — needs the user
Weather-station cron (5.1) · standing replication role (5.2) · judge-agreement for `api-key` rows
(6) · open-judge EM extension (3.6) · shipping the organism to HF (3.5) · author-facing notes on
AntiPaSTO / jordanmccann (handoff-synth §B3.6) · anything that creates a fork, issue, or post.

### Do not
Grind the drained tail · requeue past 2 tries · run two GPU jobs · count any `extension` row in
the reproduction rate · substitute an open judge and call it a replication · call a recompute
"exact" · read the 2026H2 partial period as a trend · touch anything outside `replication/` and
`prompts2/` in git.
