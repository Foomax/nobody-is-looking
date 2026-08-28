# Prompts for doing this better

Companion to `review.md`. Each prompt is self-contained and copy-pasteable. P0 is a preamble to
prepend to any of the others. Paths assume the four directories are where `meta.py` expects them.

Contents:

- **P0** — Ground rules block (prepend to everything)
- **P1** — Correction pass on the existing `readme.md`
- **P2** — Make the warrant real: `union.json`, `numbers.json`, and a prose↔script test
- **P3** — The object-level meta-analysis the repo was created for (subagent fan-out)
- **P4** — Instrument validation: LLM judge vs regex
- **P5** — Adversarial review of any LLM-written analysis document
- **P6** — Handoff document
- **P7** — Style contract for documents written for LLM readers

---

## P0 — Ground rules (prepend)

```
You are working in ~/alignment-literature-meta-analysis. Source corpora (read-only):
  ~/alignment-forum-scrape/projects.json                 (AF, 253 posts)
  ~/scrape-lesswrong/lesswrong_empirical_ai_safety_projects.json  (LW, 637 posts)
  ~/neel-nandas-chris-olah/manifest.json                 (NNCO, 101 docs)
AF ∩ LW = 149 posts, joined on the ForumMagnum post id (regex /posts/([A-Za-z0-9]+)/ over AF's
`url`; LW's `_id`). Union = 741. Date range 2024-08-28 → 2026-08-21. 2024H2 (125 days) and
2026H2 (56 days) are PARTIAL periods.

Rules that override anything else in this prompt:

1. Evidence tiers. Every quantitative or causal sentence carries exactly one tag:
   [MEASURED]   — a number a script in this repo emits, by name, into numbers.json.
   [INFERRED]   — an interpretation of measured numbers. Say what would falsify it.
   [SPECULATIVE]— a hypothesis. Never cited as evidence downstream.
   [UNRESOLVED] — the shipped data cannot decide it. Say what data would.
   A number that no script emits is not [MEASURED]. A judgment ("zero were executed") is not
   [MEASURED]. "Directly measurable" is not the same as measured.

2. Every rate gets its n and a 95% interval (Wilson for proportions) or, for medians, a
   bootstrap interval. If two rates' intervals overlap, do not call them different. If n < 30,
   do not call them the same either — say [UNRESOLVED].

3. Never compare a partial period to a full one. Report per-30-day rates or drop the period.

4. Never compare a statistic across corpora or documents unless the same code computed both.
   If you are comparing your number to a source readme's number, quote the source's
   operational definition next to yours.

5. Apply every criticism you make of a source's instrument to your own instrument, in the same
   section, before publishing the comparison. Show 8 random matches for every regex you report
   a prevalence for.

6. No superlatives, no "the single most important", no "the only reading the data supports",
   no rhetorical questions. State the claim, the evidence, the tier, the n. The reader is a
   model; it will weight your adjectives. Do not give it any.

7. Before concluding X is absent from a corpus, check the sampling frame and any sibling
   corpus on disk. Before concluding two datasets share provenance, ask what the identity
   evidence would look like under independence (two API pulls of the same post ARE identical).

8. Prose is generated from, or tested against, the script. If you write a number by hand, you
   also write the assertion that checks it.

9. Do not modify anything in the three source directories.

10. When a task fans out over independent items (per-post, per-repo, per-author), use
    subagents in parallel and synthesise; do not loop serially in one context.
```

---

## P1 — Correction pass on `readme.md`

