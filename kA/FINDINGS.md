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

## Further model families (2026-10-17)
Pre-registered as addenda in `PREREGISTRATION.md` before each run. Encodings in `encodings_gemini/` (Gemini 3.8 Flash,
original prompt), `encodings_gpt/` (GPT-6.1 Sol, original prompt), `encodings_gpt_r2/` (GPT-6.1 Sol, amended prompt)
and `encodings_astra/` (GPT-6 Astra, amended prompt). Summaries in `results/summary_<label>.md`. API cost: $2.21.

| Run | Inadmissible role encodings | Strict slack | Points recovered (strict) | Member >= insurer | Verdict |
|---|---|---|---|---|---|
| Claude (above) | 1 of 6 | 37,692 | 4 of 6 | yes | pass |
| Gemini 3.8 Flash | 0 of 6 | 54,754 | 5 of 6 (all but F6) | yes, on all five | **replicates** |
| GPT-6.1 Sol, original prompt | 5 of 6 | 0 | 0 | n/a | fails (instrument) |
| GPT-6.1 Sol, amended prompt | 3 of 6 (all member) | 0 | 0 | n/a | **fails** (instrument) |
| GPT-6 Astra, amended prompt | 3 of 6 (all member) | 0 | 0 | n/a | **fails** (instrument) |

**Gemini.** 558 strict-slack cases match no recorded predicate; they split into 42 feature groups only because the
grouping key includes the FSH pattern. All 558 share one feature: a woman with a male partner whose donor insemination
cycles meet the table but whose months of intercourse do not meet the glossary (point D below). The pre-registered
pass criterion of fewer than 20 new-point groups is therefore failed on its letter; the Gemini addendum's replication
criteria do not include it.

**GPT, original prompt.** Five of nine encodings return False for every claim (one raises on every claim): the text
requires enrollment as a student or covered dependent, the interface has no such field, and the prompt says a missing
field means the fact is unknown. Claude and Gemini assumed enrollment is checked elsewhere. This is a defect of my
interface, found by the model; the amended prompt adds one sentence ("Enrollment as a student or covered dependent is
also checked elsewhere"), disclosed as a deviation.

**GPT, amended prompt.** All three member encodings, for both GPT models, read "You or your partner has not had a
voluntary sterilization" as met when either person is unsterilized. CodeX examples `comprehensive_not_covered0b` and
`9b` (patient sterilized, partner not) say not covered; the pre-registered F6 predicate covers only the reverse case,
so these count as clear examples and the floor excludes every member encoding. As pre-registered, the GPT test fails.
POST HOC, not evidence (`posthoc_sensitivity.py`): ignoring those two examples, the strict slack would be 96,496 cases
on all six points with member > insurer on each.

**Identical outcomes.** GPT-6.1 Sol and GPT-6 Astra wrote different code (hundreds of differing lines per file) yet give
identical outcomes on all 1,814,400 cases for all nine encodings; within each role their three encodings are identical
too. Gemini's nine encodings collapse to three outcome patterns: the three neutral encodings and member_3; member_1 and
  member_2; the three insurer encodings. They are independent API calls at default sampling with different text, but the
  Gemini slack of 54,754 cases is in effect one member reading against one insurer reading.

## Cross-family comparison (descriptive, not pre-registered; `crossfamily.py`, `results/crossfamily.md`)
- Neutral disagreement within a family: Claude 3,132 cases, Gemini 0, GPT 0. Across the three families' neutral
  encodings: 39,700 cases, on F4 (34,560), F2 (3,300), F5 (2,924), F7 (1,438) and point D (678): the same points the
  opposing-role slack finds.
- This contradicts the earlier working assumption of the pilot that different model families mostly resolve these
  points the same way, so that disagreement between neutral encodings cannot reveal them. It holds within a family,
  not across families. On F4,
  Claude's neutral encodings cover 13.3% of cells, Gemini's and GPT's none (the expert port: none).
- Point D (donor cycles vs the glossary) is outside the six recorded points but not new to the pilot: the GPT-6 Astra
  discovery prompt in `k2/` listed it first (numbered, not ranked) in all three runs, and the 10 Oct abstention test
  flagged the same glossary-vs-table tension; it was left out of the kA key. Expert port and all Claude and GPT neutral encodings deny
  it; Gemini's neutral and member encodings and one Claude member encoding (member_3) grant it.
- GPT-6.1 Sol's direct answers in pilot experiment 4 granted coverage in all 8 F4 cases; GPT's encodings deny F4. The same
  family resolves the point differently as answerer and as encoder (different prompts; not a controlled comparison).

## Revised reading of the test
Within one model, readings are nearly fixed, so disagreement among samples of one model shows few of them. Encodings
for opposing parties (two of three families) and encodings by different families both reveal the same points. Which
way an open point is decided depends on the model deployed. For GPT, the opposing-role instrument fails as
pre-registered because the member side takes a reading CodeX's own tests settle.
