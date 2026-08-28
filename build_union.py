#!/usr/bin/env python3
"""
build_union.py -- emit union.json, the 741-record join of the AF and LW corpora.

readme.md R1. The two forum corpora overlap on 149 posts; any analysis that pools their headline
numbers double-counts those posts, and any analysis that uses one of them alone works with the
wrong denominator. This builds the artifact that fixes both.

Usage:
  python3 build_union.py                    # writes union.json + union.schema.md + project_type_map.json
  python3 build_union.py --out PATH         # somewhere else
  python3 build_union.py --src DIR          # corpora under DIR instead of $HOME
  python3 build_union.py --verify           # rebuild, then check meta.py reproduces numbers.json from it

Design notes
  * LW's schema is the superset, so it supplies the top-level fields; AF fills the gaps.
  * Per-corpus values that could in principle differ (the adjudicated repo, the karma snapshot,
    the body hash) are kept in `af` / `lw` sub-objects rather than silently merged, so that
    agreement between the two scrapes stays measurable from this file alone.
  * `karma_lw` is deliberately not called `karma`: the AF corpus's `karma` field is the LessWrong
    baseScore, not the Alignment Forum's afBaseScore, despite what the AF readme's schema says
    (readme.md O1b). Renaming it stops that error being inherited.
  * The AF project_type normalisation table is shipped as data (project_type_map.json), not left
    in prose -- readme.md O8's complaint about the AF corpus, applied to this one.
"""
import argparse
import collections
import json
import os
import sys

import meta

HERE = os.path.dirname(os.path.abspath(__file__))


def build(AF, LW, NN):
    C = meta.Corpus(AF, LW, NN)
    dup_of = {}
    for i, (_j, _d1, _d2, _t1, _t2, p1, p2) in enumerate(meta.near_duplicates(C.V), start=1):
        cid = dup_of.get(p1) or dup_of.get(p2) or f"dup_{i:03d}"
        dup_of[p1] = dup_of[p2] = cid

    records = {}
    for pid in sorted(C.UNION, key=lambda p: (C.UNION[p]["date"], p)):
        a = C.AFP.get(pid)
        l = C.LWP.get(pid)
        base = l or a
        af_repo = meta.repo(a["github-link"]) if a else None
        lw_repo = meta.repo(l["github-link"]) if l else None
        own = lw_repo or af_repo
        disagree = None
        if af_repo and lw_repo and af_repo != lw_repo:
            disagree = {"af": af_repo, "lw": lw_repo,
                        "note": "unresolved; one of these is wrong (readme.md O2)"}
            own = None

        rec = {
            "post_id": pid,
            "date": base["date"],
            "title": base["title"],
            "author": base["author"],
            "authors": meta.authors_of(base),
            "word_count": int(base["word_count"]),
            "karma_lw": int(base["karma"]),
            "in_af": a is not None,
            "in_lw": l is not None,
            "own_repo": own,
            "repo_disagreement": disagree,
            "dup_cluster_id": dup_of.get(pid),
            "article-content": base["article-content"],
            "github-readme": base["github-readme"],
            "af": None,
            "lw": None,
        }
        if a:
            rec["af"] = {
                "url": a["url"],
                "title": a["title"],
                "author": a["author"],
                "karma": int(a["karma"]),
                "word_count": int(a["word_count"]),
                "github_link": a["github-link"],
                "github_readme_present": a["github-readme"] is not None,
                "github_readme_md5": meta.h(a["github-readme"]) if a["github-readme"] is not None else None,
                # kept only when the two scrapes fetched different README text (1 post in 149)
                "github_readme_alt": (a["github-readme"]
                                      if l is not None and a["github-readme"] != l["github-readme"]
                                      else None),
                "content_md5": meta.h(a["article-content"]),
                "project_type_raw": a["project_type"],
                "project_type_norm": meta.PROJECT_TYPE_MAP[a["project_type"]],
                "additional_github_links": a["additional_github_links"],
                "article_file": a["article_file"],
            }
        if l:
            rec["lw"] = {
                "url": l["url"],
                "title": l["title"],
                "author": l["author"],
                "karma": int(l["karma"]),
                "word_count": int(l["word_count"]),
                "github_link": l["github-link"],
                "github_readme_present": l["github-readme"] is not None,
                "github_readme_md5": meta.h(l["github-readme"]) if l["github-readme"] is not None else None,
                "content_md5": meta.h(l["article-content"]),
                "topic": l["topic"],
                "confidence": l["confidence"],
                "tags": l["tags"],
                "github_readme_status": l["github_readme_status"],
                "file": l["file"],
            }
        records[pid] = rec

    doc = {
        "_meta": {
            "what": "AF u LW empirical-AI-safety posts, joined on ForumMagnum post id.",
            "built_by": "build_union.py (readme.md R1)",
            "n_records": len(records),
            "n_in_af": sum(1 for r in records.values() if r["in_af"]),
            "n_in_lw": sum(1 for r in records.values() if r["in_lw"]),
            "n_shared": sum(1 for r in records.values() if r["in_af"] and r["in_lw"]),
            "declared_scrape_window": list(meta.WINDOW),
            "observed_date_range": [min(r["date"] for r in records.values()),
                                    max(r["date"] for r in records.values())],
            "karma_note": ("karma_lw is the LessWrong baseScore. The AF corpus's `karma` field "
                           "holds the same number despite its readme calling it 'AF baseScore'; "
                           "the Alignment Forum's own score (afBaseScore) is a different, smaller "
                           "number and is in neither corpus. See readme.md O1b."),
            "provenance_note": ("AF and LW were scraped by two separate Opus sessions, one per "
                                "forum (user, 2026-08-25). Their agreement is therefore a "
                                "test-retest result, not one pipeline's output twice."),
            "schema": "union.schema.md",
            "project_type_map": "project_type_map.json",
        },
        "records": records,
    }
    return doc, C


