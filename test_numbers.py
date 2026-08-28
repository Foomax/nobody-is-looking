#!/usr/bin/env python3
"""
test_numbers.py -- fail if readme.md asserts a [MEASURED] number that no script emits.

readme.md's standing convention is "if you disagree with a claim here, change the script, not the
prose". That convention is unenforceable unless something checks the prose against the script.
This is that check.

What it does
  1. Reads numbers.json (written by meta.py) and collects every numeric leaf.
  2. Splits readme.md into blocks. A block is checked when it carries a [MEASURED] tag, or when
     it is a table immediately following a block that carries one.
  3. Extracts every number from those blocks and asserts each one appears in numbers.json --
     exact for integers, +/-0.05 for one-decimal values, +/-0.5 for values the prose rounds to
     a whole percent.
  4. Numbers that are references (section numbers, years, post ids) are skipped; numbers that are
     legitimately in the prose but not produced by meta.py must be listed, with a reason, in
     test_allowlist.json. An entry there is a standing admission that a figure is not backed by
     the warrant, so keep the list short and read it when it grows.

What it does NOT do -- read this before trusting a PASS
  * It checks membership in a set of values, not that each number is used for the right claim.
    A ratio the prose derives by hand can pass by coinciding with an unrelated stored value, so
    derived quantities (the in-AF contrasts, for instance) are emitted by meta.py under their own
    keys rather than left for the prose to compute.
  * It cannot tell that a correctly-emitted number supports a wrong inference. Most of the
    defects found in the 2026-08-25 review were of that kind: partial periods compared to full
    ones, evidence that is equally likely under the hypothesis and its negation, contrasts drawn
    between the two strata that maximise the gap. No test catches those; review.md's P5 procedure
    is the thing that does.

Usage:  python3 test_numbers.py            # exit 1 on failure
        python3 test_numbers.py --verbose  # also list what matched
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "readme.md")
NUMBERS = os.path.join(HERE, "numbers.json")
ALLOWLIST = os.path.join(HERE, "test_allowlist.json")

# Tokens that carry digits but assert nothing: dates, period labels, cross-references, code
# spans, URLs, model names. They are blanked out before numbers are extracted, so a real claim
# cannot hide inside one.
MASK = [
    re.compile(r"`[^`]*`"),                            # code spans (field names, ids, keys)
    re.compile(r"\]\([^)]*\)"),                        # markdown link targets
    re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b"),         # dates
    re.compile(r"\b\d{4}H[12]\b"),                     # 2026H2
    re.compile(r"§\s*[\d.]+[a-z]?"),                    # §1.3c
    re.compile(r"\b[ROMP]\d+(?:\.\d+)?\b"),            # R1, O10, M7, P4, R0.1
    re.compile(r"\b(?:19|20)\d\d\b"),                  # bare years
    re.compile(r"\b(?:gpt|GPT|Kimi|Llama|Qwen|Gemma|Claude|Gemini|o)[- ]?\S*\d\S*"),  # model names
    re.compile(r"\b[a-z0-9_.-]+/[a-z0-9_.-]+\b"),       # owner/repo
    re.compile(r"\bκ\s*=?\s*[\d.]+"),                  # kappa values live in prose about R2
    re.compile(r"\b\d+\s*KB\b"),                       # file sizes are checked via sources.*.kb
]
NUM = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)")


def numeric_leaves(obj, out):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.add(round(float(obj), 4))
    elif isinstance(obj, dict):
        for v in obj.values():
            numeric_leaves(v, out)
    elif isinstance(obj, list):
        for v in obj:
            numeric_leaves(v, out)


def blocks(text):
    """(line_no, block_text) for each blank-line-separated block."""
    out, cur, start = [], [], 1
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            if not cur:
                start = i
            cur.append(line)
        elif cur:
            out.append((start, "\n".join(cur)))
            cur = []
    if cur:
        out.append((start, "\n".join(cur)))
    return out


def measured_blocks(text):
    bs = blocks(text)
    keep, prev_measured = [], False
    for ln, b in bs:
        is_table = b.lstrip().startswith("|")
        if "[MEASURED]" in b or (is_table and prev_measured):
            keep.append((ln, b))
        if not is_table:
            prev_measured = "[MEASURED]" in b
    return keep


def check(verbose=False):
    if not os.path.exists(NUMBERS):
        print("numbers.json missing -- run `python3 meta.py` first", file=sys.stderr)
        return 2
    known = set()
    numeric_leaves(json.load(open(NUMBERS)), known)
    allow = json.load(open(ALLOWLIST)) if os.path.exists(ALLOWLIST) else {}
    allowed = {float(k.replace(",", "").rstrip("%")) for k in allow}

    text = open(README).read()
    missing, checked = [], 0
    for ln, b in measured_blocks(text):
        masked = b
        for rx in MASK:
            masked = rx.sub(lambda m: " " * len(m.group(0)), masked)
        for m in NUM.finditer(masked):
            raw = m.group(1)
            val = float(raw.replace(",", ""))
            checked += 1
            if val in allowed:
                continue
            if val in known:
                continue
            # one-decimal tolerance, and whole-percent rounding of a 1dp stored value
            if any(abs(val - k) <= 0.05 for k in known):
                continue
            if "." not in raw and any(abs(val - k) < 0.5 for k in known):
                continue
            line_txt = b.splitlines()[masked[:m.start()].count("\n")].strip()
            missing.append((ln, raw, line_txt[:96]))

    print(f"checked {checked} numbers in {len(measured_blocks(text))} [MEASURED] blocks "
          f"against {len(known)} distinct values in numbers.json")
    if allow:
        print(f"allowlisted: {len(allow)} values ({', '.join(sorted(allow))})")
    if missing:
        print(f"\nFAIL -- {len(missing)} number(s) tagged [MEASURED] are not in numbers.json:\n")
        for ln, raw, ctx in missing:
            print(f"  readme.md:{ln}  {raw:>12}   {ctx}")
        print("\nEither emit the number from meta.py, re-tier the claim, or add it to "
              "test_allowlist.json with a reason.")
        return 1
    print("\nPASS -- every [MEASURED] number in readme.md is emitted by meta.py")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    sys.exit(check(ap.parse_args().verbose))
