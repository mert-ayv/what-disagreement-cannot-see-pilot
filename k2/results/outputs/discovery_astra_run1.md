# discovery_astra_run1 (gpt-6-astra, 10130 output tokens, $0.5628)

Below, “passes” means **passes the disputed requirement**, assuming the other requirements are satisfied. “The encoding” refers only to the rules supplied; some matters could be handled by data preparation or other rules not shown.

I distinguish **genuine interpretive gaps** from **clear requirements that the code omits** and **restrictions the code adds without support in these excerpts**. Those implementation issues are summarized separately at the end.

## Relationship between the benefit and the glossary

1. **Whether the table’s donor-insemination alternative overrides the glossary for a female with a male partner.**  
   **Text:** Table: “12 months or more **or** … at least 12 cycles of donor insemination”; glossary: “frequent, unprotected heterosexual sexual intercourse.”  
   **Readings:** The benefit-specific alternative establishes eligibility notwithstanding the glossary; or both provisions must independently be satisfied.  
   **Encoding:** Requires both `patient_is_infertile` and the table. Ordinarily, donor insemination alone does not qualify a female with a male partner.  
   **Example:** A 30-year-old with a male partner has 12 unsuccessful donor cycles but no intercourse. She passes under the benefit-specific reading, but not under the conjunctive reading.

2. **Whether “timed” and “frequent” intercourse are interchangeable or cumulative requirements.**  
   **Text:** Benefit: “unprotected timed sexual intercourse”; glossary: “frequent, unprotected heterosexual sexual intercourse.”  
   **Readings:** These describe the same qualifying course of intercourse; or eligibility requires independently satisfying both descriptions.  
   **Encoding:** Uses separate facts and requires both for the ordinary intercourse pathway. It does not require the two facts to describe the same months.  
   **Example:** Twelve months of intercourse precisely timed to ovulation, but too infrequent to satisfy a separate clinical definition of “frequent,” qualifies under the interchangeable reading but not the cumulative one.

3. **How a male with a female partner satisfies the glossary.**  
   **Text:** The benefit has two rows for “a male … with a female partner”; the glossary supplies a male-specific criterion only for “a male without a female partner.”  
   **Readings:** Apply the couple’s unsuccessful-intercourse history; extend the semen-analysis criterion to these males; require both; or regard the glossary as lacking an applicable pathway.  
   **Encoding:** Requires both the female partner’s age-based intercourse history and two abnormal semen analyses at least two weeks apart.  
   **Example:** A male whose 32-year-old female partner has not conceived after 12 qualifying months, but whose semen analyses are normal, passes the couple-history reading and fails the encoding.

4. **Whether a male without a female partner can receive the benefit.**  
   **Text:** The glossary recognizes infertility through abnormal semen analyses, but the benefit table has no corresponding row.  
   **Readings:** The glossary supplies a valid pathway and the inapplicable table requirements are waived; or absence of a table pathway prevents benefit eligibility.  
   **Encoding:** Can establish `patient_is_infertile`, but cannot satisfy the table.  
   **Example:** A male with a male partner and two qualifying abnormal analyses seeks an otherwise eligible service. The glossary-based pathway could qualify him; the encoding cannot.

5. **Whether gender dysphoria establishes infertility without failure to become pregnant.**  
   **Text:** “A disease defined by the failure to become pregnant: … For an individual or their partner who has been clinically diagnosed with gender dysphoria.”  
   **Readings:** The final bullet is an independent definition; or the introductory failure-to-become-pregnant requirement still applies.  
   **Encoding:** A positive gender-dysphoria fact alone establishes `patient_is_infertile`.  
   **Example:** A person with diagnosed gender dysphoria who has never attempted conception satisfies the encoded glossary definition, but not a reading requiring actual failed attempts.

6. **Whether the gender-dysphoria pathway displaces the table’s attempts and FSH requirements.**  
   **Text:** The glossary expressly includes gender dysphoria, while the benefit says “You have met” the contact requirement and supplies only sex/partner-based rows.  
   **Readings:** The special glossary pathway substitutes for otherwise inapplicable prerequisites; or it establishes infertility only, leaving every benefit prerequisite intact.  
   **Encoding:** Adopts the latter. There is no gender-dysphoria exception to the table.  
   **Example:** An applicant with gender dysphoria and no qualifying attempts could qualify under the substitution reading but fails the encoding.

