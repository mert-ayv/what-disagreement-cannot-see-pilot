# discovery_astra_run2 (gpt-6-astra, 11181 output tokens, $0.6153)

Below, “passes” or “fails” refers to the disputed eligibility requirement, assuming unrelated requirements are satisfied. In the encoding, failure usually means that coverage cannot be derived—not necessarily that an explicit denial is derived.

I distinguish **interpretive gaps in the supplied text** from straightforward coding omissions or additional restrictions unsupported by that text. The latter are not, by themselves, policy ambiguities.

## Glossary, benefit table, and eligible persons

1. **Donor insemination for a female with a male partner: alternative or additional requirement?**
   - **Text:** The table permits “12 months … **or** … 12 cycles of donor insemination,” with corresponding six-unit thresholds at 35+. The glossary describes females with male partners only through heterosexual intercourse.
   - **Readings:** The benefit’s donor-insemination alternative supersedes the glossary’s intercourse requirement; or both provisions must independently be satisfied.
   - **Encoding:** Requires both `patient_is_infertile` and the benefit table. Ordinarily, donor cycles alone do not establish glossary infertility for a female with a male partner.
   - **Example:** A 32-year-old with a male partner has completed 12 unsuccessful donor inseminations but no heterosexual intercourse. The benefit-specific alternative would qualify her; the encoded conjunction ordinarily does not.

2. **“Frequent” intercourse versus “timed” intercourse.**
   - **Text:** Glossary: “frequent, unprotected heterosexual sexual intercourse.” Table: “unprotected timed sexual intercourse.”
   - **Readings:** These describe substantially the same qualifying conception trial; or they impose distinct requirements that must both be met.
   - **Encoding:** Uses separate counters and generally requires both, except where another glossary or table route applies.
   - **Example:** A couple has intercourse once at the predicted ovulation date each month for a year. A timed-trial reading qualifies them; an independent frequency requirement might not.

3. **Missing glossary category for males with female partners.**
   - **Text:** The table includes “A male of any age with a female partner.” The glossary supplies a male-specific definition only for a male “without a female partner.”
   - **Readings:** Apply the female-partner couple’s unsuccessful conception period; extend the abnormal-semen-analysis requirement to these males; require both; or treat the glossary as incomplete without supplying an additional test.
   - **Encoding:** Requires the partner-age-based intercourse period **and** two abnormal semen analyses at least two weeks apart, absent the gender-dysphoria route.
   - **Example:** A male with a 30-year-old female partner has had 12 months of unsuccessful qualifying intercourse but normal semen analyses. The couple-based reading qualifies him; the encoded ordinary route does not.

4. **Missing benefit-table category for males without female partners.**
   - **Text:** The glossary expressly includes “a male without a female partner” after qualifying semen analyses; the benefit table has no corresponding row.
   - **Readings:** Such a male is eligible without inapplicable table requirements; requires an analogous or separately determined conception trial; or cannot qualify for this particular benefit.
   - **Encoding:** Can establish `patient_is_infertile`, but supplies no matching table rule.
   - **Example:** A male with a male partner has two qualifying abnormal analyses. He satisfies the glossary, but cannot satisfy the encoded benefit table.

5. **Effect of the gender-dysphoria glossary provision on ordinary benefit prerequisites.**
   - **Text:** Infertility includes “[a]n individual or their partner who has been clinically diagnosed with gender dysphoria.”
   - **Readings:** This is an alternative infertility pathway that also displaces incompatible conception-trial requirements; or it changes only the glossary classification, leaving every benefit prerequisite intact.
   - **Encoding:** Makes the diagnosis sufficient for `patient_is_infertile` only. The causal-condition, sterilization, natural-process, less-costly-treatment, and table requirements remain.
   - **Example:** A person with diagnosed gender dysphoria seeks infertility treatment without a prior intercourse or insemination trial. The broader exception reading could qualify them; the encoding does not.

