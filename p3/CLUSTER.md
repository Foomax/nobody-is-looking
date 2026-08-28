# Orphaned-lead clustering (prompts.md P3 phase 2, item 6 / corpus-analysis.md R9)

Input: `p3/leads/chunk_N.json` — a list of `{idx, post_id, date, repo, lead}` objects. Each `lead`
is a "future work" item stated by the authors of a post in the AI-safety corpus and, as far as
anyone knows, never executed.

Your job: assign each lead a **theme** so that leads proposed independently by different posts
land in the same bucket. The signal we are looking for is *the same research idea proposed by
several abandoned projects* — that is a strong indicator the field wants it and nobody did it.

Write `/home/user/alignment-literature-meta-analysis/p3/leads/themed_N.json`:

```json
[{"idx": 0, "post_id": "...", "theme": "...", "scope": "narrow|moderate|broad",
  "kind": "scale-up|new-domain|ablation|robustness-check|method-extension|tooling|validation|other"}]
```

Rules:
- **`theme`**: ≤6 words, generic enough that a similar proposal from a different post would get the
  same string. "test on larger models" not "test on Llama-3.3-70B next". Reuse your own earlier
  themes aggressively — a theme used once is nearly useless to us. Aim for **under 60 distinct
  themes for your whole chunk**.
- **`scope`**: `narrow` = an afternoon; `moderate` = days-to-weeks; `broad` = a research programme.
- **`kind`**: what type of follow-up it is.
- Output one entry per input lead, same `idx`. Do not drop any.
- Valid JSON. No markdown fences. Write only to your `themed_N.json`.

Reply with: chunk number, count, and your 15 most-used themes with counts.
