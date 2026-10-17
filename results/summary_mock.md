# Pilot results: mock

907200 enumerated cases (26428 covered, 2.9%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| mockA_0 | | 75/75 | 100.0% | 0 | 0 | 0 | 100.0% |
| mockA_1 | | 75/75 | 99.7% | 2912 | 2112 | 800 | 92.0% |
| mockB_0 | | 71/75 | 99.8% | 1932 | 0 | 1932 | 100.0% |
| mockB_1 | | 53/75 | 99.5% | 4312 | 2656 | 1656 | 90.0% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|
| all encodings, mixed families | 4 | 9156 | 100.0% | 7148 | 0 (0.0%) |
| mockA only (resampled) | 2 | 2912 | 100.0% | 2912 | 0 (0.0%) |
| mockB only (resampled) | 2 | 6244 | 47.0% | 4588 | 1656 (36.1%) |
| one per family | 2 | 1932 | 100.0% | 1932 | 0 (0.0%) |

## Where each encoding goes wrong (top error groups)

- **mockA_1:** female+female, age 35 (past), fsh 1mo_18 [96]; female+female, age 35 (past), fsh 1mo_16 [96]; female+female, age 35 (past), fsh 1mo_17 [96]
- **mockB_0:** female+female, age 40 (past), fsh older19_recent18 [144]; female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **mockB_1:** female+female, age 35 (past), fsh 6mo_exact_18 [144]; female+female, age 35 (today), fsh 6mo_exact_18 [144]; female+female, age 36 (past), fsh 6mo_exact_18 [144]