6. **How “female,” “male,” and partner sex are determined.**
   - **Text:** The table and glossary use “female,” “male,” and sex-specific partner categories without defining their application to transgender, nonbinary, or intersex people.
   - **Readings:** Classification follows sex assigned at birth, current legal sex, gender identity, or reproductive anatomy/function.
   - **Encoding:** Accepts supplied `female`/`male` facts; it does not resolve their meaning. The ordinary table has no nonbinary category.
   - **Example:** A transgender man with functioning ovaries and a male partner could enter a female conception/FSH pathway under an anatomy-based reading but have no applicable table row under an identity-based reading.

7. **Whether “partner” means only the formally defined covered partner.**
   - **Text:** A covered dependent who is the student’s “legal spouse, civil union partner or domestic partner” is “referred to as ‘your partner’”; later provisions say “with a male partner.”
   - **Readings:** Every later use is restricted to that defined relationship; or the reproductive provisions use “partner” more broadly, including an uninsured or informal reproductive partner.
   - **Encoding:** Uses partner-sex and partner-age facts without checking relationship status or the partner’s enrollment.
   - **Example:** A covered student has an uninsured male boyfriend and a year of unsuccessful intercourse. A reproductive-partner reading allows the with-male-partner route; a strict defined-term reading may not.

8. **Multiple partners or different partners serving different reproductive roles.**
   - **Text:** “Your partner,” “a male partner,” and “a female partner” are singular and do not specify which person controls when several relationships exist.
   - **Readings:** Use the legal partner, the person involved in the conception attempt, any qualifying partner, or all relevant partners.
   - **Encoding:** Has unlinked partner-sex and partner-age predicates, rather than partner identities. Multiple facts can permit different rule paths without ensuring that they concern the same person.
   - **Example:** A male patient has female partners aged 32 and 38. Using the older reproductive partner yields a six-month threshold; using the younger legal partner yields 12 months.

9. **Who is “you” when the insured patient and the person undergoing the reproductive procedure differ.**
   - **Text:** “You or your partner,” documentation in either person’s records, and coverage of infertility-specialist charges.
   - **Readings:** Eligibility attaches strictly to the individual whose service is billed; or some criteria attach to the couple or the person attempting pregnancy even when another insured individual is the claim subject.
   - **Encoding:** Primarily follows the claim patient. It combines `sex_of_patient_trying_to_conceive` with the claim patient’s DOB, FSH tests, and sterilization history, without a separate reproductive-person identity.
   - **Example:** A male student’s infertility leads to IUI performed on his covered female spouse. Different choices about whose claim and eligibility control can produce different applicable trials, FSH requirements, and exclusions.

10. **Whether conception history with an earlier partner counts.**
    - **Text:** Failure to become pregnant “with a male partner” and the table’s required months or cycles.
    - **Readings:** Count the individual’s qualifying history regardless of partner; or require the trial to involve the current reproductive partnership.
    - **Encoding:** Uses claim-level totals without identifying the partner involved in each attempt.
    - **Example:** A 31-year-old has ten unsuccessful months with a former partner and two with her current partner. An individual-history reading reaches 12 months; a current-couple reading does not.

11. **Unknown partner status versus affirmatively having no partner of the specified sex.**
    - **Text:** “Without a male partner” and “without a female partner.”
    - **Readings:** Require affirmative evidence of absence; or treat the absence of evidence of such a partner as enough.
    - **Encoding:** Uses negated partner-sex predicates, not an affirmative “no such partner” fact. Under a closed-world interpretation, missing data can activate these routes.
    - **Example:** A female patient’s partner information is omitted, but she has 12 donor cycles. Treating omission as absence can qualify her through the without-male-partner route; requiring confirmation leaves eligibility unestablished.

## Exclusions, causation, and the meaning of infertility

12. **Scope of “or” in the sterilization restriction.**
    - **Text:** “You or your partner has not had a voluntary sterilization.”
    - **Readings:** At least one person must be unsterilized; neither person may have been sterilized; or only the person whose fertility or treatment is at issue must be unsterilized.
    - **Encoding:** Checks only `patient_has_had_voluntary_sterilization(C, no)`.
    - **Example:** The patient has never been sterilized, but her partner had a voluntary vasectomy. The encoding passes this condition; a neither-partner reading fails it.

