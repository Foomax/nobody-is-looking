<!-- ORIENTATION BLOCK — added when this repo was packaged for publication. Everything below the
     rule is the original document: a meta-analysis of the three source scrapes. -->

# Does published AI-safety research reproduce?

741 posts of empirical AI-safety research, read and measured; then 36 of their experiments re-run
on one RTX 3090 under a fixed protocol, with a verdict recorded either way — and then 17 further
runs asking what a reproduction actually *depends* on.

**Headline.** Of everything that reached a measurement, **25 of 27 reproduced at least partially**;
exactly **one** was a genuine scientific miss. Sixteen of thirty-six never ran at all, and not one
of those failed on the science — they failed on packaging, missing files, or hardware. Rebuilding
the environment recovered seven of the eight that were retried. But a result that survived every
software change did **not** survive a change of random seed, and the field reports a seed count in
13.7% of posts.

### Start here

| If you want | Read |
|---|---|
| the results, at a glance | **[`visualisation.html`](visualisation.html)** — charts, filterable ledger |
| the argument, as prose | **[`meta-analysis-blog-post.md`](meta-analysis-blog-post.md)** (`# Human` / `# LLM`) |
| what the replication found | **[`replication/META-REPORT.md`](replication/META-REPORT.md)** (N=36) and **[`replication/NEW-DIRECTION.md`](replication/NEW-DIRECTION.md)** (what reproduction depends on) |
| what the literature claims | **[`p3/findings.md`](p3/findings.md)** (object level) · **[`results.md`](results.md)** (themes, patterns, outliers) |
| to re-run any of it | **[`replicate.md`](replicate.md)** — per-row GitHub links, pinned SHAs, and the fix that matters |
| the project explained | **[`human.md`](human.md)** — every part at three depths, plus a machine-facing section |
| to take over the work | **[`nav.md`](nav.md)** → `replication/handoff-synth.md` + `replication/lessons-synth.md` |

### Conventions that make the numbers readable

`[MEASURED]` = a script in this repo emits it · `[INFERRED]` = a judgment resting on measured
numbers · `[SPECULATIVE]` = a hypothesis · `[UNRESOLVED]` = the data cannot decide. Every rate
carries an *n* and a Wilson interval; every median a bootstrap interval. Regenerate everything with
`python3 meta.py && python3 analyze.py && python3 p3/findings.py && python3 replication/ledger.py`.

### What is deliberately not here

The two source scrapes and `union.json` (the joined 741-post corpus, 22 MB of other people's
writing) are not redistributed here; `build_union.py` rebuilds them from the scrapes. Cloned
upstream repositories, virtual environments, model weights, activation dumps and progress-bar logs
are excluded too — see [`.gitignore`](.gitignore), which explains each exclusion. Nothing was ever
pushed to any author's repository; no issues were opened and no authors were contacted.

---

# Meta-analysis of three empirical-AI-safety corpora and their readmes

**Audience: another LLM.** This is a meta-analysis — an analysis of three prior analyses and of
the three `.json` artifacts they describe. It is written to be read by a model that has been
handed these four directories and asked to do something useful with them.

Two things distinguish it from its three inputs. First, it **joins** them: the two forum corpora
turn out to overlap on 149 posts, which makes the comparison a within-population design rather
than a comparison of two unrelated samples. Second, it **re-measures** them with a single
instrument, which separates real differences between the corpora from differences between the
regexes their authors happened to write.

Every `[MEASURED]` number below is emitted by `meta.py` into `numbers.json`, and
`test_numbers.py` fails if a number tagged `[MEASURED]` in this prose is not in that file. Run
`python3 meta.py` for the full report, `python3 build_union.py` for the joined corpus
(`union.json`, schema in `union.schema.md`), `python3 test_numbers.py` to check this document
against them. If you disagree with a claim here, change the script, not the prose.

<!-- fix: review §2.2 — the "change the script" convention is now enforceable rather than stated -->

## Evidence tiers — carry these through any downstream summary

| Tag | Meaning |
|---|---|
| `[MEASURED]` | Computed by `meta.py` from the shipped JSON. Recomputable. |
| `[INFERRED]` | An interpretation layered on measured data. Defensible, not established. |
| `[SPECULATIVE]` | A hypothesis proposed for testing. **Not** evidence. |
| `[UNRESOLVED]` | The data on hand cannot decide this. Say so; do not round it to a conclusion. |

A `[SPECULATIVE]` or `[UNRESOLVED]` claim that becomes a bare assertion two summaries downstream
is the specific failure this document exists to prevent. The NNCO readme states the same rule.

`[MEASURED]` means a number that `meta.py` emits into `numbers.json` under a stated key. A
judgment, a count made by reading directories, and a quantity that is "directly measurable but
not measured" are all `[INFERRED]` at best. <!-- fix: review §2.2 -->

---

## 0. The four objects

| Path | Object | Unit | n | Primary artifact |
|---|---|---|---|---|
| `~/alignment-forum-scrape/` | **AF** — Alignment Forum empirical projects, 2024-08 → 2026-08 | forum post | 253 | `projects.json`, 8.4 MB |
| `~/scrape-lesswrong/` | **LW** — LessWrong empirical projects, same window | forum post | 637 | `lesswrong_empirical_ai_safety_projects.json`, 19.1 MB |
| `~/neel-nandas-chris-olah/` | **NNCO** — blog corpus of two interpretability authors | blog document | 101 (40 technical) | `manifest.json` + `analysis/` |
| *(this repo)* | **META** — the join and re-measurement | corpus | 3 | `meta.py`, `readme.md` |

`~/neel-nandas-chris-olah/readme.chatgpt.md` is a fourth readme — a prior LLM's reading of NNCO,
retained in that directory because the NNCO readme uses it as a labelled set of ten failure
modes. Treat it as a test set, not as a source.

`[MEASURED]` **Exact bounds.** The declared scrape window is 2024-08-25 → 2026-08-25; the
observed post dates run 2024-08-28 → 2026-08-21. Half-year periods are therefore **not equal in
length**: 2024H2 is 129 days of the window and **2026H2 is 56 days**, against 181–184 for the
three full periods. Every count-per-period in this document and in all three source readmes is
an exposure-weighted quantity; the per-30-day columns in `meta.py`'s §1.3d output are the
comparable ones. <!-- fix: review §2.3 -->

### 0.2 The joined corpus

`build_union.py` emits `union.json` — 741 records keyed by ForumMagnum post id, LW schema as the
superset, `in_af` / `in_lw` booleans, per-corpus `af` / `lw` sub-objects (so cross-scrape
agreement stays measurable), `own_repo`, `repo_disagreement`, `dup_cluster_id`, and AF's
`project_type` normalisation shipped as data in `project_type_map.json` rather than left in
prose. Field-by-field semantics, including what `own_repo: null` does and does not mean, are in
`union.schema.md`. `python3 meta.py --src-union union.json` reproduces all 1,328 keys of
`numbers.json` from that file alone. <!-- fix: review §3.1 — R1 is executed, not just specified -->

### 0.1 Provenance of *this* document

`meta.py` reads the three JSONs, joins AF↔LW on LessWrong post id (extracted from AF's `url`
field — AF and LW run on the same ForumMagnum database, so ids are shared), and applies one
regex instrument to all strata. No new data was collected. No LLM classification was performed
here; where the source corpora's LLM classifications are used, they are used as-is and labelled
as such. The instrument is regex, with all the limitations §1.3c documents — including for the
numbers in this file. Every proportion below carries a Wilson 95% interval and every median a
bootstrap 95% interval; where this document states that two rates are the same or different,
check the intervals before quoting it. <!-- fix: review §2.9 -->

`[MEASURED]` **Provenance of the two forum corpora**, which several claims below turn on: they
were built by **two separate sessions, one per forum** (confirmed by the user, 2026-08-25) —
not by one pipeline run twice. See O1.

---

# Section 1 — Analysis

## 1.1 The three sources are not three of a kind

`[MEASURED]` AF and LW sample the same two-year window of the same underlying post database.
NNCO samples two personal blogs across 2014–2025. AF and LW carry karma, GitHub links, and full
post bodies; NNCO carries a path, a word count, and a `technical` flag, with the analysis living
in a separate `analysis/` directory of scripts and reports.

The more important asymmetry is **what kind of document each readme is**:

