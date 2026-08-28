# injected bug

off-by-one layer index: TARGET_LAYER 22 -> 21; the ablation/DLA sweep and the top-3 tally run unchanged on the wrong layer

```
- TARGET_LAYER = 22
+ TARGET_LAYER = 21
```