13. **Meaning of “voluntary sterilization” in mixed-purpose or constrained-choice cases.**
    - **Text:** Procedures are included “only if obtained as a form of voluntary sterilization.”
    - **Readings:** Sterilization must be the principal purpose; any intentional contraceptive purpose suffices; or voluntariness requires a particular degree of informed, unconstrained choice.
    - **Encoding:** Delegates the entire classification to a yes/no patient fact.
    - **Example:** A hysterectomy treats severe disease, but permanent contraception is also an expressly desired objective. A primary-medical-purpose reading may permit coverage; an any-contraceptive-purpose reading may exclude it.

14. **Scope of “or” in the natural-process restriction.**
    - **Text:** “You or your partner does not have infertility that is due to a natural physiologic process.”
    - **Readings:** Neither person may have naturally caused infertility; at least one must not have it; or examine only the relevant patient or causal condition.
    - **Encoding:** Does not separately test both people. It excludes specified natural-process values of the asserted infertility-causing condition.
    - **Example:** A patient has pathological tubal infertility, while her partner’s infertility is attributed solely to natural reproductive aging. The asserted tubal condition can pass the encoding; a neither-partner reading excludes the couple.

15. **Boundary between natural reproductive aging and a covered pathological condition.**
    - **Text:** “A natural physiologic process such as age related ovarian insufficiency,” alongside express eligibility criteria for females aged 40+.
    - **Readings:** Exclude any infertility materially associated with ordinary aging; exclude only a diagnosed natural insufficiency such as perimenopause; or distinguish disease from normal aging using an unstated clinical standard.
    - **Encoding:** Supplies named excluded categories, including `natural_male_reproductive_aging`, but provides no classification rules.
    - **Example:** A menstruating 41-year-old has diminished ovarian reserve, FSH below 19, and no diagnosis of perimenopause. Classification as natural aging excludes her; classification as a covered disorder may not.

16. **Mixed natural and non-natural causes.**
    - **Text:** “There exists a condition” causing infertility, but infertility must not be “due to a natural physiologic process.”
    - **Readings:** Any natural contribution excludes coverage; only a predominant or sole natural cause excludes; or an independently qualifying non-natural cause is sufficient.
    - **Encoding:** Its existential `Condition` can succeed on one non-excluded condition even when another asserted condition is natural.
    - **Example:** A patient has both blocked fallopian tubes and age-related ovarian insufficiency. The encoding can succeed through the blocked-tube condition; an any-natural-cause exclusion would fail.

17. **What counts as a condition “demonstrated to cause” infertility.**
    - **Text:** “Is demonstrated to cause the illness of infertility.”
    - **Readings:** Require an identified cause proven in this individual; accept a diagnosed condition generally known to impair fertility; or accept unexplained infertility itself as the qualifying condition after adequate investigation.
    - **Encoding:** Takes `demonstrated_and_documented_condition_causing_infertility` as an input and supplies no evidentiary standard.
    - **Example:** A couple has 18 months of unsuccessful attempts and a specialist’s diagnosis of unexplained infertility. A diagnosis-based reading qualifies them; a separate-identifiable-cause reading does not.

18. **Whether a partner’s condition alone can establish the claimant’s causal-condition requirement.**
    - **Text:** A condition documented “in your or your partner’s medical records.”
    - **Readings:** A condition affecting either person is sufficient for couple-based treatment; or the condition must cause the claimant’s own infertility, although documentation may be located in either record.
    - **Encoding:** Does not identify the person who has `Condition`; that attribution is left to the claim fact.
    - **Example:** A female patient has no diagnosed disorder, but her partner has severe male-factor infertility. The couple-based reading satisfies the causal-condition requirement; a claimant-specific reading may not.

