# NEW-DIRECTION.md — reproducibility variance decomposition (running LLM-audience report)

Started 2026-08-28 07:10. One RTX 3090. Written for an LLM: dense, tiered, no narrative.
**After every GPU run this file gets a new §R-n section and the "next run" decision is re-made in
§N.** Extension rows live in `experiments/<parent>--ext-<kind>/` with `experiment_class: extension`
in `spec.json` and are excluded from the reproduction rate by `ledger.py`.

## 0. The direction, in one paragraph

The N=36 ledger answered *does it reproduce?* (15/36; 18/20 of located ≥ partially). This program
asks *what does a reproduction depend on?* — decomposing the variance of a headline number into the
factors the literature does not report: **seed** (13.7% of posts report one), **library epoch**
(0% report one; the sandbagging row reproduced with a *larger* effect under a newer
`transformers`), **model family** (39% of posts are single-family), **environment perturbations
the protocol permits** (dtype, batch, attention kernel), and **the harness's own sensitivity**
(would it notice a non-reproduction?). Each GPU run adds one factor on reproduced rows, where the
baseline is known. Rows stay minute-class so each run is ≤ ~90 min and the decision loop is tight.

Rules: extension rows change *exactly one declared thing* relative to the parent's reproduced
configuration; that thing is named in `spec.json.extension.what_varies`. Everything in
`handoff-synth.md` §A0 still binds (no APIs, no pushes, no author contact, env-only otherwise).

## 1. Free data already in the ledger (no GPU)

`[MEASURED]` Two parent rows already ran multiple seeds:

| row | seeds | headline per seed | mean ± SD | author's report |
|---|---:|---|---|---|
| sandbagging-noise (lovkush-a) | 10 | per-seed gain of sandbag acc under noise, pp: 16.9, 25.4, 12.9, 16.6, 18.0, 20.3, 19.4, 12.6, 21.7, **0.9** | 16.5 ± 6.8 | 6/10 seeds show the effect; ours 9/10 |
| AntiPaSTO 1B (wassname) | 3 | Steer F1: 1.8, 0.4, 3.8 | 2.0 ± 1.7 | 31.2 ± 5.3 |

`[INFERRED]` Seed 9 of the sandbagging row is a 1-in-10 null on a result the corpus classes as
contested (5-vs-6). A single-seed post on this phenomenon has a ~10% chance of reporting "no effect"
and a ~90% chance of "effect", *from the same code* — which is one mechanism by which a phenomenon
becomes "contested" without anyone being wrong.

## R-1 — seed-variance census (running)

**Parents:** ioi (fractalmachinist, deterministic model, seeded prompt sampler, n=128 pairs);
phusroyal (predefined-manifold, `--seed`, trains a head); matryoshka toy (noanabeshima, *unseeded*
notebook — feature geometry, data and init all random). 5 seeds each (0–4). Budget 90 min.
**Pre-registered read:** for each parent, the fraction of seeds whose headline falls inside the
parent's own tolerance as ledgered; SD of the headline; and whether the parent's *reproduced*
seed is typical (inside the 5-seed range) or lucky.

## 2. CPU result while R-1 ran — the contested phenomena share no metric

`[MEASURED]` (`metric_diversity.json`, from `p3/claims/*.json` `effect.metric`, exact-string after
lower-casing and punctuation strip) Over the **29 contested phenomena with n ≥ 6** (a phenomenon is
contested if it has ≥1 positive and ≥1 negative/null primary claim): **493 posts name 493 distinct
metric strings — 100% distinct — and the number of exact metric strings shared by a positive and a
negative post is 0.** AI control protocols: 32 posts, 29 named metrics, 29 distinct. Sandbagging:
13 posts, 11 distinct.

`[UNRESOLVED]` Exact-string matching is a hard lower bound on sharing: "safety (%) at 0.3%
auditing budget" and "safety at 0.5% audit budget" are the same construct with different numbers
in the string. A judge-based metric-family pass would raise the sharing count above zero. It would
not raise it to a level where "the field measured X and got different answers" describes any
contested phenomenon here.

`[INFERRED]` **"Contested" in this corpus means "measured differently", not "measured the same and
disagreed."** Consequences: (1) adjudicating a contested phenomenon requires *choosing the
measure first* — a replication of one side settles nothing about the other; (2) the metric-battery
design (`prompts2/brainstorm.md` §3.2 — many metrics, one model pair) is the right shape for every
contested phenomenon, not just PRH; (3) `p3/findings.md` §1's "35 of 50 best-studied phenomena are
contested" should be read as "35 phenomena have no shared measurement", which is a different and
arguably worse finding.

### R-1 result (2026-08-28 08:21; 71 GPU-min; `ext_seed_census.json`)

`[MEASURED]` Three reproduced rows, five seeds each, nothing else changed:

| parent | headline | author/parent seed | seeds 0–4 | regime |
|---|---|---|---|---|
| ioi (fractalmachinist) | mean IO/S logit-diff drop, n=128 | 0.231 (seed 0, ledgered "exact") | 0.231 / 0.341 / 0.278 / 0.370 / 0.298 — mean **0.304 ± 0.054**; d 0.27–0.50; all p < 0.003 | **robust, understated**: the published seed is the *smallest* of five |
| phusroyal sphere_shell | linear-probe AUC after GFAL (target 0.57–0.67) | 0.589 (seed 1729) | 0.922 / 0.923 / 0.590 / 0.650 / 0.711 — **2/5 in range, 2/5 at 0.92** | **seed-fragile**: on 40% of seeds the feature is *not* erased; the repo's own 14-check validator fails 3/5 |
| phusroyal helix_tube | same | 0.5685 | 0.638 / 0.566 / 0.565 / 0.631 / 0.546 | stable-ish (all ≤ 0.64; 14/14 checks on 5/5) |
| matryoshka toy | absorbed latents vanilla vs Matryoshka | 9/20 vs 0/20 | 9/20 vs 0/20 on **every** seed; diag-mean SD 0.002 / 0.0007 | **stable** |

`[INFERRED]`
1. **"Exact" reproduction is a statement about the RNG.** ioi matched the author to three decimals
   because the sampler seed was the author's; the effect across seeds is 30% larger than reported.
   A reproduction tier that rewards 3-decimal agreement is measuring *determinism*, not *effect
   precision*. Tier vocabulary should add: `exact-same-seed` vs `robust-across-seeds`.
2. **One of three reproduced training rows is seed-fragile at 40%.** Had the parent replication
   drawn seed 0 or 1 instead of 1729, phusroyal would have been ledgered *not reproduced* on the
   headline AUC — with the causal-delta half of the claim still holding. Neither the post (no seed
   count) nor the ledger (1 seed) could have known. `results.md` §2: 86% of posts report no seed
   count; this is the first measured cost of that.
3. **The seed regime is row-specific and not predictable from the claim type.** Two toy/small
   settings, opposite behaviour (matryoshka invariant, phusroyal fragile). The census must be run
   per row; no corpus-level seed-variance prior can be assumed.

`[UNRESOLVED]` n = 5 seeds per row; the 2/5 sphere_shell failure rate has a Wilson interval of
roughly [12%, 77%]. Ten more seeds (≈50 min) would pin it.

### N after R-1 — next-run decision

Candidates considered: (a) library-epoch arm on the sandbagging row (staged); (b) 10 more
phusroyal seeds; (c) bug-injection control; (d) second-family campaign.

**Chosen: (a).** Reason: R-1 shows seed alone flips verdicts; the sandbagging row is the one
ledger row where *our seeds and the author's are the same seeds (0–9, `torch.manual_seed`)* and the
outcomes still differ (author 6/10 seeds show the effect, three collapse to 8–25%; ours 9/10, none
collapse). Same seeds ⇒ the discrepancy is not seed variance ⇒ it is the environment or the
model weights — and the only recorded environment difference is `transformers` (author 2025-07
era; parent pinned 4.57.6 because 5.x resolved). One-factor design: `transformers==4.53.3`, torch
2.6.0+cu124 / datasets 5.0.1 / code / seeds / noise grid held. ~100 min. If the author's
collapses reappear under 4.53.3, library epoch is an experimental variable with an effect size
larger than seed on a safety-relevant result. If not, the discrepancy moves to model-weight
revision or generation kernels and (b)/(c) follow. (b) is queued as filler after it.

## R-2 — library epoch, arm 1: `transformers` 4.53.3 vs 4.57.6 (2026-08-28 10:06; 102 GPU-min)

