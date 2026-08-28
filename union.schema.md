# union.json -- schema

741 records, one per distinct post, keyed by ForumMagnum post id. Built by `build_union.py`.
Top level is `{"_meta": {...}, "records": {post_id: record}}`.

## Why this file exists

The Alignment Forum and LessWrong corpora overlap on 149 posts (an AF post *is* an LW post with
the same id). Analyses that pool their headline numbers double-count those posts; analyses that
use either alone use the wrong denominator. This is the denominator.

## Record fields

| Field | Type | Null semantics | Source |
|---|---|---|---|
| `post_id` | str | never null | ForumMagnum id; AF's `url` and LW's `_id` |
| `date` | str `YYYY-MM-DD` | never null | LW if present, else AF (identical on all 149 shared) |
| `title` | str | never null | LW if present, else AF |
| `author` | str | never null | comma-joined, first author first |
| `authors` | list[str] | `[]` only if `author` is empty | split of `author` |
| `word_count` | int | never null | as scraped |
| `karma_lw` | int | never null | **LessWrong baseScore**, not afBaseScore. Age-confounded snapshot. |
| `in_af` / `in_lw` | bool | never null | membership |
| `own_repo` | str `owner/name` lowercase | **null means no *own-project* repo was adjudicated, not that no code exists** (19% of GitHub-mentioning posts land here by design). Also null when the two corpora disagree. | AF/LW adjudication |
| `repo_disagreement` | obj or null | non-null on exactly 1 record | the O2 post; unresolved |
| `dup_cluster_id` | str or null | null for the 735 non-duplicate posts | same-first-author title Jaccard >= 0.6 |
| `article-content` | str | never null | full post body, Markdown. Byte-identical across both scrapes on all 149 shared posts. |
| `github-readme` | str or null | null when no repo or no README | README at fetch time |
| `af` | obj or null | null when `in_af` is false | see below |
| `lw` | obj or null | null when `in_lw` is false | see below |

### `af` sub-object

`url`, `title`, `author`, `karma`, `word_count`, `github_link` (raw URL),
`github_readme_present` (bool), `github_readme_md5`, `github_readme_alt` (the AF README text,
kept only where the two scrapes fetched different text -- 1 post), `content_md5`,
`project_type_raw` (17 raw labels), `project_type_norm` (7 normalised, per
`project_type_map.json`), `additional_github_links` (list; non-empty on 13 posts),
`article_file`.

### `lw` sub-object

`url`, `title`, `author`, `karma`, `word_count`, `github_link`, `github_readme_present`,
`github_readme_md5`, `content_md5`, `topic` (free text, unnormalised -- not groupable without an
embedding pass), `confidence` (`high` 569 / `medium` 39 / `low` 29), `tags` (180 distinct;
every record has at least one; no analysis has used them yet), `github_readme_status`, `file`.

The md5s and the per-corpus scalars are kept so that cross-scrape agreement stays measurable
from this file alone, without re-reading the two source JSONs.

## Loading

```python
import json
U = json.load(open("union.json"))["records"]
shared = [r for r in U.values() if r["in_af"] and r["in_lw"]]        # 149
af     = [r for r in U.values() if r["in_af"]]                        # 253
code   = [r for r in U.values() if r["own_repo"]]                     # 376
```

## Cautions

- `karma_lw` is age-confounded; 2026 medians are biased low. Do not use it as a quality proxy.
- Deduplicate on `dup_cluster_id`, not on `post_id`, before counting projects.
- `own_repo: null` is an adjudication outcome, not evidence that no code exists.
- 2024H2 and 2026H2 are partial periods of the declared scrape window; use per-30-day rates.
- The AF-only records are provably misses of the LW pipeline (AF is a subset of LW-eligible).
  The LW-only records are **not** provably AF misses -- they may never have been promoted.