19. **“Failure to become pregnant” versus inability to attain a “successful pregnancy.”**
    - **Text:** The glossary uses “failure to become pregnant”; the benefit uses “A successful pregnancy cannot be attained.”
    - **Readings:** Any conception defeats the failure-to-become-pregnant criterion; or infertility includes inability to achieve an ongoing pregnancy or live birth. “Successful” itself may mean clinical pregnancy, viability, or live birth.
    - **Encoding:** Has no express pregnancy-outcome test in its intercourse/cycle infertility rules. “Successful pregnancy” appears only in an opaque less-costly-treatment fact.
    - **Example:** A patient conceives repeatedly but has early miscarriages. A conception-only reading may exclude her from infertility status; an ongoing-pregnancy or live-birth reading may include her.

20. **Whether and when an earlier pregnancy resets the qualifying trial.**
    - **Text:** “Failure to become pregnant … after” the stated period; required months or cycles.
    - **Readings:** Count only attempts since the most recent pregnancy; reset only after a successful pregnancy; or allow earlier unsuccessful attempts to contribute.
    - **Encoding:** Uses totals with no pregnancy dates or reset logic.
    - **Example:** A patient had ten unsuccessful cycles, conceived and miscarried, then had two further unsuccessful cycles. A cumulative reading reaches 12; a pregnancy-reset reading does not.

## Timing and qualifying conception attempts

21. **Date at which age determines the applicable category.**
    - **Text:** “Under 35,” “35 years of age or older,” and “age 40 and older.”
    - **Readings:** Use age at service, application, authorization, trial commencement, diagnosis, or each individual attempt.
    - **Encoding:** References service-date age for the patient. Female-partner age is supplied as an undated fact.
    - **Example:** A patient turns 35 after six unsuccessful months but before treatment. Service-date classification requires six months; classification fixed at trial commencement requires 12.

22. **When eligibility must be established and re-established during a treatment course.**
    - **Text:** “You are eligible … if,” advance approval, and a cycle extending beyond initiation.
    - **Readings:** Determine eligibility once at authorization or cycle initiation; or re-evaluate it for every service within the cycle.
    - **Encoding:** Evaluates claim-level facts and service dates, with no authorization-period or cycle-level eligibility lock.
    - **Example:** An FSH test is within six months when treatment begins but outside six months when a later monitoring service occurs. Locked-in cycle eligibility may continue; service-by-service evaluation may fail.

23. **Continuity and recency of the conception trial.**
    - **Text:** “Number of months” and “months trying to conceive.”
    - **Readings:** Require a continuous, recent trial; permit interruptions; or accumulate qualifying months or cycles over the patient’s history.
    - **Encoding:** Uses aggregate numerical counters without dates, gaps, or expiration rules.
    - **Example:** Six qualifying months occurred five years ago and six occurred recently. A cumulative reading reaches 12; a continuous-current-trial reading does not.

24. **How months of intercourse are measured.**
    - **Text:** “12 months or more” and “6 months or more.”
    - **Readings:** Measure elapsed calendar time, complete qualifying calendar months, menstrual cycles, or a fixed number of days.
    - **Encoding:** Accepts a supplied month count without computing it from attempt dates.
    - **Example:** Attempts run from January 31 through July 30. Counting six monthly conception opportunities may qualify; requiring six complete elapsed calendar months may not.

25. **Operational meanings of “frequent” and “timed.”**
    - **Text:** “Frequent” intercourse and “timed” intercourse.
    - **Readings:** Different clinical standards could require intercourse every few days, a specified number of acts, or one or more acts in a verified or estimated fertile window.
    - **Encoding:** Delegates these classifications to separate supplied counters.
    - **Example:** Intercourse occurs once monthly on an app-predicted fertile day, without ovulation confirmation. A permissive timing standard counts the month; a confirmed-ovulation standard may not.

26. **Whether qualifying attempts must provide a realistic opportunity for egg–sperm contact.**
    - **Text:** “Trying to conceive through egg and sperm contact.”
    - **Readings:** Count qualifying acts or procedures as attempts; or require evidence that viable sperm and an available egg could actually meet.
    - **Encoding:** Counts reported intercourse months or donor cycles without verifying ovulation, viable sperm, or actual contact.
    - **Example:** A couple completes a year of timed intercourse while the male partner has complete azoospermia. A procedural-attempt reading counts the year; a literal effective-contact reading may not.