7. **Whether a gender-dysphoria diagnosis also satisfies the required infertility-causing condition.**  
   **Text:** “There exists a condition … demonstrated to cause the illness of infertility,” alongside the glossary’s gender-dysphoria inclusion.  
   **Readings:** The expressly recognized diagnosis itself satisfies this condition; or a separately demonstrated causal condition remains necessary.  
   **Encoding:** Requires a separate `demonstrated_and_documented_condition_causing_infertility` fact; the diagnosis flag does not generate it.  
   **Example:** A diagnosed applicant who otherwise satisfies the table, but has no additional reproductive diagnosis, passes the first reading but may fail the second.

## People, partners, and attribution

8. **How “female” and “male” are assigned, and what happens outside those classifications.**  
   **Text:** “A female,” “a male,” “male partner,” and “female partner.”  
   **Readings:** Classification could follow sex assigned at birth, legal sex, gender identity, reproductive anatomy, or the person’s role in conception. The excerpts do not specify how to classify intersex or nonbinary applicants.  
   **Encoding:** Requires `female` or `male` facts without defining their basis; it has no additional patient categories.  
   **Example:** A transgender man with ovaries and a male partner might receive the female-with-male-partner pathway under an anatomy-based reading, but no applicable table pathway under a gender-identity reading.

9. **Whether “partner” means only the specified legal relationship or any reproductive partner.**  
   **Text:** A covered dependent who is the student’s “legal spouse, civil union partner or domestic partner, referred to as ‘your partner’”; later, “with a male partner.”  
   **Readings:** The defined legal/coverage relationship controls throughout; or the reproductive table and glossary use “partner” more broadly, including a boyfriend or an uninsured reproductive partner.  
   **Encoding:** Uses partner-sex and partner-age facts without checking relationship or coverage status.  
   **Example:** A covered female student has an unmarried boyfriend who is not a recognized domestic partner and 12 months of unsuccessful intercourse. She passes if he counts as a male partner, but may fall into the donor-only row if he does not.

10. **Which partner controls when more than one person could count.**  
    **Text:** Singular references to “your partner.”  
    **Readings:** Use the legal partner, the person involved in the attempted conception, any qualifying partner, or all relevant partners.  
    **Encoding:** Has no partner identifier linking sex, age, history, sterilization, and diagnosis. Multiple facts could therefore satisfy different predicates without establishing that they concern the same person.  
    **Example:** A female applicant has a female legal spouse and a male reproductive partner. Twelve months of intercourse qualifies her under the reproductive-partner reading but not necessarily under the legal-partner reading.

11. **Whose eligibility governs when treatment involves one partner but the claim or infertility diagnosis concerns the other.**  
    **Text:** “You,” “your or your partner’s medical records,” “your … FSH,” and male-specific table rows.  
    **Readings:** Apply eligibility to the billed patient; to the person trying to become pregnant; or assess the couple jointly, with requirements assigned to the relevant person.  
    **Encoding:** Combines `sex_of_patient_trying_to_conceive` with the claim patient’s DOB and FSH history, without defining how these identities relate.  
    **Example:** Ovulation induction is performed on a female spouse because of her male partner’s infertility. A couple-based reading may recognize eligibility through the affected partner; a strictly billed-patient reading may demand that she independently satisfy the disease requirement.

## The causal condition and exclusions

12. **What evidence “demonstrated to cause” requires.**  
    **Text:** “A condition that … is demonstrated to cause the illness of infertility” and is “recognized” and “documented.”  
    **Readings:** A recognized diagnosis of a generally infertility-causing condition suffices; or patient-specific causal evidence is required. It is also unclear how unexplained infertility fits a requirement for an identified causal condition.  
    **Encoding:** Delegates all of this to one composite claim fact.  
    **Example:** A patient with PCOS and unsuccessful attempts, but no demonstrated anovulation, passes a general-disease-association reading and may fail a patient-specific-causation reading.

