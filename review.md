# Critical review of this repository

Reviewed 2026-08-25. Covers `corpus-analysis.md` (51 KB), `meta.py` (18 KB), `summary.md` (11 KB), the git
history, and — for every claim checked below — the three source directories and their readmes.
`meta.py` was re-run (exit 0, 21 s, 234 lines) and its output diffed against the prose. Where a
number below is new, it was computed from the shipped JSON; the script is in `review_check.py`.

**Companion file:** `prompts.md` — drop-in prompts for redoing the weak parts.

> **Status, 2026-08-25 (later the same day): P1 and P2 have been applied.** §2.2–2.9 and §2.11
> are fixed in `corpus-analysis.md`; `meta.py` now emits `numbers.json`, `build_union.py` emits
> `union.json`, and `test_numbers.py` enforces the prose↔script link. §2.4 was **reversed** after
> the user confirmed the two corpora were built by two separate sessions. §2.1 (the repo does not
> do the object-level meta-analysis it was created for) and §2.6's core (the instrument is still
> unvalidated) are **open** — they need P3 and P4. This document is kept as written, describing
> the state it reviewed; per-finding status is in §4.

---

## 0. Verdict

The work is an unusually good **data-provenance audit** of three scrapes and a **poor meta-analysis**
of the research those scrapes contain. The join (AF ∩ LW = 149) is real, the recall bound on the
LW pipeline is the single most useful number anyone has produced about these corpora, and the
evidence-tier discipline is the right idea. But the document repeatedly breaks its own rules:
several `[MEASURED]` numbers are not emitted by `meta.py`, its loudest trend claim is a
partial-period artefact its own source warned about, its headline "one pipeline" finding
over-reads evidence that is expected under independence, and its instrument is criticised for the
sources but not for itself. Eight of its twelve research specs are re-denominated copies of
the sources' specs. The repo's stated aim — "a meta-analysis of all online empirical AI Safety
work" (commit `096cac0`) — is not attempted: nothing in 51 KB says what any of the 741 posts
*found*.

Scorecard:

| Dimension | Grade | One line |
|---|---|---|
| Reproducibility of headline numbers | B+ | Core join, strata, coverage table, rigor table all reproduce. Several numbers don't. |
| Faithfulness of the tier labels | C | `[MEASURED]` applied to inferences, judgments, and numbers the script never prints. |
| Statistical care | D | Zero uncertainty intervals. Criticises sources for the same. |
| Representation of sources | B− | Mostly fair; misses that the sources already state two of its "discoveries". |
| Novelty of research specs | C | 4 of 12 new; the rest are the sources' R-lists with a new denominator. |
| Fit to stated repo goal | D | Audit of scrapes, not meta-analysis of findings. |
| Code quality of `meta.py` | B− | Correct where it prints; one bug; no machine-checkable link to the prose. |
| Handoff (`summary.md`) | B+ | Good, now stale on git state. |
| Prose for an LLM reader | C+ | Dense, well-structured, but rhetorically loaded in the way the tiers exist to prevent. |

---

## 1. What is genuinely good — keep these

1. **The join is correct and consequential.** AF's `url` contains the ForumMagnum id; 149/149 by
   id and by normalised title. This is the right first move and neither source did it.
2. **The recall bound (58.9%, decaying by period)** is a real, hard number about the LW
   pipeline that nobody else had, and the "5 of AF's top-9 are misses" observation kills the LW
   readme's "misses are short informal posts" prediction cleanly.
3. **One instrument over every stratum** (§1.3c) is the right design to separate instrument
   effects from population effects, and it does reconcile the 5.9%-vs-17% seed discrepancy.
4. **The dependency-layer observation (O5)** — reuse lives in the repos both pipelines discard
   by rule — is the best new idea in the document and directly reverses a source conclusion.
5. **The discipline of "change the script, not the prose"** and the evidence tiers, inherited
   from NNCO, are the right conventions. They are just not enforced (see §2.2).
6. **`summary.md`** is a model handoff: exact git state, exact task quote, interpretation applied,
   limitations to repeat, ordered next actions.

---

## 2. Findings, ordered by severity

### 2.1 Scope — it answers a question the repo did not ask `[most important]`

The initial commit says the repo "aims to be a meta-analysis of all online empirical AI Safety
work." The task prompt (quoted in `summary.md`) asked for analysis of the readmes *and* the
`.json`. What was delivered is a meta-analysis of the *scrapes*: overlap, recall, label hygiene,
regex prevalence. There is no extraction of what the 741 posts claim, on which models, with what
effect sizes, which claims contradict which, or which of the 376 repos anyone has re-run. The
one object-level finding mentioned (CoT obfuscation from synthetic documents, M7) is quoted from
the LW readme.

