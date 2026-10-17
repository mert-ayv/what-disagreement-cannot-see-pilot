# Direction A one-day test: findings (2026-10-17)

Pre-registration: `PREREGISTRATION.md`. Encodings: `encodings/` (9 fresh Claude agents: 3 neutral, 3 member's advocate,
3 insurer's counsel; prompts `prompt_*.txt`, not published because they contain the policy text). Evaluation:
`evaluate_A.py`; output `results/summary.md`. Grid: 907,200 boundary cases x partner sterilization yes/no = 1,814,400.

## Pre-registered criteria
| Criterion | Result | |
|---|---|---|
| At most a third of role encodings inadmissible | 1 of 6 (member_1 fails one clear CodeX example) | pass |
| Slack region non-empty | 37,692 cases strict (member majority covers, insurer majority denies); 48,700 any pair | pass |
| At least 4 of 6 representable recorded points recovered | 6 of 6 any pair; 5 of 6 strict (F1/P3 only any pair) | pass |
| Fewer than 20 new-point groups | 0 unattributed strict-slack cases | pass |
| Member encodings cover more often than insurer encodings on every recovered point | yes, all six | pass |

**Verdict: pass.**

## Slack vs neutral disagreement (cases on the grid, per recorded point)
| Point | Strict slack | Neutral disagreement |
|---|---|---|
| F4 man without a female partner | 34,560 | 0 |
| F6 partner sterilized, patient not | 17,928 | 648 |
| F2 age 40+, no test since 40 | 3,132 | 3,132 |
| F5 tied latest FSH tests | 2,652 | 348 |
| F7 timed vs frequent across the threshold | 108 | 108 |
| F1/P3 man with a female partner | 0 (3,960 any pair) | 0 |

The three neutral encodings agree with each other on F4 and F1/P3, so comparing neutral encodings cannot reveal those
readings; encodings written for opposite sides do. Neutral disagreement touches 4 of 6 points, mostly with few cases.

## Direction (share of covered cases on the point's grid cells)
| Point | Expert port | Neutral | Member | Insurer |
|---|---|---|---|---|
| F4 man without a female partner | 0.000 | 0.133 | 0.133 | 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.009 | 0.028 | 0.000 |
| F5 tied latest FSH tests | 0.011 | 0.053 | 0.057 | 0.031 |
| F6 partner sterilized | 0.036 | 0.031 | 0.032 | 0.005 |
| F7 timed vs frequent | 0.005 | 0.003 | 0.011 | 0.003 |
| F1/P3 man with a female partner | 0.039 | 0.019 | 0.023 | 0.019 |

On the silent points (F4, F2, F5) the neutral LLM encodings sit on the member's side of the expert encoding, the same
direction as the direct answers in pilot experiment 4 (`DIRECTION_NOTE.md`). F1/P3 is the exception: the expert's own
assumption ("we're assuming ... a male with a female partner can be infertile") covers more than any LLM encoding.

## The inadmissible encoding
member_1 fails CodeX example `comprehensive_not_covered4d`: an FSH test of 19 taken on the 40th birthday. Its documented
reading: "less than 19 ... in all prior tests performed after age 40" means strictly after the birthday, and no test
means vacuously met. That is an open point not in the six-point key (the K2 discovery prompt listed it as "whether after
age 40 includes the fortieth birthday"). Under the pre-registered rule the encoding counts as inadmissible; in substance
the motivated encoder found an additional reading.

## Limits
One model family (Claude) for all encoders; nine encodings; grid counts are not prevalence; point predicates and
admissibility rule are the author's; F3 not representable; only one coverage.

## Correction (2026-10-17, after review): F6 predicate
The F6 predicate (partner sterilized, patient not) did not require a partner to exist, so cases of patients without a
partner, where the field is void, were counted as F6. Fixed in `evaluate_A.py` and re-run (`results/summary.md`):
- F6: 0 slack cases. All nine encodings, member's included, read "You or your partner has not had a voluntary
  sterilization" as barring coverage when the partner is sterilized (0 of the partnered F6 cells covered by any
  encoding); the expert port covers 4.3% of them because it checks the patient only. The encodings agree with each
  other against the expert's omission.
- Recovered points: strict 4 of 6 (F4, F2, F5, F7), any pair 5 of 6 (plus F1/P3). The pre-registered bar (4) is still
  met; the earlier "5 of 6 strict" was wrong.
- Neutral encodings: unanimous on F4 (the point with 34,560 of the 37,692 strict-slack cases); split 2 to 1 on F2;
  small disagreement on F5 and F7.
- Direction from this test is mixed: neutral encodings cover more than the expert on F4 and F5, mostly not on F2 (one
  of three), and less on F1/P3. The cleaner direction evidence is the direct-answer run (`DIRECTION_NOTE.md`).
- "No unattributed strict-slack cases" is close to true by construction: the grid varies mainly the features the six
  predicates name. It is not evidence that no other open points exist (member_1's birthday reading is one).