13. **Whether a condition documented in the partner’s records establishes the applicant’s eligibility without an individual causal condition.**  
    **Text:** “Documented in your or your partner’s medical records.”  
    **Readings:** Infertility is assessed at couple level, so either person’s condition suffices; or the partner’s record is merely an allowable evidence location for a condition establishing the applicant’s own infertility.  
    **Encoding:** Does not identify the person who has the condition, while separately requiring `patient_is_infertile`.  
    **Example:** A physiologically fertile female applicant has a partner with documented azoospermia. The couple-level reading recognizes the causal prerequisite; an individual-disease reading may not.

14. **The scope of “or” in the sterilization exclusion.**  
    **Text:** “You or your partner has not had a voluntary sterilization.”  
    **Readings:** At least one person must not have been sterilized; neither may have been sterilized; or only the person whose infertility is being treated must satisfy the restriction.  
    **Encoding:** Checks only that the patient has not had voluntary sterilization.  
    **Example:** An unsterilized applicant has a voluntarily sterilized partner. The encoding and literal “at least one” reading pass; the neither-person reading fails.

15. **What makes a procedure “voluntary sterilization” when it has mixed purposes.**  
    **Text:** Hysterectomy, tubal ligation, and vasectomy count “only if obtained as a form of voluntary sterilization.”  
    **Readings:** Contraceptive intent must be the primary purpose; any sterilizing intent suffices; or an elective procedure knowingly causing infertility counts even when predominantly therapeutic or gender-affirming.  
    **Encoding:** Takes a yes/no patient fact without defining the classification.  
    **Example:** A hysterectomy treats severe disease and also serves the patient’s wish for permanent contraception. Primary-purpose and any-contraceptive-purpose readings can produce opposite outcomes.

16. **The scope of “or” in the natural-process restriction.**  
    **Text:** “You or your partner does not have infertility that is due to a natural physiologic process.”  
    **Readings:** At least one person must lack such infertility; neither may have it; or only the relevant cause of the treated infertility must be nonnatural.  
    **Encoding:** Does not test either person comprehensively. It requires a qualifying condition outside a listed set.  
    **Example:** A patient has tubal infertility and a partner has infertility attributed to natural reproductive aging. A neither-person reading excludes the claim; the encoding can pass it.

17. **The boundary of “natural physiologic process.”**  
    **Text:** “Such as age related ovarian insufficiency (e.g. perimenopause, menopause).”  
    **Readings:** A broad class of normal physiological causes is excluded; or the provision principally addresses normal age-related reproductive decline, distinguishing premature or pathological conditions.  
    **Encoding:** Explicitly lists natural male reproductive aging and an open-ended `other_natural_physiologic_process`, but leaves classification to the input.  
    **Example:** Infertility associated with lactational amenorrhea, or ovarian insufficiency unusually early in life, may be excluded under a broad reading and allowed under a narrower one.

18. **How mixed natural and pathological causes are treated.**  
    **Text:** A qualifying “condition” must exist, but the exclusion refers to infertility “due to” a natural process.  
    **Readings:** Any natural contribution excludes; only a predominant or sufficient natural cause excludes; or one qualifying nonnatural cause is enough.  
    **Encoding:** Is existential: one documented condition outside the exclusion list can satisfy the rule even if another excluded condition is also present.  
    **Example:** A patient has both endometriosis and age-related ovarian insufficiency. The encoding can pass her; an any-natural-contribution reading fails her.

## Pregnancy, alternatives, and attempts

19. **What counts as becoming pregnant or achieving a “successful pregnancy.”**  
    **Text:** Glossary: “failure to become pregnant”; benefit: “A successful pregnancy cannot be attained”; cycle definition: “a positive pregnancy test.”  
    **Readings:** Biochemical pregnancy, clinically confirmed pregnancy, ongoing viable pregnancy, and live birth are different possible endpoints. The passages do not align them.  
    **Encoding:** Does not represent failed conception, miscarriage, live birth, or a pregnancy-success definition; it relies on attempt counts and the less-costly-treatment fact.  
    **Example:** A patient repeatedly conceives but has early miscarriages. She may fail a literal never-became-pregnant definition but qualify under inability to achieve an ongoing pregnancy.

