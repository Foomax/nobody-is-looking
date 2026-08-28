# Nobody Is Checking

*What 741 posts of empirical AI-safety research look like from above.*

---

# Human

## I. The advisor who never writes first

Start with a name that appears more often than any other in two years of empirical AI-safety
writing, and then notice what he never does.

Neel Nanda is an author on 52 of the 728 posts in this corpus — one in fourteen. He is the first
author on none of them. He is not alone in this. Arthur Conmy: eighteen posts, first author on
one. Senthooran Rajamanoharan: twenty-three, first author on two. StefanHex: sixteen, first author
on one. There is a whole stratum of people whose fingerprints are all over this literature and
whose names never lead it.

Underneath them is the opposite phenomenon, and it is enormous. Five hundred people first-authored
something in this corpus. Three hundred and seventy of them did it exactly once — 74%. They wrote
a post, and then, as far as this corpus knows, they were gone.

That is the shape of the thing. A small permanent staff, an immense transient population, and
between them a body of work that grew to 741 posts in twenty-four months. It is not a field
organised like a discipline. It is organised like a city that people pass through.

You can see the consequences everywhere once you know to look for them. The corpus names 1,819
distinct things it builds on — papers, repos, datasets. Fifteen hundred of them are cited exactly
once. It labels itself with 180 human-chosen tags, 66 of which are used once, and 130
LLM-assigned phenomena, 70 of which are used once. Four different vocabularies, built by four
different processes, all producing the same picture: a very small shared core and a tail that goes
on forever.

## II. What everyone does, and what almost nobody does

Read enough of these posts and a template emerges. Nine in ten name a comparison condition. Nine
in ten admit at least one limitation — the median post admits three. Eight in ten propose future
work, again three items, again with a striking uniformity. Two in three run an ablation.

Then look at what holds the conclusions up.

One post in five reports any measure of uncertainty at all. One in seven says how many random
seeds it ran. One in ten uses human evaluation. One in fifty pre-registers anything.

Score each post out of six on those markers and the median comes out at two. Forty-one posts score
zero. Three score five. **Not one post in 728 scores six.**

This is the pattern that should keep people up at night, and it is not a story about carelessness.
Everyone has learned the form of an empirical report — the comparison, the caveat, the honest
limitations section — and almost nobody has adopted its statistics. The genre has converged. The
inference has not. A field can look extremely rigorous, in the sense of *sounding* like careful
science on every page, while being unable to tell you whether any given result would survive a
different random seed.

If you wanted to change one thing about this literature, it would not be a topic. It would be that
13.7%.

## III. Two tribes

Split the corpus by who wrote each post — one person, or several — and almost every methodological
habit splits with it, in a way that is more interesting than "teams are better."

Solo researchers ship code 68% of the time. Teams ship code 53% of the time.

Teams run ablations 74% of the time. Solo researchers, 59%. Teams state a baseline 95% of the
time, report uncertainty 24% of the time, and position their work against prior literature 71% of
the time. On every one of those, the solo researcher is eight to fifteen points behind. And team
posts earn a median of 45 karma against the solo researcher's 15.

So: **solo work is more open and less controlled. Team work is more controlled and less open.**

The likely reason is money, in the form it takes here — model access. The solo researcher runs
Gemma on one GPU and can hand you the repo. The team runs a sweep across frontier models through
an API, has the person-hours for the ablations, and has nothing runnable to hand over even if it
wanted to.

Which brings us to the pattern that took the longest to see and matters most.

## IV. The inversion

Sort all 728 posts by karma and walk up the deciles, asking one question: did this post ship code?

The bottom decile: 75%. The third: 66%. The eighth: 48%. The top decile — the posts everyone read,
the ones that got 106 to 501 points — **47%**.

The best-read work in empirical AI safety is its least reproducible work, and the gradient is
smooth the whole way up.

The natural cynical reading is wrong, though, and the data says so. This is not fame making people
lazy. Split the corpus by whether a post studies an open-weight model, and the gradient nearly
disappears among the open-weight posts (73% at the bottom, 63% at the top) while it collapses among
the closed-model ones — from 66% at the bottom to **31%** at the top.

The chain runs: the questions that get attention are questions about frontier model behaviour.
Frontier models live behind an API. Work behind an API cannot ship you something you can run.
Karma is not causing anything. It is a marker for a topic class — and that topic class is the
interesting one and the unverifiable one at the same time.