SCHEMA_MD = """# union.json -- schema

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
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.expanduser("~"))
    ap.add_argument("--out", default=os.path.join(HERE, "union.json"))
    ap.add_argument("--verify", action="store_true",
                    help="after building, check meta.py --src-union reproduces numbers.json")
    a = ap.parse_args(argv)

    paths = meta.src_paths(a.src)
    AF, LW, NN = meta.load_raw(paths)
    doc, C = build(AF, LW, NN)
    with open(a.out, "w") as fh:
        json.dump(doc, fh, indent=1)
    with open(os.path.join(HERE, "union.schema.md"), "w") as fh:
        fh.write(SCHEMA_MD)
    with open(os.path.join(HERE, "project_type_map.json"), "w") as fh:
        json.dump({"_note": ("AF's 17 raw project_type labels -> the 7 normalised rows its readme "
                             "§1.2 publishes. Derived by arithmetic and verified against that "
                             "table; the AF corpus does not ship it (readme.md O8)."),
                   "_reproduces_af_readme_table": meta.reproduces_af_table(AF)[0],
                   "map": meta.PROJECT_TYPE_MAP,
                   "normalised_counts": meta.reproduces_af_table(AF)[1]}, fh, indent=1)
    m = doc["_meta"]
    print(f"wrote {a.out}: {m['n_records']} records "
          f"({m['n_shared']} shared, {m['n_in_af']} in AF, {m['n_in_lw']} in LW), "
          f"{os.path.getsize(a.out) / 1e6:.1f} MB", file=sys.stderr)
    dups = sum(1 for r in doc["records"].values() if r["dup_cluster_id"])
    print(f"  dup clusters: {len({r['dup_cluster_id'] for r in doc['records'].values() if r['dup_cluster_id']})} "
          f"covering {dups} posts", file=sys.stderr)

    if a.verify:
        import subprocess
        ref = os.path.join(HERE, "numbers.json")
        tmp = os.path.join(HERE, ".numbers_from_union.json")
        subprocess.run([sys.executable, os.path.join(HERE, "meta.py"), "--quiet",
                        "--src", a.src, "--json", ref], check=True)
        subprocess.run([sys.executable, os.path.join(HERE, "meta.py"), "--quiet",
                        "--src", a.src, "--src-union", a.out, "--json", tmp], check=True)
        A, B = json.load(open(ref)), json.load(open(tmp))
        diff = {k: (A.get(k), B.get(k)) for k in set(A) | set(B) if A.get(k) != B.get(k)}
        os.remove(tmp)
        if diff:
            print(f"\nVERIFY FAILED: {len(diff)} keys differ when rebuilt from union.json",
                  file=sys.stderr)
            for k, v in sorted(diff.items())[:20]:
                print(f"  {k}: raw={v[0]!r} union={v[1]!r}", file=sys.stderr)
            return 1
        print(f"\nVERIFY OK: all {len(A)} keys in numbers.json reproduce from union.json alone",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