20. **How much prospect of success makes a cheaper treatment disqualifying.**  
    **Text:** “A successful pregnancy cannot be attained through less costly treatment.”  
    **Readings:** Any nonzero possibility defeats eligibility; a reasonable clinical prospect does; or only an adequately effective alternative does.  
    **Encoding:** Uses a binary yes/no fact without a probability or clinical threshold.  
    **Example:** A cheaper treatment has a 1% predicted success rate. A possibility-based reading denies escalation; a reasonable-prospect reading may allow it.

21. **What costs are compared.**  
    **Text:** “Less costly treatment.”  
    **Readings:** Compare per-cycle charges, the total expected treatment course, expected cost per successful pregnancy, insurer expenditure, or patient expenditure.  
    **Encoding:** Does not specify the comparator or cost perspective.  
    **Example:** A cheaper-per-cycle treatment needs many more cycles and has a higher expected total cost. Per-cycle and total-course readings differ.

22. **Whether cheaper treatments must actually be tried.**  
    **Text:** “Cannot be attained through less costly treatment.”  
    **Readings:** A clinical prediction of futility suffices; or actual unsuccessful trials are normally required.  
    **Encoding:** The benefit rule delegates this to a Boolean. A separate medical-necessity rule also imposes specified contact trials for menotropin induction, but does not explain their relationship to exhaustion of cheaper treatments.  
    **Example:** A specialist documents that a covered cheaper treatment is futile and recommends proceeding directly to the requested service. Prediction-based eligibility passes; mandatory step therapy fails.

23. **Whether theoretical coverage is enough to make a cheaper treatment an available alternative.**  
    **Text:** “For which coverage is available under this plan.”  
    **Readings:** The treatment need only be a listed benefit; or coverage and practical clinical availability must exist for this patient, including remaining limits and contraindications.  
    **Encoding:** Leaves “available” inside the composite Boolean.  
    **Example:** A cheaper service is normally covered but this patient has exhausted its benefit limit. A benefit-list reading blocks escalation; a patient-specific-availability reading does not.

24. **How months of attempts accumulate and whether they reset.**  
    **Text:** “Number of months … trying to conceive” and “12 months or more” or “6 months or more.”  
    **Readings:** Require consecutive recent months, allow cumulative separated months, or count elapsed time since attempts began. Pregnancy, treatment breaks, contraception, or a resolved prior condition might or might not reset the clock.  
    **Encoding:** Accepts scalar month totals without dates, continuity, or reset rules.  
    **Example:** Six qualifying months, a year-long break, then six more months passes a cumulative reading but fails a consecutive-current-period reading.

25. **Whether attempts with a previous partner count.**  
    **Text:** “You or your partner,” and the partner-dependent table.  
    **Readings:** Attempts establish the individual’s history regardless of partner; or they must involve the present reproductive partnership.  
    **Encoding:** Does not associate attempt counts with identified partners or relationship dates.  
    **Example:** A 30-year-old has 12 unsuccessful months with a former partner and one month with the current partner. Individual-history and current-couple readings differ.

26. **Whether intercourse and donor-insemination trials can be combined.**  
    **Text:** “A. 12 months … or B. At least 12 cycles,” with corresponding six-unit alternatives.  
    **Readings:** One entire alternative must be completed; or equivalent exposure can be accumulated across methods under the broader “egg and sperm contact” requirement.  
    **Encoding:** Requires a full threshold in one method; it does not combine them.  
    **Example:** Six qualifying intercourse months plus six donor cycles fails the encoded table for an under-35 applicant but could pass an aggregate-exposure reading.

27. **What “frequent” and “timed” mean operationally.**  
    **Text:** “Frequent” intercourse in the glossary; “timed” intercourse in the benefit.  
    **Readings:** Timing could require ovulation testing, clinician direction, or simply intercourse during an estimated fertile window; frequency might mean a minimum per week or adequate fertile-window exposure.  
    **Encoding:** Accepts counts already classified under these labels and supplies no criteria.  
    **Example:** Intercourse once during each estimated fertile window may count as timed and sufficiently frequent under one standard, but not another.

