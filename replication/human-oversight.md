# human-oversight.md — things a human should know or decide (running log)

Plain-language explanations of what the machine is doing, and step-by-step instructions for anything that needs *you*. I do not stop for these; I note them here and keep the GPU busy. Newest at the bottom.

---

## 0. What is running right now (2026-08-27 07:25)

Think of a bakery with one oven (the graphics card). The queue of "cakes" is:

1. **Project 01 — "do different model families think alike?"** Six models were downloaded (22 GB, took 1 h 46 min). The first bake failed instantly because the recipe's own scripts couldn't find the recipe folder (a path setting, `PYTHONPATH`); fixed, re-baking now. Expect ~45 min.
2. **31 quick projects**, one after another, each in its own sandbox. Two of them failed in seconds on the first pass for boring reasons (a sandbox that never got created; a notebook that assumed `pip` exists). The queue was paused, the runner fixed, and it restarts from the first quick project once the oven is free.

Scorecard so far: 2 rows (AntiPaSTO — did not reproduce; noise‑injection sandbagging — reproduced). Everything is committed to `Foomax/alignment-alpha-meta` as it happens.

## 1. Decisions already taken on your behalf (say so if you disagree)

| # | decision | why | to reverse |
|---|---|---|---|
| 1.1 | **The "key repo" is `alignment-literature-meta-analysis` = `Foomax/alignment-alpha-meta`, and it is already yours** (you created it; `origin` points at your account). Nothing to fork. The three project forks (`AntiPaSTO`, `arena-sandbagging-mi`, `cross-model-alignment-geometry`) stay; no new forks will be created. | Your instruction "just the key repo" + "fork the single key repo needed to execute all the prompts" | If you meant a *different* repo, tell me which and I'll fork it. |
| 1.2 | Quick projects that would need a paid/closed API (OpenAI/Anthropic keys) will be **run anyway** and recorded as `api-key` failures rather than skipped. | The protocol says record the reason; running costs minutes and sometimes the API turns out to be optional. | Say "skip api-key projects" and I'll add them to `tree_done.txt`. |
| 1.3 | Automatic environment fixes are allowed: installing a missing Python package, `pip`/`jupyter` for notebooks, sanitising a Python version string. Never prompts, thresholds, datasets or metrics. | The replication ground rules (environment-only fixes). | — |
| 1.4 | Committing as we go: only the `replication/` folder of the meta repo, never your other uncommitted files at the repo root. | You have work in progress there (`meta.py`, `corpus-analysis.md`, `summary.md`, `p3/`, …). | Say "commit everything" if you want those included. |

## 2. Things only you can do (none blocking right now)

- ✅ Hugging Face licences: Gemma (accepted 08‑26), Llama‑3.2 (accepted 08‑27). If a quick project needs another gated model, it will show up here with the exact link to click.

## 3. Step-by-step: how to read the scorecard yourself

1. Open `replication/ledger_summary.json` or run `python3 replication/ledger.py` — it prints "attempted N, installs N, runs N, reproduced N" and the failure taxonomy.
2. For any project, open `replication/experiments/<project>/ledger.json`. The fields that matter: `installs`, `runs`, `claim_reproduced`, `observed_value` vs `claimed_value`, `blocking_reason`, `env_fixes`, `notes`.
3. `run.log` in the same folder is the timeline; the `== VERDICT` block at its end is the one-paragraph judgement.
4. `handoff-N.md` files (technical) and this file (plain language) are the narrative.

---

## 4. Quick project #1 (`ioi`, GPT‑2 small) — reproduced exactly (07:35)

**What it claims.** A famous "circuit" in GPT‑2 small handles sentences like "When Mary and John went to the store, John gave a drink to ___" (answer: Mary). The post adds a stray extra "Mary" somewhere irrelevant and asks whether the circuit gets confused. Answer: only slightly — the model's preference for the right name drops by 0.23 on its internal scale, and accuracy goes 95.4 % → 94.5 %.

**What we got.** 0.231, 95.3 % → 94.5 %, same statistics to the third decimal. The model is deterministic, so this is the "boring good" outcome: a well‑written notebook that does what it says.

**What needed fixing (nothing scientific).** The repo has no list of required packages, and notebooks run in a fresh sandbox don't have `pip`. The runner now installs those automatically; the first two attempts died on that, the third ran in 3 minutes.

**Needs you?** No.

## 5. Project 01 ("do model families think alike?") — reproduced (14:30)

**What it claims.** Same‑family models look alike inside (0.91), different families barely (≈0.2).

