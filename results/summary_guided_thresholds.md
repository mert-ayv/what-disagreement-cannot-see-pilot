# Pilot results: guided_thresholds

907200 enumerated cases (6272 covered, 0.7%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| claude_0 | | 75/75 | 100.0% | 0 | 0 | 0 | 100.0% |
| claude_1 | | 73/75 | 99.7% | 2484 | 0 | 2484 | 100.0% |
| gemini_0 | | 75/75 | 100.0% | 276 | 0 | 276 | 100.0% |
| gemini_1 | | 75/75 | 100.0% | 0 | 0 | 0 | 100.0% |
| openai_0 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |
| openai_1 | | 73/75 | 99.8% | 2208 | 0 | 2208 | 100.0% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|
| all encodings, mixed families | 6 | 7176 | 100.0% | 2484 | 0 (0.0%) |
| claude only (resampled) | 2 | 2484 | 100.0% | 2484 | 0 (0.0%) |
| gemini only (resampled) | 2 | 276 | 100.0% | 276 | 0 (0.0%) |
| openai only (resampled) | 2 | 4416 | 0.0% | 2208 | 2208 (100.0%) |
| one per family | 3 | 2484 | 100.0% | 2208 | 0 (0.0%) |

## Where each encoding goes wrong (top error groups)

- **claude_1:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **gemini_0:** female+female, age 40 (today), fsh 1mo_16 [144]; female+no_partner, age 40 (today), fsh 1mo_16 [72]; female+male, age 40 (today), fsh 1mo_16 [60]
- **openai_0:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]
- **openai_1:** female+female, age 40 (today), fsh 1mo_18 [144]; female+female, age 40 (today), fsh 1mo_19 [144]; female+female, age 40 (today), fsh 1mo_16 [144]

## Memorisation test: thresholds variant

20156 cases where the variant and the original policy give different answers. An encoding that follows the original there is recalling the public policy, not translating the text.

| Encoding | Follows the variant | Follows the original | Other or error |
|---|---|---|---|
| claude_0 | 100.0% | 0.0% | 0.0% |
| claude_1 | 100.0% | 0.0% | 0.0% |
| gemini_0 | 100.0% | 0.0% | 0.0% |
| gemini_1 | 100.0% | 0.0% | 0.0% |
| openai_0 | 100.0% | 0.0% | 0.0% |
| openai_1 | 100.0% | 0.0% | 0.0% |
