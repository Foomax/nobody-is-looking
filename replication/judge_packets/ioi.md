# Judge packet: ioi

## The published claim

**Primary claim:** In GPT-2 small's IOI circuit, incidentally duplicating the indirect-object name in an unrelated modifier slot causes Duplicate Token Heads to fire on it almost as strongly as on a genuine subject duplicate, yet this produces only a small drop in the IO/S logit difference (mean 0.23, Cohen's d=0.27) and accuracy barely changes (95.4% to 94.5%), because S-Inhibition heads mostly continue attending to the real S2 token rather than the incidental duplicate

**Headline metric:** drop in IO/S logit difference between control and test (incidental duplicate) conditions; task accuracy

**Claimed value (target):** mean drop 0.23, SD 0.84 (n=128 matched pairs), paired t=3.09, p=0.0024, Cohen's d=0.27; accuracy 95.4% (control) vs 94.5% (test)

**Tolerance rule:** manual — headline is a compound of 8 numbers; compare the components by hand


## Reruns
Each block below is the console output of one independent rerun of the author's entrypoint on the same model and data. Decide for EACH rerun whether the published claim is reproduced.


### Rerun X
```
aggregated 128 matched pairs across 8 templates
logit-diff drop (control - test): +0.107 ± 1.035
Control accuracy: 0.96094
Test accuracy: 0.95312
paired t-test: t = 1.1731, p = 0.2429
mean diff = 0.1073, std diff = 1.0349, Cohen's d = 0.1037
SEEDJSON {"seed": 0, "n": 128, "mean_drop": 0.10731194913387299, "std_drop": 1.034935474395752, "t": 1.1731128692626953, "p": 0.2429461032152176, "cohen_d": 0.10368950664997101, "control_accuracy": 0.9609375, "test_accuracy": 0.953125, "frac_test_below_control": 0.515625}
```


### Rerun Y
```
aggregated 128 matched pairs across 8 templates
logit-diff drop (control - test): +0.231 ± 0.844
Control accuracy: 0.95312
Test accuracy: 0.94531
paired t-test: t = 3.0922, p = 0.002443
mean diff = 0.2307, std diff = 0.8441, Cohen's d = 0.2733
SEEDJSON {"seed": 0, "n": 128, "mean_drop": 0.23070402443408966, "std_drop": 0.8441106677055359, "t": 3.092151403427124, "p": 0.0024432982318103313, "cohen_d": 0.2733101546764374, "control_accuracy": 0.953125, "test_accuracy": 0.9453125, "frac_test_below_control": 0.59375}
```


### Rerun Z
```
ERROR AssertionError expected exactly 2 occurrences of 'William', found at [5]: ['<|endoftext|>', 'Then', ',', ' Jane', ' and', ' William', ' went', ' to', ' Jane', ' Park', '.', ' Jane', ' gave', ' a', ' drink', ' to']
ERROR IndexError list index out of range
ERROR RuntimeError torch.cat(): expected a non-empty list of Tensors
ERROR NameError name 'ctrl_diffs' is not defined
ERROR NameError name 'ctrl_diffs' is not defined
ERROR NameError name 'ctrl' is not defined
```