**Design.** Parent row sandbagging-noise (lovkush-a), same code, same 10 seeds, same 6-point noise
grid, same Qwen2.5-1.5B-Instruct weights, torch 2.6.0+cu124, datasets 5.0.1. Only `transformers`
changed: 4.53.3 (the author's 2025-07 era) instead of the parent's 4.57.6. 102 passes × 350 GSM8K items.

`[MEASURED]` **102/102 passes identical accuracy; 35,700/35,700 items identical `is_correct`;
35,700/35,700 generated answers byte-identical** to the parent run. Per-seed gains, seed 9's
0.9-pp null, the 9/10 criterion — all unchanged to every digit.

`[INFERRED]`
1. **A `transformers` minor-version change contributes exactly zero variance to this result.**
   The generation path (bf16 forward, greedy decode, 400 tokens) is bit-stable across 4.53→4.57.
   The parent's `transformers<5` pin was the right call, but it was not what separated our
   numbers from the author's.
2. **The author-vs-us discrepancy is therefore not seed and not `transformers`.** Same seeds
   (`torch.manual_seed(seed)` before `randn_like`), same code, same library epoch → what remains
   is the stack *below* transformers — torch/CUDA kernel numerics on different hardware — or the
   HF weight revision. bf16 greedy decoding over 400 tokens is chaotic: a one-ulp matmul difference
   flips a token and the trajectory diverges. That mechanism would make the *pattern* of which
   seeds collapse a property of the hardware, not of the seed.
3. **Bit-reproducibility is achievable and cheap to check.** Two 102-pass runs, an hour apart, in
   different venvs, agree on 35,700 free-text generations. A harness that stores per-item outputs
   can test environment factors with a single `diff`, and *should* — the identity result took
   two seconds to establish and is stronger than any statistic.

### N after R-2 — next-run decision

Candidates: (a) torch arm — `torch==2.3.1+cu121` under the same transformers 4.53.3 (the closest
buildable proxy for an author-era stack; tests kernel-numerics sensitivity); (b) dtype arm
(fp16 or fp32 — an environment-permitted knob that changes numerics by more than a torch bump);
(c) 10 more phusroyal seeds; (d) second family.

**Chosen: (a), running (R-3).** It is the last software factor between us and the author; if it is
also bit-identical, the discrepancy is hardware/weights and (b) becomes the way to *measure* the
row's numerical sensitivity rather than to locate the author's stack. If (a) is *not* identical,
the per-seed collapse pattern under 2.3.1 vs 2.6.0 is the direct evidence that "seed" here is
"seed × kernel". Pre-registered read: report (i) items byte-identical, (ii) passes with identical
accuracy, (iii) which seeds satisfy criterion (b) under each torch, (iv) whether seed 9 stays null.

## R-3 — library epoch, arm 2: torch (2026-08-28 11:55; 102 GPU-min)

**Design as intended:** `torch==2.3.1+cu121` under transformers 4.53.3. **Design as realised:**
`torch 2.13.0+cu130` — the 2.3.1 pin was installed first, then the unconstrained `-e src … accelerate`
resolve pulled current `accelerate 1.14`, whose resolver upgraded torch to the newest wheel. Caught
only after the run, from the version line in `run.log`. Lesson (→ lessons-synth Part 3): *pin torch
in the same `uv pip install` call as everything else, or add `torch==X` to every later call; a
first-call pin is not a constraint.* The realised arm is still a clean one-factor change — torch
2.6.0+cu124 → 2.13.0+cu130, everything else identical — just in the other direction in time.

`[MEASURED]` vs the parent (same seeds, code, weights, transformers):
- passes with identical accuracy **4/102**; items with identical `is_correct` 31,851/35,700 (89.2%);
  **generations byte-identical 12,419/35,700 (34.8%)**; max pass-level accuracy difference 6.6 pp,
  mean 1.45 pp.
- criterion (b) still **9/10 seeds**; seed 9 still null (0.0 pp); seed 7's high-noise collapse
  (0.243 → 0.229) persists. Per-seed gains: parent {16.9, 25.4, 12.9, 16.6, 18.0, 20.3, 19.4, 12.6,
  21.7, 0.9}; torch-2.13 {18.6, 25.4, 10.6, 16.0, 18.3, 16.6, 19.1, 11.1, 24.9, 0.0};
  Spearman 0.90.
- **Variance decomposition of the per-seed gain: seed SD 6.7 pp; kernel-induced change SD 1.9 pp;
  ratio 3.5.** Seed variance dominates torch-version variance on this row by ~3.5×.

`[MEASURED]` Author's committed per-item CSVs (`src/logs/20250529_qwen_prompts1/`, 94 passes, same
350 GSM8K items in the same order) vs our parent run, *at noise 0 — no noise tensor involved*:
sandbag generations byte-identical **67.7%**, `is_correct` agreement 95.4% (acc 0.469 vs 0.463);
original-prompt generations byte-identical **43.7%**, agreement 92.6% (0.746 vs 0.723). At
(sandbag, noise 0.001, seed 3) — one of the author's collapse cells — byte-identical **12.0%**,
agreement 58.0%, **acc author 0.289 vs ours 0.629**.

`[INFERRED]`
1. **Below `transformers`, the stack is not bit-stable, but the science is.** A torch major-ish
   change rewrites 65% of the generated text and moves individual passes by up to 6.6 pp, yet the
   verdict, the seed ranking, and the null seed are unchanged. The replication tier for this row is
   `robust-across-kernels`, which is stronger than `exact` and was not measurable from one run.
2. **The author's stack differs from ours before any noise is added** (32–56% of generations differ
   at noise 0, accuracy within 2 pp), consistent with different hardware/torch. That alone does not
   produce the author's collapses: our torch arm also differs at that level and collapses nothing.
3. `[UNRESOLVED]` The collapse cells (author seed 3 at 0.001: 0.289 vs our 0.629) differ by far more
   than kernel numerics explain in our own two arms (max 6.6 pp). The remaining hypothesis is that
   **the noise tensors themselves differ** — `torch.randn_like` under `manual_seed` depends on the
   device generator and on `device_map="auto"` placement; a different GPU count or offload changes
   the stream. If so, "seed 3" is not the same experiment on two machines, and the author's 6/10 vs
   our 9/10 are two draws of 10 from one collapse-rate distribution. That is testable without the
   author's machine: estimate the collapse rate with more draws (§N).

