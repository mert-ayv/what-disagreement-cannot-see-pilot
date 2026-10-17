# Pilot results: guided

907200 enumerated cases (26428 covered, 2.9%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| claude_0 | | 73/75 | 99.8% | 1932 | 0 | 1932 | 100.0% |
| claude_1 | | 75/75 | 100.0% | 276 | 0 | 276 | 100.0% |
| claude_2 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| claude_3 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| claude_4 | | 73/75 | 99.7% | 2760 | 0 | 2760 | 100.0% |
| gemini_1 | | 75/75 | 100.0% | 0 | 0 | 0 | 100.0% |
| gemini_2 | | 73/75 | 99.8% | 1656 | 0 | 1656 | 100.0% |
| gemini_3 | | 73/75 | 99.8% | 1656 | 0 | 1656 | 100.0% |
| gemini_4 | | 73/75 | 99.8% | 1656 | 0 | 1656 | 100.0% |
| openai_0 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| openai_1 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| openai_2 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| openai_3 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| openai_4 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|
| all encodings, mixed families | 14 | 25392 | 100.0% | 2760 | 0 (0.0%) |
| claude only (resampled) | 5 | 9384 | 100.0% | 2760 | 0 (0.0%) |
| gemini only (resampled) | 4 | 4968 | 100.0% | 1656 | 0 (0.0%) |
| openai only (resampled) | 5 | 11040 | 0.0% | 2208 | 2208 (100.0%) |
| one per family | 3 | 4140 | 100.0% | 2484 | 0 (0.0%) |

## Where each encoding goes wrong (top error groups)

- **claude_0:** female+female, age 40 (past), fsh tie_18_18 [144]; female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **claude_1:** female+female, age 40 (past), fsh tie_18_18 [144]; female+no_partner, age 40 (past), fsh tie_18_18 [72]; female+male, age 40 (past), fsh tie_18_18 [60]
- **claude_2:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **claude_3:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **claude_4:** female+female, age 40 (past), fsh tie_18_18 [144]; female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]
- **gemini_2:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]; female+female, age 40 (today), fsh 1mo_17 [144]
- **gemini_3:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]; female+female, age 40 (today), fsh 1mo_17 [144]
- **gemini_4:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]; female+female, age 40 (today), fsh 1mo_17 [144]
- **openai_0:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **openai_1:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **openai_2:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **openai_3:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **openai_4:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
