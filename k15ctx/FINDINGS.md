# K15 context test: findings (2026-10-17)

Pre-registration: `PREREGISTRATION.md`. Inputs built by `build.py` (seed 20261017); answers in `results/`; scores in
`results/scores.txt` (`score.py`). Four fresh Claude subagents, one per condition, no tools beyond reading their file.

| Condition | Correct (matches the authority) | Mean confidence |
|---|---|---|
| c0 provision only | 16/16 | 80 |
| c1 provision + "apply the case law you know" | 16/16 | 81 |
| c2 provision + verbatim authority passages | 16/16 | 83 |
| c3 provision + placebo passages from another provision | 16/16 | 81 |

Of the 16 cases, 9 carry C11's LLM label `legal_ambiguity`; all 9 are answered in line with the authority without it.

## Verdict (pre-registered rule)
c0 and c1 are within 2 cases of c2, and c3 equals c2: **K15's claim that supplying authority changes the reading is
dead** on this proxy. A current model, asked directly, already picks the reading the case law or guidance supports.

## What it means
- The disagreements in C11's released cases that have an authoritative answer are, for a current frontier model asked
  directly, not hard: they look like errors of the formalizing models (mid-2026, nine models, provision text only),
  including most of those the pipeline labelled "genuinely open".
- What stays hard is the residue where no authority decides (about 23% of the 30-case sample) and the question who
  confirms the model's choice. Same pattern as every test since 10.10: detection, translation and adjudication of
  decided points are at ceiling; open points and validation are not.

## Limits
Same model family for the authority mapping (feasibility agent) and the judges; n = 16 decided cases, one run each;
a judging task, not re-formalization with context; the two readings were phrased by the feasibility agent, which knew
the authority (possible wording leak; c0 confidence 80 suggests the cases are not trivial to the judge, but this is not
a control). An independent family (GPT) would be the next check once the OpenAI key is renewed.