27. **Which donor-insemination methods and settings count.**
    - **Text:** “Donor artificial insemination cycles” and “donor insemination.”
    - **Readings:** Count clinician-performed IUI only; include intracervical or other artificial insemination; or also include adequately documented home insemination.
    - **Encoding:** Uses an unrestricted donor-cycle counter for benefit eligibility. Its separate CPB rules recognize timed intrauterine/intracervical inseminations, but do not define the donor counter.
    - **Example:** A patient has completed 12 unsuccessful home intracervical inseminations using donor sperm. A broad reading counts them; a clinic-IUI-only reading does not.

28. **Meaning of “Self paid/not paid for by plan.”**
    - **Text:** That phrase labels the donor-cycle column.
    - **Readings:** The patient must personally finance the cycles; or any financing other than this plan is acceptable. “Plan” could refer to the current coverage or a broader continuity of the same insurance arrangement.
    - **Encoding:** Does not record who paid for qualifying donor cycles.
    - **Example:** Another insurer paid for all 12 prior cycles. A not-paid-by-this-plan reading counts them; a personally-self-paid reading does not.

## Less-costly treatment

29. **Basis and time horizon for comparing treatment costs.**
    - **Text:** “Less costly treatment.”
    - **Readings:** Compare individual procedures, complete treatment courses, expected cost per successful pregnancy, billed charges, patient expense, or plan expense.
    - **Encoding:** Delegates the comparison to one yes/no fact.
    - **Example:** One alternative costs less per attempt but usually requires many more attempts. A per-attempt comparison blocks the requested treatment; an expected-total-cost comparison may not.

30. **Standard for concluding that pregnancy “cannot” be attained through an alternative.**
    - **Text:** “A successful pregnancy cannot be attained through less costly treatment.”
    - **Readings:** Require prior treatment failure; accept a specialist’s prediction; require literal impossibility; or accept a sufficiently low success probability.
    - **Encoding:** Uses an asserted `...can_be_attained...(C, no)` fact without a probability threshold or exhaustion rule.
    - **Example:** A cheaper treatment has an estimated 2% success probability and has not been tried. A literal-possibility reading blocks coverage; a medical-futility reading may permit it.

31. **Meaning of coverage being “available” for the cheaper treatment.**
    - **Text:** “For which coverage is available under this plan.”
    - **Readings:** The treatment need only be a listed benefit; or it must actually be obtainable and covered for this patient now, considering contraindications, exhausted limits, provider access, and authorization.
    - **Encoding:** Leaves all these distinctions inside the same supplied fact.
    - **Example:** A cheaper treatment is generally covered but medically contraindicated for the patient. A categorical benefit-list reading may block the requested service; a patient-specific availability reading does not.

## FSH testing

32. **What makes a test “unmedicated.”**
    - **Text:** “Unmedicated day 3 FSH.”
    - **Readings:** No fertility-stimulation medication during that cycle; no medication capable of affecting FSH; or a specified medication-free interval before testing.
    - **Encoding:** FSH records contain only level, date, and time. They have no medication or washout fields.
    - **Example:** A patient stops hormonal contraception two days before testing. A no-current-medication reading accepts the result; a washout-period reading may reject it.

33. **Meaning of “day 3” for irregular, induced, or absent menstruation.**
    - **Text:** “Day 3 FSH test.”
    - **Readings:** The third day after spontaneous full menstrual flow; a clinically designated cycle day; or an equivalent assessment after induced bleeding or in an irregular cycle.
    - **Encoding:** Assumes the supplied test list consists of qualifying day-3 tests.
    - **Example:** A test is taken on the third day after a medication-induced withdrawal bleed. One interpretation accepts it; another requires a spontaneous menstrual cycle.

