# InsLogicBench: current models on Chinese insurance claims, and labels that rest on a reading

Sample: 10 policies (seed 11), 257 inquiries, 8 per call. Labels: approved 63, denied 194. Scenario 1 = covered and no exclusion (approved); 2 = not covered; 3 = covered but excluded; 4 = neither. '+ exception' = an exception to an exclusion applies.

## Binary condition (approved / denied)

| Model | Answered | Accuracy | Wrongly denied | Wrongly approved |
|---|---|---|---|---|
| openai (gpt-6.1-sol) | 257 | 82% | 9 | 37 |

Accuracy per cell:

| Cell | n | openai |
|---|---|---|
| scenario 1 | 45 | 84% |
| scenario 1 + exception | 18 | 89% |
| scenario 2 | 40 | 90% |
| scenario 2 + exception | 26 | 54% |
| scenario 3 | 51 | 76% |
| scenario 3 + exception | 6 | 100% |
| scenario 4 | 60 | 85% |
| scenario 4 + exception | 11 | 100% |

Every model disagrees with the label on 46 of 257 inquiries (label denied 37, approved 9).

## Three-valued condition (undetermined allowed)

| Model | Answered | Undetermined | of which missing fact / open text | Accuracy on decided | Undetermined among binary disagreements | Undetermined among binary agreements |
|---|---|---|---|---|---|---|
| openai | 257 | 106 (41%) | 101 / 5 | 90% | 30/46 | 76/211 |