```
<P0>

Task: edit readme.md in place to fix the defects listed in review.md §2. Do not restructure;
do not add sections; do not add new findings except the one in item 6. Keep the tier tags. For
each edit, leave a one-line HTML comment <!-- fix: review §2.x --> at the point of change so the
diff is reviewable.

1. §1.3(e) and M4: remove "collapses to 14" and "80 → 14". Replace with per-30-day rates:
   AF 12.9 / 13.0 / 7.3 / 7.5 (2025H1, 2025H2, 2026H1, 2026H2) and LW 22.4 / 23.6 / 30.8 / 47.1.
   State that AF halved between 2025 and 2026H1 and is flat since, and that LW's rate doubled.
   Add the consequence: falling AF-in-LW coverage has two candidate causes (LW misses more AF;
   LW admits more non-AF) and the document does not separate them — tag [UNRESOLVED].
2. §1.3(d): replace "monotonically" with the Wilson intervals from review.md §2.9. Say the
   2026H1 and 2026H2 estimates are indistinguishable.
3. O1 and M1: re-tier "sibling outputs of one pipeline" to [INFERRED]. Delete the byte-identical
   text, karma, and word_count evidence as evidence of provenance (they are expected under
   independence — say so). Keep the 148/149 repo-identity agreement as the actual evidence.
   Delete the binary-has-repo κ; it is implied by "zero one-sided". Add: the AF readme describes
   12 parallel LLM classifiers over all 841 window posts; the LW readme describes a 43-tag pull,
   a regex prefilter to 909, and one LLM pass — the inclusion pipelines are documented as
   different even if the scraper and adjudication rubric were shared. Add the user's answer
   (2026-08-25): the two scrapes were built by two separate Opus sessions, one per forum.
   Therefore reverse O1's conclusion: the 148/149 repo-identity agreement is a real
   same-model test-retest result, not determinism; call it "stable under re-run by a similar
   judge", not inter-rater reliability (same model family, similar rubric). Update M1 and the
   "Agreement between AF and LW is not evidence" bullet in §2.4 accordingly. R2 (a genuinely
   independent third pipeline) still stands, with its motivation reworded.
4. §1.3(c): restore the `limitations` row (42.3 / 54.4 / 48.4 / 49.4 / 49.8 / 48.7). Rewrite the
   "instruments are close everywhere except…" sentence to list every marker whose gap to the
   source figure exceeds 3 points (limitations, held-out, multi-model, seeds). For multi-model,
   quote AF's definition ("multiple models or scales") and state that the uniform regex measures
   a narrower construct; report the crude ≥2-model-family rate (54%) as a bound in the other
   direction.
5. M3: delete "The real number, on the union, is". Replace with "Under this regex instrument,
   on the union:" and keep the figures.
6. New finding, place after O1 as O1b [MEASURED]: AF's `karma` equals LW `baseScore` on 149/149
   shared posts; the AF readme's schema says "AF baseScore". GraphQL spot-check on
   umYzsh7SGHHKsRCaA: baseScore 77, afBaseScore 39, both JSONs store 77. Conclusion: the AF
   readme's field documentation is wrong; all AF karma figures are LW karma. Note this is an
   example of M6 (joins find errors) that the prior version of this document missed.
7. O5, M5, R5: make the numbers consistent — 359 distinct own-project repos in the union
   (360 = |AF repos ∪ LW repos| because the O2 post has a different repo in each corpus; say
   this). Keep 14 and 3 only once meta.py prints them (P2).
8. §1.3(b), M2: report the in_af-vs-not contrast (n 253 / 488, median karma 56 / 18, own repo
   43.9% / 54.3%) as the primary treatment contrast. Keep AF-only vs LW-only as a secondary row
   and say why it is more selected.
9. R2: re-tier "which is where the 104 misses come from" to [UNRESOLVED]; list LW's three
   recall gates; note LW's `tags` field exists on every record and the tags of the 104 misses
   are one GraphQL query away.
10. O3: add that Nanda is first author on 0 of the 52 posts (from O4) and that for a
    stylometric corpus co-authored reports are not the author's prose; downgrade "the same
    defect as Fact 1" to "a related frame limitation". Note the word-count discrepancy with
    NNCO Fact 2 (89,437 vs 81,162; 49,739 vs 45,247) and which file each comes from.
11. §2.2 header: add a lineage table mapping R1–R12 to source-readme recommendations
    (review.md §2.11). Rewrite "12 research specs" in the intro and in summary.md as
    "12 specs, 4 new, 8 re-scoped from the sources".
12. R10 arm (d): either delete it or replace "token-matched by upsampling" with a design that
    controls for memorisation (e.g., match on unique tokens, include a shuffled-sentence
    control arm). Delete the "transfers at a higher rate per token" prediction unless the design
    can falsify it.
13. Global: remove every superlative and "most important/consequential/transferable".
    Remove "worthless as corroboration" and "the only reading the data supports".
14. §0: add exact date bounds and period lengths. Add a 12-line schema block for the union
    record (field, type, null semantics, source corpus).

Then run `python3 meta.py > /dev/null` to confirm it still executes, and produce a diff summary.
Do not commit.
```