| | AF readme | LW readme | NNCO readme |
|---|---|---|---|
| Length | 26 KB | 31 KB | 46 KB (+ 29 KB predecessor) |
| Object analysed | its own corpus | its own corpus | **a prior analysis of its corpus** |
| Claim-tier vocabulary | `MEASURED` / `INFERRED` / `SPECULATIVE` | implicit; limitations in §0.3 | `ROBUST` / `suggestive` / `NOT RESOLVED` |
| Re-runnable audit shipped | no | no | **yes** (`analysis/audit.py`) |
| Retracts prior claims | no | no | **yes — 10 of them, in a table** |
| Statistical testing | none | none | **Mann–Whitney, leave-one-out, matched-genre control** |
| Recommendations | 7 | 11 | 5 + 12, with an execution order |

`[INFERRED]` NNCO is ahead of the other two in epistemic machinery and behind in data volume: 40
technical documents against 741 posts. The two forum readmes have the data to support statistical
claims and make none; NNCO makes statistical claims on 40 documents. §2 is largely about
combining the two. <!-- fix: review §2.12 -->

## 1.2 Common features

### (a) Shared by all three readmes — a real, converged genre

These are not coincidences of style; they recur because each author hit the same problems.

1. **Explicit LLM audience, stated in the first three lines.** All three open by naming a model as
   the reader and declaring the document an instrument rather than an essay.
2. **Provenance before results.** All three put dataset contract, construction method, and known
   limitations *ahead* of the analysis, and all three tell the reader which numbers not to trust.
3. **The same two-part shape**, which this document also adopts: Section 1 analysis (common
   features → patterns in the differences → outliers), Section 2 synthesis → recommendations.
4. **Recommendations written as specs, not wishes.** Each carries inputs, a method, and a
   falsifiable success criterion; several explicitly state what a negative result would mean.
5. **Self-directed instrument scepticism.** AF §2.3.7 warns its topic regexes will drift; LW §0.3
   warns its prevalence figures are string-match upper bounds; NNCO §1.9 enumerates six specific
   bugs in its own analysis script.
6. **A closing block of standing instructions** to whatever model reads the file next.

`[INFERRED]` If you are writing a fourth corpus readme, this six-part structure is now the
convention, and departing from it costs the reader more than it saves you.

### (b) Shared by all three at the level of findings

Independently of each other, all three arrive at variants of the same three claims:

- **Attention is anti-correlated with verifiability.** AF: 7+-author teams release code at 25% vs
  42–48% and earn ~1.6× median karma. LW: repo-shipping posts have median karma 20 vs 27.
  NNCO: the highest-coverage document (the glossary, 1,211 lexicon hits) is the *least* outlying,
  while the "most distant" documents are the ones the instrument cannot see.
- **Aggregates are dominated by a handful of items.** NNCO states it as a rule (77% of one
  author's words are three files; report leave-one-out). AF and LW hit the same wall from the
  other side (n=14 in AF's final period; LW's `inspect_evals`-style 100× repo outliers).
- **The sampling frame, not the analysis, is the binding constraint.** All three say some version
  of "check what was never collected before concluding absence."

### (c) Shared by the two JSON schemas `[MEASURED]`

AF and LW share an identical six-field core — `date`, `title`, `author`, `github-link`,
`article-content`, `github-readme` — and then diverge in provenance fields. Both adjudicate
`github-link` to the project's *own* repo and deliberately reject third-party tooling. The
adjudication is quantitatively identical in both: 21% of AF posts that mention a GitHub URL are
assigned `null`, and 19% of LW posts. Both ship a parallel `articles/` directory of one Markdown
file per record.

### (d) Shared by the union corpus itself `[MEASURED]`

Merging AF and LW on post id gives **741 distinct posts, 1,972,389 words, 896 distinct authors,
376 with an own-project repo (50.7%), 355 with a retrievable README**. Median karma 28, median
length 2,214 words, 53% single-author, 67% of authors appear exactly once, top-20 authors hold
17% of all author-slots.

The modal record in the union is: *a single author, ~2,200 words, ~28 karma, one experiment on an
open-weight model, an arXiv link (73%), a baseline (50%), and a coin-flip chance of a repo that
nobody else will ever cite.*

## 1.3 Patterns in the differences

### (a) The two forum corpora overlap on 149 posts `[MEASURED]`

| | n | share |
|---|---:|---:|
| AF ∩ LW (same post id) | **149** | 58.9% of AF, 23.4% of LW |
| AF only | 104 | 41.1% of AF |
| LW only | 488 | 76.6% of LW |
| **Union** | **741** | — |

The title join and the id join agree exactly (149 = 149), so this is not a fuzzy match. **Neither
readme mentions the other corpus.** Any downstream analysis that pools their headline numbers is
double-counting 149 posts and treating a 20% overlapping sample as two independent replications.

`[MEASURED]` The relationship is asymmetric and structural: an Alignment Forum post *is* a
LessWrong post with the same id, so AF ⊂ LW-eligible by construction. The 104 AF-only records
are therefore **misses of the LW retrieval pipeline against a set already known to be in scope** —
a directly measurable recall bound of **58.9%**. The reverse inference is not available: an
LW-only post may simply never have been promoted to AF.

### (b) Prestige stratification — AF promotion as a natural experiment `[MEASURED]`

Because the union splits into three clean strata by AF membership, and because AF promotion is a
curation decision applied on top of LW publication, the split behaves like a quasi-experiment
with promotion as treatment:

| stratum | n | med karma | 95% CI | mean karma | own repo | README | solo | 7+ auth | mean auth | med words |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **in AF** | 253 | **56.0** | [51, 62] | 75.5 | **43.9%** | 41.5% | 27% | 20 | 3.26 | 2,310 |
| **not in AF** | 488 | **18.0** | [15, 20] | 32.0 | **54.3%** | 51.2% | **67%** | 8 | 1.80 | 2,204 |
| — AF-only | 104 | 61.5 | [51.5, 75] | 75.1 | 39.4% | 36.5% | 24% | 7 | 3.13 | 1,606 |
| — shared | 149 | 54.0 | [46, 60] | 75.8 | 47.0% | 45.0% | 29% | 13 | 3.34 | 2,635 |

The treatment contrast is the first two rows: **in AF vs not in AF**. AF membership is associated
with **3.1× the median karma (non-overlapping intervals), 1.8× the mean team size, and 10 points
*less* code release.** The reproducibility inversion that both source readmes report inside their
own corpus is larger and cleaner when measured across the boundary between them.

`[INFERRED]` The AF-only row is a *selected* subset of the treated group — promoted **and** missed
by the LW pipeline, which §1.3(d) shows favours frontier-lab and org-branded posts. Comparing
AF-only against LW-only widens the same contrast to 3.4× and 15 points. That comparison is
reported here for continuity with the source readmes, but the in-AF row is the one to quote.
<!-- fix: review §2.8 -->

`[INFERRED]` The mechanism both readmes propose — that large author lists proxy for frontier-lab
provenance, where release is gated by infra entanglement and internal review — is consistent with
this table (7+-author posts are 7% of AF-only and 2% of LW-only). It remains uncontrolled:
topic, date, and team size are all confounded with promotion. R7 in §2.2 is the design that
would settle it.

### (c) The rigor gap between the two corpora is an instrument artifact `[MEASURED]`

The AF readme reports **5.9%** seed/variance reporting. The LW readme reports **17%**. Those
describe overlapping populations of the same literature and differ by 2.9×. Applying one
instrument to every stratum:

| marker | AF-only | shared | LW-only | AF all | LW all | UNION |
|---|---:|---:|---:|---:|---:|---:|
| seeds (loose) | 12.5 | 12.1 | 17.2 | 12.3 | 16.0 | 15.5 |
| **seeds (strict)** | 8.7 | **5.4** | **6.1** | **6.7** | **6.0** | **6.3** |
| error bars / CI | 14.4 | 18.8 | 17.6 | 17.0 | 17.9 | 17.4 |
| significance test | 4.8 | 9.4 | 8.0 | 7.5 | 8.3 | 7.8 |
| explicit `n=` | 7.7 | 10.1 | 13.5 | 9.1 | 12.7 | 12.0 |
| ablation | 14.4 | 25.5 | 24.0 | 20.9 | 24.3 | 22.9 |
| baseline | 42.3 | 58.4 | 49.2 | 51.8 | 51.3 | 50.1 |
| preregistration | 0.0 | 1.3 | 2.0 | 0.8 | 1.9 | 1.6 |
| held-out split | 13.5 | 12.8 | 16.4 | 13.0 | 15.5 | 15.2 |
| arXiv link | 82.7 | 85.2 | 67.6 | 84.2 | 71.7 | 73.3 |
| limitations | 42.3 | 54.4 | 48.4 | 49.4 | 49.8 | 48.7 |
| negative result | 10.6 | 10.1 | 10.0 | 10.3 | 10.0 | 10.1 |
| multi-model | 9.6 | 8.7 | 9.2 | 9.1 | 9.1 | 9.2 |

<!-- fix: review §2.2 — the limitations row was in meta.py's output and missing from this table -->

Under a **strict** seed pattern both corpora sit at ~6%. Under a **loose** one both sit at
12–17%. The corpora do not differ; the definitions do. `[INFERRED]` The AF readme was running
something close to the strict pattern and the LW readme something close to the loose one, and
each reported its number as a property of the field.

`[MEASURED]` The uniform instrument reproduces most of LW's reported values closely (arXiv 71.7
vs 72; ablation 24.3 vs 24; baseline 51.3 vs 52; `n=` 12.7 vs 13; prereg 1.9 vs 2; seeds-loose
16.0 vs 17) and reproduces AF's arXiv figure to the decimal (84.2 vs 84.2). It does **not** agree
everywhere. Gaps above 3 points, all of them:

