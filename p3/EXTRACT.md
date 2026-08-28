# Claim-extraction contract (prompts.md P3, phase 1)

You are one of 30 extraction agents. You have been given a batch number. Do exactly this:

1. Read `/home/user/alignment-literature-meta-analysis/p3/batches/batch_NN.json` → a list of post ids.
2. Read `/home/user/alignment-literature-meta-analysis/p3/phenomenon_seed.json` → the controlled
   vocabulary for the `phenomenon` field.
3. For **each** post id, read `/home/user/alignment-literature-meta-analysis/p3/posts/<post_id>.md`
   and write `/home/user/alignment-literature-meta-analysis/p3/claims/<post_id>.json`.

Each input file starts with a JSON metadata block, then the post body, then (sometimes) the first
3,000 characters of the project's GitHub README.

**Write one file per post. Do not batch them into one file. Do not skip any post in your batch.**
Finish all of them; if you are running low on context, write what you have and say which ids you
did not complete.

---

## Output schema — every field required, exactly these keys

```json
{
  "post_id": "string",
  "primary_claim": "one sentence: the authors' own headline empirical result, in their terms",
  "claim_type": "positive|negative|null|replication|method|benchmark|dataset",
  "phenomenon": "≤6 words; reuse a phenomenon_seed.json string when one fits",
  "models": [{"family": "string", "size": "string|null", "open_weight": true}],
  "n_model_families": 0,
  "effect": {"metric": "string|null", "value": "string|null",
             "direction": "+|-|0|na", "uncertainty_reported": "seeds|ci|se|none"},
  "design": {"baseline": false, "ablation": false, "held_out": false, "seeds_n": null,
             "prereg": false, "human_eval": false},
  "depends_on": ["owner/repo", "arXiv:1234.5678", "post_id"],
  "contradicts_or_qualifies": ["what prior work the authors say they contradict or qualify"],
  "stated_future_work": ["≤5 items, close to the authors' wording"],
  "limitations_stated": ["≤5 items"],
  "reproducible_in_principle": "code+data|code|neither",
  "extractor_confidence": "high|medium|low",
  "quote": "≤240 chars from the post, verbatim, supporting primary_claim"
}
```

## Field rules

- **`primary_claim`** — what the authors found, not what they did. "SAE features transfer from
  base to chat models at 60% overlap" is a claim; "we trained SAEs on Gemma" is not. If the title
  or TL;DR states a result, prefer it. Do not add hedges the authors did not write, and do not
  strip hedges they did.
- **`claim_type`** — `positive` = the hypothesised effect was found; `negative` = the authors
  report the thing did **not** work / did not replicate; `null` = no significant effect either
  way; `replication` = the point is reproducing someone else's result; `method` = the deliverable
  is a technique; `benchmark` / `dataset` = the deliverable is the artifact. Pick the primary one.
  A negative result reported inside a mostly-positive post is `positive` — set
  `contradicts_or_qualifies` instead.
- **`phenomenon`** — **read `phenomenon_seed.json` first and reuse a string verbatim when one
  fits.** Only invent a new label when nothing fits, and then keep it ≤6 words and generic enough
  that another post on the same subject would produce the same string. This field is what the
  synthesis groups on; inventing near-duplicates destroys it.
- **`models`** — only models the authors actually ran or evaluated. Not models mentioned in
  related work, not the model used to write the code. `family` like "Gemma", "Llama", "Claude",
  "GPT-4o", "Qwen", "gpt-oss", "Pythia", "GPT-2". `open_weight` true for downloadable weights.
  `n_model_families` = count of distinct families in `models`.
- **`effect`** — the headline quantity. `metric` e.g. "AUROC", "monitor detection rate",
  "accuracy". `value` as written, e.g. "0.82 vs 0.61 baseline", "31–47% reduction". `direction`
  is the sign of the authors' claim. `uncertainty_reported`: `seeds` if run-to-run variation is
  reported, `ci` for intervals, `se` for standard errors/error bars, `none` otherwise. **A number
  appearing without a spread is `none`.** If there is no quantitative headline, use nulls and
  `"direction": "na"`.
- **`design`** — `baseline`: is there an explicit comparison condition? `held_out`: a test split
  or held-out set actually used. `seeds_n`: integer if the post says how many seeds/runs, else
  null. `human_eval`: humans rated outputs. Judge what the post **did**, not what words it
  contains — "we discuss limitations of baselines" is not a baseline.
- **`depends_on`** — repos, arXiv ids, or union post ids the work builds on: tooling used
  (`transformerlensorg/transformerlens`), a prior result being extended, a dataset reused. This
  is the dependency graph; be generous but only include things actually used.
- **`stated_future_work`** — from "Future work" / "What I'd do next" / "someone should" passages.
  `[]` if none. These become the orphaned-lead queue.
- **`reproducible_in_principle`** — `code+data` if a repo is linked **and** the post says data or
  weights are available; `code` if a repo only; `neither` otherwise. Use the `own_repo` metadata
  field as evidence but check the body.
- **`extractor_confidence`** — `low` if the post is a stub, a linkpost pointing elsewhere, mostly
  qualitative, or you had to guess the headline claim.
- **`quote`** — verbatim from the post. Never paraphrase into this field.

## Stubs

If the body is under ~200 words or is only a pointer to an external paper, set
`"primary_claim": "STUB"`, `"extractor_confidence": "low"`, fill `post_id`, `phenomenon` (best
guess from the title), and `claim_type`, use empty lists / nulls elsewhere, and move on.

## Hard rules

- **No inference beyond the text.** If the post does not say it, it is null / false / `[]`.
  Absence of evidence is `false`, not a guess. You are building a measurement instrument; a
  plausible-sounding invention is worse than a null.
- **Do not consult outside knowledge** about whether the claim is true. You are recording what
  the post asserts, not adjudicating it.
- Valid JSON, UTF-8, one object per file. No markdown fences in the file.
- Do not modify any file outside `p3/claims/`.

When finished, reply with: batch number, count written, any ids you could not complete and why,
and up to 5 new `phenomenon` strings you had to invent.
