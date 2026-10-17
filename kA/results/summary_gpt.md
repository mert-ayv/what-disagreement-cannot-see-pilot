# Direction A test: results

Grid: 1,814,400 cases. Encodings: insurer_1, insurer_2, insurer_3, member_1, member_2, member_3, neutral_1, neutral_2, neutral_3.

## Admissibility (CodeX comprehensive examples where the expert port's certificate-level outcome is the reference)

| Encoding | Examples failed (clear) | Failed on recorded points | Grid crashes | Agreement with expert on grid |
|---|---|---|---|---|
| insurer_1 | 25 ['comprehensive_covered0', 'comprehensive_covered1a', 'comprehensive_covered1b'] | 4 | 0 | 0.9709 |
| insurer_2 | 25 ['comprehensive_covered0', 'comprehensive_covered1a', 'comprehensive_covered1b'] | 4 | 0 | 0.9709 |
| insurer_3 | 0 [] | 0 | 0 | 0.9860 |
| member_1 | 55 ['comprehensive_covered0', 'comprehensive_covered1a', 'comprehensive_covered1b'] | 20 | 1814400 | 0.0000 |
| member_2 | 2 ['comprehensive_not_covered0b', 'comprehensive_not_covered9b'] | 2 | 0 | 0.9610 |
| member_3 | 2 ['comprehensive_not_covered0b', 'comprehensive_not_covered9b'] | 2 | 0 | 0.9610 |
| neutral_1 | 25 ['comprehensive_covered0', 'comprehensive_covered1a', 'comprehensive_covered1b'] | 4 | 0 | 0.9709 |
| neutral_2 | 0 [] | 2 | 0 | 0.9842 |
| neutral_3 | 25 ['comprehensive_covered0', 'comprehensive_covered1a', 'comprehensive_covered1b'] | 4 | 0 | 0.9709 |

Inadmissible role encodings: 5 of 6 ['insurer_1', 'insurer_2', 'member_1', 'member_2', 'member_3']

## Slack region and neutral disagreement

Any-pair slack (some member encoding covers, some insurer encoding denies): 0 cases
Strict slack (member majority covers, insurer majority denies): 0 cases
Neutral disagreement (the neutral encodings are not unanimous): 0 cases

| Point | Any-pair slack | Strict slack | Neutral disagreement |
|---|---|---|---|
| F1/P3 male with female partner | 0 | 0 | 0 |
| F4 male without female partner | 0 | 0 | 0 |
| F2 age 40+, no test since 40 | 0 | 0 | 0 |
| F5 tied latest FSH tests | 0 | 0 | 0 |
| F6 partner sterilized, patient not | 0 | 0 | 0 |
| F7 timed vs frequent across threshold | 0 | 0 | 0 |
| (no recorded point) | 0 | 0 | 0 |

Recovered points, any-pair: 0 of 6; strict: 0 of 6.

Unattributed strict-slack cases: 0 in 0 feature groups (top 15 below)


## Direction: share of cases covered, per point

| Point | Expert port | Neutral (mean) | Member (mean) | Insurer (mean) |
|---|---|---|---|---|
| F1/P3 male with female partner | 0.039 | 0.019 | nan | 0.019 |
| F4 male without female partner | 0.000 | 0.000 | nan | 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.027 | nan | 0.000 |
| F5 tied latest FSH tests | 0.011 | 0.036 | nan | 0.033 |
| F6 partner sterilized, patient not | 0.043 | 0.000 | nan | 0.000 |
| F7 timed vs frequent across threshold | 0.005 | 0.003 | nan | 0.003 |