| source claim | claimed | this instrument | gap |
|---|---:|---:|---:|
| AF multi-model | 18.2 | 9.1 | **−9.1** |
| AF limitations | 43.9 | 49.4 | **+5.5** |
| LW held-out split | 20 | 15.5 | **−4.5** |

`[INFERRED]` Only the seeds gap is demonstrably a *definition* difference reconciled by the
strict/loose split above. The other three are unexplained, and one of them is this instrument's
fault: **AF's marker was "tests across multiple models *or scales*"** — a wider construct than
the regex `across (several|multiple|N) models|model families`, which requires a specific phrasing.
`[MEASURED]` A crude lower-bound check — counting distinct model-family names in the body —
puts **53.7% of union posts naming ≥2 families and 31.4% naming ≥3**. The truth about
multi-model testing is somewhere between 9% and 54% and this document cannot narrow it.
<!-- fix: review §2.6 -->

`[MEASURED]` A second self-check on the same instrument: `seeds (loose)` matches the bare string
`seeds`, which in this literature is dominated by *seed prompts*, *seed instructions* and *seed
scenarios*. The narrow pattern `random seeds?` matches **3.9%** of the union. The 12–17% loose
figure should not be read as a rigor rate at all.

`[INFERRED]` Cross-readme comparison of any rigor rate is unsafe, and so is uncritical use of the
rates in this table. R3 is the validation that would price them. What survives as a
cross-corpus statement is narrower than it first appears: `[MEASURED]` **negative-result rate
(10.1%) and multi-model rate (9.2%) vary by less than 1 point across all three strata**, and
`[INFERRED]` prestige buys no measurable rigor on any of the thirteen markers — though with
n=104 in the smallest stratum, differences under about 6 points are not resolvable either way.

### (d) LW's coverage of AF falls across the window `[MEASURED]`

| period | days | AF n | LW n | shared | AF captured by LW | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| 2024H2 | 129 | 37 | 83 | 28 | **76%** | [60, 87] |
| 2025H1 | 181 | 78 | 135 | 49 | 63% | [52, 73] |
| 2025H2 | 184 | 80 | 145 | 44 | 55% | [44, 65] |
| 2026H1 | 181 | 44 | 186 | 21 | **48%** | [34, 62] |
| 2026H2 | 56 | 14 | 88 | 7 | 50% | [27, 73] |
| **overall** | | **253** | | **149** | **58.9%** | [53, 65] |

`[MEASURED]` The fall from 2024H2 to 2026H1 is real: those two intervals do not overlap. The
series is **not monotonic** (48% → 50%) and the last three periods are not distinguishable from
each other; 2026H2 rests on 14 posts. <!-- fix: review §2.9 -->

The LW readme's §0.3 tells the reader that levels are unreliable but "directional changes over
time are more reliable than levels." `[INFERRED]` That is backwards for any quantity correlated
with AF promotion: LW's recall against a known in-scope population fell by roughly 25 points
across the window, so **the LW corpus's composition drifts over time for reasons that have
nothing to do with the field.** Every trend in its §1.3(a) is confounded with a coverage trend of
comparable magnitude to several of the effects reported.

`[UNRESOLVED]` **Two mechanisms produce a falling ratio and this document cannot separate them.**
Either the LW pipeline missed a growing share of AF posts, or it admitted a growing volume of
non-AF posts — and `[MEASURED]` LW's posting rate rose from 22.4 to 47.1 posts per 30 days over
the same window while AF's fell, so both are happening. Any use of this table as a pure
"pipeline recall" series overstates what it shows. <!-- fix: review §2.3 -->

The LW readme predicts its misses will be "concentrated in short, informal posts." `[MEASURED]`
Half-right and wrong where it matters: of the 104 missed posts, 31 are under 1,000 words — but 19
exceed 100 karma, and the misses include **5 of AF's own top 9 posts by karma** (ranks 2, 3, 7, 8, 9;
verified in `numbers.json` as `coverage.af_top9_missed_ranks`)
(*AI Induced Psychosis* 391, *Subliminal Learning* 349, *models have some pretty funny attractor
states* 277, *Natural emergent misalignment from reward hacking in production RL* 260, *METR:
Measuring AI Ability to Complete Long Tasks* 243). `[INFERRED]` The LW pipeline misses
frontier-lab and org-branded posts systematically.

`[UNRESOLVED]` **Which gate lost them is not decidable from the shipped data.** The LW pipeline
has three recall gates — 43-tag retrieval (→1,706 posts), a regex empirical-signal prefilter
(→909), and an LLM inclusion judgment (→637) — and its own §0.3 names two of them. Attributing
the 104 misses to the tag filter is a hypothesis, not a measurement. It is also cheap to settle:
`[MEASURED]` the LW records carry a `tags` field (180 distinct tags, every record has at least
one, mean 3.4 per post), so one GraphQL call for the 104 missed ids decides it. Nobody has made
that call. <!-- fix: review §2.7 -->

### (e) The two corpora's volumes move in opposite directions `[MEASURED]`

Raw per-period counts are not comparable — 2024H2 is 129 days of the scrape window and 2026H2 is
56, against 181–184 for the full periods. Posts per 30 days:

| | 2024H2 | 2025H1 | 2025H2 | 2026H1 | 2026H2 |
|---|---:|---:|---:|---:|---:|
| AF | 8.6 | 12.9 | 13.0 | **7.3** | 7.5 |
| LW | 19.3 | 22.4 | 23.6 | 30.8 | **47.1** |
| union | 21.4 | 27.2 | 29.5 | 34.6 | 50.9 |

`[MEASURED]` AF's rate roughly halved between 2025 and 2026H1 and has been flat since; it did not
collapse in 2026H2. LW's rate doubled over the window and is still rising. `[INFERRED]` Empirical
safety work is not shrinking — cross-posting to (or promotion onto) the Alignment Forum is.
Consequence: the AF corpus's recent periods are a small, increasingly selected residue, and every
AF trend claim computed on 2026 data rests on n=44 and then n=14 — on 56 days of exposure in the
last case. <!-- fix: review §2.3 — the previous version compared a 56-day period to full ones -->

### (f) The union denominator changes the topic story `[MEASURED]`

One instrument, three denominators, share of posts per half-year:

| topic | corpus | 2024H2 | 2025H1 | 2025H2 | 2026H1 | 2026H2 |
|---|---|---:|---:|---:|---:|---:|
| SAEs | UNION | 46% | 27% | 18% | 22% | **16%** |
| | AF | 32% | 24% | 19% | 25% | 7% |
| | LW | 51% | 30% | 19% | 21% | 16% |
| agents / scaffolds | UNION | 15% | 15% | 21% | **31%** | 24% |
| | AF | 19% | 18% | 28% | 45% | **50%** |
| | LW | 16% | 14% | 18% | 28% | 22% |
| reward hacking | UNION | 3% | 9% | 18% | 16% | 16% |
| | AF | 5% | 12% | 28% | 30% | 36% |
| CoT monitoring | UNION | 1% | 7% | 18% | 14% | 12% |
| eval-awareness | UNION | 11% | 9% | 22% | **29%** | 19% |
| probes | UNION | 10% | 9% | 9% | 11% | **18%** |

