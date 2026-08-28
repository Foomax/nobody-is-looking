# handoff-30 — the new direction closed at R-15; overnight `runtime` queue running (2026-08-28 20:10)

Read `handoff-synth.md` (rules) and **`NEW-DIRECTION.md`** (this session's 15-run program: one
section per run, decision re-made after each). `lessons-25.md` has the harness lessons.

## State
- **Ledger:** N=36 replication rows unchanged (15 reproduced). **Extension rows: 17**, all
  `experiment_class: extension`, excluded from the rate by `ledger.py`, each with `spec.json`
  (`extension.what_varies`), `ledger.json`, artefacts. `python3 ledger.py` lists them.
- **Headline revision (NEW-DIRECTION.md, program-state section):** of never-located rows
  re-attempted with the environment made right, 8 reached the computation → 3 exact, 5 partial,
  0 scientific misses; pooled over everything that reached a measurement **26/28 ≥ partial**, one
  scientific miss (AntiPaSTO), one definition-ambiguous (artmtt). Seeded rows should be re-tiered as
  rates: sandbagging 67% [49, 81] reveal / 23% collapse (n=30); phusroyal 4/15 in range.
- **Overnight queue (running, detached):** `tree_late.sh` with three `runtime` rows at the authors'
  budgets — O1 g-w1 (360 min), O2 mamiglia (420), O3 james-sullivan (480). One at a time; `tree.log`
  is the pulse; stop with `touch tree_late.stop`. **These are replication re-attempts of parent
  rows**, not extensions: when each finishes, judge per `handoff-synth` §A3 and update the parent
  `ledger.json` (`runtime` → the honest outcome) — the first change to the N=36 rows since FINAL.
  Then regenerate `META-REPORT.md` numbers.
- Disk: 89 GB free after clearing the `uv` cache (78 GB) and finished ext venvs. Floor 25 GB.
  The queue deletes venvs per run.

## What to do next (priority)
1. Judge O1–O3 as they land (`tree.log` `EXIT` lines). Expect hours each.
2. CPU: P3-judge-vs-ledger validation (`prompts2/brainstorm.md` §4.2); the tolerance-rule audit
   (which `manual`/3-decimal tolerances would have failed on a different seed — R-1/R-4 data);
   a sub-tolerance bug-injection round (§4.1, second pass).
3. Do **not** re-run the seed/epoch/family arms; they are done. Do not create a W&B account for
   dajale423 (rule A0). ak47na is the one untried `unclear-entrypoint` row (W&B artefact → expected
   `model-access`).

## Harness notes for this box
- Background *tasks* get killed at startup under some conditions (three times today, once with
  disk < floor); the *processes* survive when detached (`setsid nohup … &`). Watch logs, not tasks.
- `uv pip install --exclude-newer <date>` is the rot-reversal tool; it is inapplicable to the
  PyTorch index. Pin torch in the same call as everything else.
- `replication/select.py` shadows the stdlib `select` for any Python started with cwd=`replication/`
  that imports `subprocess`/`socket`; run helper scripts from elsewhere or with absolute paths.
