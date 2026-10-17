# Self-repair loop: does feedback fix real errors, and does it know when not to?

Repairer: gpt-6.1-sol, up to 3 rounds, 58 training cases (direct_answer.py strata). Baseline = encoding and LLM adapter as generated, no hand mapping. Policy gaps = 236,160 enumerated cases whose outcome depends on a point the policy does not settle (male without a female partner, identical FSH tests, age 40+ without a test since 40); the expert denies all of them. 'Rest' = the other cases, where the expert's answer follows from the text.

## Full enumeration (907,200 cases) and CodeX examples

| Arm | Encoding | Rounds | Rest: wrongly denied | Rest: wrongly granted | Errors (crash) | Gaps: covered (reading against the expert) | CodeX examples passed |
|---|---|---|---|---|---|---|---|
| baseline | unguided2/openai_0 | 0 | 25,756 | 0 | 0 | 0 of 236,160 | 50/75 |
| baseline | unguided2/claude_4 | 0 | 25,756 | 0 | 0 | 0 of 236,160 | 50/75 |
| labels | unguided2/openai_0 | 2 | 0 | 6,720 | 0 | 1,152 of 236,160 | 71/75 |
| labels | unguided2/claude_4 | 3 | 0 | 0 | 0 | 3,328 of 236,160 | 71/75 |
| labels_contest | unguided2/openai_0 | 2 | 0 | 6,720 | 0 | 23,572 of 236,160 | 69/75 |
| labels_contest | unguided2/claude_4 | 2 | 0 | 6,720 | 0 | 6,292 of 236,160 | 69/75 |
| disagreement | unguided2/openai_0 | 2 | 0 | 6,720 | 0 | 23,572 of 236,160 | 69/75 |
| disagreement | unguided2/claude_4 | 1 | 0 | 0 | 0 | 5,812 of 236,160 | 69/75 |

## Held-out cases from the training strata

Answers as covered / not covered / error. Expert: gap strata and 'just below' are not covered, 'covered' and 'timed vs frequent' are covered.

| Arm | Encoding | male without female partner (n=8) | age 40, no test since 40th birthday (n=8) | two identical FSH tests (n=6) | control: covered (n=10) | control: just below a threshold (n=10) | control: random (n=10) |
|---|---|---|---|---|---|---|---|
| baseline | unguided2/openai_0 | 0/8/0 | 0/8/0 | 0/6/0 | 0/10/0 | 0/10/0 | 0/10/0 |
| baseline | unguided2/claude_4 | 0/8/0 | 0/8/0 | 0/6/0 | 0/10/0 | 0/10/0 | 0/10/0 |
| labels | unguided2/openai_0 | 0/8/0 | 0/8/0 | 0/6/0 | 10/0/0 | 0/10/0 | 0/10/0 |
| labels | unguided2/claude_4 | 0/8/0 | 0/8/0 | 6/0/0 | 10/0/0 | 0/10/0 | 0/10/0 |
| labels_contest | unguided2/openai_0 | 8/0/0 | 8/0/0 | 6/0/0 | 10/0/0 | 0/10/0 | 0/10/0 |
| labels_contest | unguided2/claude_4 | 0/8/0 | 8/0/0 | 6/0/0 | 10/0/0 | 0/10/0 | 0/10/0 |
| disagreement | unguided2/openai_0 | 8/0/0 | 8/0/0 | 6/0/0 | 10/0/0 | 0/10/0 | 0/10/0 |
| disagreement | unguided2/claude_4 | 0/8/0 | 8/0/0 | 6/0/0 | 10/0/0 | 0/10/0 | 0/10/0 |

## Verdicts on the training cases

Gap strata should be contested / undetermined; the other strata fixed (or kept when the encoding is right).

**labels:** male without female partner (gap): fix 8; age 40, no test since 40th birthday (gap): fix 16; two identical FSH tests (gap): none 10, fix 7; timed vs frequent (donor path): fix 12; control: covered: fix 20

**labels_contest:** male without female partner (gap): contest 8; age 40, no test since 40th birthday (gap): contest 16; two identical FSH tests (gap): contest 12; timed vs frequent (donor path): fix 12; control: covered: fix 20

**disagreement:** control: random: undetermined 2; male without female partner (gap): undetermined 16; age 40, no test since 40th birthday (gap): undetermined 16; two identical FSH tests (gap): fix 10, undetermined 2; timed vs frequent (donor path): fix 12; control: covered: fix 4

## Training cases wrong vs the expert, per round

- labels / unguided2/openai_0: 16 (shown 16) -> 22 (shown 22) -> 0 (shown 0)
- labels / unguided2/claude_4: 16 (shown 16) -> 14 (shown 14) -> 5 (shown 5) -> 5 (shown 5)
- labels_contest / unguided2/openai_0: 16 (shown 16) -> 22 (shown 22) -> 22 (shown 0)
- labels_contest / unguided2/claude_4: 16 (shown 16) -> 14 (shown 14) -> 14 (shown 0)
- disagreement / unguided2/openai_0: 16 (shown 30) -> 22 (shown 2) -> 22 (shown 0)
- disagreement / unguided2/claude_4: 16 (shown 30) -> 14 (shown 2)

Repair calls: 12, input tokens 160,847, output tokens 50,728 (incl. reasoning).

Note: the 6,720 "rest: wrongly granted" are all male patients with a female partner, 12 months of timed and
under 12 months of frequent intercourse: the glossary vs table conflict, a fourth interpretive point the
expert resolves as cumulative. On clear rules the repaired encodings make no errors.