**What we got.** 0.914 for the same‑family pair, 0.208 and 0.222 for the two cross‑family pairs we ran — identical to the post to three decimals. Two of the five pairs weren't run: each pair took ~100 minutes (my estimate was 15 — the similarity statistics, not the model runs, are the slow part) and the protocol's 4‑hour budget ran out. The protocol says the three we ran are enough to test the claim.

**Needs you?** No. If you ever want the last two pairs, it's ~3.5 hours of GPU with everything already downloaded.

## 6. The quick‑project queue is noisy by design (14:30)

Of the first 13 quick projects, 3 ran and 10 failed within seconds. Nearly all failures are *plumbing*: the catalogue's "entrypoint" is sometimes a description ("run `python -m replicate run-fast`…") that the generic runner tries to execute literally; some repos list no dependencies; one needs a package from the author's own GitHub rather than PyPI; one needs 90 minutes, not 45. I'm queuing a second pass with the correct invocation for each. Expect the scorecard to look bad *before* that pass and better after it — the taxonomy records both.

**Needs you?** Not yet. Two projects will likely end as "can't run without external stuff": one expects pre‑generated model completions and a Weights & Biases artifact; one notebook looked like it had a typo (`true` instead of `True`) — on closer inspection it was my runner feeding the notebook file to Python as if it were a script; it's being re-run properly.

## 7. Quick project `quotesbyniche` (ameya-bit, "an induction head in disguise") — reproduced exactly (14:50)

A tiny character‑level model trained on Nietzsche; the post says one attention head is a "copying" head (score 0.615, everyone else ≤ 0.35) whose weights also nudge `)` after `(`. We got 0.615, 0.347 and the same bracket nudges (+0.556 / −0.105). Nothing needed fixing. **Needs you?** No.

## 8. Nodes 15–19: mostly plumbing again, one new pattern (15:10)

- **15 `matryoshka-saes`**: trained its toy models for 11 min, then crashed on a line that uses a library the notebook never imported (`F.normalize`). Same class as the fix in project 03 — a missing `import` line, nothing measured changes. Re‑running with that one line added.
- **16 `quotesbyniche`**: reproduced exactly (see §7).
- **17 `interpretability-prototyping`**: needed five packages; my auto‑fixer allows three rounds. Re‑running with the last one installed.
- **18 `super-weight-circuit-patching`**: the catalogue's entrypoint is step 7 of a 7‑step pipeline; steps 1 and 3 produce the files it reads. Re‑running the chain (author ran it on CPU; ~30 min).
- **19 `mivlde`**: the script imports its own folder by name and needs that folder on the Python path — the same one‑line fix as project 01.

**Needs you?** No. Pattern for the record: the catalogue's "entrypoint" field is a *pointer to where the headline number is computed*, not a runnable command; about half the quick projects need a human‑written invocation. That's now the second pass's job.

## 9. Quick project `interp` (coolvision, "neurons that point at words") — reproduced (15:25)

Some neurons inside Llama‑3.2‑1B point almost directly at a specific word in the output vocabulary (one points at "coming"); most don't. The post says this "pointing" is rare, lopsided, and mostly in the later layers. We see exactly that: in the early layers essentially no neuron stands out; in the last six layers 3–13 % of neurons stand far out. The plots were interactive (plotly), so I read the numbers straight out of the figure data. **Needs you?** No.

## 10. Quick project `qwen-2.5-1.5b-echo_repeat-investigation` (mild-rgb) — reproduced, with a footnote (15:30)

When Qwen‑1.5B is asked to just repeat a word, the post says one particular attention head (head 2) is always among the three most important, across 44 words and two phrasings, and that it mostly stares at the very first token. We get head 2 in the top three 44 out of 44 times, both phrasings. The "stares at the first token ~90 %" part is true for most words and ~77 % on average. Footnote: a different importance measure (direct logit attribution) ranks other heads — the post's claim is about the ablation measure, so this is consistent, but a reader should know the two measures disagree. **Needs you?** No.

## 11. Resumed 16:56 — mirror to the external drive, and the big second pass (17:05)