28. **Which insemination practices qualify as “donor artificial insemination.”**  
    **Text:** “Donor artificial insemination cycles” and “donor insemination.”  
    **Readings:** Include home vaginal insemination, intracervical insemination, and known-donor procedures; or require specified clinical techniques or professionally sourced donor sperm.  
    **Encoding:** Uses a generic donor-cycle count with no method, setting, or donor-status definition.  
    **Example:** Twelve unsuccessful home inseminations using a known donor pass a broad reading but fail a clinic-only reading.

29. **What “self paid/not paid for by plan” permits.**  
    **Text:** The donor-cycle column is headed “Self paid/not paid for by plan.”  
    **Readings:** The applicant must personally pay; or the essential condition is simply that this plan did not pay, allowing another insurer, an employer, or charity to fund the attempts.  
    **Encoding:** Does not track who paid for the donor cycles.  
    **Example:** Twelve cycles funded by another insurer qualify under the not-this-plan reading but not a literal self-payment requirement.

30. **Whether the later “cycle” definition governs the prerequisite donor-cycle counts.**  
    **Text:** The table counts donor cycles; later, “A ‘cycle’ is an attempt at ovulation induction or intrauterine insemination.”  
    **Readings:** That definition applies throughout the benefit, including prior donor attempts; or it defines only the two covered treatment types, leaving donor-cycle counting to ordinary clinical practice.  
    **Encoding:** Accepts a donor-cycle total without deriving it from treatment events.  
    **Example:** A donor cycle begins with medication but is canceled before insemination. It might count as an initiated treatment attempt under one reading and not as a completed donor-insemination cycle under another, changing whether the applicant reaches 12.

## Age and semen-analysis rules

31. **When age and partner status are measured.**  
    **Text:** “You are” in the table; “if under the age of 35” in the glossary.  
    **Readings:** Use age and partnership at the service date, authorization date, treatment initiation, diagnosis, or start of attempts.  
    **Encoding:** Uses service-date age for the patient. Partner age is supplied directly without a stated reference date; partner status is also undated.  
    **Example:** A person turns 35 after authorization but before treatment and has only six qualifying months. Service-date and authorization-date readings differ.

32. **Whether entering a new age band reclassifies earlier attempts.**  
    **Text:** The requirements change from 12 to six months/cycles at 35.  
    **Readings:** At 35, all prior qualifying attempts count toward the lower threshold; or some or all of the applicable period must occur within the new age band.  
    **Encoding:** Applies the service-date threshold to an undifferentiated total.  
    **Example:** A patient turns 35 today after six months of attempts at age 34. The encoding allows the six-month pathway; a requirement for six months after entering the age band does not.

33. **What makes a semen analysis “abnormal.”**  
    **Text:** “At least 2 abnormal semen analyses.”  
    **Readings:** Any out-of-range parameter suffices; or the abnormality must be clinically significant for infertility, use a particular reference standard, or be consistent between samples.  
    **Encoding:** Accepts analyses already labeled abnormal, with dates only.  
    **Example:** Two analyses have a marginal abnormality not considered fertility-impairing by the specialist. A laboratory-flag reading qualifies; a clinically significant abnormality reading may not.

34. **Whether old abnormal analyses remain sufficient after normal results or recovery.**  
    **Text:** “At least 2 abnormal semen analyses obtained at least 2 weeks apart,” within a present-tense disease definition.  
    **Readings:** Any historical qualifying pair suffices; or the analyses must establish current infertility, so later normal results or treatment can defeat eligibility.  
    **Encoding:** Any qualifying pair in the supplied abnormal-analysis list suffices. It has no recency test or normal-result assessment.  
    **Example:** Two abnormal tests ten years ago are followed by successful treatment and several normal tests. The encoded analysis requirement passes; a current-disease reading may fail.

## FSH requirements

