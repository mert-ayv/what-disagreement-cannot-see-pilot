# CodeX pilot: report on all experiments (10 to 11 October 2026)

Purpose: test the assumptions behind the CodeX exposé ("What Disagreement Cannot See") against two
objections: that a fixed input interface is too strong an assumption, and that current models may no
longer make the errors the exposé wants to repair.

Setting for all experiments except the replication: CodeX's Insurance Analyst, coverage "Comprehensive
Infertility" of Stanford's Cardinal Care plan (Certificate of Coverage 2023-24, pp. 62 to 64, plus the
glossary definition of infertility). Code, data and raw outputs: this folder (`src/`, `data/`, `results/`).
Detailed logs per experiment: `results/FINDINGS.md`. Models: Claude Opus 5.5, GPT-6.1 Sol (chosen over
GPT-6 Astra for budget), Gemini 3.8 Flash (free tier; 3.1 Pro needed billing). Total API cost about $6
(Anthropic prepaid $5 used up; OpenAI about $1.5).

## Bottom line

1. **The exposé's core assumption does not hold anymore.** With the interface given, current models encode
   the coverage almost perfectly and do not rely on memory of the public encoding. Answering directly from
   the text is just as accurate on clear rules. Kant et al.'s vanilla benchmark rises from 0.78 to 0.88 (2024
   models) to 0.90 to 0.99 (current models).
2. **What remains are points the policy itself does not decide** (gaps and ambiguities). Every system,
   encoded or direct, resolves them silently and mostly in the same way, so comparing models does not reveal
   them.
3. **Offering an "undetermined" answer largely fixes that too:** both models flag the clearest gap every time,
   with no false abstentions on clear cases. Subtle ambiguities are flagged only partly.
4. Research space that survives model progress: a reference (legal annotation) of what is genuinely
   undetermined in a policy, and reliability on subtle ambiguities. Translation accuracy and repair do not.

## Experiments

### 0. Expert port and case generation
- CodeX's Epilog rules (about 400 lines, 5 files) ported to Python; reproduces all **75 of 75** CodeX test
  cases (the repo has 75 for this coverage and 53 for ART; Kant et al. evaluated on 20).
- 907,200 boundary-value cases (age 34/35/36/37/39/40 with birthday past or on the service date; months and
  cycles 5/6/11/12; FSH levels 16 to 19; tests exactly 6, 9, 12 months old or one day older; ties; five
  eligibility gates), labelled by the port. 2.9% covered, so accuracy alone is misleading.
- **Candidate defect in the expert encoding:** `Cardinal Care Core/rules.hrf` line 147 uses `FOBMonth` in
  the head and `DOBMonth` in the body of `not_yet_birthday_delta`. No CodeX test hits the affected case
  (service in the birth month on or after the birthday); the literal reading changes 7,484 outcomes.
  Unverified in Epilog.