---

## P2 — Make the warrant real

```
<P0>

Task: turn meta.py from a printer into a warrant. Three deliverables, no changes to the source
directories.

A. `meta.py` refactor
   - Wrap in functions; `if __name__ == "__main__"`; `--src DIR` override; keep the current
     text report as `--report`.
   - Add `--json numbers.json`: a flat dict of every number the text report prints, keyed by a
     stable snake_case name (e.g. "join.shared": 149, "strata.af_only.median_karma": 61.5,
     "coverage.2026H1.pct": 48, "coverage.2026H1.ci": [34, 62], "own_repos.distinct": 359,
     "own_repos.claimed_by_gt1": 14, "own_repos.claimed_by_gt2": 3). Wilson intervals on every
     proportion; bootstrap (1000 resamples, seed 0) on every median.
   - Fix: the "repos claimed by >1 union post" list currently sums two per-corpus counters
     (`ra[k]+rl[k] > 2`), double-counting shared posts. Count over the union `V`.
   - Remove the binary has-repo κ (zero discordant cells → trivially 1). Replace with the
     repo-identity agreement count and its interval.
   - Add per-30-day post rates per period per corpus, with period lengths in days.
   - Add the in_af-vs-not stratum.
   - Add the AF-karma-equals-LW-baseScore check (identity count on shared posts).
   - For every regex in RIGOR and TOPIC, add `--show-matches K` that prints K random
     50-char contexts per pattern, so the instrument can be eyeballed.
   - Lowercase and cache bodies once; target < 8 s.

B. `union.json`
   741 records keyed by post id. LW schema as superset. Fields: all LW fields; `in_af`, `in_lw`
   booleans; `af_project_type_raw`; `af_project_type_norm` using the mapping in readme.md O8
   (shipped also as `project_type_map.json`); `af_additional_github_links`; `lw_topic`;
   `lw_confidence`; `lw_tags`; `dup_cluster_id` from the same-first-author Jaccard≥0.6 pass;
   `karma_lw` (renamed from `karma`, with a `_comment` field stating that AF's `karma` is LW
   baseScore); `own_repo` normalised owner/name lowercase; `repo_disagreement` for the O2 post
   with both candidates. Emit `union.schema.md`: field, type, null semantics, source.
   Success: `meta.py --src-union union.json` reproduces numbers.json exactly.

C. `test_numbers.py`
   Parse readme.md; extract every number adjacent to a `[MEASURED]` tag in the same paragraph
   or table row; assert each appears in numbers.json (exact for integers, ±0.05 for one-decimal
   percentages). Print the numbers it could not find. The test must fail today (review.md §2.2
   lists why) and pass after P1.

Report: what changed in numbers.json vs the old text report (should be nothing except the fixed
list, the new fields, and the intervals). Do not commit.
```

---

## P3 — The object-level meta-analysis (the repo's stated aim)

