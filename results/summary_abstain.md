# Abstention test: are undecided cases flagged when the model may say so?

Answers per case over 3 runs. 'Flagged' = share of all answers that are 'undetermined'. 'Correct' = share of answers equal to the expert (gap cases: the expert's reading; controls: the clear answer). 'Consistent' = cases with the same answer in all 3 runs.

## neutral prompt, claude (claude-opus-5-5)

| Cases | Expert | Flagged undetermined | Covered | Not covered | Consistent |
|---|---|---|---|---|---|
| male without female partner | not covered | 100% | 0% | 0% | 8/8 |
| age 40, no test since 40th birthday | not covered | 50% | 50% | 0% | 2/8 |
| two identical FSH tests | not covered | 11% | 89% | 0% | 5/6 |
| timed vs frequent (donor path) | covered | 0% | 100% | 0% | 6/6 |
| control: covered | covered | 0% | 100% | 0% | 2/10 |
| control: just below a threshold | not covered | 0% | 0% | 100% | 0/10 |
| control: random | not covered | 10% | 10% | 80% | 0/10 |

## neutral prompt, openai (gpt-6.1-sol)

| Cases | Expert | Flagged undetermined | Covered | Not covered | Consistent |
|---|---|---|---|---|---|
| male without female partner | not covered | 100% | 0% | 0% | 8/8 |
| age 40, no test since 40th birthday | not covered | 25% | 75% | 0% | 2/8 |
| two identical FSH tests | not covered | 22% | 78% | 0% | 2/6 |
| timed vs frequent (donor path) | covered | 0% | 100% | 0% | 6/6 |
| control: covered | covered | 0% | 100% | 0% | 10/10 |
| control: just below a threshold | not covered | 0% | 0% | 100% | 10/10 |
| control: random | not covered | 13% | 0% | 87% | 8/10 |

## explicit prompt, claude (claude-opus-5-5)

| Cases | Expert | Flagged undetermined | Covered | Not covered | Consistent |
|---|---|---|---|---|---|
| male without female partner | | no answers | | | |
| age 40, no test since 40th birthday | | no answers | | | |
| two identical FSH tests | | no answers | | | |
| timed vs frequent (donor path) | | no answers | | | |
| control: covered | | no answers | | | |
| control: just below a threshold | | no answers | | | |
| control: random | | no answers | | | |

## explicit prompt, openai (gpt-6.1-sol)

| Cases | Expert | Flagged undetermined | Covered | Not covered | Consistent |
|---|---|---|---|---|---|
| male without female partner | not covered | 100% | 0% | 0% | 8/8 |
| age 40, no test since 40th birthday | not covered | 75% | 25% | 0% | 8/8 |
| two identical FSH tests | not covered | 6% | 94% | 0% | 5/6 |
| timed vs frequent (donor path) | covered | 0% | 100% | 0% | 6/6 |
| control: covered | covered | 0% | 100% | 0% | 10/10 |
| control: just below a threshold | not covered | 0% | 0% | 100% | 10/10 |
| control: random | not covered | 20% | 0% | 80% | 10/10 |

