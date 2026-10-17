# Pilot findings, 10.10.2026

Models: Claude Opus 5.5, GPT-6.1 Sol, Gemini 3.8 Flash. Coverage: Comprehensive Infertility (benefit level).
907,200 boundary cases labelled by the Python port of CodeX's expert encoding (port passes all 75 CodeX
test cases). 41 encodings in total; two Gemini runs failed on Google-side overload (503) and are missing.
Preliminary, one coverage section, encodings in Python rather than logic programs.

## 1. Guided setting (interface and helpers given, as in Kant et al.): translation is nearly solved

| Model | Runs | CodeX test cases | Errors on 907,200 cases | Wrongly denied |
|---|---|---|---|---|
| Claude Opus 5.5 | 5 | 73 to 75 of 75 | 276 to 2,760 | 0 |
| GPT-6.1 Sol | 5 | 73 of 75 (all runs identical) | 2,208 | 0 |
| Gemini 3.8 Flash | 4 | 73 to 75 of 75 | 0 to 1,656 | 0 |

- No threshold, age-split, partner or "and/or" errors. One Gemini run is error-free on all cases.
- Every remaining error falls into one of two edge cases, both questions of interpretation:
  1. **Age 40+ with no FSH test since the 40th birthday.** Text: "must be less than 19 mIU/mL in all
     prior tests performed after age 40". Models read it as satisfied when there is no such test (vacuous
     "all"); CodeX requires at least one. CodeX's own test cases (4b, 6b) cover this, so it shows up as
     73/75 there too.
  2. **Two FSH tests with identical date and time.** CodeX's rule says there is then no "most recent"
     test and coverage fails; models pick one. CodeX's test cases do not cover this; it is also an
     artificial case.
- All errors are "wrongly granted"; no encoding wrongly denies a covered claim.

## 2. Memorisation: none detected
On both policy variants (age split 37 and FSH 19 -> 17; "or" -> "and" and FSH window 9 months), all 12
encodings follow the changed text on 100% of the cases where variant and original differ. The models
translate; they do not recall the public encoding.

## 3. Disagreement
- Across model families, every error was revealed by disagreement (no case where all encodings agree and
  are wrong), partly because one Gemini encoding is fully correct.
- Within one model, resampling reveals nothing for GPT-6.1 Sol: its 5 runs are identical, errors included.
- With so few errors, there is little for a repair loop to do in the guided setting.

## 4. Unguided setting (model defines its own input fields): the interface is where the difficulty is
- **As generated, every unguided encoding denies every claim.** The models chose facts the expert
  interface does not have: provider is an infertility specialist, patient covered as student or dependent,
  partner's date of birth instead of age, and sterilization or natural-process infertility of **either
  partner**. The policy text mentions all of these; the expert encoding checks only the patient's
  sterilization and leaves the rest out at this level. Without the expert's interface the models make
  different, often more literal, choices.
- **LLM matching made at least one measurable error.** Claude's adapter mapped "months of timed
  intercourse" from the "frequent intercourse" field for male patients, causing 5,960 wrong decisions.
  Vernie and Grabmair state that matching correctness cannot be measured without a reference; here the
  expert interface made it measurable.
- After a hand mapping (missing fields set to "requirement met", derivable ones derived), unguided
  encodings make 15,086 to 22,966 errors each, 7 to 50 times the guided level. Part of that is my prompt:
  the unguided models did not get the glossary definition of infertility (2,746 to 9,946 errors per
  encoding). The rest is the two edge cases above plus the matching error.

## 5. Candidate defect in the expert encoding (from the port)
`Cardinal Care Core/rules.hrf` line 147: `not_yet_birthday_delta(Month, Day, FOBMonth, DOBDay, 0)` uses
`DOBMonth` in the body. Services in the birth month on or after the birthday are affected; no CodeX test
case hits this; the literal reading changes 7,484 of the 907,200 outcomes. Unverified in Epilog.

## What this means for the exposé (honest reading)
- **The ceiling objection holds for this section.** With the interface and helpers given, current models
  translate the rules almost perfectly and do not rely on memory. The exposé's premise, many encodings
  that run but decide wrongly, needing detection and repair, is not supported here.