```
<P0>

Goal (from commit 096cac0): a meta-analysis of the empirical AI-safety work itself — what the
741 posts found — not of the scrapes. Two phases. Phase 1 fans out; Phase 2 is one context.

PHASE 1 — per-post claim extraction (subagents, ~25 posts per agent, run in parallel).
Input per post: `article-content` and `github-readme` from union.json (P2), plus the LW
`topic`, AF `project_type_norm`, `own_repo`, `date`, `karma_lw`.
Output per post: one JSON object conforming to this schema, written to claims/<post_id>.json:

{
  "post_id": str,
  "primary_claim": str,            // one sentence, the authors' own headline result
  "claim_type": "positive|negative|null|replication|method|benchmark|dataset",
  "phenomenon": str,               // free text, ≤6 words, e.g. "emergent misalignment",
                                   //   "CoT obfuscation under monitoring", "SAE feature absorption"
  "models": [ {"family": str, "size": str|null, "open_weight": bool} ],
  "n_model_families": int,
  "effect": { "metric": str|null, "value": str|null, "direction": "+|-|0|na",
              "uncertainty_reported": "seeds|ci|se|none" },
  "design": { "baseline": bool, "ablation": bool, "held_out": bool, "seeds_n": int|null,
              "prereg": bool, "human_eval": bool },
  "depends_on": [str],             // repos / prior posts / papers the result is built on, as
                                   //   github owner/name, arXiv id, or post id
  "contradicts_or_qualifies": [str],  // prior work the authors say they contradict/qualify
  "stated_future_work": [str],     // ≤5 items, verbatim-ish
  "limitations_stated": [str],     // ≤5 items
  "reproducible_in_principle": "code+data|code|neither",
  "extractor_confidence": "high|medium|low",
  "quote": str                     // ≤240 chars from the post supporting primary_claim
}

Rules for extractors: no inference beyond the text; if the post is a linkpost stub (<200 words)
set primary_claim to "STUB" and stop; if two claims compete, take the one in the title or TL;DR;
`phenomenon` must reuse an existing string from claims/ when one fits — read the current set of
distinct phenomenon strings (the orchestrator supplies it) before inventing a new one.

Orchestrator: after all agents return, run a normalisation pass over `phenomenon` (embedding
cluster or an LLM merge pass with a written merge log), producing phenomenon_map.json. Validate:
sample 30 posts, hand-check primary_claim against the post, report agreement before Phase 2.

PHASE 2 — synthesis (one context, reading claims/*.json + phenomenon_map.json + numbers.json).
Produce findings.md with, in this order:

1. Phenomenon table: for each phenomenon with ≥3 posts — n posts, n distinct first authors,
   n model families, positive/negative/null split, share with any uncertainty reported, share
   with code, date of first and last post, and the union post ids. [MEASURED] from claims/.
2. Contested phenomena: any phenomenon with both positive and negative/null claims. For each,
   list the claims side by side with models and effect. Do not adjudicate; state what differs
   in design. [MEASURED] + [UNRESOLVED].
3. Replication map: claims whose `claim_type` is replication, what they replicate (by
   depends_on), and outcome. Count of union results that have ≥1 in-corpus replication.
4. Dependency graph summary: top-20 nodes by in-degree across depends_on (repos, papers,
   posts). Compare against readme.md O5.
5. Evidence-strength profile per phenomenon: share of claims with ≥2 model families, seeds,
   intervals, baseline, held-out — computed from `design`, not regex. Put readme.md §1.3(c)'s
   regex rates next to these and report the delta per marker (this is R3's headline, for free).
6. Unexecuted future work: cluster `stated_future_work` semantically; rank clusters by number
   of independent posts proposing them, minus posts that later executed them (check by
   phenomenon + date). This is R9.
7. Ten findings a researcher would want to know, each ≤3 sentences, tiered, with post ids.

Constraints: every number in findings.md must come from a script (`findings.py`) that reads
claims/ and emits findings_numbers.json; apply the P2 test pattern. Report the extraction
agreement rate from the Phase 1 validation at the top of findings.md. Do not commit.
```

---