Look at the very top of the distribution and it stops being abstract. Here are the highest-karma
posts in the corpus that shipped neither code nor data: *How Does A Blind Model See The Earth?*
(501 points). *Alignment Faking in Large Language Models* (494). *Emergent Misalignment* (336).
*Tracing the Thoughts of a Large Language Model* (308). *Natural emergent misalignment from reward
hacking in production RL* (260).

Three of those are among the most-depended-on works in the entire corpus. Alignment Faking is
cited by 22 other posts here. Emergent Misalignment by 23. These are the load-bearing beams. They
are also, by the corpus's own account of itself, the parts nobody outside the original lab can
check.

Meanwhile, of 728 posts, **24 are replications**. Twenty-three different people wrote them. Exactly
one person in this entire literature has done it twice.

## V. Four people worth knowing

The averages hide the individuals, and a few of them are doing something no one else is.

**chanind** first-authored eleven posts in eighteen months, every one of them about sparse
autoencoders — and four of the eleven are negative results about sparse autoencoders. *A is for
Absorption.* *Broken Latents.* *The "Sparsity vs Reconstruction Tradeoff" Illusion.* One person,
one method, a third of the output spent attacking it, against a field-wide negative rate of 21%.
It is the closest thing in 728 posts to a sustained adversarial program inside a subfield, and it
is one guy.

**Håvard Tveit Ihle** published five posts, all of them the same benchmark — WeirdML — measured
again and again from January 2025 to May 2026. In a corpus where 74% of authors appear once, this
is nearly the only instrument anyone bothered to read twice.

**Realmbird** published seven posts, four of them titled *Latent Reasoning Sprint #1* through *#4*.
It is a lab notebook, in public, in order. Any automated pipeline counts it as four papers. Any
human reads it as one project that got somewhere.

And then there is **Chijioke Ugwuanyi**, who is here for a duller reason: they wrote one of the 24
replications. *Replication of Koorndijk (2025).* It got nine karma.

## VI. The four lonely objections

The most useful thing in this dataset is also the smallest. Group the posts by what they are about,
and look for a topic where the field has reached a consensus — every post pointing the same way —
except for exactly one.

There are four.

Thirteen posts on crosscoders and model diffing, all positive but one: *What We Learned Trying to
Diff Base and Chat Models*, at 106 karma. Five on inoculation prompting, one dissent at 48. Five on
multi-agent dynamics, one dissent at 15. Four on steering-vector transfer, one dissent — *Steering
Gemini with BiDPO* — at 104.

These are not the field's open questions. Its open questions are elsewhere and are genuinely
50/50: on AI control protocols, twelve posts say the protocols work and twelve say they don't,
written by twenty-eight different first authors, and nobody has run the experiment that reconciles
them. That is a field disagreeing, which is healthy.

The four lone dissenters are something else. They are places where twelve people agree, one person
objected, a hundred people read the objection, and then everyone carried on. That is either a
robust finding surviving a flawed challenge, or a literature that has stopped listening. From the
outside, those look identical. From the inside, one experiment each would tell you which — and the
largest of them, the crosscoder question, runs on open models small enough to fit on a gaming GPU.

## VII. What the shape means

It would be easy to end this cynically, and it would be wrong.

The rigor markers are rising, and not marginally: across four full half-year periods, code release
went from 53% to 60% and baseline reporting from 84% to 92%. The most recent partial window looks
better still, though it is 56 days long and should not be trusted yet. The MATS cohort — 72 posts
from a structured mentorship program — reports seeds at nearly twice the rate of everyone else,
98.6% of them state a baseline, and if that is teaching rather than selection, it is the cheapest
intervention anybody in this dataset has demonstrated.

And the negative results are there. One post in five reports something that didn't work, and that
rate is astonishingly stable — it does not change with venue, or cohort, or team size, or
attention, or model access, or length. Nothing about who you are or where you publish predicts
whether you'll report a null. The only thing that seems to predict it is the question you asked.
For a young field with no publication gatekeeping, that is not a bad property to have.

What the field lacks is not honesty. Its posts are conspicuously honest — 89% list their own
limitations. What it lacks is the second half of the loop. Two thirds of these posts position
themselves against prior work. One in thirty checks it. Disagreements enter the literature far
faster than anything removes them, and they accumulate in exactly the places most people are
reading.

Nobody is checking. Not because anybody is dishonest, but because checking is the one job in this
field that no one has taken.

---

# LLM

