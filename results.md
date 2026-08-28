# Cross-cutting meta-analysis of the 741-post corpus — themes, difference patterns, outliers

Written for an LLM. Dense, tiered, no narrative. Every `[MEASURED]` number here is emitted by
`analyze.py` into `analysis_numbers.json`; the key is given in brackets like
`{contrast.solo.code}`. Tiers carry the definitions at the top of `corpus-analysis.md`:
`[MEASURED]` = a script emits it; `[INFERRED]` = a judgment resting on measured numbers;
`[SPECULATIVE]` = a hypothesis; `[UNRESOLVED]` = the data cannot separate the options.

## 0. Position relative to the other two analyses — read first

Three analyses now exist over the same corpus. They are not interchangeable.

| Document | Instrument | Question |
|---|---|---|
| `corpus-analysis.md` (via `meta.py`) | regex over post bodies | how the corpora were **collected** |
| `p3/findings.md` (via `p3/findings.py`) | LLM judge, one claim record per post | what the posts **claim** |
| **`results.md` (this, via `analyze.py`)** | joins the claim records to previously unused union fields | **structure** — themes, difference patterns, outliers |

This document adds five axes neither of the others used: LessWrong's **human-assigned `tags`**
(180 distinct, previously unread by any script), the **model landscape** (`models[]`), the
**dependency graph** (`depends_on`), **author structure**, and **multi-axis outlier detection**.

