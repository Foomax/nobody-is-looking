# handoff-synth (v3) — operating instructions + research direction (2026-08-29 08:30)

Supersedes v2 and handoff-0 … 30 (kept as history). Read this first; it bakes in `lessons-synth.md`
(v3). §A = how to operate. §B = where the research is and what to do next. §C = do-not.
Two workstreams now share this folder: the **N=36 replication ledger** (handoff-0…29) and the
**variance-decomposition / rot-reversal program** (`NEW-DIRECTION.md`, R-1…R-15, handoff-30).

═══════════════════════════════════════════════════════════════════
## §A — OPERATING

### A0. Non-negotiable rules
1. Environment-only fixes, on copies, each a `--fix` line. Never change prompts/thresholds/dataset
   slices/metrics/seed-counts/model **in a replication row**. A run that changes one of those is an
   **extension** (`spec.json: experiment_class: "extension"`, `extension.what_varies` names the one
   thing) and never enters the reproduction rate (`ledger.py` filters it).
2. No hosted-model APIs (even keyless) → `api-key`. No accounts, no logins, no credentials
   (W&B, HF-gated beyond what the user already accepted) → `model-access`.
3. Pin the `spec.json` commit; no `git pull`. For rot reversal, freeze the *resolution date*
   (`uv pip install --exclude-newer <post date + 14 d>`), not the code.
4. One venv per experiment, built and **deleted** by the queue; never touch the base env.
   Disk floor 25 GB; `uv cache clean` when the cache passes ~30 GB (it reached 78 GB once).
5. Never push to authors' repos / open issues / contact authors. Only the three allowlisted
   `Foomax` forks exist; create no new forks or PRs.
6. Commit only `replication/` and `prompts2/` in `Foomax/alignment-alpha-meta` (master). Leave the
   user's other root files. Generated `src/`, `.venv*/`, `executed*.ipynb`, `run.log` are ignored —
   copy the artefacts a verdict rests on (`results/*.json`, summaries) into the row folder before
   `git add`.
7. Don't stop for human guidance — write it in `human-oversight.md`, keep the GPU busy.
8. After every finished run/juncture: `handoff-N.md` + `lessons-N.md` (next: handoff-31,
   lessons-26) + a `human-oversight.md` section; commit. The new-direction program writes one
   section per run into `NEW-DIRECTION.md` instead — either cadence is fine, name which.
9. Tiers: `[MEASURED]` / `[INFERRED]` / `[UNRESOLVED]`; no superlatives; a ledger entry is the
   goal, not a success. A seeded result's honest tier is a **rate with an interval**, not `exact`.

### A1. State (2026-08-29 08:30)
- **Replication ledger: N=36 FINAL** — 36 attempted · 21 runs · 20 located · 15 reproduced
  (11 exact + 4 recompute); 18/20 located reproduce ≥ partially (15 reproduced + 3 partial); 16
  never ran (env 7, runtime 3, unclear-entrypoint 2, vram 2, api-key 1, data 1, model-access 1).
  `META-REPORT.md` is the report. **Selection caveat that must travel with every quotation:** the
  sample is minute-class rows plus the three protocol experiments; the hours-class scale test is
  n=2 (tarcle ✅ via the *recompute* path — the GPU stage was never regenerated — and sneaky-mamba
  `env`). The pattern is *consistent* at scale, not confirmed.
- **Extension rows: 17** (`experiments/*--ext-*/`), all in `NEW-DIRECTION.md`. Net effect on the
  headline: 8 never-ran rows re-attempted with the environment made right; **7 reached a
  measurement → 3 exact + 4 partial, 0 scientific misses**; 1 credential-gated. Pooled over every
  row that reached a measurement: **25/27 ≥ partial** (18/20 parents + 7/7 rot-reversal); the two
  exceptions are AntiPaSTO (the one scientific miss, 1B config drift) and the jlens row (hosted-API,
  never a local test). artmtt's partial is definition-ambiguous — say so when quoting it. Seeded rows re-tiered: sandbagging 67% [49, 81] reveal / 23% collapse (n=30);
  phusroyal 4/15 seeds in the claimed range.
