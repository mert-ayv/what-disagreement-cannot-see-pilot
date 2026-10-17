# Direction A test: results

Grid: 1,814,400 cases. Encodings: insurer_1, insurer_2, insurer_3, member_1, member_2, member_3, neutral_1, neutral_2, neutral_3.

## Admissibility (CodeX comprehensive examples where the expert port's certificate-level outcome is the reference)

| Encoding | Examples failed (clear) | Failed on recorded points | Grid crashes | Agreement with expert on grid |
|---|---|---|---|---|
| insurer_1 | 0 [] | 0 | 0 | 0.9860 |
| insurer_2 | 0 [] | 0 | 0 | 0.9840 |
| insurer_3 | 0 [] | 0 | 0 | 0.9860 |
| member_1 | 1 ['comprehensive_not_covered4d'] | 2 | 0 | 0.9652 |
| member_2 | 0 [] | 2 | 0 | 0.9652 |
| member_3 | 0 [] | 2 | 0 | 0.9619 |
| neutral_1 | 0 [] | 0 | 0 | 0.9669 |
| neutral_2 | 0 [] | 0 | 0 | 0.9669 |
| neutral_3 | 0 [] | 2 | 0 | 0.9652 |

Inadmissible role encodings: 1 of 6 ['member_1']

## Slack region and neutral disagreement

Any-pair slack (some member encoding covers, some insurer encoding denies): 48,700 cases
Strict slack (member majority covers, insurer majority denies): 37,692 cases
Neutral disagreement (the neutral encodings are not unanimous): 3,132 cases

| Point | Any-pair slack | Strict slack | Neutral disagreement |
|---|---|---|---|
| F1/P3 male with female partner | 3,960 | 0 | 0 |
| F4 male without female partner | 34,560 | 34,560 | 0 |
| F2 age 40+, no test since 40 | 3,348 | 3,132 | 3,132 |
| F5 tied latest FSH tests | 3,884 | 2,652 | 348 |
| F6 partner sterilized, patient not | 22,920 | 17,928 | 648 |
| F7 timed vs frequent across threshold | 5,434 | 108 | 108 |
| (no recorded point) | 558 | 0 | 0 |

Recovered points, any-pair: 6 of 6; strict: 5 of 6.

Unattributed strict-slack cases: 0 in 0 feature groups (top 15 below)


## Direction: share of cases covered, per point

| Point | Expert port | Neutral (mean) | Member (mean) | Insurer (mean) |
|---|---|---|---|---|
| F1/P3 male with female partner | 0.039 | 0.019 | 0.023 | 0.019 |
| F4 male without female partner | 0.000 | 0.133 | 0.133 | 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.009 | 0.028 | 0.000 |
| F5 tied latest FSH tests | 0.011 | 0.053 | 0.057 | 0.031 |
| F6 partner sterilized, patient not | 0.036 | 0.031 | 0.032 | 0.005 |
| F7 timed vs frequent across threshold | 0.005 | 0.003 | 0.011 | 0.003 |