The document is aware of this and does it anyway: O10 observes that the meta-layer "has produced
zero replications" and then appends 12 more unexecuted specs, taking the count from 35 to 47.

**Fix:** `prompts.md` P3 is the object-level meta-analysis this repo was created for. It is a
fan-out job (per-post claim extraction, then synthesis), which is exactly what the user's global
CLAUDE.md says to run with subagents.

### 2.2 "Every `[MEASURED]` number is emitted by `meta.py`" is false

Checked every number in the prose against the 234-line report.

| Claim in `corpus-analysis.md` | Script | Status |
|---|---|---|
| "14 of the 359 distinct own-project repos are claimed by >1 union post, and 3 by >2" (O5, M5) | Prints **360** distinct repos; never prints 14 or 3; the list it prints under "claimed by >1 union post" is computed as `ra[k]+rl[k] > 2` over the two *per-corpus* counters, which double-counts shared posts | Numbers are **correct** (recomputed: 359 / 14 / 3) but **not emitted**, and the printed list is wrong |
| R5: "359 distinct repos (105 in AF, 320 in LW, 65 shared)" | 105 + 320 − 65 = 360 | Arithmetic in the prose is internally inconsistent; the 360→359 difference is the O2 disagreement post, which nobody says |
| "5 of AF's own top 9 posts by karma (ranks 2, 3, 7, 8, 9)" (§1.3d) | Not computed | Not verified here; plausible from the AF outlier table |
| O10 "the number executed is zero `[MEASURED]`" | Not computed; a judgment from listing directories | Mis-tiered |
| §1.3(a) "a directly measurable recall bound of 58.9% `[MEASURED]`" | 104/253 is measured; that these are *pipeline misses* rather than classifier rejections is inferred (see §2.6) | Mis-tiered |
| M3 "The real number, on the union, is: 6% report seeds strictly…" `[MEASURED]` | A regex hit-rate labelled "the real number" | Contradicts §0.1's own caveat |
| §1.3c table | Script prints a `limitations` row (AF-only 42.3 … AF-all 49.4); the prose table omits it | Row dropped — and it is a row that contradicts the surrounding claim (§2.5) |

The convention "if you disagree, change the script" only works if the prose is generated from, or
tested against, the script. Neither is true. Nothing links a number in the prose to a line in the
report; drift is undetectable by design. Fix in `prompts.md` P2: emit `numbers.json`, template the
prose from it, and add a test that greps every `[MEASURED]` figure.

### 2.3 The "AF collapses to 14" claim is a partial-period artefact its own source warned about

§1.3(e): "AF volume peaks at 80 in 2025H2 and collapses to 14 in 2026H2." M4: "AF's volume fell
80 → 14 in the same window." The coverage table footnotes 2026H2 as partial (Jul 1 → Aug 25) and
then the prose compares it to full periods anyway. The LW readme §0.3 says in so many words:
"2026H2 is a partial period. Do not read trends off its final column."

Per-30-day posting rate, from the shipped dates:

| | 2024H2 (129 d) | 2025H1 | 2025H2 | 2026H1 | 2026H2 (56 d) |
|---|---:|---:|---:|---:|---:|
| AF | 8.6 | 12.9 | 13.0 | **7.3** | **7.5** |
| LW | 19.3 | 22.4 | 23.6 | 30.8 | **47.1** |

Period lengths are measured against the declared scrape window (2024-08-25 → 2026-08-25), which
is what bounds each pipeline's opportunity to collect; full periods are 181–184 days.

There is no AF collapse in 2026H2; AF halved between 2025 and 2026H1 and is flat since. LW, on
the other hand, is accelerating — 47/month is double 2025's rate — which the document does not
mention, and which matters because it is the *other* explanation for the falling coverage ratio
(§1.3d): AF-in-LW share falls if LW admits more non-AF posts, not only if LW misses more AF posts.
The document never separates those. Everything downstream that uses "2026H2" as an endpoint
(the AF "agents = 50%" on n=14, "eval-aware 59%" on n=44) inherits this.

### 2.4 O1 ("one pipeline, not two") over-reads its evidence, and the sources already describe the pipelines

O1 offers four pieces of evidence for non-independence: byte-identical `article-content`,
identical `github-readme`, identical karma/word_count, and 148/149 repo-adjudication agreement
(κ = 1.0).