34. **Which results belong in the pool from which the “most recent” test is selected.**
    - **Text:** “Your most recent lab test.”
    - **Readings:** Use the latest qualifying valid day-3 FSH result; the latest FSH result of any kind; or the latest reported result, including one later invalidated or corrected.
    - **Encoding:** Selects the latest timestamp in `day_3_fsh_tests`, with no validity, correction, or supersession status.
    - **Example:** A recent result of 21 is withdrawn because of a specimen error, leaving a valid earlier result of 12. A valid-results-only reading qualifies; retaining the withdrawn test does not.

35. **Scope of “all prior tests” at age 40+.**
    - **Text:** “Less than 19 mIU/mL in all prior tests performed after age 40.”
    - **Readings:** All qualifying unmedicated day-3 FSH tests; all day-3 FSH tests, including medicated ones; or all FSH tests regardless of cycle day.
    - **Encoding:** Examines entries in `day_3_fsh_tests` after its age-40 cutoff; medication status is not represented.
    - **Example:** A patient has qualifying unmedicated results below 19 but an FSH of 22 obtained during medication use. The narrower pool may qualify her; the broader pool may not.

36. **Whether “all prior tests” includes the current/latest qualifying test.**
    - **Text:** At 40+, “all prior tests performed after age 40.”
    - **Readings:** All tests before the coverage decision, including the latest test; or historical tests preceding the current test, whose treatment is not separately stated in that age branch.
    - **Encoding:** Includes every listed post-cutoff test, including the most recent.
    - **Example:** All older post-40 tests are below 19, but the newest is 20. Including the newest fails; a strictly prior-to-current-test reading could pass the stated historical condition.

37. **The boundary of “after age 40.”**
    - **Text:** “Performed after age 40.”
    - **Readings:** Beginning on the 40th birthday; strictly after that birthday; or after a more precisely identified birthday instant.
    - **Encoding:** Includes tests from midnight at the start of the 40th birthday.
    - **Example:** An elevated test is performed on the 40th birthday. The encoding includes it; a strictly-after-the-birthday-date reading excludes it from the historical pool.

38. **Whether a patient aged 40+ must have at least one post-40 test.**
    - **Text:** A recent test is required, and “all prior tests performed after age 40” must satisfy the limit.
    - **Readings:** A recent pre-40 test is sufficient when there are no post-40 tests, with the universal historical condition satisfied vacuously; or a post-40 test is required.
    - **Encoding:** Explicitly requires at least one test in the post-40 list.
    - **Example:** A patient turns 40 one week before service and has a qualifying test from the preceding month. The vacuous-history reading qualifies; the encoding fails until a post-40 test exists.

39. **Required completeness of the historical FSH record.**
    - **Text:** “All prior tests.”
    - **Readings:** Require a sufficiently complete history establishing that every relevant test qualifies; or evaluate only available/submitted records unless contrary evidence exists.
    - **Encoding:** Checks only the submitted list and has no completeness requirement.
    - **Example:** One submitted post-40 test is normal, but earlier records cannot be obtained. Available-records adjudication passes; a complete-history evidentiary rule leaves eligibility unestablished.

40. **Tied “most recent” tests.**
    - **Text:** “Most recent lab test.”
    - **Readings:** Use either tied result, require all tied results to qualify, prefer a designated final report, or seek clarification.
    - **Encoding:** Requires a uniquely latest entry. Two entries with the same latest timestamp each disqualify the other from selection.
    - **Example:** Two distinct qualifying results, both below 19, share the latest timestamp. An all-tied-results reading passes; the encoding cannot derive a most-recent test.

41. **Meaning and boundary of “within the past” six or 12 months.**
    - **Text:** “Done within the past” six or 12 months.
    - **Readings:** Inclusive calendar-month anniversaries; a strict less-than interval; or a fixed-day equivalent.
    - **Encoding:** Uses date-based calendar-month arithmetic and admits the exact same-day monthly anniversary.
    - **Example:** A test is exactly six calendar months old. The encoding accepts it; a strict-before-the-six-month-boundary reading rejects it.

