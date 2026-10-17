# K4 test: findings (2026-10-17)

Pre-registration: `PREREGISTRATION.md`. Ground truth: `relevance.py` over the expert port, cases in `cases.py`.
Stories: `stories.md` (Claude writer, case 4 corrected by hand: the writer had kept a default intercourse history for a
woman without a partner). Answers: `elicitation_answers.txt` (one fresh Claude agent, one run). Scored by the author.

## Scores

| Case | Ground truth (expert) | Agent | Relevant facts asked | Note |
|---|---|---|---|---|
| 3 | open: FSH | NEED INFO: FSH | 1/1 | |
| 4 | open: donor cycles | NOT COVERED | 0/1 | story says "a few times", which implies fewer than 12; defensible inference, counted as decided |
| 5 | open: FSH, cause | NEED INFO: cause, FSH | 2/2 | |
| 6 | open: timed months | NEED INFO: timed; flags timed vs frequent | 1/1 | reading point flagged |
| 7 | open: sterilization | NEED INFO: the operation | 1/1 | |
| 8 | open: semen analyses | COVERED, no question | 0/1 | expert's own assumption (male with a female partner needs the glossary's semen criterion; recorded choice F1); agent reads the table only, flags nothing |
| 11 | open: less costly | NEED INFO: less costly | 1/1 | |
| 13 | open: frequent and timed months | NEED INFO: months of timed intercourse | 1/2 | frequency (glossary) not asked |
| 14 | open: cause, FSH | NEED INFO: cause, FSH | 2/2 | |
| 17 | open: frequent months | COVERED, no question | 0/1 | timed vs frequent (F7) resolved silently, although flagged in case 6 |
| 1, 2, 12, 15, 16, 18, 19, 20 | determined | all correct, no questions | | 8 of 8 |
| 9 | denied (no table row, F4) | NOT COVERED, flags the wording | | reading point flagged |
| 10 | covered (expert checks the patient only, F6) | NOT COVERED, no flag | | literal "you or your partner" reading, opposite outcome, stated as clear |

Recall of relevant facts: 9 of 12 (75%). Open cases decided without asking: 3 (cases 4, 8, 17). Determined
non-reading cases: 8 of 8.

## Verdict (pre-registered rule)
"Alive" fires (at least 3 open cases decided without asking); recall sits exactly at the 75% boundary. Without case 4
(story-induced), 2 decided cases remain, which would read "weakened". Either way, the reason differs from the
hypothesis.

## What the result shows
- **Plain facts are at ceiling.** Where a fact is simply missing (FSH, cause, number of months, an unexplained
  operation, cheaper treatments), the agent asks for exactly that fact; all 8 fully specified cases without a reading
  point are answered correctly without questions.
- **The misses sit on interpretive points.** In the five situations that touch a recorded reading (cases 6, 8, 9,
  10, 17), the agent flags the reading twice (6, 9) and decides silently three times (8, 10, 17); in case 10 its
  confident answer is the opposite of the expert encoding's. It flags timed vs frequent in case 6 and ignores the same
  point in case 17.
- So the open problem is not "which facts to ask" but **noticing, for this user's answer, that it rests on a reading**.
  A model that lists all readings when asked (K2 test: 7 of 7) does not reliably notice them while answering.

## Limits
n = 20 author-designed cases, five reading situations, one run, one model family for writer and agent, the expert's
readings define "relevant", the scoring is the author's.

## Robustness: three runs (2026-10-17)
Runs 2 and 3 (`elicitation_answers_run2.txt`, `_run3.txt`; fresh agents, same input) give the same decision on every
case as run 1. Reading situations: flagged in 3 of 3 runs for cases 6 and 9; answered confidently without a flag in
3 of 3 runs for cases 8, 10 and 17 (case 10 always opposite to the expert encoding). Plain-fact cases identical.

Mechanism suggested by the pattern: the agent notices a reading conflict when the member's own words expose it
(case 6: "frequent" but not "timed"; case 9: a man without a partner, no table row) and misses it when the words fit
one side (case 17: "timed" only; case 8: a man with a wife, where the expert's encoding adds the glossary's semen
criterion; case 10: the literal "you or your partner" reading). The prompt already asked the agent to say where the
plan text is unclear, so a prompt-level instruction is part of the baseline.