35. **What “unmedicated” excludes.**  
    **Text:** “Unmedicated day 3 … FSH.”  
    **Readings:** No fertility medication during that cycle; no medication affecting FSH; or a specified washout period after hormones.  
    **Encoding:** Test records contain only level, date, and time. It does not independently establish unmedicated status.  
    **Example:** A patient stops hormonal medication two days before a low FSH test. A no-medication-on-test-day reading accepts it; a washout-period reading rejects it.

36. **How “day 3” is determined in atypical cycles.**  
    **Text:** “Day 3 … FSH.”  
    **Readings:** The third day of spontaneous full menstrual flow; a clinically designated third day after induced bleeding; or an accepted equivalent for someone without regular menstruation.  
    **Encoding:** Assumes the supplied tests are day-3 tests and does not define cycle-day assignment.  
    **Example:** A patient with amenorrhea is tested after a medication-induced withdrawal bleed. One reading recognizes a qualifying day-3 test; another does not.

37. **Which tests are included in “most recent” and “all prior tests.”**  
    **Text:** “Your most recent lab test” and “all prior tests performed after age 40,” within an unmedicated day-3 FSH table.  
    **Readings:** Only valid unmedicated day-3 FSH tests count; all day-3 FSH tests count; or all FSH tests count, including tests on other days or during medication.  
    **Encoding:** Uses the supplied `day_3_fsh_tests` list, without medication or validity fields.  
    **Example:** A qualifying unmedicated day-3 result is 12, but a later medicated or non-day-3 FSH result is 24. Restricting the universe to qualifying tests passes; including the later result fails.

38. **How to handle multiple results with the same latest timestamp.**  
    **Text:** “Your most recent lab test.”  
    **Readings:** Use the final authoritative report, require all tied results to pass, or accept any qualifying latest result. The text gives no tie rule.  
    **Encoding:** Its selection rule rejects a candidate if any other test is at the same or a later timestamp. Thus two equally latest entries can leave no “most recent” test—even if identical.  
    **Example:** Two copies of the same passing latest result can make the encoding fail, while a duplicate-collapsing reading passes.

39. **The reference date for “within the past” six or 12 months.**  
    **Text:** “Test done within the past” specified period.  
    **Readings:** Measure backward from authorization, cycle initiation, each service, or claim adjudication.  
    **Encoding:** Measures from `date_service_received`.  
    **Example:** A test is within six months at cycle initiation but slightly older when insemination occurs. Cycle-start and individual-service readings differ.

40. **How calendar-month boundaries and the exact anniversary are handled.**  
    **Text:** “Within the past … 6 months” or “12 months.”  
    **Readings:** Include or exclude the exact anniversary; use calendar-month arithmetic, end-of-month adjustment, or a fixed day count.  
    **Encoding:** Uses month/day arithmetic and includes an exact same-day anniversary. It does not apply a general end-of-month adjustment.  
    **Example:** An August 31 test for February 28 service can be treated as within six calendar months under an end-of-month convention but fails the supplied helper.

41. **What “after age 40” includes at the birthday boundary.**  
    **Text:** “All prior tests performed after age 40.”  
    **Readings:** Include tests on or after the 40th birthday; or interpret “after” strictly, excluding a test on the birthday itself.  
    **Encoding:** Includes tests from midnight at the start of the 40th birthday.  
    **Example:** A high FSH result on the 40th birthday followed by a low result disqualifies under the encoding, but not under a reading excluding birthday-day tests.

42. **Whether “all prior tests” includes the latest test.**  
    **Text:** For age 40 and older, “must be less than 19 … in all prior tests performed after age 40.”  
    **Readings:** “Prior” means prior to the coverage assessment, including the latest test; or it means tests before the current/latest test, with the table failing to state that latest test’s numerical rule separately.  
    **Encoding:** Includes all supplied post-40 tests, including the latest.  
    **Example:** Earlier post-40 results are below 19 but the latest is 21. The encoding fails; a strictly earlier-tests-only reading could pass.

43. **Whether someone newly 40 must have a post-40 test.**  
    **Text:** A test must be within six months, and “all prior tests performed after age 40” must be below 19.  
    **Readings:** A recent pre-40 test suffices, with an empty post-40 history satisfying the universal condition; or at least one post-40 test is required.  
    **Encoding:** Explicitly requires a nonempty post-40 list.  
    **Example:** A patient turns 40 shortly before service and has a passing test from one month earlier. She passes the first reading and fails the encoding.

