# Pilot results: guided_logic

907200 enumerated cases (24620 covered, 2.7%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| claude_0 | | 74/75 | 99.8% | 2016 | 0 | 2016 | 100.0% |
| claude_1 | | 74/75 | 99.7% | 2520 | 0 | 2520 | 100.0% |
| gemini_0 | | 74/75 | 99.8% | 1512 | 0 | 1512 | 100.0% |
| gemini_1 | | 74/75 | 99.8% | 1512 | 0 | 1512 | 100.0% |
| openai_0 | | 74/75 | 99.8% | 2016 | 0 | 2016 | 100.0% |
| openai_1 | | 74/75 | 99.8% | 2016 | 0 | 2016 | 100.0% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|
| all encodings, mixed families | 6 | 11592 | 21.7% | 2520 | 1512 (60.0%) |
| claude only (resampled) | 2 | 4536 | 11.1% | 2520 | 2016 (80.0%) |
| gemini only (resampled) | 2 | 3024 | 0.0% | 1512 | 1512 (100.0%) |
| openai only (resampled) | 2 | 4032 | 0.0% | 2016 | 2016 (100.0%) |
| one per family | 3 | 5544 | 18.2% | 2016 | 1512 (75.0%) |

## Where each encoding goes wrong (top error groups)

- **claude_0:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **claude_1:** female+female, age 40 (past), fsh tie_18_18 [144]; female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]
- **gemini_0:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]; female+female, age 40 (today), fsh 1mo_17 [144]
- **gemini_1:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_16 [144]; female+female, age 40 (today), fsh 1mo_17 [144]
- **openai_0:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **openai_1:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]

## Memorisation test: logic variant

1808 cases where the variant and the original policy give different answers. An encoding that follows the original there is recalling the public policy, not translating the text.

| Encoding | Follows the variant | Follows the original | Other or error |
|---|---|---|---|
| claude_0 | 100.0% | 0.0% | 0.0% |
| claude_1 | 100.0% | 0.0% | 0.0% |
| gemini_0 | 100.0% | 0.0% | 0.0% |
| gemini_1 | 100.0% | 0.0% | 0.0% |
| openai_0 | 100.0% | 0.0% | 0.0% |
| openai_1 | 100.0% | 0.0% | 0.0% |
