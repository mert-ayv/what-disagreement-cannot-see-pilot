# kB findings: the role test with self-defined input interfaces (2026-10-19)

Pre-registration: `PREREGISTRATION.md` (written 2026-10-18, before any run). Encodings and adapters:
`encodings_claude/` (Claude Opus 5.5 agents), `encodings_gemini/` (Gemini 3.8 Flash), `encodings_gpt/` (GPT-6.1 Sol,
$0.73). Evaluation: `evaluate_B.py` (results/summary_<family>.md); comparison with kA: `compare_AB.py`
(results/compare_AB.md). Mock checks in `mock/` passed before the run (see the pre-registration).

## Pre-registered criteria

| Family | Inadmissible role encodings | Instrument (at most a third) | Verdict |
|---|---|---|---|
| Claude Opus 5.5 | 4 of 6 (insurer_1, insurer_2, member_2, member_3) | fails | not measurable with this design |
| Gemini 3.8 Flash | 3 of 6 (insurer_1, member_1, member_3) | fails | not measurable with this design |
| GPT-6.1 Sol | 3 of 6 (all member) | fails | not measurable with this design |

As pre-registered, the role test with self-defined interfaces is not measurable in any family. Slack counts in the
summaries come from the remaining admissible encodings and are descriptive only.

## Why encodings fail the admissibility check (read in the code)
The failures are readings that the kA helper functions had fixed, and that CodeX's test cases settle:
- **FSH window boundary (new point, not in the six):** "within the past 12 months". Claude insurer_1 and insurer_2
  exclude a test exactly 12 months old ("boundary excluded"; CodeX example comprehensive_covered1a says covered);
  Gemini insurer_1, member_1 and neutral_2 include a test 12 months and one day old (calendar-month comparison;
  examples comprehensive_not_covered1b, 2c, 3b say not covered); Gemini member_3 excludes the exact boundary. In kA
  the helper `months_at_most` ("exactly n months counts") removed this choice.
- **Birthday point:** Claude member_2 and member_3 count only tests strictly after the 40th birthday (example
  comprehensive_not_covered4d), as Claude member_1 did in kA.
- **"You or your partner":** all GPT member encodings read the clause disjunctively, as in kA (examples 0b, 0c, 9b).

## Descriptive comparison with kA (valid cases only; `results/compare_AB.md`)
- **Readings are no longer nearly fixed within a family.** Neutral disagreement within family: Claude 2,484 (kA) to
  19,888 (kB); GPT 0 to 17,280; Gemini 0 to 30,154. With self-defined fields, neutral encodings of one model diverge
  on F4, F1, F7 and the FSH window.
- **Direction holds.** Where member and insurer encodings remain admissible, members cover at least as often as
  insurers on every recorded point (exception: Claude F5, member 0.056 vs insurer 0.065); neutral encodings are more
  generous than the expert port on the silent points (F4, F2, F5), as in kA.
- **Interfaces add facts.** Every encoding adds fields the CodeX interface lacks (infertility specialist, coverage
  status; insurer encodings also "no pregnancy during the counted period", "condition recognized by a physician").
- **Grid artefact.** 259,200 grid cases are contradictory (no partner, but partner sterilized "yes"); encodings
  handle them differently, which produced 4,296 unattributed neutral-disagreement cases per family. Excluded in the
  valid-case comparison.

## Reading
The fixed interface with helper functions does more than enable comparison: it removes open points (the FSH window)
and makes one model's encodings look more uniform than they are. This supports the objection that a fixed input
interface is too strong an assumption. The role test as designed needs a fixed interface to be measurable; with
self-defined interfaces the CodeX tests exclude too many role encodings.

## Limits
One coverage; nine encodings per family; adapters are themselves LLM matching steps (failures were read in the code
and are readings, not adapter errors, for the cases inspected); grid built around the known points.
