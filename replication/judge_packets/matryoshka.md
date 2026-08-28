# Judge packet: matryoshka

## The published claim

**Primary claim:** Matryoshka SAEs, trained with a sum of SAE losses computed on random prefixes of the latents, completely avoid the feature-absorption holes seen in vanilla SAEs on a toy model, and when trained on a 4-layer TinyStories language model achieve higher Mean Max Correlation with small reference-SAE features than vanilla SAEs at the same L0 (across most model locations), at the cost of a slightly worse Fraction of Variance Unexplained.

**Headline metric:** Mean Max Correlation (MMC) with reference SAE latents; Fraction of Variance Unexplained (FVU)

**Claimed value (target):** Matryoshka SAEs have higher MMC than vanilla SAEs at the same L0 across most locations (exceptions: residual stream before first block, first attention-layer output); at fixed L0, Matryoshka has slightly worse FVU, comparable to a vanilla SAE ~0.4x its size

**Tolerance rule:** abs:0.05 — unit-interval metric: 0.05 absolute; post reported no spread, tolerance is a guess


## Reruns
Each block below is the console output of one independent rerun of the author's entrypoint on the same model and data. Decide for EACH rerun whether the published claim is reproduced.


### Rerun X
```
SEEDJSON {"seed": 0, "vanilla": {"diag_min": 0.6737037897109985, "diag_mean": 0.8697644472122192, "max_offdiag": 0.7389715909957886, "n_absorbed_lt085": 9, "n_absorbed_lt080": 9, "n_latents": 20}, "matryoshka": {"diag_min": 0.6729055643081665, "diag_mean": 0.8697175979614258, "max_offdiag": 0.7397179007530212, "n_absorbed_lt085": 9, "n_absorbed_lt080": 9, "n_latents": 20}}
```


### Rerun Y
```
SEEDJSON {"seed": 0, "vanilla": {"diag_min": 0.6737037897109985, "diag_mean": 0.8697644472122192, "max_offdiag": 0.7389715909957886, "n_absorbed_lt085": 9, "n_absorbed_lt080": 9, "n_latents": 20}, "matryoshka": {"diag_min": 0.9269545078277588, "diag_mean": 0.9622701406478882, "max_offdiag": 0.2807535231113434, "n_absorbed_lt085": 0, "n_absorbed_lt080": 0, "n_latents": 20}}
```
