# nav.md — orientation for a fresh instance directing this research

**You are in `/home/user/alignment-literature-meta-analysis/`** (git `Foomax/alignment-alpha-meta`, branch `master`).
Written 2026-08-28 for another Claude asked to **run a literature review and steer where the replication goes next.**
Short by design; the files it points to carry the detail. Read this, then read the 5 starred files, then propose direction.

## What this repo is — two layers

1. **Literature meta-analysis (repo root).** An analysis of ~741 posts of empirical AI-safety / interp research,
   joined across three corpora (alignment-forum, LessWrong, Neel-Nanda/Chris-Olah). It maps *what the field claims
   and who checks it*. It does **not** run any code. Key output framing: **"Nobody Is Checking"** — almost none of
   this literature is independently replicated.
2. **Replication ledger (`replication/`).** The response to layer 1: we actually **reproduced 34 of those posts** on
   one RTX 3090 under a fixed protocol, and ledgered each. This is the live workstream (a GPU queue is running now).

Layer 1 tells you *what is worth checking*; layer 2 is *the checking*. A literature review should connect them:
take a reproduced/contested result, place it against the published work, and say which deep replication would move the field.

## Read in this order (★ = essential)

- ★ `replication/NEW-DIRECTION.md` — **the variance-decomposition + rot-reversal program (14 GPU runs, 2026-08-28)**: what a reproduction depends on (seed, sampling rate, library epoch, family, rot, harness sensitivity). Read with META-REPORT; it revises the headline to 24/26 ≥ partial and re-tiers seeded rows as rates.
- ★ `replication/META-REPORT.md` — the headline result of the N=36 ledger. Read first.
- ★ `replication/handoff-synth.md` §B — critical evaluation of research direction + next steps (the "where to go" file).
- ★ `meta-analysis-blog-post.md` — "Nobody Is Checking"; the narrative + the contested-claim landscape (`⚔ N-vs-M` splits).
- ★ `3090-prompts.md` — the 3 scaffolded protocol experiments (a negative, a positive, a replication) and why each was chosen.
- ★ `replication/lessons-synth.md` — how replication actually goes (Part 3 = symptom→cause→fix catalog). Read if you'll run code.
- Supporting: `corpus-analysis.md` + `results.md` + `p3/findings.md` (the three layer-1 instruments); `human.md` (ELI5); `summary.md` (layer-1 handoff).
- `replication/HARNESS.md` — the reusable replication harness (a contribution in its own right).
- `prompts2/brainstorm.md` — wild-pass direction menu (2026-08-28); §7 is a run order. `prompts2/00-fable-research-director.md` is the prompt that executes it, with hourly `handoff-&-lessons-HH.md` logs.

## Regenerate the numbers (don't trust prose, run the scripts)

```
python3 meta.py            # layer-1 collection numbers -> numbers.json
python3 analyze.py         # layer-1 structure numbers  -> analysis_numbers.json
python3 replication/ledger.py    # live replication tally + failure taxonomy
```

## Headline finding so far (defensible, N=34)

**When the code runs at all, this literature reproduces at a high rate to stated precision. The binding constraint is
engineering rot, not scientific fragility.** Of 19 experiments that reached a measurement, **17 (89%) reproduced ≥partially**;
exactly **one** was a genuine scientific miss. **15 of 34 (44%) never ran — every one on packaging/hardware**, never the science.
(Ledger: 34 attempted · 20 ran · 14 reproduced = 11 exact + 3 recompute · taxonomy: env 6, runtime 3, unclear-entrypoint 2, vram 2, api-key 1, data 1, model-access 1.)

## Salient results — where a literature review most helps (priority order)

| result | status | why it needs the literature | where |
|---|---|---|---|
| **AntiPaSTO honesty-steering** | ❌ config-drift | reproduces on Gemma-270M (41.7 vs 38.7) but **not** 1B (2.0 vs 31.2) — the shipped 1B preset is *not* the paper's config (`git log -S` shows it never existed). Does the 1B claim appear in the activation-steering literature at all? | `replication/experiments/…antipasto…`, `3090/02` |
| **cross-model geometry** (Platonic Rep. Hypothesis) | ✅ exact | a **negative** result on PRH (CKA within 0.91 vs cross 0.21); contested ⚔22-vs-5 in-corpus. Situate vs Huh et al. PRH + CKA-critique literature. | `…cross-model-alignment-geometry`, `3090/01` |
| **jordanmccann polymorphism-is-rotation** | ⚠ partial | toy + Haar-rotation **exact** (repo's own verify 6/6); Pythia post-rotation EV gap (0.2–0.5 vs 0.85–0.99). Is "polymorphism = rotation" consistent with the SAE feature-absorption / rotation literature? | `…polymorphism-is-rotation` |
| **sandbagging via noise** | ✅ exact | noise injection *raises* a sandbagging model's accuracy (9/10 seeds vs author 6/10); contested ⚔5-vs-6. Safety-relevant; place vs the sandbagging/elicitation literature. | `…arena-sandbagging-mi`, `3090/03` |
| **tarcle "imposter" function vectors** | ⏳ running (H36c) | a **negative** claim: FVs that ace extraction transfer to unrelated tasks. Situate vs function-vector work (Todd et al., Hendel et al.). | `…star2vec` |
| **sneaky-mamba** | ⏳ running (H57b) | **comparative**: standard Mamba fails a hidden-serial-reasoning task; a cross-channel variant solves it. Vs SSM-vs-transformer serial-reasoning literature. | `…filyp` |

The two ⏳ rows are the **hours-class scale test** — do the 89%/engineering-rot findings hold on bigger models? Judgement pending.

**Since then, `NEW-DIRECTION.md` (2026-08-28):** both ⏳ rows judged (tarcle ✅ recompute; sneaky-mamba `env`); the sandbagging row's 9/10 was a lucky batch (n=30: 67% [49, 81] reveal, 23% collapse); phusroyal is seed-bimodal (4/15 in the claimed range); six `env` rows re-attempted with the environment made right → 3 exact + 2 partial + 1 credential-gated, 0 scientific misses; the blind bug-injection control scored 7/7.

## Open questions to direct (pick 1–2)

1. **Is the meta-finding publishable, and against what?** It is essentially an ML-reproducibility result on a specific
   subfield. Position it vs the reproducibility-crisis literature (Pineau/NeurIPS checklist, Gundersen). The *harness*
   + the *engineering-rot taxonomy* may be the larger contribution than any single row.
2. **Which single contested claim deserves a deep, from-scratch replication?** AntiPaSTO (config-drift is a real finding),
   PRH-negative, and sandbagging are the strongest candidates — each is ⚔-contested in-corpus and safety- or
   epistemics-relevant. A literature review should rank these.
3. **Author-facing notes** (deferred, human-gated): AntiPaSTO config-drift and the jordanmccann Pythia-EV gap are worth
   concise notes *when the ledger is published* — via the existing forks only. Never contact authors mid-run.

## Live state / ground rules (do not disturb)

- A detached GPU queue (`replication/tree_late.sh`, one job at a time) is **running H36c + H57b** now; `tree.log` is the pulse.
  Stop it only with `touch replication/tree_late.stop`. Don't launch a second GPU job.
- Protocol is **environment-only fixes**; pin the author's commit; no hosted-model APIs; never push to authors' repos /
  open issues / contact authors. Only 3 `Foomax` forks exist and that is deliberate — create no new forks.
- Commit only inside `replication/` on `master`. Mirror: `/media/user/466CD2B96CD2A34B/home/alignment-replication-3090-2026-08/`.
- Full operating rules: `replication/handoff-synth.md` §A. Do-not list: §C.