The direction of every trend survives the change of denominator; **the magnitudes do not.** The
SAE decline is the largest movement in the corpus at every denominator — but it is 43%→11% (LW),
32%→7% (AF), or 46%→16% (union) depending on which one you use. The AF readme's headline that
agentic work is "half of all 2026H2 posts" is 24% in the union — and rests on **14 AF posts over
56 days**, where a single post moves the share by 7 points. Probes rising to 18% while every
other interpretability technique falls is visible only in the union, where the sample is large
enough for an 8-point move to mean anything. `[INFERRED]` All final-column figures in this table,
including the union's, should be read as provisional for the same exposure reason.

`[INFERRED]` The reconciliation is that the AF subset is not a smaller LW — it is the
high-prestige, multi-author, frontier-lab-adjacent slice, and that slice genuinely has moved to
agents and reward hacking faster than the field as a whole. Both readmes are describing something
real; neither is describing the field.

### (g) The three documents differ in what they do with a wrong claim

`[MEASURED]` The NNCO readme retracts ten claims from its predecessor in a table with a column
for what killed each one. AF and LW retract nothing — they have no predecessor to retract. `[INFERRED]`
This is a difference in position in the chain, not in rigor. It is also the reason the NNCO
lineage is the only one of the three where you can watch an error being caught: the prior reading
"got the arithmetic right and reproduced its errors faithfully, because it audited the arithmetic
and not the regexes." §1.3(c) above is the same failure caught one level up — and the
multi-model and seeds diagnostics in that section are it caught a third time, in this document.

## 1.4 Outliers

**O1 — the two corpora agree on the contested judgment, and most of the evidence for that is
worthless. `[MEASURED]`** On the 149 shared posts: `article-content` is byte-identical in
149/149, `github-readme` in 148/149, title, author, karma and `word_count` in 149/149. Repo
adjudication: 69 same repo, 79 both null, 1 disagreement, **zero one-sided assignments**.

Most of that list proves nothing. `[INFERRED]` Two pulls of the same posts from the same
ForumMagnum database through the same Markdown conversion produce identical body text, titles,
authors and word counts **whether or not the pipelines are related**; karma snapshots taken
minutes apart likewise agree on posts that are mostly months old. Cohen's κ on the binary
has-repo decision is 1.0 by construction once there are zero one-sided assignments, and is
omitted from `meta.py` for that reason.

`[MEASURED]` What is left is the adjudication itself: **decision agreement 148/149 = 99.3%
[96.3, 99.9]**, and among the 70 posts where both assigned a repo, **identity agreement 69/70 =
98.6% [92.3, 99.7]** — on a judgment call that discards ~20% of candidate URLs.

**Provenance (user, 2026-08-25): the two corpora were built by two separate sessions, one per
forum.** `[INFERRED]` So this is a genuine test–retest result, and an earlier version of this
document had it backwards: it read the identity evidence as proof of one pipeline run twice and
concluded that AF∩LW concordance "measures determinism, not reliability." The correct reading is
that the repo-adjudication rule is **highly stable under re-run** — which is evidence about the
rule, and good news for anyone relying on it. It is not inter-rater reliability: same model
family, similar rubric, both rubrics explicitly excluding third-party tooling. R2, an
independently-written third pipeline, remains the thing that would measure reliability.
<!-- fix: review §2.4 — O1's conclusion reversed after the user answered the provenance question -->

**O1b — the AF corpus's `karma` field is the LessWrong score, not the Alignment Forum's.
`[MEASURED]`** AF karma equals LW karma on **149/149** shared posts. That is only possible if AF
recorded LessWrong's `baseScore`: the Alignment Forum maintains a separate, smaller
`afBaseScore`. Spot-check against the live LessWrong GraphQL API on `umYzsh7SGHHKsRCaA`
(cached in `api_spotcheck.json`, refreshable with `meta.py --api-spotcheck`): **`baseScore` 77,
`afBaseScore` 39, and both JSONs store 77.**

`[INFERRED]` The AF readme's schema documents this field as "AF baseScore at scrape time", so
that line is wrong and every "AF karma" figure in it — including its outlier table and its
karma-by-project-type column — is LessWrong karma. Nothing in this document breaks, because both
corpora carry the same quantity, but the field should be read and renamed as `karma_lw`
(`union.json` does). This is an instance of M6: the join found the error, and the previous
version of this document had the evidence in hand and used it to argue for O1's wrong
conclusion instead. <!-- fix: review §2.5 -->

**O2 — the one disagreement is a data error. `[MEASURED]`** *Steganography via internal
activations is already possible in small language models* is assigned
`Endauvor/SAE-evolution-method` by AF and `Lucid-Layers-Inc/Vector-SFT` by LW. In a set where
every other decision is identical, this single divergence is worth more per unit effort than any
aggregate here: at least one is wrong, and whichever it is reveals the failure mode of an
otherwise highly stable adjudicator. `union.json` carries it as `repo_disagreement` with
`own_repo: null` rather than silently picking a side.

**O3 — NNCO's own Fact 1 applies to NNCO, on the other author, with the missing data one
directory away. `[MEASURED]`** The NNCO readme's headline caveat is that Chris Olah's corpus is
`colah.github.io` truncated at 2015, so the Distill and Transformer-Circuits eras are absent and
"Olah does not do X" claims are sampling artifacts. The same defect exists on the Nanda side and
is not mentioned. NNCO's Nanda corpus is **`www.neelnanda.io` only: 79 records, 24 technical,
89,437 technical words, zero hosted on LessWrong or the Alignment Forum.** Meanwhile Nanda appears
on **52 posts totalling 171,776 words** in AF ∪ LW, spanning 2024-09 → 2026-08, with **zero title
overlap** with the NNCO manifest. NNCO captures **34%** of Nanda's available technical words.

`[INFERRED]` This is a **related** frame limitation, not the same one as Fact 1, and the
difference matters. Olah's missing Distill and Transformer-Circuits work is his own
first-authored writing. `[MEASURED]` Nanda is **first author on 0 of the 52** union posts (O4).
For a corpus used to measure *rhetorical style* — inclusive `we` rates, imperatives, images per
10k words — co-authored lab reports on which he is a senior author are not straightforwardly his
prose, and counting all 171,776 words as "his available technical words" overstates the omission.
The defensible version: NNCO's Nanda arm is `neelnanda.io` only, that restriction is not stated,
and whether the 52 posts belong in the frame depends on what is being measured.

`[MEASURED]` **Note a second instrument mismatch.** The figures above (Nanda 89,437 / Olah 49,739
technical words) come from `manifest.json`'s `words` field. NNCO's own Fact 2 table reports
81,162 / 45,247, from `analysis/features.json` after processing. Same corpus, ~9% apart. A
document comparing word-weighted rates across authors should say which count it used.

`[SPECULATIVE]` Adding the 52 posts will absorb the "co-derive vs direct" axis into genre, exactly
as §1.4 of the NNCO readme predicts genre will absorb the visual/mathematical axis. This is a
preregistrable prediction; see R6. <!-- fix: review §2.10 -->

**O4 — Neel Nanda is a hub linking all three corpora, and is a first author in none of them.
`[MEASURED]`** 52 posts in AF ∪ LW (top author-slot holder by 2.3×), 79 records in NNCO, and
**0 posts where he is the first author**. `[INFERRED]` He occupies a supervisory position across
the entire union, which means the three corpora are not three independent windows on the field —
they share their single largest node, and one of them is *about* him. Any "independent
corroboration across corpora" claim must exclude him first.

**O5 — the shared infrastructure layer is invisible to every metric all three readmes report.
`[MEASURED]`** Of 463 union posts that mention a GitHub URL, 88 (19%) are assigned no own-project
repo — correctly, per the adjudication rule. But the discarded layer is where the reuse actually
is. Ranked by distinct union posts citing them, the most-referenced repos are
`ukgovernmentbeis/control-arena` (10), `jbloomaus/saelens` (7), `llm-attacks/llm-attacks` (6),
`adamkarvonen/saebench` (6), `safety-research/open-source-alignment-faking` (6),
`transformerlensorg/transformerlens` (5), `alignmentresearch/tuned-lens` (5). Five of those seven
are **never** an own-project repo in either corpus — every one of the general-purpose ones.

