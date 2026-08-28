# What is going on in this folder — for humans

Seven mini-projects, in the order they happened. Each has two explanations: **ELI5** (no jargon)
and **Busy researcher** (the numbers, the caveats, where the file is — 90 seconds each).
Written 2026-08-29. Every number below is emitted by a script somewhere in the repo; the
researcher sections say which one.

---

## 1. Checking the three scrapes (`corpus-analysis.md`, `review.md`, `meta.py`)

### ELI5
Someone collected a big pile of blog posts about keeping AI safe — 741 of them — from two websites,
using two robot helpers. Before reading the posts, we checked whether the robots did a good job
collecting. They mostly did, but they had counted some posts twice (149 posts were in both piles),
and one robot had labelled a number wrong (it called "LessWrong points" "Alignment Forum points").
We fixed the counts, and we wrote a little test so that every number in the write-up has to come
from a program, not from someone's memory.

### Busy researcher
- **Object:** three corpora — AF (253 posts), LW (637), Olah/Nanda blogs (101) — scraped
  2024-08-25 → 2026-08-25 by two separate Opus sessions. `corpus-analysis.md` reviews the *scrapes*, not
  the research.
- **Key fixes (`review.md`, 14 findings; 25 marked corrections in `corpus-analysis.md`):** AF ∩ LW = 149,
  union = 741 (`union.json` is the denominator); AF's `karma` is LW's `baseScore` (149/149 identical
  + live GraphQL check, `api_spotcheck.json`); a repo double-counting bug; partial-period trend
  comparisons replaced by per-30-day rates; Wilson intervals on every rate, bootstrap on every median.
- **Instrument caveat that survives everything:** the "rigor" markers in `corpus-analysis.md` are regex
  word-matches; the judge-based re-measurement (project 2) under-counts nothing and over-counts
  nothing consistently — the two instruments measure different constructs.
- **Mechanics:** `python3 meta.py` → `numbers.json` (1,336 keys); `test_numbers.py` fails if the
  prose asserts a `[MEASURED]` number no script emits. Evidence tiers `[MEASURED]/[INFERRED]/
  [SPECULATIVE]/[UNRESOLVED]` are load-bearing throughout.

---

## 2. What the 741 posts actually found (`p3/findings.md`)

### ELI5
Then we read every post — one robot reader per post, all following the same checklist — and wrote
down what each one claimed to have discovered. The surprise: for most of the questions people care
about, some posts say "yes it works" and other posts say "no it doesn't", and nobody has gone back
to sort out who is right. Also, almost nobody re-does anyone else's experiment: only 24 posts out of
728 tried.

### Busy researcher
- **Instrument:** an LLM judge with a written rubric (`p3/EXTRACT.md`), 30 agents, one claim record
  per post (`p3/claims/`), 728 substantive records after dedup. **No human validation** — `prompts.md`
  P4 is the design; treat every rate as instrument-relative.
- **Headline:** 35 of the 50 best-studied phenomena carry claims in both directions (AI control
  protocols 12-vs-12 across 28 first authors); replications 3.3% [2.2, 4.9]; 64% of posts position
  against prior work.
- **Instrument comparison (§5):** judge vs regex differ by 40 points on "has a baseline" — mostly
  construct difference, not error; `multi_model` was a genuine regex miss (9% vs 51%).
- **Rising rigor (§4):** uncertainty reporting 7% → 24% over full periods (the 2026H2 column is a
  56-day partial — do not read it as a trend).