- **The interface objection holds too, and more strongly.** Remove the fixed interface and the encodings
  stop being comparable at all; the open problems are which facts to model, how to match them across
  formalisations, and which reading of ambiguous text to take.
- **What remains interesting is interpretation, not translation:** the vacuous "all tests after 40",
  "you or your partner", the tie rule, the birthday typo. These are the "divergences that mirror genuine
  controversies" Vernie and Grabmair describe.
- **Caveats:** one section; the guided helpers already encode the trickiest parts (most recent test,
  tests since 40, month arithmetic, infertility definition), so "guided is solved" partly reflects the
  helpers; mid-tier models (Sol, Flash) rather than the largest; Python rather than logic programs.

---

# Larger unguided sample, 10.10.2026 (afternoon)

10 new unguided encodings (Claude Opus 5.5 x5, GPT-6.1 Sol x5; Gemini's free-tier daily quota was exhausted),
this time **with the glossary definition of infertility** in the prompt. Adapters by the same model; then the
hand mapping (`src/gold_fill.py`) fills fields with no reference counterpart as "requirement met".
Fields classified by an LLM judge (Claude) into the categories of `variable_matching.md`
(`results/variable_summary.md`). Costs so far: about $0.85 Claude and $0.20 OpenAI for the first run.

## Variables (185 fields across 10 encodings)
identical 54% · broader 13% · new 11% · split 11% · convertible 5% · narrower 5%.
Robust patterns: sterilization "patient or partner" (broader) in 10/10; the expert's condition enum split
into separate facts in 8/10; "infertility specialist" and coverage status (new) in 10/10; partner age as
date of birth (convertible) in 9/10. The judge agrees with the hand classification of the first five on
these big patterns but misses subtle ones (it calls "months of unprotected intercourse" identical to
"timed").

## Decisions: what separates the unguided encodings from the expert
| Divergence | Encodings | Cases each | Nature |
|---|---|---|---|
| Male patient without a female partner: the glossary calls him infertile, the table has no row for him. 8/10 grant coverage, the expert denies. | 8 of 10 | 16,128 to 17,280 | gap in the policy text |
| Age 40+ with no FSH test since the 40th birthday (vacuous "all prior tests after 40") | 10 of 10 | 1,584 to 2,208 | ambiguous wording (same as guided) |
| Two identical FSH tests | 10 of 10 | 672 to 2,800 | expert tie rule |
| "Frequent" (glossary) and "timed" (table) intercourse collapsed into one quantity, so a woman with a male partner who qualifies through donor cycles is denied | 7 of 10 | 756 | concept conflation |
| Extra facts the expert does not have ("failure to become pregnant", only "unsuccessful" donor cycles) | 2 of 10 | deny all without mapping | scope |

## Disagreement on these
The main divergences are shared across model families: taking one encoding per family, every error case
is one where both models agree and both differ from the expert (100% hidden). Comparing LLM
formalisations with each other, as in Vernie and Grabmair, does not reveal where they jointly diverge
from the expert. (The "all 10" set shows 0% hidden only because two encodings deny every claim.)

## Reading
- Guided: models are close to correct out of the box; a "detect 80%, repair to 85%" result is not
  available there.
- Unguided: large, systematic divergences from the expert, mostly on **gaps and ambiguities in the policy
  text** (male without partner, vacuous "all", timed vs frequent), shared by all models, and **invisible to
  model-to-model disagreement**. This is the blind spot of the exposé's RQ 1, measured, but its content is
  interpretation rather than translation error. Deciding these cases needs a legal judgment, i.e. the
  human-oversight question of RQ 3, and only CodeX's authors can say which reading the Insurance Analyst
  intends.

## Three-valued view, no assumptions (`summary_three_valued.md`)
Scope facts the expert does not model (provider specialty, coverage status, enrollment) treated as
unknown; each encoding is run with them met and not met. Per encoding of the second unguided run:
- about 95% of cases: same answer as the expert (mostly "not covered" for another reason);
- about 2.8%: undetermined where the expert covers, i.e. the encoding only asks for extra facts (scope);
- 0.5 to 2.4%: undetermined where the expert denies, i.e. "covered **if** the extra facts hold", while
  the expert denies regardless. These are the real divergences: male without a female partner (17,280),
  age 40+ without a test since 40 (about 2,100), identical FSH tests (about 2,800);
- about 0.1% (756): decided "not covered" where the expert covers (timed and frequent intercourse
  collapsed), plus two encodings that deny everything because they require "failure to become pregnant"
  or "unsuccessful" donor cycles.

---

# Direct answers from the policy text (`summary_direct.md`), 10.10.2026

58 cases written out in plain language, policy section plus glossary definition, scope facts stated as
satisfied. 3 runs per model, 10 cases per call. Gemini hit its free-tier daily quota after one partial run.

| Cases | Expert | Claude Opus 5.5 | GPT-6.1 Sol |
|---|---|---|---|
| Controls: clearly covered (10) | covered | 10/10 correct, consistent | 10/10, consistent |
| Controls: just below a threshold (10) | not covered | 10/10, consistent | 10/10, consistent |
| Controls: random (10) | not covered | 8/10 (2 wrong: ignored the glossary's frequent-intercourse requirement) | 10/10 |
| Timed vs frequent, donor path (6) | covered | 6/6 | 6/6 |
| Male without a female partner (8) | not covered | "covered" 8/8, consistent | "covered" 8/8, consistent |
| Age 40, no FSH test since 40th birthday (8) | not covered | "covered" 8/8, but only 2/8 consistent (one run of three says no) | "covered" 8/8, consistent |
| Two identical FSH tests (6) | not covered | "covered" 6/6 | "covered" 6/6 |

Gemini (one run only): "not covered" for 6/8 men without a female partner, i.e. the opposite reading to
Claude and GPT.

## Reading
- On clear rules, answering directly from the text is as good as an encoding: near-perfect and consistent.
  For an informational "am I covered?" query, the computable approach adds little accuracy.
- On the underdetermined points, direct answers take the same reading as the unguided encodings
  ("covered"), against the expert. The reading is silent: nothing in the answer flags that the policy does
  not settle the case.
- Where the text is ambiguous, direct answers start to wobble (Claude on age 40: different answers for the
  same case across runs) and models disagree (Gemini vs Claude and GPT on the male without a partner).
- So the open problem is the same for both approaches: the policy is underdetermined in a few decisive
  places, and every system, encoded or not, silently resolves them. What an encoding adds is that the
  choice is made once and can be inspected; it does not make the choice right.

---

# Replication: Kant et al. (2025), vanilla LLM on the Chubb policy (`summary_kant_replication.md`)

Same policy text, nine queries, disclaimer, prompt and 10 trials as the paper; each query asked separately.
Differences: provider-default sampling (temperature/top-p can no longer be set); Claude at default effort.

| Model | Accuracy (mean +- SEM) |
|---|---|
| Paper: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1, Mistral | 0.78 +- 0.00 |
| Paper: DeepSeek-R1 | 0.81 +- 0.02 |
| Paper: o1-preview | 0.88 +- 0.02 |
| **Claude Opus 5.5** | **0.90 +- 0.01** |
| **GPT-6.1 Sol** | **0.99 +- 0.01** |

- Q9 (police officer bitten by his son, off duty), failed by every model in the paper: both current models
  correct 10/10.
- Q5 (hospitalized after punching one's own face): GPT-6.1 Sol "No" 10/10 (correct). Claude Opus 5.5 answers
  "I do not know" in 9 of 10 trials. The policy has no explicit self-harm exclusion; the answer turns on
  whether a self-inflicted punch counts as "accidental injury", so Claude flags it as undetermined rather
  than guessing.
- GPT-6.1 Sol misses Q4 once.
- The paper's motivating claim, that vanilla LLMs "cannot provide answers ... with 100% accuracy and
  consistency", is close to no longer true on this benchmark. The remaining miss is the one question whose
  answer depends on interpretation.

---

# Abstention test (`summary_abstain.md`)

Same 58 cases; answers "covered", "not_covered" or "undetermined". Neutral prompt (option offered) and
explicit prompt (plus "if the policy does not settle the case, answer undetermined"). Claude's prepaid
credit ran out: neutral prompt 15 of 18 batches, explicit prompt none. OpenAI complete.

| Cases | Expert | Claude, neutral: flagged | GPT, neutral: flagged | GPT, explicit: flagged |
|---|---|---|---|---|
| Male without a female partner | not covered | 100% | 100% | 100% |
| Age 40, no FSH test since 40th birthday | not covered | 50% | 25% | 75% (consistent 8/8) |
| Two identical FSH tests | not covered | 11% | 22% | 6% |
| Controls: clearly covered / just below a threshold | clear | 0% | 0% | 0% |
| Controls: random | not covered | 10% | 13% | 20% |

- Offering an "undetermined" option is enough for the clearest gap: both models flag the male without a
  partner every time, where they previously answered "covered" with confidence.
- The subtler ambiguity (vacuous "all tests after 40") is flagged only partly and depends on the prompt.
- No false abstentions on clear cases. The flagged random controls are genuine tensions the expert resolved
  silently: the glossary defines infertility for a woman with a male partner through frequent intercourse,
  while the table also allows the donor-cycle route.
- So the simple prompt fix largely works. What remains open is reliability on subtle ambiguities and,
  above all, a reference for what counts as genuinely undetermined.

---

# Self-repair loop (`summary_self_repair.md`, `src/self_repair.py`)

Question (11 October): if an unguided encoding fails its tests, can an LLM repair its own
interface from the outcomes alone, and does it know when not to repair? Two unguided encodings
(unguided2/openai_0, unguided2/claude_4) with their LLM adapters, no hand mapping; repairer GPT-6.1 Sol;
up to 3 rounds on the 58 stratified cases; evaluation on held-out cases from the same strata, all 907,200
enumerated cases and the 75 CodeX examples. Three arms: **labels** (expected outcomes from the expert, make
them pass), **labels_contest** (same, may contest an outcome the policy does not settle), **disagreement**
(no labels; feedback where the encoding differs from GPT's explicit-prompt abstention answers; fix, keep or
mark undetermined). 12 repair calls, 161k input and 51k output tokens. OpenAI credit ran out on the last
call, so disagreement/claude_4 has one round only.

- **The interface repairs itself.** Both encodings start by denying every claim (25,756 wrongly denied).
  After one or two rounds, in every arm: 0 wrongly denied, all 10 held-out covered controls covered, no
  crashes; CodeX examples 50/75 -> 69 to 71/75.
- **Fitting labels copies the expert's readings silently.** labels/openai_0 reaches 0 wrong on training by
  adopting the expert's reading on all three gaps, and generalises it to the held-out gap cases. No warning.
- **The repairer resists some labels unprompted.** labels/claude_4 refused to fit the identical-FSH cases
  in rounds 2 and 3, using a verdict ("none") it had not been offered and arguing the policy permits them.
- **Permission to contest separates errors from gaps cleanly.** labels_contest contested exactly the gap
  cases (14/14, 22/22) and fixed everything else, naming both readings each time.
- **Without labels, the shared blind spot stays.** disagreement escalated male-without-partner and age 40
  (16/16 each) but "fixed" the identical-FSH cases toward covered, because the independent reading also
  said covered. It also escalated two random controls over the glossary vs table conflict.
- **A fourth gap shows up in the numbers.** The 6,720 "wrongly granted" cases outside the three known gaps
  are all male patients with a female partner and 12 months of timed but under 12 months of frequent
  intercourse: the glossary vs table conflict again. The expert reads glossary and table as cumulative.
  So on clear rules, the repaired encodings make no errors at all.

Implication: the self-healing loop works as engineering, and with a contest option current models
separate their own errors from policy gaps on this policy. What they cannot do without an outside
reference is find a gap that every reader resolves the same way (identical FSH tests). That supports the
reference-annotation direction (option D), not a repair method as the contribution.

---

# Public benchmarks (11 October): LegalBench insurance and InsLogicBench

Model: GPT-6.1 Sol at OpenAI's default reasoning setting ("medium"; it reasoned little: about 13 reasoning tokens
per LegalBench call, about 180 per InsLogicBench call). Gemini 3.8 Flash was started on the free tier but
stalled on overload and rate limits (5 of 532 calls). Cost about $1 (LegalBench) and about $2 (InsLogicBench).

## LegalBench insurance_policy_interpretation (`summary_legalbench.md`, `legalbench_review.md`)

133 short policy-claim pairs, crowd labels A covered 47 / B not covered 27 / C ambiguous 59; LegalBench's
own 5-shot prompt, 3 runs. Raw crowd responses (about 30 per case) and the item author's design joined in.

- Accuracy 59% (always-C baseline 44%). On clear cases GPT almost never picks the wrong side (2 of 74);
  9 clear cases it calls ambiguous.
- On the 59 crowd-ambiguous cases it says "ambiguous" 16 times and decides 43 (18 covered, 25 not
  covered), with the same answer in all runs on 127 of 133 cases overall.
- Its "ambiguous" rate rises with how split the crowd was (12% clear, 19% leaning, 31% split), so it
  responds to the dispute, but resolves about two thirds of the most split cases.
- Caveat: the crowd label rule is strict (a 66/26 split counts as ambiguous). Of 18 cases the author
  wrote as clearly not covered that the crowd split on, GPT answers "not covered" in 14.

## InsLogicBench (`summary_inslogic.md`, `inslogic_review.md`)

10 of 110 Chinese policies (seed 11), all 257 inquiries, 8 per call; labels approved 63 / denied 194.
Binary condition (approved / denied) and three-valued (plus undetermined, with kind missing_fact /
open_text). The benchmark's labels were built with the rule "if vague or insufficient -> false".

- Binary accuracy 82% (always-denied baseline 75%). Errors: 37 wrongly approved, 9 wrongly denied.
  Weakest cell: not covered but an exception applies (54%).
- Three-valued: GPT marks 106 of 257 (41%) undetermined, 101 of them for a missing fact.
- Of the 37 "wrongly approved" cases (label denied), 24 are undetermined in the three-valued run
  (23 missing fact). The facts do not settle these claims; the label denies them by the benchmark's
  convention, and GPT in the binary run resolves them the other way. Only 12 are approved confidently in
  both runs: candidates for real model errors or label errors, to be reviewed by hand.
- GPT also flags 33 approved-label cases as missing a fact, so part of the 41% is caution.

Implication: on both benchmarks, the gap to 100% sits mostly where the text or the stated facts do not
settle the case, and the reference resolves it by a convention (crowd threshold, "insufficient -> false").
Clear-cut errors are rare. Open: whether more reasoning changes this, and whether a second model resolves
the same cases the same way.

## LegalBench at maximum reasoning effort (`openai_max` in `summary_legalbench.md`)

Same model, `reasoning.effort = "max"`, one standard run plus one run with reasons (266 calls, about 444
reasoning tokens per call instead of about 13; 210k input, 124k output tokens). The "same answer in all
runs" column is 0/133 only because there is one run.

- Recall on crowd-ambiguous cases unchanged: 16 of 59 (27%). It still decides 43 of 59 (16 covered,
  27 not covered), and mostly the same way as at the default setting.
- More thinking makes it more cautious on clear cases (called ambiguous: 12% -> 20% of cases the crowd
  agreed on), not on the split ones (31% -> 28%). Accuracy 59% -> 56%.
- So the confident resolution of disputed cases is not a matter of reasoning budget.

## GPT-6 Astra on the 59 crowd-ambiguous LegalBench cases

Stronger and pricier OpenAI model, reason prompt, one run. Default effort: all 59 (about 23 reasoning
tokens per call). Max effort: only 15 of 59 before the OpenAI credit ran out (about 808 reasoning tokens
per call; Astra's output price made this far more expensive than estimated).

- Astra at default gives the same answer as Sol (default, 3-run majority) on 54 of 59. It flags 19 as
  ambiguous (Sol 16) and decides 40 (18 covered, 22 not covered).
- 37 of 59 are resolved the same way by Sol default, Sol max and Astra default: a dispute among readers
  that no comparison of these configurations would reveal.
- Astra max on the 15 it finished: 3 covered, 8 not covered, 4 ambiguous (Astra default on the same 15:
  4 / 6 / 5). No sign that the stronger model at maximum effort flags more.
- Caveat: one provider; Sol and Astra may share training and behaviour. A second provider is still open.
