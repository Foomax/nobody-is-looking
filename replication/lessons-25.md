# lessons-25 — the variance-decomposition / rot-reversal session (2026-08-28, R-1 … R-14)

New, for `lessons-synth` Part 3:

| symptom | cause | fix |
|---|---|---|
| a pinned torch silently becomes the newest torch | a later unconstrained `uv pip install` (e.g. `accelerate`) re-resolves torch | pin torch in the *same* resolver call as everything else, or repeat `torch==X` in every call; check the version line before trusting an arm |
| `--exclude-newer` resolves nothing from the PyTorch index | that index carries no upload timestamps; every wheel is filtered | pin torch exactly from the CUDA index, freeze the rest of the set by date |
| `KeyError: '<sae id>'` in an SAE notebook | an upstream loader `continue`d past a missing local artefact; the KeyError is two cells downstream | read the loader before classifying as registry drift; populate the cache from the public release |
| `KeyError: 'GITHUB_WORKSPACE'` from a research package | this shell exports `CI`; the package then requires CI paths | `unset CI` in the runner |
| `IndexError` deep in a data loop after a successful env | the committed dataset is smaller than the script indexes (author had an uncommitted larger file) | check `len(data)` vs the script's index range before running; deviation on a copy, ledger as partial with n |
| the entrypoint crashes on unpacking a helper's return | code broken at publication (script written against another version of the helper) | fix on a copy only if the extra value is unused; class = `code-bug at HEAD`, not `env` |
| requirements.txt will not resolve at any date | self-contradictory pins (a git dep pins a different major of a listed package) | install the file minus the contradiction, the git dep `--no-deps`; class = `broken lockfile at publication` |
| background tasks killed ~20 s after start while the process is fine | (i) disk below the 25 GB floor — the `uv` cache grows ~5 GB per environment; (ii) harness task limits | `uv cache clean`, delete finished venvs; detach long runs with `setsid nohup` and watch the log, not the task |
| an "exact" 3-decimal reproduction | same RNG seed as the author, not effect precision | re-tier as `exact-same-seed`; a seeded result's honest tier is a rate with an interval |

Confirmed: P2 (entrypoints are pointers — two catalogue entrypoints lacked required positionals), P4 (env-only on copies), P7 (judge the named measure — the tenseisoham "pairwise distance" was perplexity), P13 (the first exception is the shallowest layer; every `env` row this session was an onion).
