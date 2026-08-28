# What the empirical AI-safety literature actually found

**741 posts read, one structured claim record each.** This is the object-level meta-analysis the
repo was created for (commit `096cac0`) and that `readme.md` does not attempt: `readme.md` and its
three source readmes analyse *how the articles were collected*; this analyses *what they report*.

Every number here is emitted by `p3/findings.py` into `p3/findings_numbers.json`, the same
contract `meta.py` has with `readme.md`. Tiers carry the meaning defined in `readme.md`.

## 0. Provenance and its limits — read before quoting anything

`[MEASURED]` 741/741 union posts extracted, 0 schema errors, 10 STUBs (linkposts with no own
result), 738 projects after collapsing `dup_cluster_id`, **728 substantive records** analysed.
Extractor confidence: 491 high / 210 medium / 27 low.

**The instrument is an LLM reading each post against a written rubric** (`p3/EXTRACT.md`),
fanned out over 30 agents. That is a *different* instrument from `meta.py`'s regex, not a better
one by assumption. Specifically:

- `[UNRESOLVED]` **No human has validated it.** I hand-checked a stratified sample of 24 against
  the posts' own TL;DRs and agreed with `claim_type` on 24/24, but I am the same kind of judge
  that produced the labels. `prompts.md` P4 is the design that would price this properly.
- `[INFERRED]` **Design flags are judgment calls with real slack.** "Is there a baseline?" was
  rubric'd as "an explicit comparison condition," which is broader than "the post says the word
  *baseline*." §5 shows the two instruments 40 points apart on that marker; most of that gap is
  construct difference, not error.
- `[MEASURED]` A worked reminder that partial data lies: on the first ~70 records the judge's
  any-uncertainty rate looked like ~10% against the regex's 17.4%. At n=728 it is **19.4%**.
  The early reading was noise and is retracted.

---

## 1. Most well-studied questions in this field are contested

`[MEASURED]` 130 distinct phenomena; 50 have ≥3 substantive posts, covering 87.6% of the corpus.
**38 phenomena carry claims in both directions — 35 of the 50 best-studied ones (70%).**

That is the single most consequential thing in this analysis. On the topics the field has actually
worked on, it has produced positive and negative findings in roughly equal measure, and nobody has
adjudicated them. Examples, with the split:

| phenomenon | n | positive | negative/null | first authors | model families |
|---|---:|---:|---:|---:|---:|
| AI control protocols | 32 | 12 | 12 | 28 | 32 |
| activation steering | 31 | 19 | 6 | 31 | 21 |
| representation geometry | 31 | 22 | 5 | 29 | 25 |
| introspection / self-report accuracy | 29 | 17 | 8 | 26 | 23 |
| eval methodology critique | 28 | 8 | 14 | 26 | 39 |
| sparse autoencoder quality | 24 | 13 | 6 | 17 | 11 |
| circuit discovery | 23 | 16 | 5 | 22 | 19 |
| alignment faking | 22 | 13 | 3 | 20 | 21 |
| emergent misalignment | 19 | 14 | 2 | 18 | 11 |
| reward hacking | 19 | 12 | 5 | 19 | 22 |
| sandbagging | 13 | 5 | 6 | 13 | 14 |

`[INFERRED]` **AI control protocols is the clearest case**: 12 positive, 12 negative-or-null,
28 distinct first authors, across two years. Read the side-by-side in `findings.py`'s §2.2 output —
one post finds SFT on 10–100 samples "almost fully removes" an untrusted monitor's resistance,
another finds `report_scheming()` training cuts scheming 56%→6%. Both plausible; nobody has run
the design that reconciles them.

`[MEASURED]` The distinct-first-author counts matter: these are not one lab arguing with itself.
`AI control protocols` has 32 posts from 28 first authors.

---

## 2. The field almost never replicates, and constantly claims to overturn

`[MEASURED]`

- Posts whose primary contribution is a **replication: 24/728 = 3.3%** [2.2, 4.9].
- Posts that state they **contradict or qualify prior work: 467/728 = 64.1%**.