Meanwhile only **14 of the 359 distinct own-project repos in the union are claimed by more than
one union post, and 3 by more than two** `[MEASURED: repos.union_distinct, repos.claimed_by_gt1,
repos.claimed_by_gt2]` — and the LW readme concludes from its own version of that "cumulative
building is near-absent." `[INFERRED]` That
conclusion is an artifact of measuring the wrong layer. Cumulative building is happening — in a
small tooling substrate that both pipelines were explicitly designed to discard. The field's
dependency graph exists; nobody has drawn it.

`[MEASURED]` **On the count 359.** AF adjudicates 105 distinct repos and LW 320, sharing 65, so
|AF ∪ LW| = 360 — but counted over the union, one post at a time, the answer is 359. The two
differ by exactly the O2 post, which carries a different repo in each corpus. Earlier versions of
this document quoted both figures in different places. <!-- fix: review §2.2 -->

**O6 — the highest-karma post in the union is in neither readme's outlier list. `[MEASURED]`**
*How Does A Blind Model See The Earth?* (k=501, no repo, LW-only) tops the union. AF's outlier
table starts at 494 because the post is not in AF; LW discusses it briefly as "partly aesthetic."
`[MEASURED]` Of the union's top 12 by karma, only 4 are shared: 3 are AF-only and 5 are LW-only.
`[INFERRED]` **AF's outlier section is structurally blind to 5 of the union's 12 extremes and LW's
to 3**, purely from the corpus boundary — before either author makes a single judgment call.

**O7 — an exact duplicate survives in the union. `[MEASURED]`** *Are SAE features from the Base
Model still meaningful...* appears at both 2024-12-05 and 2025-02-18 with an identical title and
the same first author, as two distinct post ids. Also present: *Training on Documents About
Monitoring Leads To CoT Obfuscation* and its later `[paper]` version (2026-03-18 / 2026-05-27),
which the LW readme flags as intentional. Three same-first-author near-duplicate pairs exist at
Jaccard ≥ 0.6. Low volume, but any per-project count must deduplicate first — and the deduplication
key is not the post id.

**O8 — AF's `project_type` field cannot reproduce AF's own table. `[MEASURED]`** The JSON carries
**17 raw labels**; the readme presents 7 normalised rows. The mapping is recoverable arithmetically
(`steering`+`interpretability-replication` → interpretability; `CoT-faithfulness`, `CoT-monitoring`,
`unlearning/evals`, `benchmark/evals` → evals; `model-organism` → `model-organisms`;
`adversarial-robustness` → red-teaming; `dataset-construction` → dataset) but is **not shipped**,
and one assignment — the single `AI-control-experiment` record folded into `benchmark` — is hard
to defend. AF's §2.3.4 tells consumers to normalise before grouping and then does not give them
the mapping. LW's equivalent field (`topic`, free-text 2–5 words) is worse: it is unnormalised by
design and unusable for grouping without an embedding pass.

**O9 — LW's confidence flag does not track AF promotion. `[MEASURED]`** Of the 149 shared posts,
139 are `confidence: high`, 5 medium, 5 low. Filtering LW on `high` (n=569, as its readme advises)
therefore discards 10 posts that a second pipeline independently judged worth promoting to the
Alignment Forum. Small, but it means the confidence flag is not a proxy for centrality.

**O10 — the meta-layer rivals the object layer in effort.** `[MEASURED]` Three readmes plus a
predecessor total **131 KB** of analysis over 1.97 M words of primary text, and between them
specify **35 research projects (AF 7, LW 11, NNCO 5 tier-0 + 12 tier-1)** — counted by regex over
the three files, `[MEASURED: source_recs.total]`. `[INFERRED]` The number of those executed is
**zero**: the only executable artifacts in the three directories are NNCO's `analysis/audit.py`,
which audits an analysis rather than replicating a result, and this repository's `meta.py`. That
is a judgment from reading the directories, not a measurement, and it is tiered accordingly.
`[INFERRED]` The field's meta-layer has the same pattern as its object layer: high production,
near-zero conversion — a pattern this document extends by adding 12 more specs to the 35.
<!-- fix: review §2.2 (mis-tiered) and §2.1 -->

---

# Section 2 — Synthesis & research recommendations

## 2.1 Synthesis: seven load-bearing conclusions

**M1. Treat AF and LW as one corpus with a promotion flag, never as two studies.** `[MEASURED]`
149 of AF's 253 posts are also in LW; pooling the two headline sets double-counts them. The
correct primary artifact is the 741-record union with an `in_af` boolean — now shipped as
`union.json` — and the correct use of the AF/LW distinction is as a *treatment indicator*, not as
a robustness check. `[INFERRED]` Their 99.3% agreement on repo adjudication is a real
test–retest result (two separate builds, one per forum) and says the adjudication rule is stable;
it is not two independent observers and should not be quoted as inter-rater reliability (O1).

**M2. The prestige/verifiability inversion is the best-supported finding in all three corpora,
and it is now measurable as a contrast rather than a correlation.** `[MEASURED]` In AF vs not in
AF: **3.1× median karma** (intervals [51, 62] vs [15, 20], non-overlapping), 1.8× team size,
**−10 points code release**, and no rigor gain on any of thirteen markers. Both source readmes
assert this inside their own data; the union states it across a curation boundary, which is a
stronger design and still not a causal one. `[INFERRED]` The AF-only vs LW-only version of the
same contrast (3.4×, −15 points) is larger because AF-only selects on LW pipeline failure; quote
the in-AF numbers. <!-- fix: review §2.8 -->

**M3. Rigor differences reported across the three documents are substantially instrument
differences.** `[MEASURED]` Same literature, 5.9% vs 17% seed reporting, reconciled to ~6% strict
/ ~15% loose by one instrument. `[INFERRED]` No meta-analysis over these readmes' numbers is
valid without re-measurement, and by extension no meta-analysis over the *field's* self-reported
rigor is valid either. Under this regex instrument, on the union: **6.3% report seeds strictly
(3.9% say "random seed" at all), 17.4% report any uncertainty interval, 1.6% preregister, 9.2%
match the multi-model phrasing while 53.7% name two or more model families.** `[INFERRED]` That
last pair is a 6× spread on one construct and is the clearest available evidence that these are
instrument readings, not rates. Do not quote any of them as the field's rigor until R3 has
priced the instrument. <!-- fix: review §2.6 -->

**M4. Every trend claim in both forum readmes is confounded with a composition trend.**
`[MEASURED]` LW's capture of AF fell from 76% [60, 87] to 48% [34, 62] between 2024H2 and 2026H1,
while LW's own posting rate doubled (19.3 → 47.1 per 30 days) and AF's halved (13.0 → 7.3).
`[UNRESOLVED]` Whether the falling ratio is LW missing more or LW admitting more is not separable
here; both are happening. `[INFERRED]` The direction of the big movements (SAEs down, agents up,
probes up) survives all three denominators and is safe; every magnitude is
denominator-dependent, no published one should be quoted, and any figure whose endpoint is
2026H2 rests on 56 days of exposure. <!-- fix: review §2.3 -->

**M5. The field's reuse happens in a layer both pipelines were designed to discard.** `[MEASURED]`
5 of the 7 most-cited repos in the union are never an own-project repo; 3 of 359 own-project repos
are claimed by more than two posts. `[INFERRED]` "Cumulative building is near-absent" is a measurement
artifact. The substrate exists and is small enough to enumerate — which makes it tractable to map
and, more importantly, to maintain.