## P4 — Instrument validation (regex vs LLM judge vs human)

```
<P0>

Task: price the regex instrument in meta.py before anyone quotes it again.

1. Sample 80 union posts stratified by (in_af, half-year), seed 0. Write the ids to
   validation/sample.json.
2. Write validation/rubric.md: for each of the 13 RIGOR markers, one paragraph defining what
   counts, with two positive and two negative examples from posts NOT in the sample. "Mentions
   seeds" ≠ "reports run-to-run variance"; "contains ±" ≠ "reports an uncertainty interval on
   the headline result". Commit to the rubric before labelling.
3. LLM-judge pass (subagents, 10 posts each): for each post × marker, output
   {present: bool, quote: ≤200 chars or null, confidence: high|medium|low}. Judges see the
   rubric and the post only; not the regex output, not each other.
4. Human pass: the user labels 20 of the 80 (provide validation/human_form.md with the rubric
   and blanks). If the user declines, say so and report judge-only results as [INFERRED].
5. Compute per marker: regex rate, judge rate, regex-vs-judge Cohen's κ with CI, judge-vs-human
   κ on the 20, and the regex false-positive and false-negative rates against the judge.
6. Output validation/report.md: one table, then for each marker with |regex − judge| > 5 points,
   five example regex false positives with context. Apply the verdict rule from readme.md R3:
   if the delta is large and marker-dependent, add a retraction note to readme.md §1.3(c) and
   M3; if small, say the regex era is fine and remove the hedging.

The judge model must not be told what result would be convenient.
```

---

## P5 — Adversarial review of an LLM-written analysis document

```
You are reviewing an analysis document written by an LLM for LLM readers, together with the
script that is claimed to warrant its numbers and the source data it analyses. Your job is to
find where it is wrong, over-claimed, mis-tiered, or unfaithful to its sources — not to
summarise it. Assume it is persuasive and that persuasiveness is the hazard.

Do, in order, and report what you actually did:

1. Run the warrant script. Diff its output against every number in the prose. List numbers
   that appear in the prose and not in the output, and vice versa. List rows or columns the
   script prints that the prose omits, and check whether the omitted ones contradict the
   surrounding text.
2. For every [MEASURED] tag, ask: is this a number, or a judgment? Is it computed, or
   "directly measurable"? Re-tier in a table.
3. For every trend or time claim: find the period boundaries in the data. Check whether any
   endpoint is a partial period. Recompute as a rate.
4. For every "X and Y are the same / not independent / identical" claim: write down what the
   evidence would look like if they were independent. Discard evidence that looks the same
   either way.
5. For every comparison of the document's number to a source's number: find the source's
   operational definition. If it differs, the discrepancy is not evidence of anything.
6. For every regex or lexical instrument: print 8 random matches in context. Estimate the
   false-positive rate by eye. Apply the document's own instrument criticisms to itself.
7. For every rate: compute n and a Wilson interval. Flag every "same", "flat", "identical" and
   "different", "larger", "decays" that the interval does not support.
8. For every contrast between groups: ask whether the groups chosen are the natural ones or the
   ones that maximise the contrast. Recompute the natural one.
9. For every recommendation: find its nearest ancestor in the sources. Tabulate lineage.
10. Read the sources' provenance/limitations sections in full. List every "discovery" in the
    document that a source already states.
11. Find at least one thing the document's own method proves that the document did not notice
    (joins, identities, and null counts are the usual places).
12. List the superlatives. Count how many distinct things are "the most important".
13. Check the handoff/summary file against actual repo state (git log, remote, file list).
14. Check the document against the repository's stated purpose (first commit, README title,
    task prompt). Say whether it delivered that or something adjacent.

Output: review.md with a one-paragraph verdict, a scorecard table, findings ordered by severity
each with the exact recomputed number and the command or script that produced it, a list of
what is good and should be kept, and an ordered fix list. Save your verification script next to
it. Do not fix the document; do not commit.
```

---

