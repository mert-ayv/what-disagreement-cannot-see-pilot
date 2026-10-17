# Pilot results: unguided_mock

907200 enumerated cases (26428 covered, 2.9%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| mockU_0 | | 58/75 | 97.7% | 20468 | 14376 | 6092 | 45.6% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|

## Where each encoding goes wrong (top error groups)

- **mockU_0:** female+female, age 35 (past), fsh 6mo_plus1d_18 [96]; female+female, age 35 (past), fsh tie_18_18 [96]; female+female, age 35 (today), fsh 6mo_plus1d_18 [96]

## Input fields each encoding chose (for the hand mapping to the expert interface)

- **mockU_0:** treatment, is_woman, has_male_partner, age_years, months_trying, donor_cycles, latest_fsh, fsh_age_months, eligible_flags_ok, infertile