- **Overnight `runtime` queue (`tree_late.sh`, detached, running):** O1 g-w1 timed out at its
  360-min budget (EXIT 124 → judge as `runtime`, honest timing); O2 mamiglia running (420);
  O3 james-sullivan queued (480). These are **parent-row re-attempts**: when judged, update the
  parent `ledger.json` and regenerate `META-REPORT.md` (`make_report_table.py`).
- Repo `~/alignment-literature-meta-analysis/replication/` (=`$R`); mirror script `mirror.sh`;
  forks `Foomax/{AntiPaSTO,arena-sandbagging-mi,cross-model-alignment-geometry}` branch
  `replication-3090` (three only, by the user's decision; `publish.sh` is allowlisted to them; each
  fork README carries a `# human` and a `# LLM` section). Disk ~73 GB free.

### A2. Runners and helpers
- `tree_late.sh` — the queue: reads `tree_late.txt` (`name|slug|timeout_min|cmd`), skips
  `tree_late_done.txt`, waits for a free GPU and ≥25 GB, `tree_prep.sh` → cmd → **delete venv**;
  one line per node in `tree.log`. Stop: `touch tree_late.stop`. Relaunch detached:
  `setsid nohup ./tree_late.sh > tree_late_nohup.out 2>&1 < /dev/null & disown`.
- Extension helpers: `ext_ledger.py <dir> --observed … --notes … [--fix …]` (schema-compatible
  ledger for an extension folder); `ext_seed_nb.py` (seeded notebook copies); `ext_seed_census.sh`,
  `ext_seed_analyze.py`, `ext_phus_more.sh`, `ext_buginject.sh` (R-1/R-4/R-13 runners);
  per-row `run_tt.sh` / `run_epoch.sh` / `run_family.sh` / `run_rate.sh` / `run_art.sh`.
- `ledger.py` (tallies; prints extensions separately) · `annotate_tiers.py` · `make_report_table.py`
  · `tree_prep.sh` / `tree_imports.py` / `tree_autofix.py` / `nb_colab_stub.py` · `publish.sh`.
- **Run long jobs detached and watch the log**, not the harness task: background tasks were killed
  at startup several times (once with disk < floor, twice without an identified cause) while the
  detached process kept running. A `Monitor` on `grep -q 'RUN-EXIT' run.log` is the reliable wake-up.
- `replication/select.py` shadows stdlib `select` for any Python started with cwd=`replication/`
  that imports `subprocess`/`socket`; run helper scripts from another directory or with the script's
  own `sys.path` fix (`ext_ledger.py` has one).