### N after R-3 — next-run decision

R-4 (phusroyal seeds 5–14, ~50 min) is on the card, closing R-1's `[UNRESOLVED]` on the 2/5
fragility rate. **R-5 chosen: sandbagging collapse-rate estimate** — 20 more noise draws (seeds
10–29) at the two informative levels (0.001, 0.002), sandbag prompt only, ≈40 passes ≈ 40 min,
same env as the parent. Read: the fraction of draws with gain > 5 pp (n = 30 with the parent's 10),
and the fraction that *collapse* (sandbag acc at 0.001 or 0.002 below sandbag@0 − 10 pp). If the
author's 3/10 collapses and our 1/10 are both inside the n=30 interval, the discrepancy is a
sampling story and the post's "for some seeds" wording was exactly right. Not chosen now: a
dtype arm (numerics are now bounded), the second-family arm (next after R-5), bug-injection.

## R-4 — phusroyal, seeds 5–14 (2026-08-28 12:50; 54 GPU-min; n = 15 total)

`[MEASURED]` sphere_shell linear-probe AUC after GFAL, 15 seeds: 0.922, 0.923, 0.590, 0.650,
0.711, 0.811, **1.000**, 0.569, 0.577, 0.774, 0.908, 0.560, 0.591, 0.676, 0.730 — mean 0.733 ±
0.150. Strictly inside the claimed 0.57–0.67: **4/15 = 27% [11, 52]**. Feature clearly *not* erased
(AUC ≥ 0.77): **6/15 = 40% [20, 64]**. The repo's own 14-check validator passes on 7/15. Causal
delta stays 1.9–3.4 on every seed (the other half of the claim is seed-stable). helix_tube: 15/15
pass, AUC 0.546–0.684, mean 0.607 ± 0.045, 7/15 strictly in range.

`[INFERRED]` The R-1 reading holds at three times the sample: **on the sphere_shell geometry the
headline erasure happens on roughly half the seeds**, with a bimodal AUC (a cluster at 0.56–0.68
and a cluster at 0.77–1.00), while the causal effect is seed-stable. The post's stated range is the
lower mode. The parent replication's single seed (1729 → 0.589) drew from the lower mode. A
one-seed "reproduced" verdict on this row carries roughly a coin-flip's worth of information about
the headline number — and a one-seed *post* carried the same. The helix_tube geometry is stable and
would have been the safer headline.

`[UNRESOLVED]` Whether the upper mode reflects a GFAL optimisation failure (a training-dynamics
property the author could fix with more steps) or a genuine geometry-dependence is not separable
from these runs; both readings leave the *published* claim seed-fragile.

### N after R-4 — next-run decision

R-5 (sandbagging collapse rate, seeds 10–29 × {0.001, 0.002}, ≈40 min) is on the card — it was
chosen after R-3 and nothing in R-4 changes that. After R-5 the seed/kernel thread has four runs;
the plan is to switch factor: **second family** on the sandbagging row (Llama-3.2-1B-Instruct,
cached; stop-rule if no sandbag gap at noise 0), then the bug-injection control, unless R-5 shows
a collapse rate high enough (≥ 30%) that the noise-injection claim itself needs restating first.

## R-5 — sandbagging collapse rate, 20 more noise draws (2026-08-28 13:30; 40 GPU-min; n = 30)

**Design.** Seeds 10–29 at noise 0.001 and 0.002, sandbag prompt only, env bit-identical to the
parent (R-2). Combined with the parent's seeds 0–9 at the same two levels: 30 independent noise
draws against one sandbag@0 baseline (0.463). `experiments/…--ext-rate/rate_summary.json`.

`[MEASURED]`
- gain > 5 pp (the post's "reveals capability" criterion): **20/30 = 67% [49, 81]**.
  Seeds 0–9: 9/10. Seeds 10–29: **11/20**.
- collapse (sandbag accuracy under noise falls > 10 pp *below* the sandbagged baseline):
  **7/30 = 23% [12, 41]**. Seeds 0–9: 1/10. Seeds 10–29: 6/20 — five of them to 0.11–0.17,
  i.e. the model breaks rather than un-sandbags.
- mean gain over 30 draws **+5.8 pp, SD 17.9** — bimodal, not a shifted distribution.
- Author's committed CSVs at the same two levels, seeds 0–9: gain > 5 on 4/10, collapse 4/10.

`[INFERRED]`
1. **The author-vs-parent discrepancy is resolved: it was sampling.** With p ≈ 0.67 the parent's
   9/10 (P ≈ 0.14) and the author's 4–6/10 (P ≈ 0.2–0.5) are both ordinary draws. R-2/R-3 showed
   the software stack could not produce it; R-5 shows it did not need to. The post's phrase "for
   some seeds" was the precise claim; the parent ledger's "9/10 (author 6/10)" over-read a lucky
   batch and should be re-tiered `reproduced (direction; rate 67% [49, 81], n=30)`.
2. **Noise injection is a coin-weighted diagnostic, not a detector.** On this organism a single
   noise draw reveals hidden capability two times in three and *destroys* the model one time in
   four; nothing in the per-draw output distinguishes the two outcomes from the sandbagged
   baseline without the ground truth. A defender using this test needs ≥ ~5 draws per model and a
   collapse guard; the corpus's 5-vs-6 contested tally on sandbagging (`p3/findings.md` §1) is
   consistent with single-draw studies landing on either side of this coin.
3. **The first ten seeds were the least representative ten of the thirty.** This is what a seed
   count of 10 buys on a bimodal effect; it is also why R-1's "regime is row-specific" matters —
   ioi's 5 seeds were enough, this row's 10 were not.

### N after R-5 — next-run decision

Collapse rate 23% is below the 30% "restate first" threshold set after R-4, but the restatement is
made above anyway because the *rate* — not just the collapse — changed the claim. **R-6 (second
family) launched as planned:** Llama-3.2-1B-Instruct, same prompts / items / grid / seeds 0–9 /
env. Pre-registered: (i) stop-rule at noise 0 — if sandbag acc is not ≥ 15 pp below original, the
prompted organism does not exist on this model and the run reports that, not a rate; (ii) if it
exists, report gain > 5 rate and collapse rate over 10 draws with intervals, beside Qwen's 67% /
23%. After R-6: bug-injection control, then the time-travel env test.

## R-6 — second family: Llama-3.2-1B-Instruct on the sandbagging row (2026-08-28 14:53; 80 GPU-min + 1 env fix)

**Design.** Model swapped, everything else held (prompts, GSM8K train[0:350], noise grid, seeds 0–9,
greedy decoding, env). One env fix: Llama's tokenizer has no pad token → `pad_token = eos`
(padding side was already left in the author's batch code). Pre-registered stop-rule: the prompted
organism "exists" only if sandbag accuracy at noise 0 is ≥ 15 pp below original.

`[MEASURED]`
- noise 0: original **0.526**, sandbag **0.434** — gap **9.1 pp** (Qwen: 26 pp). **Stop-rule fires.**
- criterion (b): **0/10 seeds** gain > 5 pp (per-seed gains −8.0 … +2.3 pp). Both prompts degrade
  together: original 0.526 → 0.482 → 0.437 → 0.229 → 0.029 across the grid; sandbag 0.434 → 0.423
  → 0.355 → 0.185 → 0.028. Criterion (a) monotone: true.
- the noise scale tuned for Qwen2.5-1.5B destroys Llama-3.2-1B two grid points earlier
  (0.002: −30 pp on the original prompt; Qwen −5 pp at the same scale).

`[INFERRED]`
1. **The result does not transfer as an experiment, and the reason is upstream of the noise.** On
   Llama-1B the sandbag prompt only half-works (9 pp, not 26), so there is little hidden capability
   for noise to reveal; the run measures organism construction, not noise injection. That is what
   `p3/findings.md` §8's 19 first authors were pointing at when they asked for training-induced
   organisms: a prompted organism is a (model × prompt) artefact and its existence has to be
   re-verified per family before any downstream claim is portable.
2. **The noise grid is model-specific.** Absolute noise σ relative to weight scale differs across
   families; a fair second-family test needs the grid re-derived (e.g. as a fraction of per-tensor
   RMS), which is a *design* change, not an environment one — out of scope for this arm, in scope
   for a follow-up.
3. Ledger reading: `second-family: organism absent (gap 9 pp < 15); noise effect untestable` — not
   "does not reproduce".

### N after R-6 — next-run decision

Six runs have covered seed (R-1/R-4), sampling rate (R-5), transformers (R-2), torch (R-3) and
family (R-6). The remaining factor in the program is **rot itself** — whether the 7 `env` rows in
the N=36 ledger hide reproductions or fragility. Tool: `uv pip install --exclude-newer <date>`
gives a date-frozen resolution with one flag. **R-7: time-travel environment, one env row per GPU
run**, starting with `tenseisoham/finetuning-mechinterp` (post 2025-02-28; failure: the
`TrainingArguments(evaluation_strategy=)` kwarg removed mid-4.x). Frozen at the post date + 14 d.
Pre-registered: (i) if the frozen env runs and the headline (latent-space collapse
160.87 → 49,802 mean pairwise distance) lands within the spec tolerance → `located` with attempt
class `env-timetravel`; (ii) if the frozen env *still* fails on the same kwarg, the code was rotten
at publication — a distinct finding (author's own stack predated the post); (iii) if it runs and
misses, rot was hiding fragility. Bug-injection and the dtype arm are deferred behind this.

## R-7 — time-travel environment, row 1: `tenseisoham/finetuning-mechinterp` (2026-08-28 15:32; 21 GPU-min)

**Design.** Parent ledgered `env`: "`TrainingArguments(evaluation_strategy=)` removed in transformers
~4.46; would need ~4.40". Extension: nothing changed but the resolution date —
`uv pip install --exclude-newer 2025-03-14` (post date 2025-02-28 + 14 d) over the notebooks' import
list. Resolved: **torch 2.6.0+cu124, transformers 4.49.0, datasets 3.3.2**.

`[MEASURED]`
- fine-tune notebook: **0 errors** — `evaluation_strategy` is accepted by transformers 4.49.0. The
  parent's diagnosis ("removed ~4.46") was wrong; the kwarg was removed *later* (the parent's
  `transformers<5` pin resolved 4.57.6, where it is gone). 1.5 epochs, checkpoints 1563/3126/4686,
  ~30 min.
- logit-lens notebook (the headline): base-model average perplexity **160.873** (target 160.87;
  the catalogue mislabelled this "mean pairwise distance" — it is perplexity, see the notebook's
  own output); fine-tuned **52,156** vs target 49,802 → **+4.7%, inside the spec's rel:0.15**.
  Entropy 4.366/4.730 vs the author's 4.366/4.733.
- post-finetune notebook: fails on a missing `seaborn` (not in my import list; not the headline).

`[INFERRED]`
1. **Undoing the rot yields an exact reproduction.** One flag, no code change, no pin hunting: an
   `env` row became `located + reproduced` at the post date. This is the first direct test of the
   headline "rot, not fragility" on a never-located row, and it comes out on the rot side.
2. **The failure taxonomy has a resolution problem.** The parent's `env` verdict rested on a
   version claim that was false by three minor releases. Date-freezing removes the need to know
   *which* version — the post date is a fact, the removal version is a guess. `--exclude-newer`
   should be the harness's *first* attempt, not a rescue.
3. The author's committed logit-lens output carries a transformers ≥ 4.46 warning that our 4.49
   run also emits, so the author's stack was in the 4.46–4.49 window — the frozen date landed on it.

### N after R-7 — next-run decision

Continue the time-travel series, one `env` row per run, because each run converts a taxonomy
entry into a measurement of the headline finding. Order by expected cleanliness: **R-8
`ibm/sae-steering`** (2024-10-25; failure "torch 2.3.1 ↔ transformer-lens arity drift" — a pure
version-consistency case a date freeze should dissolve); then `thebuleganteng` (2026-02-04; the
`11-res-jb` sae-lens id, which `lessons-synth` says lived only in sae-lens 1.x–2.x — a test of the
"rotten at publication" branch); then `jim-maar`, `dajale423`, `uchicago-xlab`. Freeze at post
date + 14 d; step back only if the *same* error recurs, and record the offset.

## R-8 — rot reversal, row 2: `thebuleganteng/interpretability-prototyping` (2026-08-28 16:22; 19 min, CPU-only notebook)

**Parent verdict:** `env` — "legacy sae-lens registry id `11-res-jb` removed in ≥ 3; needs sae-lens
1.x–2.x, which conflicts with torch 2.6". **What the notebook actually does:** loads four SAEs *from
disk* at `~/.cache/sae_lens/blocks.{6,8,10,11}.hook_resid_pre` — an uncommitted local cache — with a
loop that `continue`s silently when a path is missing; the `KeyError: '11-res-jb'` the parent saw
is a later cell indexing the dict that the loop left empty. Not a registry id, not version drift:
**an uncommitted artifact, misfiled as version drift.**

**Extension.** Packages at the repo's own `requirements.txt` pins (sae-lens 6.18.0, transformer-lens
2.16.1, transformers 4.57.1, torch 2.9.0), frozen at 2026-02-18; the cache populated from the
public release `gpt2-small-res-jb` (the four `blocks.N.hook_resid_pre` SAEs) via
`SAE.from_pretrained` + `save_model`. Nothing else touched.

`[MEASURED]` 30/30 cells, 0 errors, 4/4 SAEs loaded. Headline: **mean Jaccard across surface forms
0.131** (target 0.13); **within-topic cosine 0.503 vs cross-topic 0.137** (target 0.50 vs 0.14),
difference 0.366, permutation p < 0.001. All three inside `abs:0.05`. → **reproduced, tier exact**
(deterministic feature extraction over released SAEs).

`[INFERRED]`
1. Two rot-reversal attempts, two conversions. Neither required the author. One needed a date
   flag; this one needed *reading the loading code* instead of the traceback — the parent's
   diagnosis stopped at the exception, which was two cells downstream of the cause.
2. **Silent-skip loaders convert `data` failures into misleading `env` failures.** A `continue` on a
   missing artifact is a rot amplifier: it turns "file not found" into an unrelated KeyError that
   pattern-matches a known library-drift story (`lessons-synth` Part 3 had a row for exactly that
   story, and the parent applied it). The catalog needs a counter-rule: *before classifying a
   KeyError as registry drift, check whether an upstream loader swallowed a miss.*
3. The `env` bucket in the N=36 taxonomy is heterogeneous: so far it contains one true
   post-date drift (tenseisoham, fixed by freezing) and one misfiled artifact miss. The rate of
   "never ran, but reproduces once the environment is right" is now 2/2 on the rows tried.

**Rot-reversal running tally** (of the 7 `env` rows in N=36):

| row | parent diagnosis | actual cause | fix class | result |
|---|---|---|---|---|
| tenseisoham | kwarg removed ~4.46 | removed later; post-date freeze has it | `--exclude-newer` | ✅ exact (160.87; 52,156 vs 49,802) |
| thebuleganteng | sae-lens registry id removed | uncommitted SAE cache + silent skip | artifact fetch | ✅ exact (0.131; 0.503 / 0.137) |
| jim-maar | dir-name assert | assert + empty gitlink for `othello_world` | copy + upstream clone + freeze | ⏳ R-9 |
| ibm, dajale423, uchicago-xlab, (sunmoonron = vram) | — | — | — | queued |

### N after R-8 — next-run decision

R-9 (jim-maar) is running. After it: `ibm/sae-steering` needs an uncommitted OpenAI SAE file
(`{path}/gpt.top_k32.f0.pt`, `path=""`) — fetchable from the OpenAI blob the repo's own utils use,
but its headline is a *timing* claim (< +0.001 s/token) that is hardware-specific; run it, judge
direction only. Then `dajale423` (e2e_sae fork, torch 2.2 era → freeze 2024-09-20) and
`uchicago-xlab` (2026-08-01 — if a freeze at the post date fails, that is the "rotten at
publication" branch, the one outcome the series has not yet produced).

## R-9 — rot reversal, row 3: `jim-maar/interpretability` (Othello-GPT flipping circuit) (2026-08-28 17:41; 74 GPU-min + 2 restarts)

**Parent verdict:** `env` — the repo asserts its checkout is literally named `interpretability`;
the harness's symlink resolved to `src`. **What it took to run:** (1) a *copy* named
`interpretability` (trivial); (2) the `othello_world` inputs — an **empty gitlink with no
`.gitmodules` entry** — restored by cloning `likenneth/othello_world` at the gitlink's commit
(`f23bb56`, exists upstream); (3) `training_probes/` on `PYTHONPATH` (notebook-era path);
(4) a 2025-02-16 date-frozen resolution (torch 2.0.1, transformer-lens 2.0.0) — ran first time.
Then: **`IndexError: index 100100 out of bounds for size 100000`** — the script indexes games
200 … 200,200 (`batches=1000 × batch_size=200 + start=200`); the committed upstream file at the
author's own gitlink commit has **100,000** games. The author ran on an uncommitted larger file.
Deviation, on a copy and logged: `batches=499` (every available batch).

`[MEASURED]` (`accuracy_summary.json`) over layers 1–7 × 59 positions × 64 tiles, 25,207 populated
cells, 99,800 games:
- the script's own designated summary (layer 1, position 10, tile D3): **0.8354** with real
  attention, 0.8409 with the attention-pattern approximation — target "0.818 overall": **+0.017,
  inside abs:0.05**.
- naive aggregates over *all* cells: micro 0.682 / macro 0.662 / max 1.00 (target "up to 0.97").
- `[UNRESOLVED]` which aggregation the post's "0.818 overall" denotes. The number the author's
  script prints as its result is the D3 cell and it lands within tolerance; the all-cell mean
  does not. Read as **partial (direction + the scripted metric within tolerance; n = 99,800 of
  the author's ≥ 200,200 games)**.

`[INFERRED]`
1. Three layers of rot were stacked on one row, and the parent's taxonomy recorded only the outermost
   (the assert). Under it: a broken submodule pointer, a notebook-only import path, and an
   uncommitted dataset. **`env` rows should be expected to be onions**; the first fix reveals the
   next reason, and the stopping rule (2–3 tries) guarantees the ledger records the shallowest.
2. Once the environment was right, the computation ran and its own printed metric matched. The
   residual uncertainty is a *reporting* ambiguity ("overall") plus a *data* gap (uncommitted
   games) — neither is scientific fragility.

**Rot-reversal running tally** (7 `env` rows in N=36):

| row | parent diagnosis | actual causes (in order found) | result |
|---|---|---|---|
| tenseisoham | kwarg removed ~4.46 | version claim wrong; post-date freeze runs | ✅ exact |
| thebuleganteng | sae-lens registry id removed | uncommitted SAE cache + silent-skip loader | ✅ exact |
| jim-maar | dir-name assert | assert → empty gitlink → notebook path → uncommitted larger dataset | ⚠ partial (scripted metric 0.835 vs 0.818 on half the games) |
| ibm | torch↔transformer-lens arity | requirements.txt unsatisfiable as a set (sparse_autoencoder pins TL 1.9.1 vs 2.2.2); uncommitted SAE file; entrypoint is pipeline step N with uncommitted CSVs | ⏳ R-10 |

### N after R-9 — next-run decision

R-10 (ibm) is on the card: environment built by dropping the contradictory pin and installing the
OpenAI package `--no-deps`; the SAE file and the three intermediate CSVs regenerated with the
repo's own functions. Headline is timing; direction only. After R-10: `dajale423` (2024-09;
e2e_sae fork) and `uchicago-xlab` (2026-08-01, the "rotten at publication" test). Then this
series is summarised and the direction re-evaluated against the remaining program items
(bug-injection control, dtype arm).

## R-10 — rot reversal, row 4: `ibm/sae-steering` (2026-08-28 17:56; 1 GPU-min + 6 min prep)

**Parent verdict:** `env` — "torch 2.3.1 ↔ transformer-lens arity drift". **What was actually under
it, in the order found:** (1) the repo's own `requirements.txt` is **unsatisfiable as a set** —
`sparse_autoencoder@4965b94` (pinned git dep) requires `transformer-lens==1.9.1`, the file pins
`2.2.2`; no resolver could ever have installed it (the author must have `pip install`ed
sequentially, letting the last write win); (2) the SAE the entrypoint loads (`{path}/gpt.top_k32.f0.pt`,
`path=""`) is **uncommitted** — regenerated from the OpenAI blob the repo's own utils name
(v5_32k, resid_post_mlp, layer 9, 201 MB); (3) the entrypoint is **step N of a pipeline** whose
three intermediate CSVs (`D_ref_embeds`, `dref_latents_9`, `D_align_embeds`) were never committed —
regenerated with the repo's own `process_D_ref` / `D_align_scoring`; (4) `timing_tests.py`
**unpacks five values from a `setup()` that returns four at the pinned commit** — broken code at
publication (the repo has a single commit, 2024-09-20, five weeks before the post). Fixed on a copy
(the fifth value is unused). Env frozen at 2024-11-08: torch 2.3.1+cu121, transformer-lens 2.2.2,
transformers 4.42.4.

`[MEASURED]` The script's output (a LaTeX table row, s/token, mean ± 95% CI over the 150 reference
prompts): sentence-embedding **0.355 ± 0.008**; SAE-latent **0.007 ± 0.001**; min-distance
**0.000 ± 0.000**; feature-score **0.000 ± 0.000**. Target: "< +0.001 s/token on unoptimized code".

`[UNRESOLVED]` Which component(s) the post's "+0.001" bounds. Two of four are below it; the SAE
encode is 7× above; the embedding step is 350× above (and is a baseline cost, not an overhead).
Timing is hardware-specific (RTX 3090 vs the author's unknown machine). Read: **partial —
direction only; the steering-specific steps (distance, score) are below the claimed bound; the
SAE step is not.**

`[INFERRED]`
1. **Four independent rot classes on one row, none of them the one recorded.** Broken lockfile at
   publication · uncommitted model artefact · uncommitted pipeline intermediates · code that never
   ran at HEAD. The parent's `env` label was the first exception the harness hit, not the cause.
2. **"Broken at publication" now has two instances** (this row's unpack bug and its requirements
   set). That is the branch the series had not produced until now — and it lands in the *code and
   packaging* column, still not the science.
3. Once inputs existed, the computation took one minute. The 6-minute prep is what the paper
   would have needed to commit.

**Rot-reversal running tally** (7 `env` rows in N=36):

| row | parent diagnosis | causes found (in order) | result |
|---|---|---|---|
| tenseisoham | kwarg removed ~4.46 | wrong version claim; post-date freeze runs | ✅ exact |
| thebuleganteng | sae-lens id removed | uncommitted SAE cache + silent-skip loader | ✅ exact |
| jim-maar | dir-name assert | assert → empty gitlink → path → uncommitted dataset | ⚠ partial |
| ibm | torch↔TL arity | unsatisfiable requirements → uncommitted SAE → uncommitted intermediates → unpack bug at HEAD | ⚠ partial (direction) |
| dajale423 | e2e_sae dep web | ⏳ R-11 (hard-coded wandb run id on every path) | ⏳ |
| uchicago-xlab, (sunmoonron=vram) | — | queued | — |

### N after R-10 — next-run decision

R-11 (dajale423, 2024-09) is on the card; its pre-registered branch is the wandb fetch. After it,
`uchicago-xlab` (post 2026-08-01 — a freeze at the post date is the cleanest test of
"rotten at publication" the series can run: the environment *is* the post-date environment).
Then the series closes with a summary section and the program re-evaluates: 4 rot-reversal rows
have produced 2 exact + 2 partial and **0 scientific misses**; the bug-injection control becomes
the priority, because the series so far has only ever *confirmed* and a harness that only confirms
needs its false-negative rate measured.