- Byte-identical body text is **expected under independence**: both are GraphQL pulls of the same
  post from the same database through the same Markdown conversion. It is not evidence of anything.
- Identical karma 17 minutes apart is expected for posts that are mostly months old.
- Identical `word_count` follows from identical text.
- κ = 1.0 on *binary has-repo* is **implied trivially** by "zero one-sided assignments"; reporting
  it to four decimals is theatre. The real evidence is the 148/149 *repo identity*, which is
  strong but is one number, not four.

Meanwhile the source readmes describe **different** construction: AF pulled all 841 window
posts and ran "12 parallel LLM classifiers" on each; LW pulled 1,706 tag-filtered posts, regex-
prefiltered to 909, and ran one LLM pass. Same scraper, same adjudication rubric, different
inclusion steps. The honest tier for "sibling outputs of one pipeline" is `[INFERRED]`, and the
document itself (summary.md §5) admits the user could settle it in one sentence. It is labelled
`[MEASURED]` and called "the single most important finding in this document."

**Resolved by the user (2026-08-25), and now fixed in `corpus-analysis.md`:** the two scrapes were built by two separate Opus sessions,
one per forum. So O1's conclusion is wrong as stated: the 148/149 repo-identity agreement is a
genuine test-retest result across two builds (same model family, similar rubrics — so "stable
under re-run by the same kind of judge", not full inter-rater reliability), and the document's
claim that AF/LW agreement is "worthless as corroboration" should be reversed, not softened.

What the identity evidence *does* prove, the document missed — see next item.

### 2.5 A finding the join proves, and the document walked past

The AF readme's schema says `karma` is "AF baseScore at scrape time." The meta-readme's own
result — AF karma == LW karma on 149/149 shared posts — is only possible if the AF scrape recorded
the **LessWrong** `baseScore`, because AF karma (`afBaseScore`) is a separate, smaller number.
Spot-check via the public GraphQL API on one shared post (`umYzsh7SGHHKsRCaA`): `baseScore` 77,
`afBaseScore` 39; both JSONs store 77.

So the AF readme's schema documentation is wrong, every "AF karma" statement in it is LW karma,
and the meta-readme had the proof in hand and used it as evidence for the wrong conclusion. This
is precisely the "cross-corpus joins are the cheapest error detector" lesson in M6 — applied to
the sources, not to itself.

### 2.6 Its own instrument gets the scepticism it applies to the sources, but only in the preamble

§1.3c frames every AF/LW discrepancy as the *sources'* instrument being loose or strict. The
uniform instrument is not validated either, and on inspection it is worse than the sources' in
at least two places:

- **`multi_model`** regex (`across (several|multiple|N) models|model families`) gives 9.1% and the
  document says AF's 18.2% is an instrument artefact. AF's definition was "test across multiple
  models **or scales**" — a different construct. A crude count of distinct model-family names in
  the body gives **54% of union posts naming ≥2 families, 31% naming ≥3**. The 9.1% is the outlier
  instrument here, not the 18.2%.
- **`seeds_loose`** matches `seeds?\b` anywhere — 433 hits, a random sample of which includes
  "seed prompt", "seed instruction", "seed scenario", "seed the judge's training data". "random
  seed(s)" alone is 3.9%. The 12–17% "loose" figure is mostly noise.
- **`sig_test`** includes `bootstrap`, which in this literature also matches "bootstrapped
  alignment", DSPy's `BootstrapFinetune`, and agent "bootstrapping process".
- **`errorbar`** includes a bare `±`, which matches hyperparameter tables and "±3 steering dose".
- **`agents`** includes `agentic`, 638 hits, many in passing ("more agentic set-ups… is not yet
  clear"). Prevalence, not topic.

And the "instruments are close everywhere *except* seeds and multi-model" sentence (§1.3c) is
selective: the script's own `limitations` row (AF 49.4 vs AF readme 43.9) was dropped from the
prose table, and LW `held-out` (15.5 vs 20) and `error bars` (17.9 vs 16) are 4-point gaps on a
16–20% base.

The document's closing defence is that R3 (LLM-judge validation) will "price" the regex. Fine —
but then M3's "the real number is" should not exist.

### 2.7 "The misses come from the tag filter" is asserted, not measured

R2 states as fact that the 104 AF-only posts are misses of "the 43-tag filter." LW's pipeline has
**three** recall gates — tag retrieval (1,706), regex prefilter `emp≥4` (909), LLM inclusion
(637) — and LW's §0.3 already says recall is bounded by two of them. Which gate lost each of the
104 is `[UNRESOLVED]` on the shipped data. It is also *cheaply resolvable*: the LW JSON ships a
`tags` list per record (180 distinct tags; every record has ≥1; mean 3.4 per post, identical in
shared and LW-only strata), and the tags of the 104 misses are one GraphQL call away. That call
was not made. The document also never uses AF's `additional_github_links` (13 non-empty) — it
mentions the field in R8 as an input and stops.

### 2.8 The "promotion as treatment" contrast picks the two rows that maximise the effect

§1.3(b) and M2 report **AF-only vs LW-only**: 61.5 vs 18.0 karma, 39.4% vs 54.3% repos. But
"AF-only" is not "promoted"; it is "promoted *and missed by LW's pipeline*," which by the
document's own §1.3(d) is a selected subset (frontier-lab, org-branded, high-karma). The
natural treatment contrast is `in_af` vs not:

| | n | median karma | own repo |
|---|---:|---:|---:|
| in AF (all 253) | 253 | 56 | 43.9% |
| not in AF | 488 | 18 | 54.3% |

The finding survives (3.1×, −10 points) — so the cherry-pick was unnecessary, and the reported
version (3.4×, −15 points) is the one a reader will quote.

### 2.9 No uncertainty, anywhere

The document scolds the forum readmes for "statistical claims: none" and reports every number as
a point. Wilson 95% intervals on the coverage series it calls "monotonic decay":

| 2024H2 | 2025H1 | 2025H2 | 2026H1 | 2026H2 |
|---|---|---|---|---|
| 76% (60–87) | 63% (52–73) | 55% (44–65) | 48% (34–62) | 50% (27–73) |

The decline from 2024H2 to 2026H1 is real; "monotonically" is false (48 → 50) and the last two
periods are indistinguishable from each other and nearly from 2025H2. Likewise "negative-result
rate 10.1% and multi-model 9.2% are identical to within a rounding error across all three
strata" is stated with n = 104 in the smallest stratum, where a ±6-point interval is the rounding
error. Both "flat" and "different" need intervals; the document uses neither.

### 2.10 O3 and O4 contradict each other

O3: NNCO captures only 34% of "Nanda's available technical words" because 52 AF/LW posts
(171,776 words) are missing. O4: Nanda is first author on **0** of those 52. NNCO is a corpus of
two people's *writing* used for stylometric/rhetorical contrasts (`we` rate, imperatives, images
per 10k words). Co-authored lab reports where he is a senior author are not his prose, and
counting all 171,776 words as his is the same error as counting a supervisor's students' theses
as the supervisor's writing. The point that NNCO should state its frame is valid; "the same
defect as Fact 1" is not — Olah's missing Distill/Circuits papers are his own first-authored work.

Also unremarked: the meta-readme's technical word counts (Nanda 89,437; Olah 49,739, from
`manifest.json`) differ from NNCO's own §Fact 2 table (81,162; 45,247, from `features.json`
after processing). A "one instrument" document should say which it is using and why they differ.