42. **Which date represents when a test was “done” or “performed.”**
    - **Text:** “Test done” and “tests performed.”
    - **Readings:** Use specimen collection, laboratory analysis, report issuance, or final corrected-report time.
    - **Encoding:** Supplies one undifferentiated date/time per FSH test.
    - **Example:** A specimen was collected just outside the six-month window, but the result was issued inside it. Collection-date and report-date readings differ.

## Semen analyses

43. **Clinical standard for an “abnormal semen analysis.”**
    - **Text:** “At least 2 abnormal semen analyses.”
    - **Readings:** Any out-of-range parameter suffices; a clinically significant fertility impairment is required; or both analyses must show a specified abnormality.
    - **Encoding:** Receives already-classified abnormal analyses and contains no values, reference ranges, or diagnostic criteria.
    - **Example:** Two analyses have a minor isolated morphology deviation but otherwise normal fertility-related findings. An any-abnormality reading qualifies; a clinically-significant-impairment reading may not.

44. **Whether qualifying abnormal analyses must demonstrate current or persistent abnormality.**
    - **Text:** “At least 2 abnormal semen analyses obtained at least 2 weeks apart,” without a recency or normal-intervening-result rule.
    - **Readings:** Any historical pair suffices; or the pair must support current infertility, potentially requiring recent or consistently abnormal findings.
    - **Encoding:** Accepts any qualifying pair in the abnormal-analysis list; it does not examine normal results or age of results.
    - **Example:** Two abnormal tests occurred years ago, followed by several normal tests. The historical-pair reading qualifies; a current-condition reading may not.

45. **How the two-week interval is measured.**
    - **Text:** “Obtained at least 2 weeks apart.”
    - **Readings:** Compare collection dates, precise collection times, analysis times, or report dates; two calendar weeks may be distinguished from 336 elapsed hours.
    - **Encoding:** Uses date-only entries converted to timestamps and compares their absolute difference to 14 days.
    - **Example:** Samples collected at 11 p.m. on the first day and 8 a.m. 14 dates later qualify under date-based measurement but are less than 336 hours apart.

46. **What constitutes two distinct analyses.**
    - **Text:** “2 abnormal semen analyses.”
    - **Readings:** Require two independently collected specimens; or permit separately performed analyses or reports concerning the same specimen.
    - **Encoding:** Requires two different list positions, not distinct specimen identities.
    - **Example:** One specimen is analyzed twice and reported 15 days apart. A report-based reading could count two; an independent-specimen reading counts one.

## Approval, providers, and covered service components

47. **Requesting advance approval versus actually receiving it.**
    - **Text:** “Your provider will request approval from us in advance.”
    - **Readings:** The stated procedural requirement is an advance request; or actual advance approval is an implied condition of payment.
    - **Encoding:** Requires `precertification_received(C, yes)`.
    - **Example:** A timely request remains pending when treatment occurs. A request-compliance reading may preserve eligibility; the encoded receipt requirement fails.

48. **Scope and timing of advance approval.**
    - **Text:** Approval is requested “in advance for your infertility services.”
    - **Readings:** Approval covers a treatment plan, one cycle, each treatment type, or each separately billed service; its timing may be measured against therapy initiation or the individual procedure.
    - **Encoding:** Uses a claim-level approval flag without approval dates, authorized services, cycle identifiers, or validity periods.
    - **Example:** Approval for a course of ovulation induction is obtained before therapy, and IUI is later added. Course-wide approval could suffice; service-specific approval may not.

49. **Who qualifies as an “infertility specialist.”**
    - **Text:** “Recognized by your physician or infertility specialist” and “charges made by an infertility specialist.”
    - **Readings:** Require a reproductive-endocrinology subspecialist; accept another physician with infertility expertise; or include appropriately credentialed nonphysician clinicians.
    - **Encoding:** Does not identify or test specialist credentials.
    - **Example:** A general obstetrician with substantial infertility practice performs IUI. An expertise-based reading permits the provider; a subspecialty-certification reading does not.

