# injected bug

config not applied: matryoshka_config n_prefixes 10 -> 1, so the 'Matryoshka' SAE is trained as a vanilla SAE; the comparison code, labels and plots are unchanged

```
- 'n_prefixes': 10,
+ 'n_prefixes': 1,
```
