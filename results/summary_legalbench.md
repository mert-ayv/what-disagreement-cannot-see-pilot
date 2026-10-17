# LegalBench insurance_policy_interpretation: do current models recognise ambiguity?

133 cases; crowd labels A covered 47, B not covered 27, C ambiguous 59. LegalBench base prompt verbatim (5-shot), 3 runs; majority answer per case (ties count as C). Majority-class baseline (always C): 44%.

| Model | n | Accuracy | Recall covered | Recall not covered | Recall ambiguous | Answers 'ambiguous' | Same answer in all runs |
|---|---|---|---|---|---|---|---|
| openai (gpt-6.1-sol) | 133 | 59% | 79% | 96% | 27% | 19% | 127/133 |
| openai_max (gpt-6.1-sol) | 133 | 56% | 72% | 89% | 27% | 23% | 0/133 |

Confusion, openai (rows crowd, columns model): 

| crowd \ model | A | B | C |
|---|---|---|---|
| A | 37 | 2 | 8 |
| B | 0 | 26 | 1 |
| C | 18 | 25 | 16 |

Confusion, openai_max (rows crowd, columns model): 

| crowd \ model | A | B | C |
|---|---|---|---|
| A | 34 | 2 | 11 |
| B | 0 | 24 | 3 |
| C | 16 | 27 | 16 |

## Crowd-ambiguous cases (C)

- 18 of 59 flagged ambiguous by at least one model.
- 40 of 59 resolved the same way by every model (no model would reveal the ambiguity by disagreeing): covered 16, not covered 24.

Model 'ambiguous' rate by how split the crowd was (share of the larger of yes / no):

| Crowd split | n | openai | openai_max |
|---|---|---|---|
| clear (>= 80%) | 56 | 12% | 20% |
| leaning (60 to 80%) | 48 | 19% | 23% |
| split (< 60%) | 29 | 31% | 28% |

By the item author's design (controversial vs written to be clear):

| Design | Crowd label | n | openai: A/B/C | openai_max: A/B/C |
|---|---|---|---|---|
| controversial | A | 7 | 4/0/3 | 4/0/3 |
| controversial | B | 1 | 0/1/0 | 0/0/1 |
| controversial | C | 37 | 12/11/14 | 11/12/14 |
| unambiguous_covered | A | 40 | 33/2/5 | 30/2/8 |
| unambiguous_covered | C | 4 | 3/0/1 | 3/0/1 |
| unambiguous_uncovered | B | 26 | 0/25/1 | 0/24/2 |
| unambiguous_uncovered | C | 18 | 3/14/1 | 2/15/1 |
