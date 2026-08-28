# injected bug

variable swap: the 'incidental duplicate' inserted into the test prompt is the S name instead of the IO name (a one-token slip in the matched-pair generator); every downstream statistic is computed unchanged

```
- test_text = fill(f\"{io_name} {place_noun}\")
+ test_text = fill(f\"{s_name} {place_noun}\")
```