`[INFERRED]` A field where two thirds of papers position against prior work and one in thirty
checks it is generating disagreement much faster than it resolves it. §1's contested-phenomenon
count is what that looks like downstream. This is a sharper version of `readme.md` O10's point,
measured on the object layer rather than the meta layer.

`[MEASURED]` Replication share by period: 2% → 4% → 3% → 2% → 7%. The 2026H2 uptick rests on 94
posts over 56 days; do not read a trend off it.

---

## 3. Negative results are twice as common as the regex could see

`[MEASURED]` **19.9%** [17.2, 23.0] of substantive posts report a negative or null primary result.
`meta.py`'s `neg_result` regex says 10.1%.

`[INFERRED]` The regex needed a stock phrase ("negative result", "failed to replicate"). Authors
mostly just report that the thing did not work, in their own words. All three source readmes
concluded from their ~10% figures that the community is unusually tolerant of negative results;
that conclusion survives and roughly doubles in strength.

`[MEASURED]` Negative-result share is flat across strata: **18.8% in AF, 20.5% not in AF** — the
prestige stratum does not publish more or fewer negative results.

---

## 4. Rigor is rising, and that trend was invisible to the word-search

`[MEASURED]` Share of substantive posts per period:

| | 2024H2 | 2025H1 | 2025H2 | 2026H1 | 2026H2 |
|---|---:|---:|---:|---:|---:|
| reports any uncertainty on the headline effect | 7% | 12% | 17% | 24% | **37%** |
| has a baseline / comparison condition | 84% | 89% | 90% | 92% | 96% |
| tests ≥2 model families | 42% | 42% | 60% | 59% | 40% |
| n | 90 | 159 | 179 | 206 | 94 |

`[INFERRED]` Uncertainty reporting **five-timed** over the window. `meta.py`'s regex `errorbar`
rate is flat at 17–18% across the same period because it counts the presence of strings like `±`,
which does not move. This is a real trend in the field's practice that none of the four prior
documents could see, and it is the most encouraging finding here. `[UNRESOLVED]` The 2026H2 column
is 56 days of exposure; the 7%→24% rise through 2026H1 is the part that stands on full periods.

---

## 5. Judge vs regex, per marker — R3 executed as a by-product

`[MEASURED]` n=728 for the judge arm, 741 for the regex arm.

| marker | judge % | 95% CI | regex % | delta |
|---|---:|---:|---:|---:|
| baseline / comparison condition | 90.7 | [88.3, 92.6] | 50.1 | **+40.6** |
| ablation | 66.3 | [62.8, 69.7] | 22.9 | **+43.4** |
| held-out split | 34.3 | [31.0, 37.9] | 15.2 | +19.1 |
| seeds count given | 13.7 | [11.4, 16.4] | 6.3 | +7.4 |
| preregistration | 2.2 | [1.4, 3.5] | 1.6 | +0.6 |
| any uncertainty on headline | 19.4 | [16.7, 22.4] | 17.4 | +2.0 |
| ≥2 model families | 51.1 | [47.5, 54.7] | 9.2 | **+41.9** |

`[MEASURED]` **`readme.md` R3's prediction is falsified in direction.** R3 predicted the regex
would *over*-count by >2× on loose markers. Every delta is positive: the regex **under**-counts.

`[INFERRED]` Two different things are mixed in that table and they must not be reported as one
number. For `baseline` and `ablation`, the judge and the regex measure **different constructs** —
posts that *have* a comparison condition versus posts that contain the word. The 40-point gap is
mostly definitional, and neither number is "the rigor rate."

For **`multi_model` the gap is a genuine instrument miss**: 9.2% by regex, 51.1% by reading, and
53.7% by naively counting distinct model-family names (`meta.py`). Two independent methods land
within 3 points of each other and 42 points from the regex. `readme.md` §1.3(c) already flagged
this marker as construct-invalid; it is now measured. **The field tests multiple model families
about half the time, not 9% and not AF's claimed 18.2%.**

