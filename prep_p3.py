#!/usr/bin/env python3
"""
prep_p3.py -- lay out the inputs for the object-level extraction pass (prompts.md P3, phase 1).

Writes:
  p3/posts/<post_id>.md      one self-contained input file per union post
  p3/batches/batch_NN.json   the post ids each extraction agent is responsible for
  p3/phenomenon_seed.json    a controlled vocabulary agents reuse before inventing a label
  p3/claims/                 (empty) where agents write <post_id>.json

Why per-post files rather than passing text in prompts: 741 posts is ~2.6M tokens of body text.
Files let each agent read only its own slice, and let a re-run target the ids that are missing.

LW's `topic` field is free text and is 635 distinct strings over 637 posts, so it cannot seed a
vocabulary. The seed below is built from the topic instrument in meta.py plus the recurring
subject matter named in the three source readmes; it is a starting point, not a closed list.
"""
import json, os, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
P3 = os.path.join(HERE, "p3")
MAX_WORDS = 9000        # 16 posts exceed this; the tail is appendices and transcripts
MAX_README = 3000       # inspect_evals alone is 117 KB of shared infrastructure docs
BATCH = 25

PHENOMENON_SEED = [
    "sparse autoencoder quality", "SAE feature interpretability", "dictionary learning method",
    "crosscoder / model diffing", "linear probe detection", "probe generalisation",
    "activation steering", "steering vector transfer", "circuit discovery", "activation patching",
    "attribution / attribution patching", "superposition", "polysemanticity",
    "emergent misalignment", "narrow-to-broad misalignment generalisation", "alignment faking",
    "deceptive alignment / scheming", "reward hacking", "specification gaming",
    "reward tampering", "sycophancy", "introspection / self-report accuracy",
    "chain-of-thought faithfulness", "chain-of-thought monitorability", "CoT obfuscation",
    "monitor evasion", "evaluation awareness", "sandbagging", "situational awareness",
    "jailbreaking / adversarial prompting", "adversarial robustness", "red-team elicitation",
    "unlearning", "machine unlearning robustness", "AI control protocols", "untrusted monitoring",
    "agentic task capability", "agent scaffolding", "long-horizon agent behaviour",
    "tool use safety", "multi-agent dynamics", "subliminal / data-mediated trait transfer",
    "synthetic document finetuning effects", "inoculation / mitigation prompting",
    "persona and character generalisation", "model welfare / psychology",
    "benchmark construction", "eval methodology critique", "dataset construction",
    "replication of prior result", "capability forecasting / time horizons",
    "training dynamics", "fine-tuning side effects", "RLHF / preference learning effects",
    "refusal behaviour", "hallucination / calibration", "prompt injection",
    "interpretability tooling", "representation geometry",
]


def main():
    src = os.path.join(HERE, "union.json")
    if not os.path.exists(src):
        print("union.json missing -- run `python3 build_union.py` first", file=sys.stderr)
        return 2
    U = json.load(open(src))["records"]
    for d in ["posts", "batches", "claims"]:
        os.makedirs(os.path.join(P3, d), exist_ok=True)

    ids = sorted(U, key=lambda p: (U[p]["date"], p))
    truncated = 0
    for pid in ids:
        r = U[pid]
        body = r["article-content"] or ""
        words = body.split()
        if len(words) > MAX_WORDS:
            body = " ".join(words[:MAX_WORDS]) + f"\n\n[TRUNCATED at {MAX_WORDS} words of {len(words)}]"
            truncated += 1
        readme = (r["github-readme"] or "")[:MAX_README]
        af = r["af"] or {}
        lw = r["lw"] or {}
        head = {
            "post_id": pid, "date": r["date"], "title": r["title"], "author": r["author"],
            "karma_lw": r["karma_lw"], "word_count": r["word_count"],
            "in_af": r["in_af"], "in_lw": r["in_lw"], "own_repo": r["own_repo"],
            "af_project_type": af.get("project_type_norm"), "lw_topic": lw.get("topic"),
            "lw_confidence": lw.get("confidence"), "dup_cluster_id": r["dup_cluster_id"],
        }
        with open(os.path.join(P3, "posts", f"{pid}.md"), "w") as fh:
            fh.write("<!-- METADATA -->\n```json\n")
            json.dump(head, fh, indent=1)
            fh.write("\n```\n\n<!-- POST BODY -->\n\n")
            fh.write(body)
            if readme:
                fh.write(f"\n\n<!-- GITHUB README ({r['own_repo']}), first {MAX_README} chars -->\n\n")
                fh.write(readme)

    batches = [ids[i:i + BATCH] for i in range(0, len(ids), BATCH)]
    for i, b in enumerate(batches, start=1):
        json.dump({"batch": i, "n": len(b), "post_ids": b},
                  open(os.path.join(P3, "batches", f"batch_{i:02d}.json"), "w"), indent=1)
    json.dump(PHENOMENON_SEED, open(os.path.join(P3, "phenomenon_seed.json"), "w"), indent=1)

    print(f"{len(ids)} post files ({truncated} truncated at {MAX_WORDS} words)")
    print(f"{len(batches)} batches of up to {BATCH}")
    print(f"{len(PHENOMENON_SEED)} seed phenomenon labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
