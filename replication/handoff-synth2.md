# handoff-synth2.md — the documentation pass, as a re-runnable prompt (2026-08-29)

`handoff-synth.md` tells a fresh instance how to **operate the GPU queue**. This file is the other
half: how to **rebuild the documentation layer** — the two syntheses, `human.md`, `replicate.md`,
and `visualisation.html`. Everything below has been executed once; the outputs are in the repo. Use
it to redo the pass after new rows land, or to audit what the last pass did.

Run it as a single prompt to a fresh Claude session with the repo as the working directory.

---

## The prompt

> You are in `/home/user/alignment-literature-meta-analysis` (git `Foomax/alignment-alpha-meta`,
> branch `master`). Produce five documents. Do the work in this order; each depends on the last.
> Bind yourself to `replication/handoff-synth.md` §A0 throughout: no pushes to authors' repos, no
> issues, no author contact, no new forks, no accounts or hosted-model APIs, commit only inside
> `replication/` and `prompts2/` plus the root documents named below.
>
> **1 — Verify, then synthesise the running notes.** Read every `replication/handoff-[n].md` and
> `replication/lessons-[n].md` in full — not a sample, and not your memory of them. Then rewrite
> `replication/handoff-synth.md` (operating rules + current state + research direction + a do-not
> list) and `replication/lessons-synth.md` (principles · phase checklist · a symptom → cause → fix
> catalogue · reproduction-quality tiers · timings for this card) so that a fresh instance needs
> only those two files plus `nav.md`. Rules for the synthesis:
> - Every lesson in a numbered file must survive somewhere, be explicitly superseded, or be dropped
>   with a stated reason. Dropping by omission is the failure mode — the previous pass silently lost
>   ~20 lessons, including the `pgrep` launcher trap, the string-vs-list notebook `source` gotcha,
>   and "never rewrite a running bash script".
> - Where a later run **revises** an earlier lesson, keep both and say which won (example:
>   lessons-1 A8 said "don't chase seeds"; the seed census showed seeds flip verdicts, so the rule
>   became "5 seeds is cheap and high-information; a tenth on a settled row is not").
> - **Recompute every aggregate from the ledgers rather than copying it forward.** Load all
>   `replication/experiments/*/ledger.json`, split on `experiment_class == "extension"`, and derive
>   the funnel, the taxonomy, the tier mix and any pooled figure. The last pass propagated a wrong
>   pooled number (26/28) into four files because it was carried from prose instead of counted; the
>   correct figure is 25/27 (18/20 parent rows + 7/7 rot-reversal rows). Show your count.
> - Preserve the selection caveats verbatim: the sample is minute-class plus three protocol runs;
>   the hours-class test is n=2, one of which used the recompute path; the corpus-level rigor rates
>   come from an unvalidated LLM judge.
>
> **2 — `human.md` at the root.** One section per mini-project, in the order the projects happened,
> each with an **ELI5** part (no jargon, no numbers the reader cannot feel) and a **busy researcher**
> part (the numbers, the caveat, and the file that emits them — ~90 seconds each). Finish with a
> single `# LLM` section: direct, unambiguous, no narrative — object, layers in dependency order,
> findings with tiers, the rules any continuation inherits, entry points, and the one command that
> regenerates everything.
>
> **3 — `replicate.md` at the root.** How to re-run all of it, written for an LLM. Mostly links:
> for each of the 36 rows give the GitHub URL, the pinned SHA, the LessWrong post URL, the
> entrypoint *as actually run* (not as catalogued — about a third of catalogued entrypoints are
> prose, a pipeline step, or a command missing its required positional), the target, the outcome,
> and the one specific thing that would otherwise cost an hour. Then a second table for the rows
> that never reached a measurement, each with the reversal recipe that worked or the reason none
> exists. Then recipes for the controlled variations (seed census, sampling rate, library epoch,
> second family, bug injection, rot reversal) so they can be redone on other rows. Generate the
> tables from `spec.json` + `ledger.json` with a script; do not hand-copy SHAs.
>
> **4 — `visualisation.html` at the root.** A single self-contained page for a technically-inclined,
> busy human: the attrition funnel, the failure taxonomy with what happened when the environments
> were rebuilt, the seed/library/sampling evidence, the corpus context, and a filterable table of
> all 36 rows with links. Inject every number from the JSON artefacts — never type a figure by hand.
> Load `artifact-design` before writing it and `dataviz` before choosing any chart form or colour;
> validate the categorical palette with the validator rather than reasoning about it, and design
> both themes at token level. Then publish it as an Artifact and give the user the link.
>
> **5 — Commit** (`replication/` and the root documents), and report what changed in the numbers.

---

## What the executed pass produced (2026-08-29)

| output | what it is |
|---|---|
| `replication/handoff-synth.md` v3 | operating rules, state (N=36 + 17 variations), direction, do-not list |
| `replication/lessons-synth.md` v3 | 18 principles, phase checklist, ~45-row failure catalogue, tiers, timings |
| `human.md` | 7 mini-projects × (ELI5 + busy researcher), plus a machine-facing `# LLM` section |
| `replicate.md` | per-row GitHub links + SHAs + entrypoint translations + reversal recipes |
| `visualisation.html` | published Artifact, "The 3090 Replication Ledger" |

Corrections the verification pass forced, and which a future pass should not undo:

1. **Pooled figure 26/28 → 25/27.** 20 parent measurements (18 ≥ partial) + 7 rot-reversal
   measurements (7 ≥ partial). The two exceptions are AntiPaSTO (the one scientific miss) and the
   jlens row (hosted API, never a local test).
2. **"8 rot-reversal rows → 3 exact + 5 partial" → 7 of 8 reached a measurement → 3 exact + 4
   partial**; the 8th (dajale423) is credential-gated.
3. **~20 lessons restored** from the numbered files into `lessons-synth.md`, and the hours-class
   `n=2` caveat restored into `handoff-synth.md` §A1 and §B1.

## Cadence from here

Numbered notes continue at `handoff-31.md` / `lessons-26.md`. Re-run this pass when the overnight
`runtime` rows (O1–O3) are judged, since they change the parent ledgers and therefore every figure
above. `handoff-synth.md` §B lists the CPU work that does not need the card.
