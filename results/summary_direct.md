# Direct answers from the policy text vs the expert

58 cases, 3 runs per model, 10 cases per call. 'Correct' = majority answer equals the expert; 'consistent' = same answer in every run.

## claude (claude-opus-5-5)

| Cases | n | Correct (majority) | Consistent across runs | Answer mostly given |
|---|---|---|---|---|
| male without female partner (expert: not covered) | 8 | 0/8 | 8/8 | covered in 8/8 |
| age 40, no test since 40th birthday (expert: not covered) | 8 | 0/8 | 2/8 | covered in 8/8 |
| two identical FSH tests (expert: not covered) | 6 | 0/6 | 6/6 | covered in 6/6 |
| timed vs frequent (donor path) (expert: covered) | 6 | 6/6 | 6/6 | covered in 6/6 |
| control: covered (expert: covered) | 10 | 10/10 | 10/10 | covered in 10/10 |
| control: just below a threshold (expert: not covered) | 10 | 10/10 | 10/10 | covered in 0/10 |
| control: random (expert: not covered) | 10 | 8/10 | 10/10 | covered in 2/10 |
| all (expert: mixed) | 58 | 34/58 | 52/58 | covered in 40/58 |

## openai (gpt-6.1-sol)

| Cases | n | Correct (majority) | Consistent across runs | Answer mostly given |
|---|---|---|---|---|
| male without female partner (expert: not covered) | 8 | 0/8 | 8/8 | covered in 8/8 |
| age 40, no test since 40th birthday (expert: not covered) | 8 | 0/8 | 8/8 | covered in 8/8 |
| two identical FSH tests (expert: not covered) | 6 | 0/6 | 6/6 | covered in 6/6 |
| timed vs frequent (donor path) (expert: covered) | 6 | 6/6 | 6/6 | covered in 6/6 |
| control: covered (expert: covered) | 10 | 10/10 | 10/10 | covered in 10/10 |
| control: just below a threshold (expert: not covered) | 10 | 10/10 | 10/10 | covered in 0/10 |
| control: random (expert: not covered) | 10 | 10/10 | 10/10 | covered in 0/10 |
| all (expert: mixed) | 58 | 36/58 | 58/58 | covered in 38/58 |

## gemini (gemini-3.8-flash)

| Cases | n | Correct (majority) | Consistent across runs | Answer mostly given |
|---|---|---|---|---|
| male without female partner (expert: not covered) | 8 | 6/8 | 0/8 | covered in 2/8 |
| age 40, no test since 40th birthday (expert: not covered) | 8 | 1/8 | 0/8 | covered in 7/8 |
| two identical FSH tests (expert: not covered) | 4 | 0/4 | 0/4 | covered in 4/4 |
| timed vs frequent (donor path) (expert: covered) | 0 | 0/0 | 0/0 | covered in 0/0 |
| control: covered (expert: covered) | 0 | 0/0 | 0/0 | covered in 0/0 |
| control: just below a threshold (expert: not covered) | 0 | 0/0 | 0/0 | covered in 0/0 |
| control: random (expert: not covered) | 0 | 0/0 | 0/0 | covered in 0/0 |
| all (expert: mixed) | 20 | 7/20 | 0/20 | covered in 13/20 |

