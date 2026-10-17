# K4b findings (2026-10-17)

Pre-registration: `PREREGISTRATION.md`. Spec `spec.md`; messages written by a Claude agent (`messages_ordered.md`),
shuffled and relabelled (`messages_shuffled.md`, `id_map.json`, seed 20261017). Judges: fresh Claude agents; condition
A = the K4 prompt (already asks to say where the plan text is unclear), two runs; condition B = A plus a neutral list of
the six reading points, one run. Scorer `score.py` (keyword rule) plus manual review; raw output `scores_raw.txt`.

Manual rule applied on top of the keyword rule: an answer that asks only a fact question presupposing one reading
(P1: "was your husband's vasectomy voluntary?") without naming the wording or the alternative counts as silent.

| | A run 1 | A run 2 | B (reading list) |
|---|---|---|---|
| Silent on reading-dependent messages | 10/24 (42%) | 10/24 (42%) | 3/24 (12.5%) |
| False flags on controls | 0/10 | 0/10 | 0/10 |
| P1 partner's sterilization | 4 silent | 4 silent | 0 silent |
| P2 timed vs frequent | 0 silent | 0 silent | 0 silent |
| P3 man with a female partner (CodeX encoders' "we're assuming" gap) | 4 silent | 4 silent | 0 silent |
| P4 man without a female partner | 2 silent (both fitting) | 2 silent | 3 silent |
| P5 age 40, no test since | 0 | 0 | 0 |
| P6 partner's natural decline | 0 | 0 | 0 |
| Exposed vs fitting wording (silent) | 4/12 vs 6/12 | 4/12 vs 6/12 | 1/12 vs 2/12 |

Pre-registered verdicts: core claim **holds** (at least 30% silent in both runs, controls at most 20%); mechanism
**fails** (17 points, needed 25): silence depends on the reading point, not on the member's wording; the K4 account
(timed vs frequent wording) is withdrawn, since P2 is flagged in every variant here. The reading-list baseline cuts
silence from 42% to 12.5% but not below the 10% bar; its remaining misses are P4, where the agent treats a man without
a female partner under the wrong row or attends only to the surrogate question.

Examples (run 2): P3, M09: "the plan sets no semen-analysis requirement for a male with a female partner, so the normal
results do not disqualify you" (states one reading of the glossary gap as fact). P1, M01: "The plan excludes members
whose partner has had a voluntary sterilization" (literal reading, no alternative noted).

## What it means
- Silent answers on reading-dependent questions are frequent and stable for a capable model (42%, identical across
  runs), concentrated on two of six known points; clear cases are not over-flagged.
- Telling the agent which readings exist removes most silent answers. The open problem is getting that list without a
  human (K2: one prompt lists all seven recorded choices among 55 to 62 points, so a raw model list may over-escalate)
  and deciding, per member, which listed readings change the outcome and what the answer should say.

## Limits
Author-specified situations (six points, 24 + 10 messages), Claude writer and Claude judges, scoring by the author,
three runs. A second model family is the next check.

## Correction (2026-10-17, after review): pre-registered numbers
The table above applied a scoring rule added after the runs (fact questions that presuppose one reading count as
silent) and counted NEED INFO answers that missed the point. The pre-registered metric is narrower: "answered COVERED
or NOT COVERED without naming the point". Under it:
- Run A1: 6 of 24 (P1: M01, M02; P3: M09 to M12) = 25%. Run A2: 8 of 24 (P1: M01, M02; P3: M09 to M12; P4: M15,
  M16) = 33%. The pre-registered core claim (at least 30% in both runs) **fails in run A1**.
- P1 ("you or your partner") is not a fair two-reading point: the agent's literal reading is the ordinary one, and the
  encoding's patient-only rule is an uncommented omission. Without P1: 4 of 20 (A1) and 6 of 20 (A2).
- Robust part: on P3, the gap the CodeX encoders marked "we're assuming", all 8 answers in the two runs were confident
  decisions without naming the point; P2, P5 and P6 were named in every answer. P4 is mixed, and the reading list did
  not fix it (condition B: wrong-row questions, not confident answers).

## Condition C: machine-generated list (2026-10-17, pre-registered addendum)
With GPT-6's 55-point list from the K2 discovery run in the prompt, the Claude agent answered 0 of 24 reading-dependent
messages with a confident decision that did not name the point, and escalated 0 of 10 controls (`answers_C1.txt`).
P4 messages M14 to M16 were NEED INFO on the surrogate question rather than on the table gap (not confident answers).
Pre-registered reading: a two-step prompt with an automatic list already solves detection on this test set. The
detection problem is at ceiling on this test set.