### 2.11 The research specs are mostly the sources' specs

| Meta | Source | Relationship |
|---|---|---|
| R3 | AF R4 | same idea, adds regex-vs-judge delta |
| R5 | LW R1 (+AF R1/R5) | same, union denominator |
| R7 | AF R3 | same, adds matching |
| R8 | LW R8 | same, adds dependency layer (the one real addition) |
| R9 | LW R4 | same, union + dedup |
| R10 | LW R3 | same, adds arm (d) |
| R11 | LW R6 + AF R7 | same, union |
| R12 | AF R6 | **near-verbatim** — same inputs, method, success criterion, prediction, and phrasing |

New: R1 (union artefact), R2 (independent third pipeline), R6 (NNCO completion — partly NNCO's
own R0.1), and the O2 hand-check. The document is honest about lineage in the "Gap" lines but the
headline "12 research specs" and `summary.md`'s "12 research specs (R1–R12)" are inflated.

R10 arm (d) — fine-tune on the ~133 KB of readmes "token-matched by upsampling" against millions
of tokens of organic posts — is not a sound design: at that upsampling ratio the arm measures
memorisation of five documents, not "meta-layer transfer per token." The prediction that this
document "transfers at a higher rate per token" is unfalsifiable as specified. The whole M7/R10
thread also reads as self-importance: a 30 KB audit of scrapes is not a meaningfully denser
account of monitoring than the posts it summarises.

### 2.12 Rhetoric aimed at an LLM reader

