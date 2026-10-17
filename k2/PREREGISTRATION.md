# K2 discovery test: pre-registration (written 2026-10-17, before any paid call)

## Question
Does one strong prompt, given the same information, find the interpretive choices that humans recorded for this
encoding? If it does as well as the pilot's pipeline, discovery is not a thesis contribution and the proposal
makes no discovery claim.

## Input (same information for every run)
- Policy text: Cardinal Care 2023-24 Certificate of Coverage, Comprehensive infertility services, pp. 62 to 64
  (`inputs/policy.txt`) and the glossary entry "Infertile or infertility" (`inputs/glossary.txt`).
- CodeX's expert encoding of the coverage (consolidated `Deploy/rules.hrf`, Epilog) with **all comments removed**
  (`inputs/encoding_no_comments.hrf`), because two comments state answer-list items verbatim.

## Frozen list of recorded interpretive choices (answer key)
Recorded by people (CodeX encoders, CodeX issues) or by the pilot's analysis, before this test. Each is a point where
the text does not settle the outcome and the encoding commits to one reading.

| id | Choice | Recorded by |
|---|---|---|
| F1 | A male with a female partner is treated as possibly infertile although the glossary has no such row | encoder comment ("NOT ACTUALLY MENTIONED IN THE GLOSSARY, but we're assuming ...") |
| F2 | Age 40 or older: "all prior tests performed after age 40" with no test since 40 is read as failing (at least one test required), not as vacuously met | encoder comment (ART rules, "Another practical assumption: There must be at least one test after age 40"); pilot |
| F3 | The date at which the patient's age is determined (date of service vs date of claim; birthday edge) is not stated | CodeX issue cardinal-care-dev #22 (open) |
| F4 | A male without a female partner: the glossary defines him as infertile, but the eligibility table has no row; the encoding denies | pilot (three-valued analysis, exp. 3 and 4) |
| F5 | Two FSH tests with the same date and time: "most recent" is undefined; the encoding applies a tie rule | pilot |
| F6 | "You or your partner has not had a voluntary sterilization": the encoding checks the patient only | pilot |
| F7 | Table requires "timed" intercourse, glossary "frequent" intercourse; the encoding uses them in different places | pilot |

Excluded from the key: CodeX issue #45 (Stanford summary vs Aetna PDF wording), because it needs a document the input
does not contain; encoder notes on implementation (date arithmetic) and scope (leaves of absence, out-of-network),
because they are not readings of the text; points found only by an LLM (for example the partner's natural ageing,
blind reader item 35), to avoid circularity. Such points are reported as extras, not scored.

Pilot pipeline (unguided encodings, three-valued comparison, self-repair with contest, human analysis) found F2, F4,
F5, F6, F7: **5 of 7**.

## Runs
- Model: GPT-6 Astra (`gpt-6-astra`), provider-default reasoning, 3 runs, identical prompt (`prompt.txt`).
- Budget: hard stop when the summed cost from returned token counts reaches $3.00 for this test (list prices $10 / M
  input, $50 / M output); total OpenAI budget $5.44.

## Scoring
An answer item matches a key item if it names the same text element and states that the text leaves open the point
the key item describes (or that the encoding commits to one of several readings there). One answer item can match at
most one key item. Scored by the author (Claude) with a one-line justification per match, in `results/scoring.md`.
Mock checks before the paid runs: the key itself scores 7 of 7; an empty answer scores 0 of 7.
Report per-run recall, the union over runs, and extras.

## Kill criterion
Discovery is **not** a contribution (the proposal makes no discovery claim) if the median single-prompt run finds at least 5
of 7 key items (the pipeline's score). Discovery **may** be a contribution if the union over three runs finds 3 or
fewer. In between: report as "a single prompt finds most, but not reliably".

## Bundled authority check (GPT-6.1 Sol, about $0.05)
CodeX issue #27 records Aetna's answer on "Covered according to the type of benefit and the place where the service
is received" (basic infertility row of the schedule): "The reason for the service is less important than the service
you actually get". Two phrasings x 3 runs ask which reading is more plausible, without the answer. n = 1 recorded
answer, so this is a qualitative probe, not a measurement.