**Mirror.** Everything now also lives at `/media/user/466CD2B96CD2A34B/home/alignment-replication-3090-2026-08/` (the whole meta‑analysis repo minus rebuildable Python sandboxes — the drive is NTFS and can't hold their symlinks — plus the `~/prompts` folder and my memory notes). It re‑syncs every 10 minutes (`last-mirror.txt` shows when). Stop it with `touch mirror.stop` in that folder.

**While paused, the oven kept baking.** Pass 1 finished all 31 quick projects; the first rerun pass ran 8 of its 9. Score of the reruns: 1 clean success (`data_leakage_detect` with the headline dataset: AUC 0.989 vs claimed 0.986 ✓), 7 more one‑package‑short failures. The fix for that class is now automatic: a scanner reads every `import` in a repo and installs the whole list before running (`tree_imports.py`). Nineteen reruns are queued behind the one job on the GPU now (`codi`, ~95 min).

**Needs you?** No. One thing to know: two projects will likely end as "can't run here" for reasons no fix addresses — `soo-jailbreak` imports `google.colab` (Colab Drive), and `attribution-graph-probing` regenerates its graphs through a paid Neuronpedia API (though its committed graphs may suffice — trying).

## 12. `codi` (cywinski, "where does a latent‑reasoning model keep its intermediate numbers?") — reproduced (17:50)

A model that "thinks" in six hidden vectors instead of words. The post says the third and fifth vectors hold the intermediate arithmetic: swap them for vectors from a problem with a *different* intermediate value and accuracy collapses; swap for *same*‑value vectors and nothing changes. We see exactly that: −30 and −22 points at those two positions, ≈0 everywhere else, and same‑value swaps ≈0 throughout. Baseline 52 % vs their 55 %. One number from a sibling script (the "recovers ~20 %" figure) is queued separately. First attempt died at the 45‑minute limit — the author's own timings say it needs ~50; the rerun took 52. **Needs you?** No.

## 13. `matryoshka-saes` (noanabeshima) — reproduced on the toy model (17:58)

Sparse autoencoders sometimes learn "holes": a feature for *child* concepts secretly also carries the *parent* concept. The post's trick (train on random prefixes of the dictionary) is claimed to remove the holes in a toy setting. Vanilla: all 9 child features show the hole (only 0.66–0.75 match to their true direction, 0.7 leaking to the parent). Matryoshka: every feature ≥ 0.92 to its own direction, nothing leaking. The second half of the post (real language‑model results) has no code in the repo, so it can't be checked. First attempt crashed on the author's own missing `import` — fixed in a copy. **Needs you?** No.

## 14. Incident: the disk filled up (17:54) — no results lost, one hour of queue time wasted (18:10)

**What happened.** Each quick project gets its own Python sandbox (~4 GB each, mostly the GPU libraries). Twenty‑odd of them, plus 44 GB of downloaded models, filled the system drive to 100 %. Every queued rerun then "failed" in under a second — those lines in the log from 17:55 are not real results and have been reset.

**What I did.** Deleted the sandboxes of projects already scored (they can be rebuilt in minutes), deleted four re‑downloadable models and 4 GB of raw activation dumps from project 01 (its results are kept), and changed the queue so it builds one sandbox, runs, then deletes it — at most one on disk at any time — and refuses to start if less than 12 GB is free. Free space now ≈ 90 GB.

**Needs you?** Only if you want the 44 GB of model downloads kept off the system drive permanently: the Hugging Face cache can't live on the NTFS drive (it uses symlinks), but it could live on any ext4/xfs volume via `HF_HOME=<path>`. Not required for the queue to finish.

## 15. `natural_language_autoencoders` (syvb) — out of scale for this card (19:20)

The setup script wants to download six 7‑billion‑parameter model variants (~90 GB, about four hours at this machine's download speed) and run two of them at once; the author says a 48 GB card is "plenty" — ours is 24 GB. Logged as "too big for this hardware" without spending the hours. **Needs you?** Only if you want it badly enough to run it elsewhere.

## 16. `phu-bluedot_1st_puzzle` (phusroyal, "teach a model to hide a feature from linear probes") — reproduced (20:05)

Can you train a model so that a concept (here "country") is still *used* but no longer readable by a simple linear probe? The post says: with the ordinary objective a probe reads it perfectly (AUC ≈ 1.0) and the concept has little causal pull (0.02–0.04); with the new objective the probe drops to ≈ 0.6 while the causal pull jumps to 2–3.5. We get exactly that on both of the repo's geometries: 0.9997 → 0.57–0.59 and 0.02–0.04 → 2.6–3.5. Five minutes, no fixes beyond running the command the author actually documented. **Needs you?** No.

## 17. `polymorphism-is-rotation` (jordanmccann, "SAE features are universal up to a rotation") — two of three parts reproduce (21:25)

Train the same small model twice with different random seeds: do they learn the same features, just rotated? Three sub‑claims. (1) On a toy model, rotating one seed's activations onto the other's makes a sparse autoencoder work again — we get 0.977–0.991, the post says 0.976–0.990. ✓ (2) The rotation is statistically indistinguishable from a *random* rotation — the repo's own six checks all pass to three decimals. ✓ (3) On the real Pythia‑70m models the rotation should recover 85–99 % of the variance — we get 20–48 %. ✗ This last number is the one the post leads with, so the scorecard says "not reproduced" with the two ✓s recorded. I could not find a benign explanation (same script the author cites); the 14‑hour full retrain is the only remaining thing to try. **Needs you?** No — unless you want that 14 h spent.

## 18. Disk pressure again (21:25) — two nodes lost to it, recovered

Two projects failed while *installing* their libraries: building a 6 GB sandbox while unpacking big packages briefly needs ~15 GB of scratch, and the drive was too tight. I freed 16 GB by deleting downloaded models belonging to projects already scored (they re-download in minutes if ever needed), and raised the queue's safety margin. Both projects are requeued. One of them (`error_pathology`) was also dragging in a second copy of PyTorch because a helper library pins an old version — I switched it to load that library in place instead. **Needs you?** No.

## 19. `activation_plateau_mechanisms` (mshinkle) — reproduced (22:10)

GPT‑2‑large has "plateaus": as you slide a word‑embedding from one word to another, the model's output stays frozen for a stretch, then jumps. The post says these plateaus are made by the MLP layers, not the attention layers. Test: re‑run with the MLP frozen (the plateau vanishes — the curve becomes a straight ramp) and with attention frozen (the plateau stays). Both plots came out exactly that way; judged by eye since it's a claim about curve shape. One follow‑up analysis (a Jacobian on the full residual stream) ran out of GPU memory on the big model — a side‑claim, left unresolved. I deleted 35 GB of intermediate activation files afterward (the plots are kept). **Needs you?** No.

## 20. `arithmetictransformer` (james-sullivan, grokking stages) — needs multi-hour training, deferred (22:15)

"Grokking" is when a small model memorises the training data fast but only *generalises* much later. The post asks whether, when a model learns two tasks at once, there are extra hidden learning stages. Checking it means training these models for ~6000 epochs each across eight task mixes — hours — because the checkpoints aren't included in the repo. That's outside the "quick project" budget, so it's logged as "too long to run here"; the author's own result graphs are in the repo and look right. **Needs you?** Only if you want to spend the training hours.

## 21. `interpretability-prototyping` (thebuleganteng) — blocked by a renamed library asset (00:35)

This project loads a specific pre-trained "sparse autoencoder" by a short code (`11-res-jb`) from the `sae-lens` library. That code was valid in the old version of the library the author used, but was renamed in later versions, and the version that still has it needs an old PyTorch that clashes with everything else. Untangling that is a rabbit hole, so it's logged as an environment/versioning failure. **Needs you?** No — it's a known kind of "the library moved on" breakage.

## 22. `seq2feature` (patrickod32, "a 5 MB text probe that mimics a 9B SAE") — reproduced (00:50)

The claim: a tiny (5 MB) text-only probe can recover what a giant sparse autoencoder "sees" in text, per concept. We get the headline exactly — the probe scores 0.90 (matching the post), beats a keyword baseline on every concept, and classifies text 88% as well as the real 9-billion-parameter model's 89%. One cosmetic final cell (a Colab file-download) errored harmlessly. **Needs you?** No.

## 23. codi follow-up (R6c) — the recovery mechanism reproduces, magnitude lower (04:35)

The earlier codi headline (which latent vectors hold the intermediate numbers) reproduced. This follow-up checked the secondary "~20% recovery" figure: patching a different intermediate value into the latent makes the model give the correspondingly changed answer 7.0% of the time, vs 6.2% for same/random patches and 1.5% at baseline — the effect points the right way, but at ~7% not the post's ~20% (sensitive to the exact patch settings). The main result stands. **Needs you?** No.

## 24. `llm-typos` (idostik) — mechanism reproduces, exclusivity blocked (05:15)

Which part of a small model fixes a typo like "comptuer"→"computer"? The post says one specific attention head (layer 0, head 3) does the subword merging, and it's the *only* head that matters. We confirmed the head does the merging (its output points straight at the right completion, and switching it off hurts the model). But the final comparison that proves *only* that head matters is in three cells that crashed on a library version mismatch, so the "only" part is unconfirmed. Counted as a partial. **Needs you?** No.

## 25. `super-weight-circuit-patching` (sunmoonron) — out of RAM (05:25)

This one deletes a single critical weight in a 1-billion-parameter model (which wrecks it), then patches it back. The final comparison step loads three full copies of the model at once into main memory (not the graphics card), which needs more than the 31 GB this machine has — it gets killed. Using half-precision would fit but would slightly change the numbers, so I left it. The training steps worked; only the three-way comparison is blocked. **Needs you?** Only if you want it run on a bigger-RAM box.

## 26. `soo-jailbreak-conceptual-fusion` (shivasrightfoot) — method reproduces, ASR% not isolated (05:35)

This is published safety research documenting a jailbreak: a small fine-tune ("conceptual fusion") that makes a model answer harmful requests it would normally refuse. The training ran cleanly and the resulting model does bypass its refusals on the test prompts — so the method reproduces. The specific success-rate number (~20%→~90%) is measured by a separate evaluation notebook (not the training one), and the run used a different retention setting than the headline quotes, so the percentage itself isn't confirmed here. Counted as partial. **Needs you?** No.

## 27. `tarcle` imposter function vectors (star2vec) — H36c — REPRODUCED (recompute)

**ELI5.** A "function vector" is a little direction you can add inside a model to make it do a task
(here: "shift a month forward by k"). This project's claim: vectors that look great when tested on the
SAME narrow set of examples they were built from are *imposters* — on a wider set they fall apart.
We re-ran the author's committed analysis. It reproduced: on the rich 12-month set the vector scores
**+0.35** (good); on the cramped September–December set it scores **−1.00** (total collapse) — exactly
their number. Meanwhile a separate behavioral check says the vectors DO ace the narrow task ("GO") —
which is the whole point: they ace it, then fail to generalise. Imposters, confirmed.

**No human action needed.** Two of the analysis steps "failed" only because the author's code politely
refuses to overwrite its own saved results — the numbers were computed fine. Nothing to fix.

## 28. `sneaky-mamba` (filyp) — H57 — NOT REPRODUCED (build failure, no human action)

**ELI5.** This project asks whether a "Mamba" model (a non-transformer design) can secretly reason step-by-step.
To test it we first have to install a special GPU component ("mamba-ssm") that has to be compiled to match the
exact deep-learning library version on the machine. On this box those versions don't line up, and every way we
tried to build it produced a component that won't load. We tried three different fixes and stopped there (chasing
a fourth wouldn't teach us anything). So we never got to run the actual science.

**Why this still counts.** It's a clean example of the report's main point: this work fails on *plumbing*
(a GPU component that won't compile), not on the *idea*. The repo right next to it (tarcle) reproduced fine
because its authors saved their intermediate results and shipped a plain-CPU re-analysis. **No human action needed.**

## 29. The new direction (2026-08-28, R-1 … R-14) — plain language

A second Claude session took the GPU after the N=36 ledger and asked a different question: not
"does it reproduce?" but "what does a reproduction *depend on*?". Fourteen runs, all written up in
`replication/NEW-DIRECTION.md` (one section per run, decision re-made after each).

What it found, in one breath: a result that matched the author to three decimals was matching
the author's random seed, not the effect (the effect was actually 30% larger); one reproduced
result only comes out on about half of the seeds; the noise-injection sandbagging result works on
about two draws in three and breaks the model one draw in four (the earlier "9 out of 10" was a
lucky batch, and the author's "6 out of 10" was an ordinary one); changing the `transformers`
library version changed *nothing* (35,700 generations byte-identical) while changing torch rewrote
65% of the text but no conclusions; the sandbagging trick does not carry over to Llama-1B because
the "sandbagging" prompt barely works there; six of the seven "couldn't run" rows *could* run once
the environment was reconstructed (three exact, two partial, one behind a Weights & Biases login),
and none of the original diagnoses had named the real cause; a blind test with deliberately
injected bugs was caught 7 times out of 7.

**Decisions taken on your behalf:** nothing was pushed, forked, or sent to authors. All new rows
are `extension` class and do **not** count in the reproduction rate. The `uv` cache (78 GB) and
finished extension environments were deleted to free the disk (nothing of the record was lost).

**Needs you:** nothing blocking. If you want the last `env` row (dajale423) it needs a W&B login,
which I will not create. R-15 (ayoakin, an overnight ~2–4 h job) may be running when you read this;
its verdict goes in `NEW-DIRECTION.md` when a session judges `experiments/…ayoakin--ext-timetravel/`.