44. **Whether superseded, invalid, or erroneous FSH results remain disqualifying.**  
    **Text:** “Most recent lab test” and “all prior tests.”  
    **Readings:** Use only final, clinically valid results; or every performed/reported test remains part of the history.  
    **Encoding:** Has no invalidation or correction mechanism except removing or replacing entries before evaluation.  
    **Example:** A post-40 result of 25 is formally corrected by the laboratory to 12. Keeping both entries fails the encoding; using the corrected authoritative result passes.

45. **What evidence is needed to establish a complete test history or the absence of a partner.**  
    **Text:** “All prior tests” and “without a male [or female] partner.”  
    **Readings:** Require affirmative verification or complete records; allow a patient/provider attestation; or adjudicate from the available claim record unless contrary evidence appears. The excerpts provide no evidence-completeness rule.  
    **Encoding:** Searches only supplied tests and uses negated partner-sex facts. Under negation-as-failure, missing partner information can act as absence, and an incomplete test list can act as complete.  
    **Example:** A claim supplies one passing post-40 test but says earlier records are unavailable. An available-records approach passes; a complete-history approach defers or rejects eligibility. This is an evidence-handling gap, not permission to disregard a known high result.

## Services, providers, and approval

46. **Who qualifies as an “infertility specialist.”**  
    **Text:** “Charges made by an infertility specialist.”  
    **Readings:** Require a particular subspecialty certification, insurer designation, fertility-focused practice, or relevant expertise.  
    **Encoding:** Checks locations, not specialist qualifications.  
    **Example:** A general obstetrician with substantial infertility experience performs IUI. An expertise-based reading may cover it; a subspecialty-certification reading may not.

47. **Whether the specialist must bill, personally perform, or merely direct the service.**  
    **Text:** “Charges made by an infertility specialist.”  
    **Readings:** The billing entity must be the specialist; the specialist must personally render treatment; or services performed under specialist supervision qualify.  
    **Encoding:** Does not represent billing, rendering, or supervising providers.  
    **Example:** A nurse performs IUI under a specialist’s direction, but a hospital submits the bill. A supervised-care reading covers it; a specialist-billing or personal-performance reading may not.

48. **Whether associated services are included in a covered treatment cycle.**  
    **Text:** “Comprehensive infertility care,” followed by coverage for “ovulation induction cycle(s) with menotropins” and “intrauterine insemination.”  
    **Readings:** These service descriptions include necessary monitoring, preparation, and associated components; or they identify only the core procedures, with component coverage requiring separate authority.  
    **Encoding:** Recognizes only two service-type atoms and provides no component or bundling rules.  
    **Example:** An ultrasound used solely to monitor a covered menotropin cycle qualifies under a bundled-cycle reading but not necessarily as a separately billed service under the narrow reading.

49. **How much use of menotropins makes an induction cycle a cycle “with menotropins.”**  
    **Text:** “Ovulation induction cycle(s) with menotropins.”  
    **Readings:** Any menotropin use suffices; menotropins must be the principal induction agent; or only a particular treatment protocol qualifies.  
    **Encoding:** Takes the service label as given without examining the drug regimen.  
    **Example:** A predominantly oral-agent induction cycle includes one supplemental menotropin dose. It passes an any-use reading but may fail a principal-agent reading.

50. **Whether requesting advance approval is enough, or actual approval is a condition of coverage.**  
    **Text:** “Your provider will request approval from us in advance.”  
    **Readings:** The stated duty is to submit the request before treatment; or treatment is covered only if approval is actually granted beforehand. The consequence of a timely unresolved request is unstated.  
    **Encoding:** Requires `precertification_received(..., yes)`.  
    **Example:** The provider requests approval on time, but the insurer has not responded by treatment day. A request-compliance reading passes; the encoding fails.