Structured restatement. Corpus: 741 union posts, 738 projects after deduplication, **728
substantive records**. Source: `results.md`; numbers emitted by `analyze.py` into
`analysis_numbers.json`. Tiers per `corpus-analysis.md`.

## Provenance

- The claim records are one LLM judge's reading of each post's self-report. `[UNRESOLVED]` No
  human has validated the instrument (`prompts.md` P4 is the design that would).
- `reproducible_in_principle` = "the post states code/data exist", not "the code runs".
- `karma_lw` is an age-confounded snapshot; karma contrasts are stratified by period in
  `results.md` §7.
- The `tags` axis covers 630/728 = 86.5%; the 98 uncovered are exactly the AF-only posts.
- **0 of 87 replication specs have been executed.** No claim below is independently verified.

## Findings

1. `[MEASURED]` **Long-tail structure, confirmed by four independent vocabularies.** Tags: 180
   distinct, 66 used once. Phenomena: 130 distinct, 70 used once. Dependencies: 1,819 distinct,
   83.1% cited once. First authors: 500 distinct, 74.0% appear once. Gini of first-authorship
   0.259.

2. `[MEASURED]` **Presentation markers are near-universal; inference markers are rare.**
   Baseline 90.7% [88.3, 92.6] · limitations 89.1% · future work 81.3% · ablation 66.3% ·
   ships code 60.7% [57.1, 64.2] · held-out 34.3% · **uncertainty reported 19.4% [16.7, 22.4]** ·
   **seeds reported 13.7% [11.4, 16.4]** · human eval 9.8% · pre-registration 2.2%.
   Design-marker score (0–6): median 2; 41 posts score 0; 3 score 5; **0 score 6**.

3. `[MEASURED]` **Solo (384) vs team (344).** Ships code 68.0% vs 52.6% (z = +4.23); baseline
   86.7% vs 95.1% (z = −3.86); ablation 59.4% vs 74.1% (z = −4.21); uncertainty 15.1% vs 24.1%
   (z = −3.08); median karma 15 vs 45.5; median model families 1 vs 2.
   `[INFERRED]` Openness and control trade off along a resource axis.

4. `[MEASURED]` **Attention is inversely related to reproducibility.**
   Spearman(karma, ships-code) = −0.149, n = 728. Code release by karma decile: 75.0% (d1) →
   46.6% (d10). Top vs bottom karma quartile 52.2% vs 70.5%, z = −3.6.

5. `[MEASURED]` **The mediator is model access.** Open-weight share falls 86.2% → 56.8% across
   karma quintiles. Within open-model posts the karma gradient is 72.5% → 62.9% (z = −1.67);
   within closed-model posts it is **66.0% → 31.4% (z = −3.48)**. The gradient inverts inside
   interpretability-tagged posts (70.4% vs 67.3%).
   `[INFERRED]` Causal chain: high-attention questions concern frontier behaviour → frontier
   behaviour is API-gated → API work cannot ship a runnable artifact.
   `[INFERRED]` **Ranking replication candidates by attention selects against runnability.**

6. `[MEASURED]` **Reproducibility hole at the top.** Highest-karma posts shipping neither code nor
   data: 501, 494, 336, 318, 308, 284, 278, 260 karma. Three are top-25 dependencies —
   `arXiv:2502.17424` (in-degree 23), `arXiv:2412.14093` (22), `arXiv:2507.14805` (9).

7. `[MEASURED]` **Replication is not a role.** 24 replication posts; 23 distinct first authors;
   maximum 2 by one person. Against 64.1% of posts positioning against prior work.

8. `[MEASURED]` **Model landscape.** 211 families named. Most-studied: Claude 24.9% (closed),
   Llama 23.8%, Qwen 20.7%, Gemma 15.8%, Gemini 13.7%. ≥1 open model 72.1% [68.7, 75.3];
   all-open 47.7%; single-family 39.1%; median families 2.
   `[INFERRED]` Interpretability is the monoculture (median 1 family); evaluation is the sweep
   (median 3).

9. `[MEASURED]` **AF membership is a prestige filter, not a quality filter.** In-AF vs LW-only:
   median karma 57 vs 18; ships code 51.0% vs 65.6% (z = −3.81); negative rate 20.0% vs 21.7%
   (z = −0.54); seeds and uncertainty indistinguishable.
   `[INFERRED]` Reproduces `corpus-analysis.md` M2 with a different instrument.