## P6 — Handoff document

```
Write summary.md for a fresh model instance that will continue this work with no other context.
Under 150 lines. Sections, in order:

1. Repo purpose — quote the first commit message and the original task prompt verbatim.
   State in one sentence what the current deliverable is and how it differs from that purpose.
2. Exact state — `git log --oneline -5`, `git status -sb` output, remote URL, which commits are
   pushed, whether the tree is clean. Run these commands; paste output; do not describe from
   memory.
3. Files — one table: path, size, what it is, whether it is generated and by what.
4. Read-only inputs — paths, n, primary artifact, and the exact date range from the data.
5. Findings — a pointer per finding to the section of the deliverable, one line each, with its
   tier. Do not restate the argument. Do not repeat numbers that live in the deliverable.
6. Known defects and open questions — anything a reviewer found (link review.md), anything the
   author knows is weak, and the questions only the user can answer, phrased as questions.
7. Next actions — ordered, each with an estimated effort and what it unblocks.
8. Conventions — commit trailers, git identity flags, tier tags, "change the script not the
   prose", subagent policy from the user's CLAUDE.md.

No superlatives; no narrative; every path absolute or repo-relative; every claim about git
state from a command run in this session.
```

---

## P7 — Style contract for documents written for LLM readers

```
When writing a document whose stated audience is another model:

- Front-load the contract: what the object is, its schema, its date bounds, its n, its
  provenance, and its known defects — all before any finding. A model reads top-down and
  weights early text.
- One claim per sentence. One tier tag per claim. n and interval next to every rate.
- Numbers come from a named file the reader can open (numbers.json) with the key given inline,
  e.g. "58.9% [MEASURED: coverage.overall.pct]". A number without a key is not [MEASURED].
- No adjectives of importance. No "the single most", "worthless", "invalidates", "the only
  reading". If a finding matters more than another, say why in terms of what it changes
  downstream, once, in the synthesis section.
- Do not use rhetorical structure — no "Read the first and last rows against each other", no
  aphorisms, no closing zingers. They are persuasion; the reader will weight them.
- Every recommendation names its ancestor if it has one. "New" means no source proposes it.
- Say what you did not do. A "limitations" section is not a substitute for tiering each claim,
  but it is required in addition.
- Length budget: findings ≤ 3k tokens, synthesis ≤ 1k, specs ≤ 250 tokens each. If the
  document exceeds the budget, the extra text is almost always rhetoric or repetition.
- Self-reference is a smell. A document that discusses its own importance as training data,
  or nominates itself as an experimental arm, has stopped analysing the object.
- End with instructions to the next reader that are checkable ("run X; assert Y") rather than
  attitudinal ("carry the tier labels").
```

---

## P8 — Select and inspect what is replicable on one GPU

```
<P0>

Hardware in scope: one RTX 3090 (24 GB VRAM), 31 GB RAM, ~150 GB free disk, Linux, no cloud
credits, no closed-model API keys. Everything that does not fit this is out of scope, and "fits"
is decided by reading the repo, not by optimism.

This pipeline already exists under replication/. Re-run it, do not rewrite it:

1. `python3 replication/select.py` — filters p3/claims/*.json to posts whose models are all
   open-weight, whose repo exists, and whose headline is a number. Tiers by parameter count
   parsed from the extracted size strings (T1 <= 9B any workload except full FT; T2 <= 14B with
   8-bit/QLoRA or <= 32B inference-only at 4-bit; T3 no). The tier is a heuristic from strings
   an LLM extracted; treat it as a pre-filter only.
2. Liveness: `git ls-remote --exit-code https://github.com/<repo> HEAD` for every candidate
   repo -> replication/liveness.txt. Pin that sha. Never inspect or run HEAD-of-main.
