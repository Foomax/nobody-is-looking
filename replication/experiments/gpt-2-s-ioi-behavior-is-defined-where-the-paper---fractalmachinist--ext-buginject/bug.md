# injected bug

variable swap: the 'incidental duplicate' inserted into the test prompt is the S name instead of the IO name (a one-token slip in the matched-pair generator); every downstream statistic is computed unchanged

```
- test_text = fill(f\"{io_name} {place_noun}\")
+ test_text = fill(f\"{s_name} {place_noun}\")
```

# second injected bug (bug2) -- silent variant

wrong word list for the control modifier: a third *name* (not IO, not S) instead of a place-name word, so the control prompt also carries a distractor name and the matched pair is no longer matched on 'name vs non-name'. Passes the author's input assertions; every statistic is computed unchanged.

```
- mod = _rng.choice(NAMEABLE_PLACE_NAMES)
+ mod = _rng.choice([n for n in NAMES if n not in (io_name, s_name)])
```