10. `[MEASURED]` **MATS cohort (72) is methodologically distinct.** Baseline 98.6% vs 89.8%
    (z = +2.44); seeds 23.6% vs 12.7% (z = +2.56); ablation 77.8% vs 65.1%; median karma 52.5 vs
    25. Code release not higher (56.9% vs 61.1%).
    `[UNRESOLVED]` Teaching vs selection is not separable in this corpus.

11. `[MEASURED]` **Negative-result rate is invariant.** Corpus 21.2% [18.3, 24.3]. Every tested
    split returns a null: AF 20.0/21.7 · MATS 19.4/21.3 · solo 22.1/20.1 · code 20.1/22.7 ·
    karma 19.5/22.7 · length 22.3/20.1 · open-weight 21.3/20.7. Per-tag deviations (Introspection
    40.0%, Inner Alignment 7.7%) all have intervals containing the corpus rate at n = 10–21.
    `[SPECULATIVE]` Negativity is a property of the question, not the researcher.

12. `[MEASURED]` **Dependency graph is a reading list, not a toolchain.** 2,580 edges: arXiv
    50.4%, repos 31.3%, other 18.3%. Top repo in-degrees are 10 (`control-arena`,
    `TransformerLens`) and 7 (`SAELens`); top paper in-degree is 27.

13. `[MEASURED]` **Length predicts rigor better than venue, karma, team size, or topic.**
    Above vs below median 2,224 words: ablation 75.5% vs 57.1% (z = +5.26); uncertainty 24.5% vs
    14.3% (z = +3.47); positions against prior work 72.3% vs 56.0% (z = +4.56). Code release does
    not differ (62.1% vs 59.3%, z = 0.76).

14. `[MEASURED]` **Rigor is rising.** 2024H2 → 2026H1 (four periods): code 53.3 → 60.2%,
    baseline 84.4 → 92.2%, negative rate 17.8 → 23.8%.
    `[UNRESOLVED]` 2026H2 (code 76.6%, baseline 95.7%) is a 56-day partial period. Do not treat
    it as a trend endpoint.

15. `[MEASURED]` **Four lone dissenters** — the sole negative post in a phenomenon of ≥4 that is
    otherwise entirely positive: crosscoder / model diffing (n=13, dissent at 106 karma);
    inoculation prompting (n=5, 48); multi-agent dynamics (n=5, 15); steering vector transfer
    (n=4, 104).
    `[INFERRED]` Highest information-per-experiment targets in the corpus. Distinct from
    `p3/findings.md` §1's 50/50 contested phenomena: these are consensus-plus-one-read-objection.

16. `[MEASURED]` **No structural aristocracy.** Composite unusualness (mean |percentile − 0.5|
    over 8 axes): max 0.454, median 0.250, theoretical max 0.5. Extremity on one axis does not
    predict extremity on others.
    `[INFERRED]` Single-axis rankings (karma, in-degree) are poor selectors over this dataset.

17. `[MEASURED]` **Author outliers.** Neel Nanda 52 posts / 0 first-author (advisor stratum, with
    Conmy 18/1, Rajamanoharan 23/2, StefanHex 16/1). chanind 12/11, all SAE work, 4 negative.
    Håvard Tveit Ihle 5 posts, one benchmark over 19 months. Realmbird 7 posts, 4 a numbered
    sprint series.

## Actions, priority order

1. Adjudicate the four lone dissenters (finding 15). Start with crosscoder / model diffing —
   13 posts, one 106-karma objection, open models, 3090-feasible.
2. Execute the replication queue (`~/prompts/3090`, then `replication/queue.md`, 87 specs).
   Finding 6 is the argument; nothing here substitutes for running them.
3. Validate the extraction instrument (`prompts.md` P4) before quoting any *rate* externally.
   Contrasts are more robust than levels: a judge bias shifting both arms cancels in a contrast.
4. Test the MATS effect (finding 10) against a matched non-MATS cohort.
5. Do not rank by karma (findings 4, 5, 16). Gate on feasibility, then weight by value, as
   `replication/pareto.py` does.

## Do not assert

- That any claim in the corpus is true. `[UNRESOLVED]`, and 0 replications have been run.
- Causal direction on findings 3, 10, 13. All observational; all admit selection explanations.
- That the 2026H2 improvement is real. Partial period.
- Tag-conditioned rates as corpus rates. The tag axis excludes the 98 AF-only posts, and finding 9
  shows AF membership is not a neutral filter.

## Reproduce

```
python3 analyze.py            # report + analysis_numbers.json (116 keys)
python3 p3/findings.py        # the claim-level layer this builds on
python3 meta.py               # the collection-level layer
```