### A3. Judgement loop (per `NODE … EXIT` line, or per detached run)
`tail -40 tree.log`; read `$d/run.log` (strip ANSI, `tr '\r' '\n'`, `awk '/RERUN:/{f=1}f'`),
`autofixes.txt`, `prep.log`. Decide: system-failure (disk/RAM/network/harness — fix, don't ledger)
→ my-invocation (translate the entrypoint; two catalogue entrypoints lacked required positionals)
→ environment (per `lessons-synth` Part 3; **read the loader before believing the traceback**;
requeue ≤2–3, then ledger the honest reason) → it-ran (judge). To judge: match `target_value` on the
*named measure* (check what the notebook actually prints — one "pairwise distance" was perplexity),
extract from `executed.ipynb` / HTML-plotly / CSV / `results/*.json`, append `== VERDICT`, run
`report.py` (or `ext_ledger.py` for extensions), add a `human-oversight.md` section, commit.
For a parent-row re-attempt (the overnight queue), update the parent `ledger.json` fields
directly and say so in `notes`.

═══════════════════════════════════════════════════════════════════
## §B — RESEARCH DIRECTION (critical evaluation + next steps)

### B1. What the data says now
Two programs, one conclusion, twice tested:
- **Ledger (N=36):** when the code runs, it reproduces (18/20 ≥ partial); what stops it running is
  packaging, not science. (Minute-class sample; hours-class n=2 — consistent, not confirmed.)
- **New direction (15 runs):** (i) the never-ran rows, once the environment is right, reproduce at
  the same rate (7/8 reached a measurement → 3 exact + 4 partial, 0 misses; the 8th needs a login); (ii) `env` was never one thing — version
  drift, uncommitted artefacts (the most common), code/lockfiles broken at publication, harness
  bugs, credential gates — and 0/6 first-traceback diagnoses named the cause; (iii) the software
  stack below `transformers` moves generated text (65%) but not verdicts; (iv) **seeds do move
  verdicts**: one reproduced training row is bimodal across seeds (4/15 in range), and the
  sandbagging result is a 67%/23% coin, not a 9/10; (v) the harness's judging step caught 7/7
  injected bugs; (vi) contested phenomena in the corpus share no metric (493/493 distinct).

**Headline (defensible now):** *Published alignment-forum empirical work reproduces when its
environment is reconstructed — 25/27 of everything that reached a measurement, one scientific miss.
The binding constraints are packaging and, underneath, unreported seeds: a single-seed "exact"
reproduction is a statement about the RNG, and the honest unit of reproducibility for a seeded result
is a rate with an interval.*

### B2. Where the trajectory could go wrong
- Re-running more minute-class rows or more seed/epoch arms adds confirmation, not information.
- The `runtime` rows are budget, not rot; they cost 6–8 h each and will move the tally by ≤3.
- The one-scientific-miss figure is precious; do not dilute it by counting extensions in the rate
  or by re-tiering partials upward.

### B3. Next steps, in priority order
1. **Judge O1–O3** as they land; update parent ledgers; regenerate `META-REPORT.md` with an
   addendum pointing at `NEW-DIRECTION.md` for the revised headline. (~1 h of judging, spread out.)
2. **Tolerance-rule audit (CPU, ~2 h):** using R-1/R-4/R-5 data, list which parent tolerances
   (`manual`, 3-decimal, `abs:`) would have flipped on a different seed; propose per-row `rate`
   tolerances. This converts the seed finding into a harness rule.
3. **P3-judge validation against ledger ground truth (CPU, 30 min):** `p3/claims`
   `reproducible_in_principle` vs ledger `installs/runs/located` for the 36 rows.
4. **Sub-tolerance bug-injection round (1 GPU-h):** perturbations smaller than the tolerance, to
   price the tolerance rules rather than the judge.
5. **Write-up:** `META-REPORT.md` v2 + `NEW-DIRECTION.md` summary → one document for the user, with
   the rot taxonomy (5 classes), the seed re-tiering, and the metric-sharing result. The harness +
   `lessons-synth` Part 3 remain the largest reusable contribution.
6. Deferred, human-gated: author-facing notes (AntiPaSTO config drift; jordanmccann Pythia-EV;
   phusroyal seed bimodality; the silent-skip loader in thebuleganteng) — via the existing forks
   only, and only when the user says so.

### B4. The things to ask the user
(a) Publish/push the ledger + `NEW-DIRECTION.md`? (b) Fund the two remaining reversible rows that
need credentials (dajale423 W&B; ak47na W&B artefact)? (c) Start the tolerance audit + write-up, or
keep the card on `runtime` rows? Everything else is decided.

## §C — Do-not
Don't count extension rows in the rate · don't re-tier a recompute or a same-seed match as `exact`
· don't grind requeues past 2–3 · don't relaunch `tree_queue.sh`/`tree_rerun*.sh` (superseded by
`tree_late.sh`) · don't ledger from a disk-full window or a killed harness task · don't create
forks/PRs/issues/accounts · don't commit outside `replication/` and `prompts2/` · don't paste tokens
· don't "fix" author code beyond imports/paths/device/unpacking-an-unused-value on copies · don't
read the 2026H2 partial period as a trend · pause the agent, not the GPU.