`[UNRESOLVED]` Which arm is closer to truth on `baseline`/`ablation` cannot be settled without
human labels. P4.

---

## 6. Reuse is diffuse — `readme.md` M5's substrate prediction is falsified

`[MEASURED]` From `depends_on` across 728 posts: 2,580 dependency edges over 1,811 distinct
dependencies, split into **670 repo-shaped** (807 edges) and **744 arXiv papers** (1,301 edges).

| | distinct | edges | top-20 share | top-40 share | cited exactly once |
|---|---:|---:|---:|---:|---:|
| repos | 670 | 807 | 12.4% | **18.0%** | **89.3%** |
| papers | 744 | 1,301 | 17.9% | 26.7% | 74.2% |

`readme.md` R8 predicted `[SPECULATIVE]`: *"the substrate is under 40 repos, carries the majority of
reuse edges, and has a maintainer count in the single digits."*

`[MEASURED]` **It does not.** The top 40 repos carry 18% of repo dependency edges, and 89.3% of
named repos are cited by exactly one post. There *is* a recognisable core —
`ukgovernmentbeis/control-arena` (10), `transformerlensorg/transformerlens` (10),
`jbloomaus/saelens` (9), `saprmarks/dictionary_learning` (5), `adamkarvonen/saebench` (5) — and
`readme.md` O5 is right that these are almost never adjudicated as anyone's "own project" repo.
But they are a small minority of reuse, not the majority.

`[INFERRED]` This partially **rehabilitates the LessWrong readme's "cumulative building is
near-absent"** conclusion, which `readme.md` M5 called "an artifact of measuring the wrong layer."
Measuring the right layer, the answer is: there is a real shared-tooling core, and it is thin.
The dominant pattern is still one-off dependencies.

---

## 7. Prestige buys nothing, measured by reading

`[MEASURED]` in-AF (n=253 substantive) vs not-in-AF:

| | in AF | not in AF |
|---|---:|---:|
| reports any uncertainty | 20.0% | 19.0% |
| has a baseline | 93.5% | 89.2% |
| tests ≥2 model families | 55.5% | 48.9% |
| negative/null result | 20.0% | 21.7% |
| replication | 4.1% | 2.9% |

`[INFERRED]` `readme.md` M2 asserted "no rigor gain on any of thirteen markers" from regex counts.
Reading the posts confirms it: every gap is inside its interval. Alignment Forum promotion tracks
karma and team size, not method quality.

---

## 8. The orphaned-lead queue

`[MEASURED]` **1,937 stated next steps across 592 posts (81.3%)**; 368 of those posts ship code a
successor could inherit. Raw items are in `p3/future_work.json`.

`[MEASURED]` All 6 clustering chunks returned: **1,937 leads themed, 306 distinct themes** after
cross-chunk alias merging, **131 themes proposed by ≥3 independent first authors**.
`p3/rank_leads.py` ranks by distinct first authors — `readme.md` R9's own criterion: "the same
lead proposed independently by three abandoned projects is the signal, not a duplicate."

| theme | first authors | posts | leads | posts shipping code |
|---|---:|---:|---:|---:|
| investigate underlying mechanism | 107 | 114 | 159 | 62 |
| scale to larger models | 68 | 74 | 80 | 41 |
| ablation of design choices | 61 | 62 | 75 | 40 |
| extend to new domains/tasks | 54 | 56 | 68 | 26 |
| explore alternative training methods | 47 | 48 | 55 | 35 |
| test generalization of an effect | 45 | 45 | 54 | 24 |
| test on more model families | 40 | 42 | 43 | 28 |
| make experiments more realistic | 29 | 30 | 33 | 19 |
| improve detection/monitoring methods | 28 | 28 | 34 | 15 |
| build benchmark or eval suite | 27 | 28 | 32 | 11 |
| **build more realistic model organisms** | **19** | 20 | 28 | 12 |
| detection and mitigation countermeasures | 16 | 16 | 18 | 9 |
| develop new alignment method | 15 | 15 | 16 | 8 |
| build ground-truth eval benchmark | 14 | 14 | 19 | 10 |