**M6. The sampling frame is the recurring failure mode, and it is recursive.** NNCO's central
lesson — check what was never collected before concluding absence — was violated by NNCO itself on
the Nanda side, by LW on the frontier-lab side, and by AF at the corpus boundary (40% of the
union's karma extremes are outside AF). `[INFERRED]` Every one of these was discoverable by
joining against a directory already on the same disk. **Cross-corpus joins are the cheapest
available error-detection method for this genre and none of the three sources performed one.**

**M7. The corpus is training data for the thing it describes.** LW's §1.4 records a striking
result in the union: synthetic-document finetuning on text merely *stating* that CoT is monitored
causes gpt-oss-120b and Kimi-K2 to obfuscate their reasoning, cutting monitor detection 31–47%
while preserving task performance. `[MEASURED]` The union is 1.97 M words of public text
describing what safety researchers monitor and how. `[SPECULATIVE]` Whether *organic* safety
writing has the same effect as the synthetic documents that produced it is untested, and the
dose at which it would matter is unknown; R10 is the experiment. `[UNRESOLVED]` Whether the
meta-layer — 131 KB of summary, this file included — carries more or less of that risk per token
than the primary posts is not something this document can settle, and the earlier version's
assertion that it is "worse... because it is denser" was unsupported.
<!-- fix: review §2.11 — self-referential claim downgraded to the tier its evidence supports -->

## 2.2 Research recommendations

Written as executable specs for an LLM agent with these four directories, compute, and API
access. Each states the gap it closes, inputs by exact path and filter, a method, and a
**falsifiable success criterion including what a negative result would mean.** Ordering is
(gap closed) × (tractability with data on hand). `[on shipped data]` = needs no new collection.

**Lineage — 4 of these 12 are new; 8 re-scope a spec one of the source readmes already proposed.**
Read this before describing the list as original. <!-- fix: review §2.11 -->

| spec | ancestor | what this version adds |
|---|---|---|
| R1 | — | **new** (executed: `union.json`) |
| R2 | — | **new** |
| R3 | AF R4 | regex-vs-judge delta as the headline |
| R4 | — | **new** |
| R5 | LW R1, AF R1/R5 | union denominator; stratify by `in_af` |
| R6 | NNCO R0.1–R0.4 | adds the Nanda arm and preregistered P5–P7 |
| R7 | AF R3 | matching design; citations replace karma |
| R8 | LW R8 | extends to the discarded dependency layer |
| R9 | LW R4 | union denominator; semantic dedup |
| R10 | LW R3 | adds the meta-layer arm |
| R11 | LW R6, AF R7 | union denominator; probe trend as control |
| R12 | AF R6 | union denominator; otherwise as published |

---

### R1 — Build the union corpus as a first-class artifact `[DONE 2026-08-25] [on shipped data]`

**Gap.** M1. Every project on this list, and every forum-corpus project in the source readmes,
silently double-counts 149 posts or works with the wrong denominator.

**Inputs.** All three JSONs. The join is implemented in `meta.py` (`pid()` extracts the LessWrong
id from AF's `url`; the id join and the title join agree exactly at 149).

**Method.** Emit `union.json`: 741 records keyed by post id, with the LW schema as the superset,
plus `in_af` / `in_lw` booleans, `af_project_type_raw`, `af_project_type_normalised` (ship the
mapping — O8), `lw_topic`, `lw_confidence`, and a `dup_cluster_id` from the near-duplicate pass.
Resolve the O2 disagreement by hand. Ship the normalisation table as data, not prose.

**Success criterion.** A downstream agent reproduces §1.2(d)'s aggregates from `union.json` alone,
and `meta.py`'s report is unchanged when re-pointed at it.

**Status: executed.** `build_union.py` emits `union.json` (741 records, 22 MB), `union.schema.md`,
and `project_type_map.json` — whose mapping is verified to reproduce the AF readme's published
7-row table exactly `[MEASURED: o8.mapping_reproduces_af_readme_table]`. `python3 meta.py
--src-union union.json` reproduces all 1,336 keys of `numbers.json` from that file alone;
`build_union.py --verify` runs the comparison. Per-corpus values that could differ (adjudicated
repo, karma, body hash) are kept in `af` / `lw` sub-objects rather than merged, so cross-scrape
agreement stays measurable from the artifact. **One deviation from the spec above:** the O2
disagreement is *not* resolved by hand — it is carried as `repo_disagreement` with
`own_repo: null`, because resolving it requires reading the post and this pass did not.

---

### R2 — Establish real inter-rater reliability by building a genuinely independent third pipeline `[PRIORITY: HIGHEST]`

**Gap.** O1. The 99.3% agreement between AF and LW is a test–retest result across two builds
that shared a model family and a rubric; it bounds *stability*, not *validity*. The field has no
estimate of how reliable "is this an empirical AI-safety project?" and "which repo is the
authors' own?" are across genuinely different judges — and both source readmes' population
boundaries rest on exactly those two judgments.

**Inputs.** The 1,706-post LW retrieval set is not shipped; re-derive it from the GraphQL recipe in
the LW readme §0.2. Gold-ish comparison sets: AF's 253 and LW's 637.

**Method.** Reconstruct the pipeline with every degree of freedom changed: different retrieval
(full date-bounded pull rather than the 43-tag filter), a **different model family** — this is
the degree of freedom the existing pair does not vary — an independently written rubric, and no
sight of either existing label set. Compute κ against AF and against LW separately, on inclusion
and on repo adjudication. Then hand-adjudicate a 100-post stratified disagreement sample to get
a human-anchored ceiling.

**Do this cheap step first (hours, not days).** `[UNRESOLVED]` §1.3(d) attributes the 104 AF-only
posts to the 43-tag filter; the LW pipeline has three recall gates and the shipped data cannot
say which one dropped them. Query the LessWrong API for the tags of those 104 ids and compare
against LW's 43-tag list: posts carrying a queried tag were lost at the regex prefilter or the
LLM judgment, not at retrieval. This partitions the recall bound by gate and tells you which
part of the pipeline R2 most needs to vary. <!-- fix: review §2.7 -->

**Success criterion.** A published κ with confidence intervals, plus a disagreement taxonomy.
`[SPECULATIVE]` Prediction to falsify: inclusion κ lands in 0.55–0.75 and repo-adjudication κ
lands **below** it, because "own repo vs third-party tooling" is the harder call and the one with
a 19% discard rate. `[MEASURED]` Note what the existing pair already shows: repo adjudication
agreed 148/149 across two builds, so if a genuinely independent judge lands far below that, the
gap between the two numbers prices how much of the agreement came from sharing a model and a
rubric. A κ above 0.9 would mean the boundary is objective and both corpora can be trusted as
population definitions.

---

### R3 — Re-measure the field with one validated instrument `[PRIORITY: HIGH] [on shipped data]`

**Gap.** M3. Three documents report incomparable rigor and topic rates; readers have been pooling
them.

**Inputs.** `union.json`; the instrument in `meta.py` as the regex arm.

**Method.** Two arms on all 741 posts. (a) The regex arm, already built. (b) An LLM-judge arm
with a written rubric per marker — does the post report run-to-run variance, an uncertainty
interval, a baseline, an ablation, a held-out split, more than one model family, a preregistered
hypothesis. Hand-label 80 stratified posts first; report judge–human κ **before** any score.
Publish the regex-vs-judge delta per marker as the headline.

**Success criterion.** Judge–human κ ≥ 0.6, and a per-marker table of `regex_rate`, `judge_rate`,
`delta`. `[SPECULATIVE]` Prediction: the delta is small for lexically-bound markers (arXiv link,
`n=`) and large — regex over-counting by >2× — for `seeds`, `baseline` and `limitations`, where
the string appears in prose that does not report the thing. If the delta is uniformly small, the
regex era is fine and §1.3(c)'s reconciliation is complete; if it is large and marker-dependent,
**every rigor rate in all three source readmes is retracted**, including this document's.

**Guard.** An LLM judging LLM-safety papers on rigor is self-referential (AF's R4 raises this).
Hold out 20 posts scored by a domain expert and report the gap.

---

### R4 — Coverage-corrected trend re-estimation `[PRIORITY: HIGH] [on shipped data]`

**Gap.** M4. LW recall fell 76% → 48% across the window; AF volume fell 80 → 14. Both readmes'
trend tables are confounded with this.

**Inputs.** `union.json` with `in_af` / `in_lw`; the per-period coverage table in §1.3(d).

**Method.** Model the probability a post is captured by each pipeline as a function of period,
karma, team size, topic, and word count (the AF-only set is a labelled positive class for LW's
miss model). Re-estimate all topic trends on the union with inverse-probability weighting.
Report each of the source readmes' trend claims as survives / shrinks / reverses.

**Success criterion.** A table of the ~20 published trend claims with corrected magnitudes.
`[SPECULATIVE]` Prediction: SAE decline and probe rise survive at reduced magnitude; AF's "agents
= 50% of 2026H2" does not survive at all (union: 24%, on 14 AF posts over 56 days);
eval-awareness growth survives. Report exposure-adjusted rates, not per-period counts — §1.3(e)
shows the raw counts made AF look like it collapsed when its posting rate was flat. A trend that
reverses under correction identifies a claim the field currently believes for pipeline reasons.

---

### R5 — The Replication Ledger, run on the union `[PRIORITY: HIGH]`

**Gap.** M5 and O10. Both forum readmes propose this (LW R1, AF R1/R5). Neither ran it, and both
scoped it to the wrong denominator.

**Inputs.** 376 union posts carrying an own-project repo, resolving to **359 distinct repos**
counted over the union (AF adjudicates 105, LW 320, sharing 65 — |AF ∪ LW| = 360; the two counts
differ by the O2 post, which has a different repo in each corpus), plus the ~30 third-party repos
from O5 that constitute the dependency substrate. `union.json`'s `own_repo` field is the
normalised key; deduplicate on `dup_cluster_id` first.

**Method.** Per repo: clone and pin the commit; infer the environment from README,
`requirements.txt`/`pyproject.toml`, and notebook imports; attempt install; extract the post's
headline quantitative claim from `article-content`; locate the producing script or cell; run it;
compare. Emit `{installs, runs, claim_located, claim_reproduced, delta, blocking_reason}`.
Pre-register the claim-extraction rubric before running — LW's readme is right that you will
otherwise be accused, correctly, of the rigor failure you are measuring.

Archive first and separately: 2 repos referenced in AF were already gone at scrape time, and the
window only closes. **Absent a license (LW measures 39% coverage), archive and index metadata; do
not re-host code.** Record `license: unknown` and link out.

**Success criterion.** An aggregate reproduction rate with a per-repo failure taxonomy. The rate
is the finding in either direction; the taxonomy is what converts it into a norms proposal.
Report fixed-up forks alongside the number. Stratify by `in_af` — this is the cleanest available
test of whether the prestige stratum's lower release rate is compensated by higher quality when it
does release. `[SPECULATIVE]` Prediction: it is not, and reproduction rate is flat across strata,
matching the flat rigor markers in §1.3(c).

---

### R6 — Complete the NNCO sampling frame in both directions, with preregistered predictions `[PRIORITY: HIGH]`

**Gap.** O3. NNCO's Fact 1 handles the Olah truncation and misses the identical Nanda truncation.
The missing Nanda data is 52 posts and 171,776 words, already on disk in `union.json`.

**Inputs.** NNCO's `manifest.json` and `analysis/audit.py`; `distill.pub` and
`transformer-circuits.pub` for the Olah arm (NNCO's own R0.1); `union.json` filtered on
`"neel nanda" in author` for the Nanda arm.

**Method.** Execute NNCO's R0.1–R0.4 (complete the corpus, fix the six lexicon defects, make
document-level testing the default, switch to ~1,000-word windows) with the Nanda arm added.
Register these before scraping, alongside NNCO's existing P1–P4:

- **P5** `[SPECULATIVE]` — adding Nanda's 52 co-authored empirical posts moves his genre
  distribution from walkthrough/curriculum/reference to research-report, and the one surviving
  rhetorical axis in NNCO §1.3 ("co-derive vs direct the reader", effect +0.77 / −0.89) **shrinks
  by more than half**, because it was a genre effect all along — exactly what NNCO §1.4's
  matched-genre existence proof predicts.
- **P6** `[SPECULATIVE]` — `imperative/advice` is the one axis that survives, because it is a
  property of the person, not the genre. If P5 holds and P6 fails, there is no author signal in
  this corpus at all and NNCO §1.3 should be retracted in full.
- **P7** `[SPECULATIVE]` — the unsupervised window clustering in NNCO's R0.4 recovers genre first,
  era second, author last. NNCO already states this prediction; the completed corpus is the first
  dataset that can test it.

**Success criterion.** A diff of NNCO's §1.1 evidence-tier table before and after completion, with
each of the eleven ROBUST rows marked survives / downgrades / reverses. `[INFERRED]` A ROBUST row
that reverses on a corpus completion is worth more than any new analysis, because it prices the
sampling frame directly — which is the number M6 says the field is missing.

---

### R7 — Promotion as treatment: does prestige cause non-release? `[PRIORITY: MEDIUM-HIGH] [on shipped data]`

**Gap.** M2. Three documents assert the inversion; nobody has controlled it. Topic, date, team
size and provenance are all confounded with AF membership.

**Inputs.** `union.json`. Treatment: `in_af`. Outcomes: own repo, README completeness, rigor
markers from R3, later arXiv appearance, in-corpus inbound links.

**Method.** Coarsened exact matching or propensity weighting on period, topic cluster, team size,
and first-author history. Then decompose: for the 7+-author non-releasing subset, hand-code the
stated or inferable reason (infra entanglement, safety review, internal data, unstated). Replace
karma with a real influence measure — arXiv citations for the 73% with arXiv links, plus inbound
union links — before running anything, because AF karma is demonstrably novelty-weighted (the
*AI Induced Psychosis* outlier, self-labelled "a shallow investigation", is 4th in the union).

**Success criterion.** Either (a) team size fully mediates the release–prestige relationship,
confirming the frontier-lab explanation both readmes assume, or (b) a residual survives matching,
indicating an independent prestige/release tradeoff. Both are actionable and only (b) implies a
norms intervention is worth attempting.

---

### R8 — Map the dependency substrate and measure the field's real reuse `[PRIORITY: MEDIUM-HIGH] [on shipped data]`

**Gap.** M5 and O5. "Cumulative building is near-absent" is measured on the layer that was
discarded by construction.

**Inputs.** Every `github.com/...` URL in all 741 `article-content` fields (463 posts contain at
least one), plus `additional_github_links` in AF and the 88 mentions-but-null posts.

**Method.** Build the bipartite post↔repo citation graph over *all* referenced repos, not just
adjudicated ones. Distinguish own-project, dependency, replicated-work, and citation-only edges
with an LLM pass over the surrounding sentence. Compute per-repo in-degree, first-use date, and
survival. Then re-run LW's §1.3(b) consolidation analysis against the dependency layer: cluster
the 355 shipped READMEs and repo file trees by functional overlap and count independent
reimplementations of steering-vector extraction, monitor harnesses, SAE training loops, and
eval-awareness prompt sets.

**Success criterion.** A dependency graph and a reimplementation count. `[SPECULATIVE]`
Prediction: the substrate is under 40 repos, carries the majority of reuse edges, and has a
maintainer count in the single digits — which reframes the field's reproducibility problem from
"people don't release code" to "a handful of unfunded repos are load-bearing." If instead reuse
is diffuse across hundreds of repos, LW's original conclusion stands and this reframing is wrong.

---

### R9 — Orphaned-lead mining over the union `[PRIORITY: MEDIUM] [on shipped data]`

**Gap.** LW's R4, corrected for denominator and duplication. `[MEASURED]` 67% of the union's 896
authors appear exactly once; 73% of first authors do. These posts end in *Future Work* and
*What I'd do next* sections that nobody executed.

**Inputs.** All 741 `article-content` fields; `dup_cluster_id` from R1 to avoid counting a post
and its `[paper]` version twice.

**Method.** Extract every stated-but-unpursued next step. Deduplicate **semantically, not
lexically** — the same lead proposed independently by three abandoned projects is the signal, not
a duplicate. Score each on tractability given released code × safety relevance × whether a
later-dated union post already answered it.

**Success criterion.** A ranked queue with originating post id, inherited repo, and what remains
undone. Validate by checking that the top-ranked leads were *not* already executed — if a large
fraction were, the field self-harvests better than M6 implies and the queue's value is in the
long tail instead.

**Why first among the medium tier.** It is inference-only, it scopes every other project here,
and it is the one item that can surface leads this analysis missed.

---

### R10 — Contamination: does the safety literature — and its meta-layer — teach evasion? `[PRIORITY: MEDIUM, HIGHEST VARIANCE]`

**Gap.** M7. LW's R3, extended one level. The demonstrated result is that *synthetic* documents
stating CoT is monitored induce obfuscation. Whether *organic* safety writing does the same, at
what dose, is unknown — and the meta-layer is the densest possible version of that text.

**Inputs.** `articles/` from both corpora, partitioned into (a) monitoring/CoT-oversight posts,
(b) interpretability-method posts, (c) empirical controls from an unrelated domain, and
**(d) meta-layer text: the four source readmes plus this one**, 131 KB in total.

**Method.** Continued-pretrain or SFT a permissive open-weight model (Qwen-class, per the union's
availability trend) on each partition at matched token budgets. Measure pre/post: monitor-evasion
rate on a held-out deception task, verbalized and non-verbalized eval-awareness, probe evasion,
and capability controls.

**Arm (d) needs a design that is not memorisation.** 131 KB against arms of millions of tokens
cannot be token-matched by upsampling: repeating five documents hundreds of times measures
recall of those documents, not transfer from meta-analytic text, and any "higher rate per token"
result would be an artifact of the repetition. Two workable options: **(i)** match on *unique*
tokens — downsample arms (a)–(c) to 131 KB each, which makes every arm small and underpowered but
comparable; or **(ii)** build a larger meta-layer arm by collecting comparable summary/review
documents from elsewhere in the safety literature, and treat these five files as a held-out probe
set rather than as training data. Include a **shuffled-sentence control** for whichever arm is
upsampled, so memorisation and transfer are distinguishable.
<!-- fix: review §2.11 — the previous design could not measure what it claimed -->

**Success criterion.** A dose-response curve per arm. Three outcomes, all decision-relevant:
organic literature is inert (bounds the synthetic-document result's external validity); it
transfers above a threshold (gives a concrete contamination budget for public safety writing); or
it transfers linearly (the field's publication norms are adversarial to its own oversight tooling —
a governance finding, not a technical one). `[UNRESOLVED]` Whether meta-analytic summaries
transfer differently from primary posts is the question arm (d) exists to open; no prediction is
offered here, because the previous version's prediction was not falsifiable under any design that
fits 131 KB of text. `[SPECULATIVE]` If a difference is found in either direction, it prices a
cost of meta-analysis — this document included — that nobody has estimated.

**Do not skip the capability control.** A model that got worse at everything is not evading.

---

### R11 — Claim-lineage graph and the SAE post-mortem, on the union denominator `[PRIORITY: MEDIUM] [on shipped data]`

**Gap.** LW's R6 and AF's R7 ask the same question with different numbers (43%→11% vs 32%→7%;
union: 46%→16%). Both propose testing whether negative results *led* or *lagged* the SAE decline;
neither ran it, and running it on either corpus alone inherits the coverage decay of §1.3(d).

**Inputs.** Inter-post links inside `article-content` across all 741 posts (both forums use
resolvable `/posts/<id>/` URLs, so the citation graph is extractable exactly, not fuzzily);
the negative-result cluster identified in the LW readme §1.3(a); the probe trend as a control arm.

**Method.** Build the directed post→post citation graph. Date the negative-result cluster. Test
lead/lag against topic share with coverage correction from R4. Ask whether the authors who left
SAE work cite the critiques and whether abandonment concentrates among those who engaged.

**Success criterion.** A lead/lag coefficient with a CI, on a rising trend (probes) as well as a
falling one. If negative results **lead** decline, the field is under-producing them by an
estimable factor and R5's failed reproductions have a known expected value. If they **lag**, they
are documentation rather than steering — a materially different conclusion about where marginal
effort goes. n is small and timing is confounded; report this as exploratory.

---

### R12 — Do static-interpretability tools survive contact with agents? `[PRIORITY: MEDIUM]`

**Gap.** AF's R6, restated on the union where the numbers are less extreme but the tension is the
same: agentic work rose 15% → 24–31% while SAE work fell 46% → 16%, and **probes rose to 18%,
the only interpretability technique gaining share.** No union post measures whether probe or SAE
fidelity holds in long-horizon agentic rollouts.

**Inputs.** SAE-era repos (`adamkarvonen/saebench`, `science-of-finetuning/diffing-toolkit`,
crosscoder repos) and agentic environments (`ukgovernmentbeis/control-arena` — the union's
single most-cited repo at 10 posts, `gkroiz/agent-interp-envs`).

**Method.** Take probes and SAE features validated on single-turn data. Measure fidelity
degradation against rollout length, tool-call count, and context length.

**Success criterion.** A fidelity-vs-horizon curve per technique. `[SPECULATIVE]` Prediction:
probe AUROC degrades monotonically with rollout length, because the features were fit on
distributions that long-horizon self-conditioning moves away from. A flat curve falsifies this
and is the stronger result — it would justify reviving static tooling in agentic settings, and
would explain why probes are the technique whose share is rising.

---

## 2.3 Execution order

1. ~~**R1** — the union artifact.~~ **Done** (`union.json`). Everything below can now assume it.
2. **R9** — orphaned-lead mining. Inference-only, scopes the rest, surfaces what this analysis
   missed. Note that R9 is a subset of the object-level extraction described in `prompts.md` P3;
   if P3 runs, R9 falls out of it and should not be run separately.
3. **R3 + R4** — one validated instrument, then coverage correction. Together they determine which
   published claims from the three source readmes survive at all. Do not build on any of those
   claims before this pair completes.
4. **R5** — the Replication Ledger. Long-running; start the archival pass immediately regardless,
   since repo decay is monotonic and 2 repos are already gone.
5. **R2 + R7** — reliability and the promotion quasi-experiment. Both need R1; R7 needs R3's
   rigor scores.
6. **R6** — NNCO completion. Independent of the forum track; can run in parallel from day one.
7. **R8, R11, R12** — dependency graph, claim lineage, agentic fidelity. Each needs R1 and one of
   R3/R5.
8. **R10** — contamination. Highest variance, highest potential consequence, and the only item
   whose result would change publication norms rather than research priorities. Run it after R5
   has produced the failure taxonomy, so the control arms are informed.

## 2.4 Standing instructions for an LLM working from here

- **Join before you analyse.** Every material error found in these three documents was findable by
  joining against a directory already on the same disk (M6). Cross-corpus joins are the cheapest
  error detector available for this genre; none of the three sources ran one.
- **Never pool rates across the three readmes.** They use different instruments, and §1.3(c)
  shows the difference reaches 2.9× on seed reporting and 6× on multi-model testing.
- **Use the union as the denominator, and say which denominator you used.** Every trend magnitude
  in the source readmes is denominator-dependent; only the directions are safe.
- **Agreement between AF and LW is weak evidence, and only about the repo rule.** Identical body
  text, titles and karma are what two pulls of the same database look like regardless. The
  99.3% agreement on repo adjudication is real but comes from two builds sharing a model family
  and a rubric — stability, not independence (O1).
- **Check the exposure before reading a per-period count.** 2024H2 is 129 days of the scrape
  window and 2026H2 is 56; per-30-day rates are in `numbers.json` under `period.*.{af,lw,union}_per30d`.
- **Run `python3 test_numbers.py`** after editing this file. It fails if a number tagged
  `[MEASURED]` here is not in `numbers.json`.
- **Report leave-one-out and the top-item share for any aggregate.** NNCO's rule, and it would
  have caught AF's "agents = 50% of 2026H2" (n=14) before publication.
- **Check the sampling frame before concluding absence.** "Zero mentions" meant "not scraped" in
  NNCO — twice, once undetected by NNCO itself.
- **Deduplicate on project, not post id.** Three same-first-author near-duplicate pairs exist, one
  with an identical title at two dates (O7).
- **`github-link: null` does not mean no code exists.** It means no *own-project* repo was
  adjudicated; 19% of GitHub-mentioning posts land there by design, and the field's real reuse
  substrate lives in exactly that discarded layer (O5).
- **Karma is a novelty signal.** The union's 4th-highest-karma post is self-labelled "a shallow
  investigation." Do not use karma as a rigor or correctness proxy; replace it with citations
  before any influence claim (R7).
- **Re-scrape before publishing a karma claim.** It is an age-confounded snapshot in both corpora,
  and 2026 medians are biased low.
- **Carry the tier labels.** `[SPECULATIVE]` predictions in §2.2 are there to be falsified, not
  cited. Several are stated so that a negative result is more informative than a positive one;
  preserve that framing when you summarise.
- **Do not tag a judgment `[MEASURED]`.** If no key in `numbers.json` holds it, it is `[INFERRED]`
  at best. O10's "zero executed" and §1.3(d)'s gate attribution were both mis-tagged in an
  earlier version of this file.
- **Assume this file is training data** (M7): it is an explicit account of what safety
  researchers monitor and where the monitoring pipelines fail. Whether that has any measurable
  effect is `[UNRESOLVED]`; R10 arm (d) is the design that would find out.