50. **Meaning of charges “made by” a specialist when care is delegated or institutionally billed.**
    - **Text:** “Charges made by an infertility specialist.”
    - **Readings:** The specialist must personally perform and bill the service; specialist supervision suffices; or facility/group billing is acceptable for specialist-directed care.
    - **Encoding:** Checks service location, not the billing or rendering professional or supervision relationship.
    - **Example:** A nurse performs IUI under a specialist’s treatment plan, and a hospital submits the bill. A supervised-care reading covers it; a personal-performance-and-billing reading may not.

51. **Which ancillary components are included in the named infertility services.**
    - **Text:** “Ovulation induction cycle(s) with menotropins” and “Intrauterine insemination.”
    - **Readings:** Cover the procedure alone; cover its clinically integral drugs, monitoring, laboratory work, and sperm preparation; or distinguish bundled from separately billed components.
    - **Encoding:** Recognizes two service-type atoms and provides no component or bundling rules.
    - **Example:** Sperm washing is billed separately from IUI. An integral-service reading covers it; a procedure-code-only reading does not.

## Cycle definition and counting

52. **When a cycle earns credit: initiation or completion.**
    - **Text:** A cycle “is an attempt,” “begins with the initiation of therapy,” and has a specified end.
    - **Readings:** An initiated attempt counts immediately; or only a completed cycle counts toward qualifying history.
    - **Encoding:** Takes numerical cycle/attempt counts as inputs and never derives them from start and completion events.
    - **Example:** A patient has 11 completed donor cycles and has undergone the insemination in a twelfth cycle, but pregnancy status is not yet known. Initiation-based counting reaches 12; completed-cycle counting does not.

53. **What separates multiple attempts of the same treatment type into cycles.**
    - **Text:** A cycle is “an attempt at … intrauterine insemination”; “Each treatment type is counted as a separate cycle.”
    - **Readings:** Multiple inseminations in one ovulatory treatment course form one cycle; or each insemination procedure is a separate attempt. The separate-treatment-type sentence does not settle repeated procedures of the same type.
    - **Encoding:** Does not group procedures into courses or cycles.
    - **Example:** Six ovulatory cycles each contain two donor IUIs on consecutive days. Counting treatment courses yields six cycles; counting individual attempts yields 12.

54. **Canceled or abandoned cycles without the stated endpoint.**
    - **Text:** A cycle begins with therapy and ends with confirmation of non-pregnancy, or the stated pregnancy endpoint.
    - **Readings:** A canceled treatment is still a counted attempt; it counts only after a qualifying endpoint; or it never becomes a countable cycle if the intended procedure was not completed.
    - **Encoding:** Has no cancellation, abandonment, or endpoint logic.
    - **Example:** Therapy starts for a twelfth donor-insemination cycle, but treatment is canceled before insemination because of an excessive response. Counting initiated attempts may satisfy the threshold; requiring completed insemination does not.

55. **Pregnancy loss before six weeks after a positive test.**
    - **Text:** Non-pregnancy ends a cycle with a negative test or menstrual period; “in the case of the achievement of pregnancy,” completion occurs six weeks after a positive test.
    - **Readings:** Once pregnancy occurs, the six-week completion rule controls; or an intervening loss and confirmation of non-pregnancy end the cycle earlier.
    - **Encoding:** Does not model pregnancy, loss, or cycle completion.
    - **Example:** A positive test is followed ten days later by a confirmed early loss. At three weeks, one reading treats the cycle as completed and available for historical counting; the other does not.

56. **Which positive pregnancy test starts the six-week completion period.**
    - **Text:** “6 weeks following a positive pregnancy test.”
    - **Readings:** Use the first positive home test, the first laboratory-positive test, or the first provider-confirmed qualifying result.
    - **Encoding:** Does not record positive-test events or choose a reference test.
    - **Example:** A home test is positive on January 1 and the first laboratory confirmation occurs January 10. On February 15, the cycle is complete under the first-positive reading but not under the laboratory-confirmation reading.

**Implementation caveat:** These descriptions identify the encoding’s substantive choices. They do not certify its execution: for example, the final birthday-adjustment rule has inconsistent month-variable names and can undermine the intended service-date age calculation. Such defects are separate from ambiguities in the policy text.