`[INFERRED]` **The head of the queue is a deflating result for R9 as specified, and worth stating
plainly.** `readme.md` R9 expected the queue to surface specific, inheritable research directions.
What dominates it is *routine follow-up*: understand the mechanism, scale it up, ablate it, try
another model family. **107 different first authors ended a post by saying someone should work out
why the effect happens.** That is not a research queue — it is a measurement of how much of this
literature stops at the demonstration and hands the mechanism to nobody.

`[MEASURED]` **The tractable queue is the conjunction**, not the raw 1,937: themes with ≥3
independent first authors *and* ≥3 posts shipping inheritable code. Below the generic head, these
get specific — model organisms, circuit-level analysis, SAE feature structure, ground-truth
benchmarks.

`[INFERRED]` **"Build more realistic model organisms" is the strongest specific signal in the
queue** — **19 independent first authors, 12 shipping code**, and the recurring ask is consistent:
model organisms whose quirk, backdoor or sandbagging arises from *training* rather than from a
system prompt. Several posts in §1's contested set (sandbagging 5-vs-6, alignment faking 13-vs-3)
name the artificiality of prompt-induced organisms as the reason their results may not hold. This
is a case where the field has independently identified a missing shared artifact and nobody has
built it — the closest thing here to the "field wants it, nobody did it" pattern R9 was designed
to find, and the one item on this list I would fund.

`[UNRESOLVED]` **Merge sensitivity, stated honestly.** The six agents themed independently, so
cross-chunk synonyms are merged by a hand-written alias map in `rank_leads.py` (run
`--show-unmerged` to extend it). Successive merge rounds took the theme count 540 → 487 → 306 and
single-author themes 362 → 292 → **116**, and they move the numbers materially: "build more
realistic model organisms" went from 11 first authors to 19 across the last round alone. The top
five themes held their order throughout; ranks 6–8 swapped among themselves on the final round,
because they are near-ties. **Treat every count here as a lower bound and the ordering below rank
5 as unstable.** A proper embedding-based clustering would supersede this; the alias map is an
honest stopgap, not a result.

## 9. What this changes in `readme.md`

| `readme.md` claim | Status after reading the corpus |
|---|---|
| R3 prediction: regex over-counts loose markers by >2× | **Falsified in direction** — regex under-counts every marker (§5) |
| §1.3(c): `multi_model` is construct-invalid | **Confirmed and quantified** — 9.2% vs 51.1% (§5) |
| R8 prediction: substrate <40 repos carrying most reuse | **Falsified** — top-40 carry 18%, 89% of repos cited once (§6) |
| M5: "cumulative building is near-absent" is an artifact | **Partly retracted** — the core exists but is thin (§6) |
| M2: prestige buys no rigor | **Confirmed** by a second instrument (§7) |
| Negative-result rate ~10% | **Revised to 19.9%** (§3) |
| O10: high production, near-zero conversion | **Strengthened** — 3.3% replication vs 64.1% claiming to overturn (§2) |

## 10. What to do next

1. **P4 first.** Two instruments now disagree by 40 points on `baseline`. Neither is anchored to a
   human. Until 80 hand-labelled posts exist, §5 is a comparison of two guesses.
2. **Adjudicate the contested phenomena** (§1), starting with AI control protocols (12 vs 12,
   28 first authors). This is where the field's uncertainty actually lives.
3. **Finish R9** (§8) — rerun `p3/rank_leads.py` once chunk 6 lands, and extend the theme alias
   map; then work the *code-shipping* intersection rather than the raw 1,937.
4. **Do not re-derive the phenomenon vocabulary.** `p3/phenomenon_map.json` carries a 25-entry
   merge log; adjacent-but-distinct labels were deliberately left unmerged, because collapsing
   them would manufacture agreement the data does not contain.
