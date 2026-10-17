# K2 discovery test: scoring and verdict (2026-10-17)

Model GPT-6 Astra, provider-default reasoning, identical prompt, 3 runs; encoding with comments removed.
Cost: $0.563 + $0.615 + $0.590 = **$1.77** (5,629 input tokens, 10,130 to 11,181 output tokens per run).
Mock checks: the key scores 7 of 7 against itself; an empty answer 0 of 7 (trivial, by the matching rule).

## Matches (answer item number per run, with the passage that decides the match)

| Key | Run 1 | Run 2 | Run 3 | Matching passage (run 1) |
|---|---|---|---|---|
| F1 male with female partner, no glossary row | 3 | 3 | 3 | "the glossary supplies a male-specific criterion only for 'a male without a female partner'" |
| F2 40+, no post-40 test | 43 | 38 | 46 | "A recent pre-40 test suffices, with an empty post-40 history satisfying the universal condition; or at least one post-40 test is required. Encoding: Explicitly requires a nonempty post-40 list." |
| F3 date at which age is measured | 31 | 21 | 13 | "Use age and partnership at the service date, authorization date, treatment initiation ..." |
| F4 male without female partner, no table row | 4 | 4 | 4 | "The glossary recognizes infertility through abnormal semen analyses, but the benefit table has no corresponding row." |
| F5 tied most recent FSH tests | 38 | 40 | 41 | "The text gives no tie rule ... two equally latest entries can leave no 'most recent' test" |
| F6 "you or your partner" sterilization | 14 | 12 | 17 | "The scope of 'or' in the sterilization exclusion ... Encoding: Checks only that the patient has not had voluntary sterilization." |
| F7 timed vs frequent | 2 | 2 | 2 | "Benefit: 'unprotected timed sexual intercourse'; glossary: 'frequent, unprotected heterosexual sexual intercourse.'" |
| **Recall** | **7/7** | **7/7** | **7/7** | |

Items per run: 55, 56, 62 numbered points. Extras include: excluded key-adjacent items (two-week interval
measurement, the encoder's own implementation note: run 2 item 45, run 3 item 51), the partner's natural ageing
(all runs), gender-dysphoria pathway, partner definition, cycle counting, approval timing. Run 1 also flags the
`FOBMonth`/`DOBMonth` variable mismatch and the "24_25" label against the 2023-24 certificate without being asked.

## Verdict (pre-registered rule)
Median run 7 of 7, at or above the pipeline's 5 of 7: **discovery is not a contribution**. One same-information prompt
recovers every recorded choice, in every run, and more. The proposal makes no discovery claim.

## What this shifts
The bottleneck is no longer finding readings but **deciding which of about 55 to 60 flagged points are real and
material**: the model lists every recorded choice among many minor or speculative ones (home insemination, intersex
classification, lab corrections). Triage and validation by people who can judge materiality is the open part. 

## Limits
One coverage, one model family (OpenAI), three runs, the key has 7 items (three from CodeX encoder comments and issue #22, four from
the pilot; the pilot items were found by analysis that a reader of the pilot report could know about, but the model
received no pilot material). Scored by the author.

Addendum (2026-10-17): in all three GPT-6 Astra runs, item 1 is whether the table's donor-insemination alternative
overrides the glossary's intercourse requirement for a female with a male partner. It is not among the seven recorded
choices and was not listed among the extras above; `kA/` later found it again through opposing-role encodings.