The tiers exist so that a downstream model weights claims by evidence, not by prose force. The
prose then does the opposite: "This is the single most important finding in this document"
(O1), "the most consequential difference in the whole comparison" (§1.3d), "the most transferable
finding in any of the three files" (§1.3g), "the only reading the data supports," "worthless as
corroboration," "Neither combination is the one you want." Three different things are the most
important. A model reading this will carry the superlatives, not the tiers. For a document
"written for LLM consumption" this is the specific failure mode it says it is preventing.

### 2.13 `meta.py`

- The `> 2` list bug (§2.2). Fix: count over `V`, not `ra + rl`.
- κ is computed on a variable with zero discordant cells; drop it or compute it on repo identity.
- No output contract: prints a report; nothing downstream can consume it. Emit JSON.
- No `__main__` guard, no argparse, absolute home paths, `AF`/`LW`/`NN` loaded at import.
- 21 s, almost all in the 6 × 13 regex passes over 741 bodies and the O(n²)-per-bucket dedup;
  acceptable, but pre-lowercasing bodies once would halve it.
- No test. The "warrant" cannot be checked mechanically against the prose it warrants.
- `rstrip("/")` in `repo()` is a no-op after the regex capture.

### 2.14 `summary.md`

Good, and now wrong in the one place that matters: it says HEAD is `4f01622`, unpushed; HEAD is
`c355fbe` and the branch is **2 ahead** of `origin/master`. It also records the commit trailer
model as "Claude Opus 5" — fine, but a handoff doc should not need to know that. It repeats ~40%
of `corpus-analysis.md`'s findings instead of pointing at them, and it does not record the repo's stated
aim (commit `096cac0`), which is the fact a fresh instance most needs to avoid repeating §2.1.

---

## 3. What an LLM reader actually needs and does not get

1. **A schema.** The union's fields, types, null semantics, and one example record. The AF and
   LW readmes each have one; the meta-readme has none and its R1 spec describes one in prose.
2. **The numbers as data.** A `numbers.json` keyed by the label used in the prose.
3. **Object-level content.** What the posts found (§2.1).
4. **Exact date bounds** (2024-08-28 → 2026-08-21) and period lengths, not "same window."
5. **Which readme section a claim depends on**, resolved inline, so the reader does not need
   the 35k tokens of sources to check a sentence.
6. **Confidence intervals** or at least `n` next to every rate.
7. **Fewer words.** The document is 13k tokens; the load-bearing content is ~4k.

---

## 4. Recommended actions, ordered

| # | Action | Prompt | Status |
|---|---|---|---|
| 1 | Correct the prose: partial periods (§2.3), O1 (§2.4), M3 (§2.6), "monotonically" (§2.9), R5 arithmetic (§2.2), restore the `limitations` row, add the karma-field finding (§2.5) | P1 | **done** |
| 2 | Make the warrant real: `numbers.json`, `union.json`, a prose↔script test, fix the `>2` bug | P2 | **done** |
| 3 | Ask the user how the two scrapes were built | — | **done** — two separate sessions; O1 reversed |
| 4 | Fetch tags for the 104 misses (one GraphQL query) and settle which gate lost them | P4 preamble / R2 | open |
| 5 | Do the object-level meta-analysis the repo was created for | P3 | open — **the main remaining gap** |
| 6 | Validate the instrument before quoting it again: 80 hand-labelled posts, judge–human κ | P4 | open |
| 7 | Refresh `summary.md` | P6 | **done** |

**What changed in the repo when 1–3 and 7 were applied**

| File | State |
|---|---|
| `corpus-analysis.md` | 25 marked corrections; every `[MEASURED]` figure now resolves to a key in `numbers.json` |
| `meta.py` | functions + CLI, `numbers.json` output, Wilson/bootstrap intervals everywhere, per-30-day rates, in-AF stratum, contrast ratios, karma-field check, `--show-matches`, `>2` bug fixed, κ dropped, 21 s → 6.8 s |
| `numbers.json` | 1,336 keys — new |
| `build_union.py`, `union.json`, `union.schema.md`, `project_type_map.json` | R1 executed — new; 741 records, verified to reproduce all 1,336 keys on its own |
| `test_numbers.py`, `test_allowlist.json` | new; fails on the pre-P1 `corpus-analysis.md`, passes now |
| `api_spotcheck.json` | new; the live `baseScore`/`afBaseScore` evidence for O1b |

Still do not push without reading `corpus-analysis.md` §1.3(c) and §2.2 — the instrument is corrected and
labelled but not yet validated, and P3 is what the repo actually set out to do.
