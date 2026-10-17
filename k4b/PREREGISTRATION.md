# K4b: do coverage agents notice when an answer depends on a reading? (pre-registered 2026-10-17, before any message is written)

Why: the K4 test showed three silent answers in five reading situations, too few to rely on, and "which reading
is right" must not be the ground truth.

Ground truth (no judgement of which reading is right): a message is **reading-dependent** if the coverage outcome for
the stated facts differs between two readings of the plan text; the agent should then flag the point (name the wording
or the alternative) or ask about it. A **control** message has complete facts and no reading point; the agent should
answer without flagging.

Reading points (each with two readings that change the outcome for the designed facts):
- P1 "You or your partner has not had a voluntary sterilization": the partner, not the patient, had a vasectomy.
- P2 "timed" (table) vs "frequent" (glossary) intercourse: the member reports only one kind.
- P3 a man with a female partner: the glossary defines infertility for a man only "without a female partner"; does
  the glossary bar him, add the semen criterion (CodeX's encoders: "we're assuming"), or not apply?
- P4 a man without a female partner: the glossary defines him as infertile, the table has no row for him.
- P5 age 40 or older: "must be less than 19 mIU/mL in all prior tests performed after age 40", and she has had no
  test since turning 40 (only a recent test from before her birthday).
- P6 "You or your partner does not have infertility that is due to a natural physiologic process": the partner (not
  the patient) has age-related decline, the patient has her own documented cause.

Messages: 4 per point (2 "exposed": the member's own words put the conflicting element in view; 2 "fitting": the
words fit one side and the conflicting element is not mentioned), plus 10 controls; 34 in total. Written by one Claude
agent from a fixed spec (`spec.md`).

Conditions (fresh Claude agents, same plan text as K4): A plain (the K4 prompt, which already asks to say where the plan
text is unclear), two runs; B reading list (the same prompt plus a neutral list of the six reading points), one run.

Metrics: silent rate on reading-dependent messages (answered COVERED or NOT COVERED without naming the point), by
condition, point and wording; false-flag rate on controls.

Claims, fixed in advance:
- Core claim holds if, in condition A, the silent rate on reading-dependent messages is at least 30% (in both runs)
  and the false-flag rate on controls is at most 20%.
- Mechanism holds if the silent rate for "fitting" wording exceeds "exposed" by at least 25 points in condition A.
- If condition B brings the silent rate below 10% with controls at most 20%, the cheap baseline (give the agent the
  reading list) solves detection; the thesis then rests on obtaining the list and on what to tell the member.

Limits: author-specified situations, one model family, a Claude writer, the six points come from CodeX's encoding and
my pilot; scoring by the author with a stated rule (flag = the answer names the wording at issue or an alternative
reading, or asks a question whose answer depends on the reading).

## Addendum C (2026-10-17, before the run): machine-generated list
Condition C = condition A plus the 55-point list that GPT-6 Astra produced in the K2 discovery test (run 1, text and
encoding as input; `../k2/results/raw/discovery_astra_run1.json`), presented as "points where the plan text may allow
more than one reading". One run, fresh Claude agent, same 34 messages.
Metrics as pre-registered: silent = COVERED or NOT COVERED without naming the point (reading-dependent messages);
needless escalation = a control answered NEED INFO or flagged as unclear.
Reading fixed in advance: if C reaches silent <= 2 of 24 with at most 1 of 10 controls escalated, a two-step prompt with
an automatic list already solves detection and the proposal says so, leading with the parameterised per-member check as
the part a prompt cannot produce. If C stays near A (silent >= 5 of 24) or escalates at least 3 of 10 controls, the
automatic-list problem is open and is the thesis motivation.