51. **What event approval must precede, and how long it remains effective.**  
    **Text:** “In advance for your infertility services.”  
    **Readings:** Approval is required before each service, before each cycle, or once for an authorized course. Renewal after protocol changes or additional cycles is not specified.  
    **Encoding:** Uses one undated claim-level approval flag, without authorized scope or validity dates.  
    **Example:** One approval covers a planned induction/IUI course, but a later cycle is added. A course-wide reading may cover it; a per-cycle reading requires new approval.

## Cycle boundaries and unfinished treatment

52. **What happens to a cycle canceled or abandoned after therapy begins.**  
    **Text:** “The cycle begins with the initiation of therapy and ends when the treatment is followed by confirmation of non-pregnancy,” or six weeks after a positive test.  
    **Readings:** Initiation creates an attempt that remains a countable treatment cycle even if abandoned; or specified completion evidence is necessary before it counts as a completed cycle. There is no cancellation rule.  
    **Encoding:** Does not model cycle states or derive counts from starts and completions.  
    **Example:** A prior donor-associated IUI cycle starts but is canceled, and the patient has 11 other cycles. Depending on the scope and counting interpretation of “cycle,” the patient may or may not meet a 12-cycle prerequisite. The text does not itself say that unfinished treatment charges are categorically excluded.

53. **How an early pregnancy loss interacts with the two completion rules.**  
    **Text:** Completion at confirmed non-pregnancy versus “6 weeks following a positive pregnancy test.”  
    **Readings:** Any positive test commits the cycle to the six-week rule; or a subsequent loss and negative test completes it earlier under the non-pregnancy rule.  
    **Encoding:** Does not address this interaction.  
    **Example:** A positive test is followed by a confirmed loss two weeks later. A new treatment shortly afterward could be classified as a new cycle under the loss-completion reading but as treatment during the previous cycle under the fixed-six-week reading, affecting cycle-based service classification or prerequisite counts.

54. **Which positive test starts the six-week clock.**  
    **Text:** “6 weeks following a positive pregnancy test.”  
    **Readings:** Use the first positive home test, first laboratory confirmation, or a provider-recognized definitive positive result.  
    **Encoding:** Does not represent pregnancy tests or completion dates.  
    **Example:** A home test is positive ten days before laboratory confirmation. Treatment or cycle accounting near the six-week boundary falls into different cycles depending on which test controls.

55. **How to distinguish repeated procedures within one treatment type from separate attempts.**  
    **Text:** “A ‘cycle’ is an attempt” and “Each treatment type is counted as a separate cycle.”  
    **Readings:** Multiple inseminations in one ovulatory cycle form one IUI attempt; or each separately initiated insemination procedure is an attempt. The explicit separation of different treatment types does not resolve repetition within the same type.  
    **Encoding:** Accepts donor-cycle counts and counts of other artificial-insemination attempts without defining their relationship.  
    **Example:** Six ovulatory cycles each include two donor IUIs. Counting biological treatment cycles gives six; counting individual insemination attempts gives 12, potentially changing under-35 prerequisite eligibility.

## Important distinctions: not additional policy ambiguities

The following should **not** be presented as competing interpretations of these passages:

- **Clear requirements omitted or not explicitly checked:** covered-student/eligible-dependent status; specialist involvement; genuinely unmedicated qualifying FSH testing; and qualifying prior donor cycles not being paid by this plan. The exact interpretation of some terms is uncertain, as listed above, but their express presence is not.
- **Unsupported added restrictions:** the age-37 menotropin ceiling, the separate three-/four-insemination medical-necessity trials, the six-other-attempt IUI limit, and the named provider-location restrictions are not supplied by these excerpts. They may have authority elsewhere, but they are not readings that can be derived here.
- **Coding defects or scope mismatches rather than policy ambiguity:** the benefit predicate’s `24_25` label versus the supplied 2023–2024 certificate; the `FOBMonth`/`DOBMonth` variable mismatch in the age helper; and the recency helper’s failure to prohibit future-dated tests. “Within the past” does not authorize future tests.
- **Clearly settled numerical and treatment-type rules:** below 19 excludes exactly 19; the table expressly changes bands at 35 and 40; reversal does not remove the voluntary-sterilization restriction; and induction and IUI are counted separately when both treatment types occur. The uncertainties above concern application, scope, and missing edge-case rules—not those explicit statements.