### 1. Guided encodings (interface and helper functions given, as in Kant et al.)
14 encodings (Claude 5, GPT 5, Gemini 4).
- No threshold, age, partner or and/or errors; one Gemini encoding fully correct on all 907,200 cases.
- Remaining errors are two edge cases, both interpretive: age 40+ without an FSH test since the 40th
  birthday (vacuous "all prior tests after 40"; CodeX requires at least one test, and its own test cases
  catch this), and two FSH tests with identical date and time (CodeX's tie rule).
- No encoding wrongly denies a covered claim. GPT's 5 runs are identical, errors included.

### 2. Memorisation test (policy variants)
Paired edits to text and expert port: age split 35 to 37 with FSH 19 to 17; "or" to "and" with FSH window
12 to 9 months. All 12 encodings follow the changed text on 100% of the cases where the variants differ.
No memorisation.

### 3. Unguided encodings (models define their own input fields)
15 encodings in two runs (the second with the glossary definition, 10 encodings).
- As generated, every encoding denies every claim: the models ask for facts the expert interface lacks
  (infertility specialist, coverage status, partner's date of birth, sterilization of either partner).
- **Variable classification** (185 fields, LLM judge, checked by hand on the first five): identical 54%,
  broader 13%, new 11%, split 11%, convertible 5%, narrower 5%. Robust patterns: "patient or partner"
  sterilization in 10/10 (the text says "you or your partner", the expert checks the patient only);
  specialist and coverage status added in 10/10; the expert's single condition field split in 8/10.
- **One measurable matching error:** an LLM adapter mapped "timed" from "frequent" intercourse months.
- **Three-valued comparison** (scope facts treated as unknown, no assumptions): about 95% agreement with the
  expert; about 2.8% "undetermined" only because the encoding asks for extra facts; 0.5 to 2.4% "covered if
  the extra facts hold" where the expert denies. The real divergences: male without a female partner
  (the table has no row; 17,280 cases), the age-40 rule, identical tests; plus a timed/frequent conflation
  (756) and two encodings requiring "failure to become pregnant" or only "unsuccessful" donor cycles.
- These divergences are shared across model families: one encoding per family, 100% of the divergent cases
  are ones where both models agree and differ from the expert.

### 4. Direct answers from the policy text
58 cases (gap cases plus controls), described in plain language; 3 runs.
- Controls: Claude 28/30, GPT 30/30, consistent.
- Gap cases: both answer "covered" against the expert; their reasons often name the gap ("no row in the
  table, so the criteria do not apply") and resolve it themselves. Claude wobbles across runs on the age-40
  case. Gemini (one run) reads the male-without-partner case the opposite way.

### 5. Replication of Kant et al. (2025), vanilla approach
Same Chubb policy, nine queries, prompt and 10 trials as the paper.
| Model | Accuracy |
|---|---|
| Paper: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1, Mistral | 0.78 |
| Paper: DeepSeek-R1 / o1-preview | 0.81 / 0.88 |
| Claude Opus 5.5 | 0.90 +- 0.01 |
| GPT-6.1 Sol | 0.99 +- 0.01 |
Q9 (failed by every model in the paper) now 10/10 for both. Claude answers "I do not know" on Q5 (self-inflicted
injury vs "accidental injury") in 9 of 10 trials.

### 6. Abstention test
Same 58 cases with a third option "undetermined"; neutral prompt and an explicit one (GPT only; Claude's credit
ran out).
| Cases | Claude, neutral | GPT, neutral | GPT, explicit |
|---|---|---|---|
| Male without a female partner | 100% flagged | 100% | 100% |
| Age 40, no test since 40 | 50% | 25% | 75% |
| Identical FSH tests | 11% | 22% | 6% |
| Clear controls | 0% | 0% | 0% |
The flagged "random" controls are genuine tensions the expert resolved silently (glossary requires frequent
intercourse for a woman with a male partner; the table also allows donor cycles).

### 7. Self-repair loop (11 October)
Unguided encodings plus LLM adapters, no hand mapping; GPT-6.1 Sol repairs adapter and encoding from failing
cases, up to 3 rounds, 2 encodings, three arms. Details: `results/summary_self_repair.md`.
| Arm | Real errors after repair | Policy gaps |
|---|---|---|
| Expected outcomes, fit them | none (from 25,756 wrongly denied) | expert's reading adopted silently (GPT-written encoding); on the Claude-written one the repairer refused to fit identical tests |
| Expected outcomes, may contest | none | contested exactly the gap cases (36 of 36), nothing else |
| No labels, disagreement with a direct reading | none | male without partner and age 40 escalated; identical tests "fixed" toward covered (shared blind spot) |
The 6,720 remaining differences on non-gap cases are the glossary vs table conflict (timed vs frequent
intercourse for a man with a female partner), a fourth interpretive point. So repairing the interface is
solved by a feedback loop; finding gaps that all readers resolve the same way still needs an outside reference.

### 8. Public benchmarks (11 October)
GPT-6.1 Sol at default reasoning ("medium"; it chose to reason little). Details: `results/FINDINGS.md`.
| Benchmark | Accuracy | Where the gap is |
|---|---|---|
| LegalBench insurance (133 cases, crowd: covered / not / ambiguous) | 59% (baseline 44%) | wrong side on clear cases 2 of 74; decides 43 of 59 crowd-ambiguous cases confidently |
| InsLogicBench (257 inquiries, 10 Chinese policies) | 82% (baseline 75%) | 24 of 37 "wrongly approved" are cases GPT marks undetermined for a missing fact, which the labels deny by convention ("insufficient -> false") |
At maximum reasoning effort (about 34 times more reasoning) LegalBench is unchanged: it still decides 43 of 59
crowd-ambiguous cases. On both benchmarks, clear-cut errors are rare; the gap sits where text or facts do not settle the case and the
reference resolves it by a convention.

## Caveats
Self-repair: 2 encodings, one repairer, 12 calls, one arm cut short by credit. One coverage section; encodings in Python rather than logic programs; guided helper functions already encode
the hardest parts; mid-tier models for OpenAI and Google; several Gemini runs missing (overload, quota); the
hand mapping in the unguided setting fills unknown facts as "met" (the three-valued analysis avoids that);
the LLM judge misses subtle variable differences; the expert's labels are one reading, not the truth.