Denominators are identical to `p3/findings.md` by construction (`analyze.py` imports
`p3/findings.py`'s loader): 741 union posts → 738 projects after collapsing `dup_cluster_id`
→ **728 substantive records** after dropping 10 STUBs `{base.substantive}`.

**Instrument caveats that limit everything below.**

- `[UNRESOLVED]` The claim records come from an LLM judge that no human has validated
  (`prompts.md` P4 is the design that would price it). Everything derived from `claim_type`,
  `design.*`, and `reproducible_in_principle` inherits that.
- `[MEASURED]` The `tags` axis covers **630/728 = 86.5%** of records `{tags.coverage}`. The 98
  uncovered are exactly the AF-only posts — they have no LessWrong record, so no tags. Tag-based
  findings are therefore about the LessWrong-visible corpus, and §3.1 shows AF membership is not
  a neutral filter.
- `[MEASURED]` `karma_lw` is an age-confounded snapshot; a 2024 post has had two years to
  accumulate it. Every karma contrast below is stratified by period where the stratification is
  large enough to support it (§7).
- `reproducible_in_principle` means *the post says code/data exist*, not that they run.
  `replication/` measured the difference: ~8% of linked repos do not contain the experiment.

---

## 1. Themes — the corpus is a thin dense core inside a very long tail

`[MEASURED]` Four independent vocabularies over the same 728 records all show the same shape:

| vocabulary | assigned by | distinct values | used exactly once | key |
|---|---|---:|---:|---|
| `tags` | LessWrong users | 180 | 66 | `{tags.distinct}`, `{tags.used_once}` |
| `phenomenon` | LLM judge | 130 | 70 | `{phenomena.distinct}`, `{phenomena.singletons}` |
| `depends_on` | LLM judge | 1,819 | 1,512 (83.1%) | `{deps.distinct}`, `{deps.indeg1_pct}` |
| first author | the corpus | 500 | 370 (74.0%) | `{authors.distinct_first}`, `{authors.one_post_only}` |

`[MEASURED]` The top 10 tags carry **71.8%** of all tag assignments `{tags.top10_share_pct}`;
median 3 tags per post. **529 of 1,819 dependencies carry half of all 2,580 edges**
`{deps.n_for_half_of_edges}`. Gini of first-authorship = **0.259**
`{authors.first_author_gini}` — low, because the tail is enormous, not because the core is small.

`[INFERRED]` This is a **long-tail field with a small shared core**, not a set of coherent
sub-literatures. Two labelling systems built by different processes (humans tagging for
navigation, an LLM labelling for content) independently produce ~50% singleton labels. That
agreement makes the shape a property of the corpus rather than of either instrument.

### 1.1 Tag profiles

`[MEASURED]` `{tags.profiles}` — all tags with ≥10 posts. Selected rows:

| tag | n | negative % | ships code % | baseline % | median karma | median families |
|---|---:|---:|---:|---:|---:|---:|
| AI | 605 | 21.2 | 62.5 | 90.7 | 25 | 2 |
| Interpretability (ML & AI) | 305 | 19.0 | 67.5 | 90.5 | 21 | 1 |
| Language Models (LLMs) | 136 | 19.1 | 66.2 | 89.0 | 28 | 2 |
| AI Evaluations | 102 | 26.5 | 56.9 | 90.2 | 24 | 3 |
| AI Control | 92 | 25.0 | 60.9 | 92.4 | 18 | 2 |
| MATS Program | 72 | 19.4 | 56.9 | **98.6** | **52** | 2 |
| Sparse Autoencoders (SAEs) | 70 | 22.9 | 65.7 | 92.9 | 28 | 1 |
| Deceptive Alignment | 50 | 24.0 | 52.0 | 98.0 | 26 | 2 |
| Activation Engineering | 33 | 21.2 | **78.8** | 93.9 | 11 | 1 |
| Introspection | 10 | **40.0** | 60.0 | 100.0 | 33 | 3.5 |

`[INFERRED]` Two clusters with different methodological signatures:
**interpretability-family tags** (Interpretability, SAEs, Activation Engineering) — high code
release, **median 1 model family**, low uncertainty reporting; and **behavioural-evaluation tags**
(AI Evaluations, AI Control, Deceptive Alignment) — median 2–3 families, more negatives, less
code. Confirmed by contrast: Interpretability-tagged posts report uncertainty **13.1%
[9.8, 17.4]** vs **23.9% [20.1, 28.2]** elsewhere `{contrast.interp}`, z = −3.63.

### 1.2 Tag co-occurrence

`[MEASURED]` `{tags.top_lift_pairs}` — observed/expected for pairs with n≥5. Strongest:
AI Evaluations + Situational Awareness ×3.77 (n=11); MATS Program + Scalable Oversight ×3.37;
MATS Program + Reinforcement learning ×3.22; AI Evaluations + Sandbagging ×3.09;
AI Evaluations + Deceptive Alignment ×2.35 (n=19).

`[INFERRED]` The evaluation tags form a tight bundle — situational awareness, sandbagging,
deception and benchmarking are studied by the same posts. Interpretability's only strong pair is
with Transformers (×1.91), i.e. it does not bundle with anything; it *is* the substrate.

### 1.3 The two label systems agree on structure but not on grain

`[MEASURED]` `{tags.purity}` — inside each big tag, how concentrated are the LLM's phenomena?

| tag | n | distinct phenomena | top phenomenon share |
|---|---:|---:|---:|
| Activation Engineering | 33 | 14 | 51.5% |
| Deceptive Alignment | 50 | 22 | 32.0% |
| Sparse Autoencoders | 70 | 17 | 25.7% |
| AI Control | 92 | 39 | 25.0% |
| Interpretability | 305 | 71 | 8.9% |
| AI | 605 | 114 | 5.0% |

`[INFERRED]` Human tags are **navigational**, not analytic: the two largest cover 83% of the
corpus and shatter into 71–114 phenomena. Below the top two, tags and phenomena track each other
(a tag of ~50 posts holds ~20 phenomena — the same ~3-posts-per-phenomenon density as the corpus).
**Use `phenomenon` for aboutness and `tags` for community-visible framing; do not substitute one
for the other.**

---

## 2. Common features — what nearly every post in this corpus does

`[MEASURED]` n = 728. The modal post is remarkably uniform on presentation and remarkably thin
on inference control.

| feature | rate | 95% CI |
|---|---:|---|
| states a baseline / comparison condition | 90.7% | [88.3, 92.6] |
| states ≥1 limitation (median 3) | 89.1% | [86.7, 91.2] |
| proposes future work (median 3) | 81.3% | [78.3, 84.0] |
| runs an ablation | 66.3% | [62.8, 69.7] |
| positions against prior work | 64.1% | [60.6, 67.5] |
| ships code or code+data | 60.7% | [57.1, 64.2] |
| uses a held-out set | 34.3% | [31.0, 37.9] |
| **reports any uncertainty** | **19.4%** | [16.7, 22.4] |
| **reports a seed count** | **13.7%** | [11.4, 16.4] |
| uses human evaluation | 9.8% | [7.8, 12.1] |
| pre-registers | 2.2% | [1.4, 3.5] |

`[MEASURED]` Design-marker score (0–6, counting baseline/ablation/held-out/prereg/human-eval/seeds):
**median 2**; histogram `{design.score_hist}` = {0: 41, 1: 115, 2: 318, 3: 190, 4: 61, 5: 3, 6: 0}.
**No post in the corpus scores 6.** 41 posts (5.6%) score 0 `{design.zero_markers}`; 3 posts
(0.4%) score ≥5 `{design.five_plus}`.

`[INFERRED]` **The universal features are rhetorical; the rare ones are statistical.** Nine in
ten posts name a comparison and admit a limitation. Fewer than one in five say how much of the
result could be noise. The corpus has converged hard on the *form* of an empirical report and
barely at all on its inferential machinery. This is the single most actionable pattern here: an
intervention that moved seed-reporting from 13.7% to 50% would change more about what this
literature can support than any topic-level intervention.

---

## 3. Patterns in the differences — nine paired contrasts

`[MEASURED]` `{contrast.*}`. Each contrast reports both groups with Wilson intervals and an
unpooled two-proportion z. **z is reported, never used as a decision gate**; with nine contrasts
× seven markers, |z| < 3 should be read as suggestive.

### 3.1 The three contrasts that reproduce across markers

**Solo author (384) vs team (344)** `{contrast.solo}` — the largest coherent split:

| marker | solo | team | z |
|---|---|---|---:|
| ships code | **68.0%** [63.1, 72.4] | 52.6% [47.3, 57.8] | +4.23 |
| baseline | 86.7% [83.0, 89.8] | **95.1%** [92.2, 96.9] | −3.86 |
| ablation | 59.4% [54.4, 64.2] | **74.1%** [69.3, 78.5] | −4.21 |
| reports uncertainty | 15.1% [11.9, 19.0] | **24.1%** [19.9, 28.9] | −3.08 |
| positions against prior work | 57.8% [52.8, 62.7] | **71.2%** [66.2, 75.8] | −3.77 |
| median karma | 15 | 45.5 | — |
| median model families | 1 | 2 | — |

`[INFERRED]` **Solo work is more open and less controlled; team work is more controlled and less
open.** Both directions are large and neither is a rounding artifact. The plausible mechanism is
resource: a solo researcher on one open model can push a repo; a team running a frontier model
sweep has both the person-hours for ablations and the reasons not to publish the harness.

**Longer than median (2,224 words) vs shorter** `{contrast.length}` — the strongest single
predictor of every rigor marker in the corpus: ablation **75.5% vs 57.1%** (z = +5.26),
uncertainty **24.5% vs 14.3%** (z = +3.47), positions against prior work **72.3% vs 56.0%**
(z = +4.56), baseline 94.0% vs 87.4% (z = +3.06). Code release does **not** differ (62.1% vs
59.3%, z = 0.76).

`[INFERRED]` Length is a proxy for effort, and effort buys controls — but not artifacts. A
one-line screen for this corpus: *word count predicts rigor markers better than venue, karma,
team size, or topic.* `[SPECULATIVE]` It may be partly tautological (reporting an ablation costs
words), which is why the code-release null matters: code costs no words and does not move.

**Studies an open-weight model (525) vs not (203)** `{contrast.open}` — ships code
**65.5% [61.4, 69.5]** vs **48.3% [41.5, 55.1]** (z = +4.27); baseline 92.6% vs 85.7%
(z = +2.85); median karma 23 vs 40. This is the mediator for §7.

### 3.2 Alignment Forum membership is a prestige filter, not a quality filter

`[MEASURED]` `{contrast.af}` — in AF (245) vs LessWrong-only (483): median karma **57 vs 18**
(3.2×); ships code **51.0% [44.8, 57.2] vs 65.6% [61.3, 69.7]** (z = −3.81); positions against
prior work 70.2% vs 61.1% (z = +2.43); negative-result rate statistically indistinguishable
(20.0% vs 21.7%, z = −0.54); seeds, uncertainty indistinguishable.

`[INFERRED]` This reproduces `corpus-analysis.md` M2 on the object layer with a *different instrument*
(judge-read design flags rather than regex): **AF admission tracks attention and citation posture,
not inferential quality, and it selects against code release.** Two independent instruments
agreeing on a null makes the null much harder to dismiss as a measurement artifact.

### 3.3 The MATS cohort is a visible, distinct methodological population

`[MEASURED]` `{contrast.mats}` — 72 posts tagged `MATS Program` vs 656 not:
baseline **98.6% [92.5, 99.8]** vs 89.8% (z = +2.44); ablation 77.8% vs 65.1% (z = +2.16);
**seeds 23.6% [15.3, 34.6] vs 12.7% [10.3, 15.4]** (z = +2.56); median karma **52.5 vs 25**;
median words 2,870 vs 2,156. Code release is *not* higher (56.9% vs 61.1%, z = −0.69).

`[INFERRED]` A structured research program leaves a measurable methodological fingerprint —
nearly double the seed-reporting rate of the field around it, and the highest baseline rate of any
group in this analysis. `[SPECULATIVE]` The candidate mechanism is mentorship transmitting
specific habits; the candidate confound is selection into the program. The corpus cannot separate
them, but the *size* of the seed gap makes MATS the most promising natural experiment in the
dataset for "does teaching methodology work".

### 3.4 Contrasts that came back null

`[MEASURED]` **The negative-result rate is stable across every split tested**: AF vs not
(20.0/21.7), MATS vs not (19.4/21.3), solo vs team (22.1/20.1), code vs not (20.1/22.7),
high vs low karma (19.5/22.7), long vs short (22.3/20.1), open vs closed (21.3/20.7).
Corpus rate **21.2% [18.3, 24.3]** `{corpus.negative}`.

`[INFERRED]` Whatever governs whether a post reports a negative result, it is **not** venue,
cohort, team size, resources, attention, length, or model access. `[SPECULATIVE]` The remaining
candidate is the phenomenon itself — consistent with `p3/findings.md` §1, where 35 of the 50
best-studied phenomena carry claims in both directions. Negativity looks like a property of the
question, not of the researcher.

---

## 4. The model landscape — a two-tier monoculture

`[MEASURED]` `{models.*}` 211 distinct families named. Posts studying each:

| family | posts | % of 728 | weights |
|---|---:|---:|---|
| Claude | 181 | 24.9 | closed |
| Llama | 173 | 23.8 | open |
| Qwen | 151 | 20.7 | open |
| Gemma | 115 | 15.8 | open |
| Gemini | 100 | 13.7 | closed |
| DeepSeek | 74 | 10.2 | open |
| GPT (generic) | 67 | 9.2 | closed |
| GPT-4o | 65 | 8.9 | closed |
| Mistral | 43 | 5.9 | open |
| GPT-2 | 38 | 5.2 | open |

`[MEASURED]` ≥1 open-weight model: **525/728 = 72.1% [68.7, 75.3]** `{models.any_open}`;
all-open **347 = 47.7%** `{models.all_open}`; no model named 71. **Single-family posts:
285 = 39.1%** `{models.single_family}`; median families 2 [1, 2].

`[INFERRED]` **The most-studied model in AI-safety research is one nobody outside Anthropic can
open.** Two in five posts test on a single family, so the corpus's most common claim shape is *a
behaviour observed in one model lineage*. Combined with §1.1 (interpretability median = 1 family,
evaluation median = 3), interpretability is the monoculture: it goes deep on Gemma/GPT-2 and
almost never checks whether the geometry transfers. That is exactly the gap
`replication/pareto.md` ranked first for the 3090 queue, arrived at here from a different
direction.

`[MEASURED]` Drift `{periods}`:

| period | n | ≥1 open % | median families | negative % | ships code % | baseline % |
|---|---:|---:|---:|---:|---:|---:|
| 2024H2 | 90 | 76.7 | 1 | 17.8 | 53.3 | 84.4 |
| 2025H1 | 159 | 67.3 | 1 | 19.5 | 60.4 | 89.3 |
| 2025H2 | 179 | 70.9 | 2 | 20.7 | 57.0 | 90.5 |
| 2026H1 | 206 | 70.4 | 2 | 23.8 | 60.2 | 92.2 |
| 2026H2 | 94 | 81.9 | 1 | 22.3 | **76.6** | **95.7** |

`[INFERRED]` Rigor markers and code release rise monotonically; the 2026H2 jump is large
(+16 points of code release in one half-year). `[UNRESOLVED]` **2026H2 is 56 days, not 181** — it
is a partial period, and this corpus has a documented survivorship pattern in partial windows
(`corpus-analysis.md` §1.3(d)). Do not read the 2026H2 row as a trend endpoint until the period closes.
The 2024H2→2026H1 segment is four full-ish periods and is safe: code 53.3→60.2, baseline
84.4→92.2.

---

## 5. Dependency structure — the field builds on papers it cannot run

`[MEASURED]` `{deps.*}` 1,819 distinct dependencies, 2,580 edges, 5.8% of posts declare none.
By kind: **arXiv 1,301 (50.4%), repos 807 (31.3%), other 472 (18.3%)**. 83.1% of dependencies are
cited exactly once. Top nodes: `arXiv:2312.06942` (27), `arXiv:2502.17424` (23),
`arXiv:2412.14093` (22); the top *repos* are `UKGovernmentBEIS/control-arena` (10),
`TransformerLensOrg/TransformerLens` (10), `jbloomAus/SAELens` (7) `{deps.top25}`.

`[INFERRED]` The dependency graph is **1.6 papers per repo**. The shared substrate of this field
is a reading list, not a toolchain — three infrastructure repos carry the only double-digit repo
in-degrees. This independently corroborates `p3/findings.md` §6 (reuse is diffuse) from the
dependency side rather than the own-repo side, and it explains the replication findings in
`replication/README.md`: when what you inherit is a PDF, reproducing a result means rebuilding it.

---

## 6. Author structure — a field of one-post authors with a small permanent staff

`[MEASURED]` `{authors.*}` 893 distinct authors, 500 distinct first authors, **74.0% of first
authors appear exactly once** `{authors.one_post_only}`. Most prolific by any authorship, with
first-author count in brackets: **Neel Nanda 52 [0]**, Senthooran Rajamanoharan 23 [2],
Fabien Roger 23 [8], Arthur Conmy 18 [1], Josh Engels 18 [8], StefanHex 16 [1], Sam Marks 15 [4],
chanind 12 [11].

`[INFERRED]` Two disjoint roles are visible in one table. **Last-author/advisor** — Nanda 52
posts, 0 as first author; Conmy 18/1; StefanHex 16/1 — a supervisory layer that appears on a tenth
of the corpus without ever leading it. **Sustained first author** — chanind 12/11 — is rare
enough to be an outlier (§7.4). `[MEASURED]` The 24 replication posts have **23 distinct first
authors** (only `abhayesian` appears twice): **nobody in this corpus occupies replication as a role.**

---

## 7. The sharpest inverse pattern: attention vs reproducibility

`[MEASURED]` Spearman(karma, ships-code) = **−0.149**, n = 728
`{attention.spearman_karma_code}`. By karma decile `{attention.karma_deciles}`:

| decile | karma range | n | ships code % | 95% CI |
|---:|---|---:|---:|---|
| 1 | −1–6 | 72 | **75.0** | [63.9, 83.6] |
| 2 | 6–9 | 73 | 68.5 | [57.1, 78.0] |
| 3 | 9–13 | 73 | 65.8 | [54.3, 75.6] |
| 5 | 20–28 | 73 | 65.8 | [54.3, 75.6] |
| 8 | 52–70 | 73 | 47.9 | [36.9, 59.2] |
| 10 | 106–501 | 73 | **46.6** | [35.6, 57.9] |

Top vs bottom karma quartile: **52.2% vs 70.5%**, z = −3.6 `{attention.strata}`.

**The mediator is model access** `{attention.mediation_quintiles}`:

| karma quintile | ≥1 open model % | ships code % | code \| open | code \| closed |
|---:|---:|---:|---:|---:|
| 1 (lowest) | 86.2 | 71.7 | 72.8 (n=125) | 65.0 (n=20) |
| 3 | 69.0 | 64.8 | 67.0 (n=100) | 60.0 (n=45) |
| 5 (highest) | 56.8 | 52.7 | **69.9** (n=83) | **30.2** (n=63) |

`[MEASURED]` Within open-model posts the karma gradient nearly vanishes (top quartile 62.9% vs
bottom 72.5%, z = −1.67) `{attention.within_open}`. Within closed-model posts it is steep
(**31.4% vs 66.0%, z = −3.48**) `{attention.within_closed}`.

`[INFERRED]` **The corpus's most-read work is its least reproducible, and the reason is what it
studies, not who wrote it.** The causal chain the data supports: high-attention questions are
about frontier behaviour → frontier behaviour lives behind an API → API work cannot ship a
runnable artifact. Karma is not causing anything; it is a marker for a topic class.

`[UNRESOLVED]` The pattern is directionally present in every stratum tested but individually
significant in few `{attention.strata}`, and it **inverts inside interpretability-tagged posts**
(high 70.4% vs low 67.3%, z = +0.39). That inversion is the strongest evidence for the mediation
reading: interpretability is where open weights are, and there attention costs nothing.

`[INFERRED]` **Consequence for anyone building a replication queue**: ranking candidates by
attention selects *against* runnability. `replication/pareto.py` gates on `api` and `fits` before
weighting value, which is the correct order; this section is the measurement that justifies it.

---

## 8. Outliers

Four kinds. Univariate extremes are the least interesting; the structural ones carry the
information.

### 8.1 Univariate extremes `{outliers.karma|words|families|deps|limitations|future|contra}`

- **Karma**: 501 *How Does A Blind Model See The Earth?* (henry, 2025-08-11) — corpus max, and
  the top of the distribution is dominated by frontier-behaviour investigations:
  494 *Alignment Faking in LLMs*, 401 *A Mechanistic Explanation of Prompt Injection*,
  391 *AI Induced Psychosis*, 369 *A global workspace in language models*, 349 *Subliminal Learning*.
- **Length**: 16,951 words, *You don't need error nodes, you need better features* — 7.6× the
  median.
- **Model sweep**: 13 families, *Some models don't identify as their official name* (jordinne);
  then 12 (*models have some pretty funny attractor states*), 11 (*Claude is a Ravenclaw*).
  `[INFERRED]` **The widest model sweeps in the corpus are all behavioural-curiosity posts, not
  benchmark papers.** Breadth here is cheap prompting, not expensive evaluation.
- **Contradiction count**: maximum is **4** (*Inception in DiffusionGemma*). `[INFERRED]` Posts
  position against prior work constantly (64.1%) but never against *many* pieces at once — the
  corpus argues one-to-one, which is what makes the contested phenomena of `p3/findings.md` §1
  accumulate without resolving.

### 8.2 Structural outlier — the reproducibility hole at the top

`[MEASURED]` `{outliers.high_karma_no_code}` — highest-karma posts shipping **neither code nor
data**: 501 *How Does A Blind Model See The Earth?*, 494 *Alignment Faking in LLMs*,
336 *Emergent Misalignment*, 318 *Beware General Claims about "Generalizable Reasoning"*,
308 *Tracing the Thoughts of a Large Language Model*, 284 *Gemma Needs Help*,
278 *Estimating No-CoT Task-Completion Time Horizons*, 260 *Natural emergent misalignment from
reward hacking in production RL*.

`[MEASURED]` Three of these eight are among the corpus's most-depended-on works:
*Emergent Misalignment* = `arXiv:2502.17424`, in-degree 23; *Alignment Faking* =
`arXiv:2412.14093`, 22; *Subliminal Learning* = `arXiv:2507.14805`, 9 — all in `{deps.top25}`.

`[INFERRED]` **The field's most-cited empirical results are among its least
independently checkable.** This is §7's pattern at its extreme and is the strongest single
argument in this document for a funded replication program.

### 8.3 Structural outlier — the lone dissenters

`[MEASURED]` `{outliers.lone_dissenter}` — the *only* negative post inside a phenomenon of ≥4
posts that is otherwise entirely positive. There are **4**:

| phenomenon | n | the dissenter | karma |
|---|---:|---|---:|
| crosscoder / model diffing | 13 | *What We Learned Trying to Diff Base and Chat Models* | 106 |
| inoculation / mitigation prompting | 5 | *How hard is it to inoculate against misalignment generalization?* | 48 |
| multi-agent dynamics | 5 | *The Multi-Agent Minefield: Can LLMs Cooperate to Avoid It?* | 15 |
| steering vector transfer | 4 | *Steering Gemini with BiDPO* | 104 |

`[INFERRED]` **These are the four highest-value adjudication targets in the corpus**, and they
are a different set from `p3/findings.md` §1's contested list. §1 finds phenomena split roughly
50/50 — genuinely open questions. These are phenomena with a *consensus and one well-read
objection*; 106 and 104 karma mean the objection was read and not answered. A 12-to-1 split that
persists is either a robust finding with one flawed challenge or a literature that has stopped
listening, and one experiment each would tell you which.

### 8.4 Author outliers

- `[MEASURED]` **Neel Nanda: 52 posts, first author on 0.** Already noted in `corpus-analysis.md` O3; here
  it is the extreme of a general advisor pattern (Conmy 18/1, Rajamanoharan 23/2, StefanHex 16/1).
- `[MEASURED]` **chanind: 12 posts, first author on 11**, all on sparse autoencoders,
  spanning 2024-09 → 2026-03; **4 of the 11 are negative results about SAE methodology**
  (*A is for Absorption*, *Broken Latents*, *The "Sparsity vs Reconstruction Tradeoff" Illusion*,
  *Training Matching Pursuit SAEs*). `[INFERRED]` The nearest thing in the corpus to a sustained
  adversarial program inside one method — one person, one subfield, a third of the output negative,
  against a corpus-wide negative rate of 21.2%.
- `[MEASURED]` **Håvard Tveit Ihle: 5 posts**, all one benchmark (WeirdML) tracked over 19 months
  (2025-01 → 2026-05). `[INFERRED]` The corpus's clearest longitudinal instrument; almost nothing
  else in 728 posts is measured twice by the same person.
- `[MEASURED]` **Realmbird: 7 posts**, four titled *Latent Reasoning Sprint #1–#4*.
  `[INFERRED]` A published lab notebook — a post genre that regex-based collection would treat as
  4 papers and a reader would treat as one project.

### 8.5 Multi-axis outliers `{outliers.composite}`

Ranked by mean |percentile − 0.5| across 8 axes (karma, words, families, deps, limitations,
future work, design score, team size); corpus median 0.250 `{outliers.composite_median}`:
0.454 *Inoculation prompting* (Sam Marks), 0.437 *Claude is a Ravenclaw*, 0.422 *Analyzing how SAE
features evolve across a forward pass*, 0.422 *AI Mood Ring*, 0.413 *How Language Models
Understand Nullability*.

`[INFERRED]` Nothing in this corpus is *very* unusual — the top composite score is 0.454 against
a theoretical max of 0.5 and a median of 0.208, and the list mixes high-resource lab output with
solo curiosity posts. **The corpus has no structural aristocracy**: extremity on one axis does not
predict extremity on others. That is consistent with §6's Gini of 0.259 and is the reason
single-axis rankings (karma, in-degree) are poor selectors here — a point that generalises to any
downstream prioritisation over this dataset.

### 8.6 Tag-level outliers `{outliers.tag_negativity}`

Corpus negative rate 21.2% [18.3, 24.3]. Furthest tags (n≥10): **Introspection 40.0%
[16.8, 68.7]** (n=10), Transformers 30.8% (n=13), Sandbagging 30.0% (n=10); at the other end
Inner Alignment 7.7% (n=13), LLM Personas 9.1% (n=11), AI Safety 9.5% (n=21).

`[UNRESOLVED]` **Every one of these intervals contains the corpus rate.** At n=10–21 this axis
cannot resolve a real difference from noise; the row is included because the *absence* of a
detectable topic effect on negativity — after §3.4 found no detectable effect from any structural
variable either — is itself the finding.

---

## 9. What this corpus cannot tell you

- `[UNRESOLVED]` **Whether any of it is true.** Every claim record is one LLM's reading of one
  post's self-report. `replication/` exists to convert self-report into observation; it has 87
  specs and **0 completed runs**.
- `[UNRESOLVED]` **Causal direction on every contrast in §3.** Solo-vs-team, MATS-vs-not and
  length-vs-rigor are all observational and all admit selection explanations.
- `[UNRESOLVED]` **Whether the 2026H2 rigor jump is real** (§4) — partial period.
- `[MEASURED]` **The tag axis does not cover AF-only posts** (98 records), and §3.2 shows AF
  membership correlates with karma, code release and citation posture. Any tag-conditioned rate is
  a rate over the LessWrong-visible corpus.
- `[UNRESOLVED]` The `lw.topic` free-text field (one per LW post) remains unanalysed; it would
  need an embedding pass to be groupable and is the last unused field in `union.json`.

---

## 10. What to do with this, in priority order

1. **Adjudicate the four lone dissenters (§8.3)** — highest information per experiment in the
   whole corpus. Crosscoder/model-diffing first: 13 posts, one 106-karma objection, and the
   models involved are open (Gemma-scale), so it is 3090-feasible.
2. **Run the replication queue** (`~/prompts/3090`, then `replication/queue.md`). §8.2 says the
   most-cited results are the least checked; nothing in this document substitutes for running them.
3. **Validate the instrument** (`prompts.md` P4) before quoting any rate in §2 or §3 outside this
   repo. §3's *contrasts* are more robust than its levels: a judge bias that shifts both arms
   equally cancels in a contrast and does not cancel in a rate.
4. **Test the MATS hypothesis (§3.3)** against a matched non-MATS cohort. If methodology teaching
   really doubles seed reporting, that is a cheaper intervention than anything else measured here.
5. **Do not rank by karma** (§7, §8.5). Rank by gated feasibility × value, as
   `replication/pareto.py` does.

---

## Reproducing every number here

```
python3 analyze.py            # report to stdout + analysis_numbers.json (116 keys)
python3 analyze.py --quiet    # numbers only
```

`analyze.py` imports `p3/findings.py` for its loader, so the denominators cannot drift from
`p3/findings.md`. It reads `union.json` and `p3/claims/` and writes nothing else.