3. Inspection fan-out (subagents, 8 repos each): replication/INSPECT.md is the contract.
   Read-only — shallow clone, read README / requirements / the entrypoint, do not install, do
   not run. Output one JSON per repo with entrypoint, env, VRAM estimate WITH ITS BASIS,
   data availability, runtime estimate, needs_closed_api, blockers. An inspector that guesses
   a VRAM number from vibes has failed; null with a reason beats a number without one.
4. `python3 replication/inspection_summary.py` — tabulates fits / closed-API / no-entrypoint /
   data-missing over every inspected repo. This is a finding in itself (README "What the
   inspection found"); record it before building the queue, because it is the answer to
   "why is the queue smaller than the candidate list".
5. `python3 replication/build_specs.py --include-tight` — merges into
   experiments/<slug>/{spec.json,PROMPT.md} and writes queue.md. Only fits_3090 in {yes, probably} and needs_closed_api == false get a
   folder; everything else is listed under "Not queued" with the reason.

Report: the funnel (741 -> ... -> queued), how many need a closed API, how many have no
identifiable entrypoint, and the five most surprising inspection findings. Do not start runs.
```

---

## P9 — Replication run protocol (one Claude Opus session per experiment)

```
<P0>

You are running ONE replication attempt from the queue in replication/queue.md. Start by
reading replication/experiments/<slug>/PROMPT.md and spec.json. Hardware: RTX 3090 24 GB, no
closed-model API keys. The goal is a ledger entry, not a success — R5's finding is the rate and
the failure taxonomy, so an honest failure with a reason is a complete result.

Protocol, in order:

1. Sanity: `nvidia-smi` shows a free 3090; `df -h` shows > 40 GB free; HF token present if the
   spec lists a gated model. If any fails, stop and report it — do not improvise.
2. `./run.sh`. It pins the sha, builds a per-experiment venv from the repo's own requirements
   (torch from the cu124 index first), runs the entrypoint under `timeout`, and logs to
   run.log + vram.log. Do not bypass it.
3. Environment failures: fix only the environment — a pin, a missing system package, a path,
   a CUDA-index wheel. Every fix is one `--fix "..."` line in the ledger. Thirty minutes, then
   `--reason env`. Never edit code that decides what is measured.
4. Entrypoint arguments: if the inspection did not capture them, take them from the README
   or the script's argparse, choosing the configuration the post describes. Record the exact
   command as a fix line.
5. Model access: gated Llama/Gemma is fine with the local token. Any step that needs
   OpenAI / Anthropic / Google is `--reason api-key`. Do not swap in an open model as a
   judge and call it a replication; that is a follow-up experiment, note it and stop.
6. Budget: spec.json `budget_minutes` for the run (setup capped separately at 30). On overrun,
   stop, `--reason runtime`, record how far it got. Breadth beats depth here.
7. Seeds: run one. If one run finishes in under 10 minutes, run three with different seeds and
   report the spread in --notes — the spread is worth more than the point estimate, and it is
   the number the field mostly does not publish.
8. Reading the result: find the headline metric in the output; compare against
   `target_value` under `tolerance` (a default, stated in `tolerance_rationale`; override with
   `--reproduced true|false` and say why when the metric is not scalar). If you cannot tell
   which number is the headline, `--reason unclear-entrypoint` — do not pick the one that
   matches.
9. `python3 report.py --observed "<value|null>" --reason <reason> [--fix ...] [--notes ...]
   [--seeds N]`. Then append a `== VERDICT` block (3–6 lines) to run.log: observed vs claimed,
   what changed, what you would need to go further.
10. Never: git push, open issues, contact authors, delete anything outside the experiment
    folder, install into the base environment, run two experiments concurrently on the card.

What you report back: the ledger entry verbatim, the VERDICT block, and one sentence on
whether the post's claim survives — tiered [MEASURED] for what you observed, [INFERRED] for
what you conclude, [UNRESOLVED] for what the budget did not reach.

After N attempts, `python3 replication/ledger.py` aggregates. Do not summarise the rate until
at least 20 entries exist; below that it is noise.
```
