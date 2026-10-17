# Direction A one-day test: motivated disagreement (pre-registered 2026-10-17, before any encoding is written)

Idea (ideation-fable-2026-10-17.md, direction A): encodings written to serve the member and encodings written to serve
the insurer, each bound to defensible readings, disagree on the points the text leaves open. The cases where they
diverge (the "slack region") should contain the recorded interpretive choices that neutral disagreement misses.

## Setup
- Rule: Comprehensive Infertility, Cardinal Care 2023-24 text and glossary (as in the pilot).
- Interface: the pilot's guided interface plus one field, `partner_has_had_voluntary_sterilization` ("yes"|"no"),
  so that the "you or your partner" reading can be expressed. Helpers reduced to readings-free ones (patient age,
  FSH tests since the 40th birthday, calendar months); no infertility helper (the glossary text is given instead) and
  no "most recent test" helper (it fixes the tie rule).
- Roles: neutral, member's advocate, insurer's claims counsel. Role prompts ask for the reading most favourable to
  the side that a court could accept, with every departure from the plainest reading justified in a comment
  quoting the text. Three encodings per role, each by a separate fresh Claude agent (9 in total). One model family:
  the OpenAI key is invalid, so this is a Claude-only test, stated as a limit.
- Grid: the pilot's 907,200 boundary-value cases crossed with partner sterilization yes/no (1,814,400 cases);
  CodeX's 75 example claims with the new field set to "no".

## Measures
- Admissibility: an encoding is inadmissible if it fails any of CodeX's 75 example claims that the expert port
  passes, except examples whose outcome turns on a recorded open point (identified by the point predicates below).
- Slack region: cases where at least one member encoding says covered and at least one insurer encoding says not
  covered (any-pair), and the stricter version where the member majority covers and the insurer majority denies.
- Attribution to recorded points, by predicates on the case: F1/P3 male patient with a female partner; F4 male
  patient without a female partner; F2 female 40 or older with no FSH test since the 40th birthday; F5 two FSH tests
  with the same latest date and time; F6 partner sterilized, patient not; F7 timed and frequent month counts on
  different sides of the threshold. F3 (date at which age is computed) is not representable in the grid; recall is
  over the six representable points.
- Neutral baseline: cases where the three neutral encodings disagree with each other, and which points that set
  touches.
- New points: slack-region cases matching none of the predicates, grouped by their case features.
- Direction: on each recorded point, the share of covered outcomes for the expert port, the neutral encodings,
  the member encodings and the insurer encodings.

## Kill criteria (from the ideation, adapted)
- Instrument dead if more than a third of the role encodings (member or insurer) are inadmissible.
- Content dead if the slack region is empty or touches none of the six representable points.
- Pass (would justify one sentence and RQ3 wording in the note): region non-empty, at least 4 of the 6
  representable points recovered (the ideation's 5 of 7 rescaled), fewer than 20 distinct new-point groups, and
  member encodings cover more often than insurer encodings on every recovered point.
- Comparison of interest: points in the slack region that neutral disagreement does not touch.

## Limits stated in advance
One model family (Claude) for all encoders; nine encodings; author-defined point predicates; the expert port defines
admissibility on clear tests.

## Addendum: second model family (written 2026-10-17, before the Gemini run)
Same prompts, interface, grid and criteria, with Gemini 3.8 Flash (free tier) as encoder: 3 neutral, 3 member, 3
insurer encodings via the API (one call each; the prompt's instruction to write a file is replaced by "reply with a
single python code block"). Evaluated alone and pooled with the Claude encodings.
Replication holds if, for Gemini alone, at most a third of role encodings are inadmissible, the strict slack recovers
at least 4 of the 6 representable points, and member encodings cover at least as often as insurer encodings on every
recovered point. Of particular interest: whether the Gemini neutral encodings are also unanimous on F4.
If Gemini fails on rate limits or returns unusable code for more than a third of calls, the run is reported as
incomplete, not as a replication failure.

## Addendum: OpenAI family (written 2026-10-17, before the GPT run)
Same prompts, interface, grid and criteria as the Gemini addendum, with GPT-6.1 Sol as encoder (3 neutral, 3 member,
3 insurer; one call each; same "reply with a single python code block" substitution; cost cap $3). Evaluated alone,
and pooled with the Claude encodings. The same replication criteria apply to GPT alone. If both second families are
available, the two-family claim in the note is made only for families whose replication holds.

### Deviation (written 2026-10-17, after the first GPT run, before the second)
In the first GPT run, 5 of 9 encodings (neutral_1, neutral_3, member_1, insurer_1, insurer_2) return False for
every claim: the text requires enrollment as a student or covered dependent, the interface has no such field, and the
prompt says a missing field means the fact is unknown. The Claude encodings had assumed enrollment is established
elsewhere. This run is scored and reported as pre-registered (results/summary_gpt.md). A second GPT run (encodings_gpt_r2)
adds one sentence to the list of requirements "checked elsewhere": "Enrollment as a student or covered dependent is also
checked elsewhere." Everything else is unchanged; the same criteria apply. It is reported as an amended run, not as the
pre-registered one.

### Addendum: GPT-6 Astra (written 2026-10-17, before the Astra run)
The strongest OpenAI model available to me, as a check on the ceiling risk: 3 neutral, 3 member, 3 insurer encodings
with the amended prompt (enrollment checked elsewhere), cost cap $2, into encodings_astra. Same criteria; reported
alongside the amended GPT-6.1 Sol run.