- **Orphaned-lead queue (§8):** 1,937 stated next steps; the head is generic ("investigate the
  mechanism", 107 authors); the one specific, widely-requested artefact is *training-induced model
  organisms* (19 independent first authors).

---

## 3. Themes, patterns, outliers (`results.md`, `meta-analysis-blog-post.md`, `analyze.py`)

### ELI5
We looked at the whole pile from above. The posts everyone reads the most are the ones you *can't*
check yourself, because the model they studied lives behind a paywall. People working alone share
their code more; teams do more careful checks. And almost everyone does the "looks like science"
parts (a comparison, a list of caveats) while very few do the "is it real" parts (running it more
than once). The blog post is called *Nobody Is Checking*.

### Busy researcher
- **Five axes nobody had used:** LW's 180 human tags, the model landscape, the `depends_on` graph,
  author structure, multi-axis outliers. All numbers from `analyze.py` → `analysis_numbers.json`.
- **Form vs inference:** baseline 90.7%, limitations 89.1%, ablation 66.3% — but uncertainty 19.4%,
  seeds 13.7%, prereg 2.2%; **no post scores 6/6** on design markers.
- **Attention ↔ reproducibility:** code release 75% → 47% across karma deciles (Spearman −0.149);
  mediated by model access (closed-model posts 66% → 31%; open-model gradient vanishes).
  Ranking replication candidates by attention selects *against* runnability.
- **Solo vs team:** solo ships code 68% vs 53%; teams ablate 74% vs 59% and report uncertainty 24%
  vs 15%. Negative-result rate (21.2%) is invariant to every split tested.
- **Outliers worth acting on:** eight highest-karma no-code posts include three top-25 dependencies;
  four "lone dissenters" (a single negative post in an otherwise-unanimous phenomenon), the
  crosscoder one being 3090-runnable.

---

## 4. Which experiments fit a home GPU (`replication/select.py`, `pareto.md`, `3090-prompts.md`, `prompts2/`)

### ELI5
Some experiments need a giant computer; some fit the one gaming graphics card in this house. We
sorted them, opened each one's code to see whether it could actually run, and picked the best
three to try first. The sorting found that the hard part isn't the size of the computer — it's
that lots of code needs a paid AI service or is missing pieces.

### Busy researcher
- **Pipeline:** 741 posts → 142 candidates (open weights, code linked, a number to hit, ≤24 GB on
  paper) → 18 inspection agents read the repos → 87 runnable specs (`replication/experiments/`,
  each `spec.json` + `PROMPT.md` + `run.sh`), ranked in `queue.md`.
- **What inspection found:** VRAM was the *least* binding filter. 20% of code-shipping open-model
  posts compute their headline through a closed-API judge; ~8% link a repo without the experiment.
- **80/20 (`pareto.py`):** geometric mean of value (contested ×2, in-degree ×1.5, negative claim,
  rigor…) and feasibility (closed API = hard zero, fits, entrypoint, data…). Result: flat, not
  Pareto — top 20% hold 28% of score. Top three: cross-model geometry (a PRH negative), AntiPaSTO
  honesty steering, noise-injection sandbagging — scaffolded in `~/prompts/3090/`.
- **Direction menu for the next agent:** `prompts2/brainstorm.md` (§7 is a run order) and
  `prompts2/00-fable-research-director.md`.

---

## 5. Running them: the replication ledger (`replication/META-REPORT.md`, N = 36)

### ELI5
A robot tried to re-run 36 experiments on the home graphics card, one at a time, with strict rules
(don't change the experiment, only fix the plumbing; never cheat by using a paid AI). Fifteen worked
and gave the same answer as the original. Sixteen never got started — every single one because of
broken plumbing (old software, missing files), not because the science was wrong. Only one
experiment ran and gave a different answer, and that one turned out to have shipped the wrong
settings file.

### Busy researcher
- **Protocol:** pin the author's commit, one venv per experiment, environment-only fixes logged as
  `--fix` lines, no hosted-model APIs, a time-box, pre-registered tolerance, a `== VERDICT` block
  per row; quality tiers exact / recompute / partial / not.
- **Result:** 36 attempted · 20 located · 15 reproduced (11 exact + 4 recompute) · **18/20 located
  reproduce ≥ partially** · 16/36 never ran, all on packaging/hardware (env 7, runtime 3,
  unclear-entrypoint 2, vram 2, api-key/data/model-access 1 each).
- **The one scientific miss:** AntiPaSTO 1B (Steer F1 2.0 vs 31.2) — the shipped 1B preset never
  matched the paper's config (`git log -S`); reproduces on 270M.
- **Reusable outputs:** `HARNESS.md` (queue + prep + autofix tooling) and `lessons-synth.md`
  (Part 3 = symptom → cause → fix catalogue).

---

## 6. The new direction: what does a reproduction *depend on*? (`replication/NEW-DIRECTION.md`, R-1 … R-15)

### ELI5
Instead of asking "does it work again?", we asked "what makes it work again?". We re-ran the
experiments that had worked while changing exactly one thing at a time — the random seed, the
software version, the kind of model — and we went back to the ones that "couldn't run" and fixed
the plumbing properly. Findings: some results only come out on about half of the random seeds;
one popular trick works two times in three and *breaks* the model one time in four; changing the
software changed nothing important; and almost all the "couldn't run" experiments could run after
all, and gave the right answer. We also planted fake bugs to see whether our checker would notice.
It noticed every time.

### Busy researcher
Fifteen GPU runs, one factor each, all `experiment_class: extension` (excluded from the rate).
- **Seed (R-1, R-4):** ioi's 3-decimal "exact" match was an RNG match — across seeds the effect is
  30% larger; phusroyal's headline is bimodal, **4/15 seeds** in the claimed range; matryoshka
  invariant. Re-tier seeded rows as rates.
- **Sampling (R-5):** sandbagging noise-injection at n = 30: **67% [49, 81] reveal, 23% [12, 41]
  collapse**; parent 9/10 and author 6/10 are both ordinary draws.
- **Library epoch (R-2, R-3):** `transformers` minor → 35,700/35,700 generations byte-identical;
  torch major → 65% of text rewritten, verdict unchanged; seed SD / kernel SD = 3.5.
- **Family (R-6):** prompted organism absent on Llama-3.2-1B (gap 9 pp vs 26); untestable.
- **Rot reversal (R-7…R-12, R-14, R-15):** 8 never-ran rows re-attempted; **7 reached a
  measurement → 3 exact + 4 partial, 0 misses**; 1 credential-gated (W&B login). `uv --exclude-newer <post date>` and *reading the loader before the
  traceback* did most of the work. `env` is five distinct classes; 0/6 parent diagnoses named the
  terminal cause.
- **Harness calibration (R-13):** blind Sonnet judges on clean vs bug-injected reruns: **7/7**.
- **CPU side-result:** the 29 contested phenomena share no metric (493/493 distinct strings; none
  shared across sign) — "contested" means "measured differently".
- **Revised headline:** **25/27** rows that reached a measurement reproduce ≥ partially (18/20
  parent rows + 7/7 rot-reversal); the two exceptions are one scientific miss (AntiPaSTO) and one
  hosted-API artefact that was never a local test.

---

## 7. What is running now, and what's next (`replication/handoff-30.md`)

### ELI5
Three experiments were too slow for the daytime, so they're running overnight, one after another.
Someone (a robot or a person) needs to look at the results in the morning. Nothing has been sent to
anyone outside this computer.

### Busy researcher
- **Overnight queue (`tree_late.sh`, detached):** O1 g-w1 (timed out at 360 min — judge as
  `runtime` with the honest timing), O2 mamiglia running (420-min budget), O3 james-sullivan
  queued (480). These are replication re-attempts of N=36 rows: judge per `handoff-synth` §A3,
  update the parent ledgers, regenerate `META-REPORT.md`.
- **Next CPU work:** P3-judge validation against ledger ground truth; tolerance-rule audit (which
  `manual`/3-decimal tolerances fail on a different seed); a sub-tolerance bug-injection round.
- **Do not:** create a W&B login (dajale423), push/fork/contact authors, count extensions in the
  rate, read 2026H2 as a trend.

---

# LLM

Machine-facing summary of the whole repo. Direct, unambiguous, no narrative. Every number is
emitted by a named script. Tiers: `[MEASURED]` = a script emits it; `[INFERRED]` = judgment resting
on measured numbers; `[UNRESOLVED]` = the data cannot decide.

## Object

741 distinct posts of empirical AI-safety research (union of an Alignment Forum scrape n=253 and a
LessWrong scrape n=637, overlap 149; plus an Olah/Nanda blog corpus n=101 used only in `corpus-analysis.md`).
Window 2024-08-25 → 2026-08-25. Two questions were asked of it: **what does this literature claim**,
and **does it reproduce on one RTX 3090**.

## Layers, in dependency order

1. `union.json` (741 records, keyed by ForumMagnum post id) ← `build_union.py`. The denominator.
   Pooling AF and LW double-counts 149 posts.
2. `numbers.json` (1,336 keys) ← `meta.py`. Collection-level measures for `corpus-analysis.md`.
   `test_numbers.py` fails if `corpus-analysis.md` asserts a `[MEASURED]` number no script emits.
3. `p3/claims/*.json` (741 records) ← 30 LLM extraction agents against `p3/EXTRACT.md`.
   `p3/findings_numbers.json` ← `p3/findings.py` → `p3/findings.md`.
4. `analysis_numbers.json` ← `analyze.py` (imports `p3/findings.py`'s loader, so denominators
   cannot drift) → `results.md`, `meta-analysis-blog-post.md`.
5. `replication/experiments/<slug>/{spec.json,ledger.json}` ← inspection + `run.sh`/queue.
   `ledger.py` → `META-REPORT.md`. Extension rows in `<slug>--ext-<kind>/` ← `ext_ledger.py` →
   `NEW-DIRECTION.md`.

## Findings that survive scrutiny

- `[MEASURED]` **Contested by default.** 35 of the 50 best-studied phenomena carry both positive and
  negative primary claims. Replications 3.3% [2.2, 4.9]; posts positioning against prior work 64.1%.
- `[MEASURED]` **The contested phenomena share no measure.** Across the 29 with n ≥ 6, 493 posts
  name 493 distinct `effect.metric` strings; the count shared between a positive and a negative post
  is 0 (exact-string, a lower bound). `[INFERRED]` "Contested" means "measured differently".
- `[MEASURED]` **Form without inference.** baseline 90.7%, limitations 89.1%, ablation 66.3%;
  uncertainty 19.4%, seeds 13.7%, preregistration 2.2%. No post scores 6/6 on design markers.
- `[MEASURED]` **Attention is inversely related to reproducibility.** Code release 75% → 47% across
  karma deciles; mediated by model access (closed-model posts 66% → 31% across karma; the gradient
  vanishes among open-model posts). `[INFERRED]` Ranking replication candidates by attention selects
  against runnability.
- `[MEASURED]` **Reproduction, N=36 ledger:** 20 located, 15 reproduced (11 exact + 4 recompute),
  18/20 ≥ partial; 16 never ran, all on packaging or hardware.
- `[MEASURED]` **Rot is reversible.** 8 never-ran rows re-attempted with the environment
  reconstructed: 7 reached a measurement → 3 exact + 4 partial, 0 scientific misses; the 8th needs a
  Weights & Biases login. Pooled over every row that reached a measurement: **25/27 ≥ partial**;
  exceptions are AntiPaSTO (the one scientific miss — the repo's shipped 1B preset never matched the
  paper's config) and one hosted-API row that was never a local test.
- `[MEASURED]` **`env` is five distinct classes**, and the first traceback named the terminal cause
  in 0 of 6 rows: post-date version drift, uncommitted artefacts (most common), code or lockfiles
  broken at publication, harness bugs, credential gates.
- `[MEASURED]` **Seeds move verdicts; library versions do not.** One reproduced training row is
  bimodal across seeds (4/15 inside the claimed range); a "for some seeds" claim is a 67% [49, 81]
  effect with a 23% [12, 41] model-collapse rate at n=30. A `transformers` minor change left
  35,700/35,700 generations byte-identical; a torch major rewrote 65% of generated text and changed
  no verdict (seed SD / kernel SD = 3.5).
- `[MEASURED]` **Judging is calibrated at realistic bug size.** Blind judges on clean vs
  bug-injected reruns of three reproduced rows: 7/7 correct.

## Rules that constrain any continuation

1. Replication rows: environment-only fixes on copies, each logged as a `--fix` line. Changing
   model, seed set, library epoch, dataset size or metric makes it an **extension**
   (`experiment_class: "extension"`), which never enters the reproduction rate.
2. No hosted-model APIs (→ `api-key`), no accounts or logins (→ `model-access`).
3. No pushes to authors' repos, no issues, no author contact, no new forks.
4. A 3-decimal match with the author's seed is `exact-same-seed`, not evidence of a robust effect;
   a seeded result's honest tier is a rate with a Wilson interval.
5. Do not read the 2026H2 period as a trend (56 days vs 181–184).
6. Do not quote any rigor rate outside this repo before `prompts.md` P4 (human validation of the
   extraction instrument) has run.

## Entry points

`nav.md` (orientation) → `replication/handoff-synth.md` (rules + direction) →
`replication/lessons-synth.md` Part 3 (symptom → cause → fix) → `replication/NEW-DIRECTION.md`
(what a reproduction depends on) → `p3/findings.md`, `results.md` (what the literature claims) →
`replicate.md` (how to re-run any of it).

Regenerate everything: `python3 meta.py && python3 analyze.py && python3 p3/findings.py &&
python3 replication/ledger.py`.
