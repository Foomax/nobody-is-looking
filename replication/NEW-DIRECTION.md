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

