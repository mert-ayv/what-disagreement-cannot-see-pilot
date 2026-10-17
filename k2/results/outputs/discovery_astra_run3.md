# discovery_astra_run3 (gpt-6-astra, 10672 output tokens, $0.5899)

The list below distinguishes **genuine interpretive questions** from straightforward encoding omissions or added restrictions. “Passes” means passes the disputed requirement, assuming all other requirements are met. Where the encoding merely accepts a claim field, it generally **delegates**, rather than resolves, the underlying interpretation.

## Relationship between the benefit and glossary

1. **Whether the benefit’s donor-insemination alternative overrides the glossary’s intercourse requirement.**  
   **Text:** A female with a male partner may qualify through “12 cycles of donor insemination” or six cycles, but the glossary defines infertility for that category through heterosexual intercourse.  
   **Readings:** The benefit supplies an alternative to the glossary’s definition; or the glossary and benefit are cumulative, so donor insemination satisfies only the benefit’s waiting requirement.  
   **Encoding:** Requires both `patient_is_infertile` and the benefit table. Ordinarily, a female with a male partner must therefore have the glossary’s intercourse history even when using the table’s donor-insemination alternative.  
   **Example:** A 32-year-old with a male partner has completed 12 unsuccessful donor inseminations but cannot have intercourse. The benefit-specific reading permits qualification; the cumulative reading does not.

2. **Whether “frequent” and “timed” intercourse are separate requirements or descriptions of the same qualifying history.**  
   **Text:** The glossary says “frequent, unprotected heterosexual sexual intercourse”; the table says “unprotected timed sexual intercourse.”  
   **Readings:** Both distinct conditions must be established; or satisfying the benefit’s timed-intercourse requirement also satisfies the glossary’s intended conception-attempt requirement.  
   **Encoding:** Uses separate claim fields and requires both for the ordinary intercourse route. It supplies no implication between them.  
   **Example:** A couple has intercourse once per month at confirmed ovulation for 12 months. That may qualify as timed intercourse but not as “frequent” intercourse.

3. **The missing glossary definition for a male with a female partner.**  
   **Text:** The benefit has rows for such males; the glossary expressly addresses males only “without a female partner.”  
   **Readings:** Use the female partner’s unsuccessful conception history; require independently demonstrated male-factor infertility; extend the semen-analysis criterion to partnered males; or regard the glossary as leaving this category unresolved.  
   **Encoding:** Requires intercourse history based on the female partner’s age **and** two abnormal semen analyses at least two weeks apart, unless the gender-dysphoria rule supplies infertility status.  
   **Example:** A male with normal semen analyses and a 30-year-old female partner has tried unsuccessfully for 12 months. A couple-based reading can qualify him; the encoding’s ordinary route cannot.

4. **The missing benefit-table row for a male without a female partner.**  
   **Text:** The glossary recognizes infertility after two qualifying abnormal semen analyses, but the benefit table has no corresponding row.  
   **Readings:** The glossary route is sufficient, with inapplicable table conditions waived; or the table exhaustively identifies eligible configurations.  
   **Encoding:** Can establish `patient_is_infertile`, but cannot establish the table requirements for this configuration.  
   **Example:** A male with a male partner has two abnormal analyses three weeks apart. He satisfies the glossary but cannot satisfy the encoded benefit table.

5. **The effect of the gender-dysphoria definition on the other eligibility requirements.**  
   **Text:** Infertility includes an individual “or their partner who has been clinically diagnosed with gender dysphoria,” while the benefit still requires a demonstrated condition, conception attempts, and applicable FSH criteria.  
   **Readings:** The diagnosis replaces only the glossary’s ordinary infertility definition; also replaces the conception-attempt requirements; or requires a special eligibility pathway where ordinary reproductive criteria are inapplicable. There is also an unresolved question whether the diagnosis itself constitutes the benefit’s demonstrated infertility-causing condition.  
   **Encoding:** The diagnosis satisfies only `patient_is_infertile`; all benefit conditions and a table row remain necessary.  
   **Example:** An otherwise qualifying 30-year-old with a male partner and a gender-dysphoria diagnosis has not attempted intercourse or insemination. A substituted-pathway reading can qualify them; the encoding does not.

## Persons, partners, and applicable categories

6. **What determines “female” and “male.”**  
   **Text:** The table and glossary organize eligibility around “female” and “male,” without defining those classifications.  
   **Readings:** Sex assigned at birth, current legal sex, gender identity, reproductive anatomy, or reproductive role.  
   **Encoding:** Takes `sex_of_patient_trying_to_conceive` and partner-sex facts as inputs; it does not define their meaning.  
   **Example:** A transgender man with ovaries and a male partner could enter a female-with-male-partner pathway under an anatomical classification, but a male-without-female-partner pathway under an identity-based classification.

7. **People who do not fit either binary category.**  
   **Text:** All table rows use “female” or “male.”  
   **Readings:** The categories are exhaustive eligibility restrictions; or an intersex or nonbinary person should be assigned the requirements appropriate to their reproductive circumstances.  
   **Encoding:** Has no direct pathway for a patient whose sex field is neither `female` nor `male`, including through the gender-dysphoria rule alone.  
   **Example:** A nonbinary person with ovaries has completed 12 unsuccessful donor cycles and has qualifying FSH results. A functional reading permits qualification; an exhaustive-category reading does not.

8. **Whether every use of “partner” has the opening paragraph’s legal-relationship meaning.**  
   **Text:** The opening refers to the student’s “legal spouse, civil union partner or domestic partner,” called “your partner”; the table then uses “male partner” and “female partner.”  
   **Readings:** Only those recognized relationships count throughout; or the table refers more broadly to a sexual or reproductive partner. Whether a student’s partner must also be covered is likewise not clearly carried through into the table.  
   **Encoding:** Uses partner-sex and partner-age facts without checking relationship type or the partner’s enrollment.  
   **Example:** A student attempting conception with an uninsured boyfriend could use the with-male-partner intercourse route under the broader reading, but be treated as without a qualifying male partner under the narrower one.

9. **Whose infertility-causing condition can support whose services.**  
   **Text:** A condition must be documented “in your or your partner’s medical records.”  
   **Readings:** Either person’s infertility can support services furnished to the other; or the claimant must themselves have infertility, although supporting evidence may be located in either record.  
   **Encoding:** Requires `patient_is_infertile(C)` and an unassigned condition field. It does not identify the person who has the condition or explicitly establish a partner-based attribution rule.  
   **Example:** A female receives insemination solely because of her male partner’s infertility, before she independently meets the glossary’s waiting period. A partner-based reading can qualify the service; the patient-specific encoded route generally cannot.

10. **Who “you” is when the claimant, treated person, and person attempting pregnancy differ.**  
    **Text:** The benefit combines “you,” “your partner,” and patient-specific table requirements without explaining claims involving different reproductive participants.  
    **Readings:** Apply requirements to the person receiving the billed service, the insured whose benefit is used, or the intended pregnant person.  
    **Encoding:** Uses the claim patient’s age and FSH history, while separately naming the sex field `sex_of_patient_trying_to_conceive`. No rule reconciles different persons.  
    **Example:** An insured male submits a claim associated with insemination performed on his female partner. Applying his male row and applying her female row produce different FSH requirements.

11. **Multiple partners or reproductive participants.**  
    **Text:** The policy speaks of “your partner” in the singular.  
    **Readings:** Use the current legal partner, the person providing gametes, the person with whom conception is attempted, or evaluate all relevant partners.  
    **Encoding:** Does not enforce a single partner or tie sex, age, condition, and history facts to one identified person. Multiple facts can support different rule branches.  
    **Example:** A male has a 32-year-old legal spouse and is attempting conception with a 38-year-old reproductive partner. The applicable waiting requirement could be 12 or six months.

12. **What establishes that a person is “without” a partner of a specified sex.**  
    **Text:** “Without a male partner” and “without a female partner.”  
    **Readings:** Affirmative evidence of absence is required; or absence of a recorded qualifying partner is sufficient operationally. The policy supplies no evidentiary default.  
    **Encoding:** Uses negation, such as `~claim.sex_of_patients_partner(C, male)`. Under negation-as-failure evaluation, missing information functions as absence.  
    **Example:** A female’s partner information is omitted, but she has 12 donor cycles and no intercourse history. Treating the omission as “without a male partner” can qualify her; requiring confirmation leaves eligibility unestablished.

13. **When age determines the applicable category.**  
    **Text:** “Under 35,” “35 years of age or older,” and “age 40 and older,” without specifying the assessment date.  
    **Readings:** Age when attempts began, when infertility was diagnosed, at authorization, at cycle initiation, or on each service date.  
    **Encoding:** Uses the patient’s age on the service date. The female partner’s age is supplied directly, without an encoded reference date.  
    **Example:** A patient begins attempts at 34 and turns 35 after six unsuccessful months. Service-date classification permits the six-month route; classification fixed at the start can require 12 months.

## Infertility, pregnancy, and qualifying conditions

14. **“Failure to become pregnant” versus inability to attain a “successful pregnancy.”**  
    **Text:** The glossary uses the former; the less-costly-treatment provision uses the latter.  
    **Readings:** Any pregnancy defeats the relevant failure criterion; or biochemical pregnancy, ectopic pregnancy, miscarriage, or other unsuccessful pregnancy does not establish reproductive success. “Successful” could itself mean clinical pregnancy, viability, or live birth.  
    **Encoding:** Does not define either pregnancy endpoint. It uses attempt counts and a boolean about successful pregnancy through cheaper treatment.  
    **Example:** A patient conceives repeatedly but miscarries early. A literal failure-to-become-pregnant definition may exclude her; a successful-pregnancy definition may recognize infertility.

15. **The effect of previous pregnancy on the qualifying history.**  
    **Text:** “Failure to become pregnant” after a stated period; no restart rule is supplied.  
    **Readings:** A pregnancy resets the waiting period; only a successful pregnancy resets it; or qualifying prior unsuccessful attempts remain usable for recurrent or secondary infertility.  
    **Encoding:** Uses aggregate counts without pregnancy dates or reset logic.  
    **Example:** A patient had 12 unsuccessful months, then a miscarriage, followed by two unsuccessful months. Preserving the prior history permits qualification; restarting after any pregnancy does not.

16. **What counts as a condition “demonstrated to cause” infertility.**  
    **Text:** “There exists a condition” that is “demonstrated to cause the illness of infertility.”  
    **Readings:** A specific causal diagnosis is necessary; a clinical diagnosis of unexplained infertility is sufficient; or a condition known generally to cause infertility suffices without proof of causation in this patient.  
    **Encoding:** Delegates the determination to `demonstrated_and_documented_condition_causing_infertility`.  
    **Example:** A couple has a well-documented infertility diagnosis after normal diagnostic testing, but no identified cause. A diagnosis-based reading permits qualification; a specific-cause reading does not.

17. **The scope of “or” in the voluntary-sterilization condition.**  
    **Text:** “You or your partner has not had a voluntary sterilization.”  
    **Readings:** Neither person may have been sterilized; it is sufficient that at least one has not; or only the person whose fertility is relevant to the claimed service must not have been sterilized.  
    **Encoding:** Checks only that the patient has not had voluntary sterilization.  
    **Example:** An unsterilized patient has a partner who underwent voluntary vasectomy. The encoding passes this condition; a neither-person reading fails it.

18. **“Voluntary sterilization” when a procedure has mixed purposes.**  
    **Text:** Hysterectomy, tubal ligation, and vasectomy count “only if obtained as a form of voluntary sterilization.”  
    **Readings:** Contraception must be the primary purpose; any intentional contraceptive purpose suffices; or a medically indicated procedure is outside the exclusion despite a concurrent desire for permanent contraception.  
    **Encoding:** Delegates everything to a patient-level yes/no field.  
    **Example:** A hysterectomy treats severe bleeding and also fulfills the patient’s request for permanent contraception. The different purpose tests produce different eligibility outcomes.

19. **The scope of “or” in the natural-physiologic-process condition.**  
    **Text:** “You or your partner does not have infertility that is due to a natural physiologic process.”  
    **Readings:** Neither person may have naturally caused infertility; one unaffected person is enough; or the exclusion concerns only the infertility supporting the claimed treatment.  
    **Encoding:** Tests the supplied condition against a list, without separately evaluating both people’s infertility.  
    **Example:** A patient has acquired tubal damage, while their partner has infertility attributed to natural reproductive aging. A couple-wide exclusion fails; a patient-condition reading can pass.

20. **The boundary of “natural physiologic process.”**  
    **Text:** “Such as age related ovarian insufficiency (e.g. perimenopause, menopause).”  
    **Readings:** The category extends to normal male reproductive aging and other ordinary biological processes; or it is limited to processes comparable to the specified ovarian examples. The distinction between pathological premature insufficiency and natural aging also needs clinical interpretation.  
    **Encoding:** Expressly includes `natural_male_reproductive_aging` and a catch-all `other_natural_physiologic_process`, but delegates classification into those labels.  
    **Example:** A male’s infertility is attributed to ordinary age-related sperm decline. A broad reading excludes him; a narrower ovarian-process reading does not.

21. **Mixed natural and non-natural causes.**  
    **Text:** Infertility “due to” a natural process, combined with “there exists a condition” causing infertility.  
    **Readings:** Any natural contribution triggers exclusion; natural physiology must be the predominant or independently sufficient cause; or one qualifying non-natural cause is enough.  
    **Encoding:** Can satisfy the rule using any supplied infertility-causing condition outside the exclusion list. It does not globally reject a claim because another supplied condition is natural.  
    **Example:** A patient has both tubal obstruction and age-related ovarian insufficiency. Selecting tubal obstruction can satisfy the encoding; an any-contribution exclusion fails the claim.

## The less-costly-treatment prerequisite

22. **How certain it must be that cheaper treatment cannot work.**  
    **Text:** “A successful pregnancy cannot be attained through less costly treatment.”  
    **Readings:** Literal impossibility, medical futility, an unacceptably low probability, or a physician’s reasonable judgment that escalation is appropriate.  
    **Encoding:** Delegates the standard to a yes/no claim field.  
    **Example:** A cheaper treatment has a two-percent success probability. Literal possibility defeats eligibility; a clinical-futility standard may permit it.

23. **Whether cheaper treatment must actually have been attempted.**  
    **Text:** “Cannot be attained through less costly treatment,” without an express fail-first protocol.  
    **Readings:** Documented clinical unsuitability is enough; or actual unsuccessful trials are required before inability is established.  
    **Encoding:** Requires the boolean “no,” not evidence of failed cheaper treatments. Its separate CPB rules concern conception trials, not a general cheaper-treatment exhaustion rule.  
    **Example:** A specialist predicts that a cheaper treatment will not work and recommends skipping it. A predictive reading permits escalation; a fail-first reading does not.

24. **What “less costly” compares.**  
    **Text:** “Less costly treatment.”  
    **Readings:** Per procedure, per cycle, total expected treatment course, expected cost per successful pregnancy, plan expenditure, or patient expenditure.  
    **Encoding:** Does not calculate or define cost.  
    **Example:** A cheaper individual procedure requires many expected repetitions and costs more overall. Per-procedure comparison can bar escalation; course-level comparison may not.

25. **When coverage for an alternative is “available.”**  
    **Text:** Treatment “for which coverage is available under this plan.”  
    **Readings:** The alternative need only be a generally covered benefit; or it must actually be payable and accessible for this person, with limits remaining and applicable authorization and provider requirements satisfied.  
    **Encoding:** Delegates this to the same boolean.  
    **Example:** A cheaper treatment is listed as covered, but the patient has exhausted its benefit allowance. General-benefit availability blocks escalation; patient-specific availability does not.

26. **Which alternative reproductive routes must be considered.**  
    **Text:** “A successful pregnancy” through cheaper treatment, without specifying whose gametes or which reproductive objective must be preserved.  
    **Readings:** Any medically feasible covered route to pregnancy counts; or only alternatives consistent with the patient’s intended use of their own or their partner’s gametes count.  
    **Encoding:** Does not identify or compare alternative routes.  
    **Example:** Donor-sperm insemination is cheaper and likely to work, but the couple seeks treatment using the male partner’s sperm. The broader alternative-treatment reading can bar that treatment; the narrower one may not.

## Conception-attempt requirements

27. **What makes intercourse “frequent” or “timed.”**  
    **Text:** “Frequent” in the glossary and “timed” in the table are undefined.  
    **Readings:** A specified frequency or documented ovulation timing is required; or reasonable regular attempts during an estimated fertile window suffice.  
    **Encoding:** Accepts counts already labeled with these terms.  
    **Example:** Intercourse twice monthly using calendar estimates may qualify under a practical standard but fail a standard requiring confirmed ovulation timing.

28. **How a qualifying “month” is measured.**  
    **Text:** “12 months or more,” “6 months or more,” and “1 year.”  
    **Readings:** Elapsed calendar time, qualifying calendar months, menstrual cycles, or a specified number of days.  
    **Encoding:** Accepts numerical month counts; it does not derive them from dated attempts.  
    **Example:** A patient has 12 short menstrual cycles in nine calendar months. Cycle-based measurement qualifies; elapsed-calendar measurement does not.

29. **Whether attempts must be consecutive, recent, and ongoing.**  
    **Text:** The required months and cycles have no express continuity or lookback rule.  
    **Readings:** Cumulative lifetime qualifying attempts suffice; or there must be one continuous or reasonably recent period of active unsuccessful attempts.  
    **Encoding:** Uses aggregate counts with no continuity or recency checks.  
    **Example:** Six qualifying months five years ago plus six recent months satisfy a cumulative reading, but not a continuous-current-period reading.

30. **Whether attempts with a previous partner count.**  
    **Text:** The requirements refer to “your partner” but do not attribute historical attempts to a particular relationship.  
    **Readings:** Qualifying attempts belong to the individual and carry forward; or the current couple must satisfy the period together.  
    **Encoding:** Does not associate attempt counts with a partner identity.  
    **Example:** A patient has ten unsuccessful months with a former partner and two with the current partner. An individual-history reading qualifies; a current-couple reading does not.

31. **Combining intercourse and donor-insemination attempts.**  
    **Text:** The with-male-partner rows offer “A” intercourse “or B” donor insemination.  
    **Readings:** One complete alternative is necessary; or mixed egg-and-sperm-contact attempts may be credited toward a common minimum. No conversion rule is supplied.  
    **Encoding:** Requires the full intercourse threshold or full donor-cycle threshold; it does not add them together.  
    **Example:** A 32-year-old has six qualifying intercourse months and six donor cycles. A combined-contact reading qualifies; the encoded alternatives do not.

32. **Which procedures count as “donor artificial insemination.”**  
    **Text:** “Donor artificial insemination cycles” and “donor insemination,” without a procedure or setting definition.  
    **Readings:** Any intentional insemination using donor sperm counts; or only clinically performed, documented procedures of specified types count.  
    **Encoding:** Uses a generic donor-cycle count, with no procedure or setting verification.  
    **Example:** Twelve documented home intravaginal inseminations qualify under the broad reading but not under a clinic-only reading.

33. **The financing qualifier on qualifying donor cycles.**  
    **Text:** “Self paid/not paid for by plan.”  
    **Readings:** Personally self-funded cycles are required; or any cycles not paid by this plan count, including those funded by another insurer, a grant, or another person. Partial payment is also unaddressed.  
    **Encoding:** Does not track funding at all.  
    **Example:** Twelve cycles fully paid by a previous insurer qualify under the not-this-plan reading but not under a strictly self-paid reading.

34. **Whether multiple inseminations in one reproductive cycle count separately.**  
    **Text:** “Cycles of donor insemination”; later, a cycle is an “attempt” at specified treatment.  
    **Readings:** Count each insemination procedure; or count one menstrual/treatment cycle even if it contains multiple inseminations.  
    **Encoding:** Accepts an unexplained numerical donor-cycle count.  
    **Example:** Six menstrual cycles each contain two donor inseminations. Procedure counting gives 12; treatment-cycle counting gives six.

35. **Whether the later cycle definition governs the earlier donor-cycle prerequisites.**  
    **Text:** “Each treatment type is counted as a separate cycle,” following a definition covering ovulation induction and IUI.  
    **Readings:** This defines cycles only for covered treatment accounting; or it also informs the historical cycle counts used for eligibility. In particular, the treatment-type rule’s relationship to “cycles of donor insemination” is not explained.  
    **Encoding:** Uses independent supplied counts and does not connect them to the cycle definition.  
    **Example:** A history contains six combined menotropin-plus-donor-IUI treatment episodes. Separate treatment-type accounting produces 12 treatment cycles, but an insemination-only prerequisite count produces six.

## FSH testing

36. **What “unmedicated” excludes.**  
    **Text:** “Unmedicated day 3 FSH.”  
    **Readings:** No ovarian-stimulation medication during that cycle; no medication affecting FSH; or no relevant medication for a specified washout period.  
    **Encoding:** The test records have no medication attribute. Qualification must be assumed or established upstream.  
    **Example:** A patient stops hormonal contraception shortly before testing. The result may qualify under a same-cycle stimulation rule but not under a washout rule.

37. **What counts as “day 3.”**  
    **Text:** “Day 3 FSH,” without defining cycle day one or treatment-induced bleeding.  
    **Readings:** Third day after full menstrual flow, third day after any bleeding, or a clinically accepted equivalent for irregular or induced cycles.  
    **Encoding:** Accepts tests already classified as day-three tests.  
    **Example:** Testing occurs on the third day after spotting but the second day after full flow. The competing day-one conventions produce different qualifying-test outcomes.

38. **The test universe for “most recent lab test.”**  
    **Text:** The FSH result must qualify “in your most recent lab test,” in a table about unmedicated day-three FSH.  
    **Readings:** The most recent qualifying unmedicated day-three FSH test; or the latest FSH result, even if obtained under different conditions.  
    **Encoding:** Selects the latest item in `claim.day_3_fsh_tests`; it does not inspect other FSH tests or separately filter medication status.  
    **Example:** A qualifying day-three result is 15, followed by a non-day-three FSH result of 22. The qualified-test reading passes; a latest-FSH-result reading fails.

39. **The test universe for “all prior tests” after 40.**  
    **Text:** “Less than 19 mIU/mL in all prior tests performed after age 40.”  
    **Readings:** All prior qualifying unmedicated day-three tests; all day-three FSH tests; or every FSH test after the age boundary.  
    **Encoding:** Checks all supplied day-three tests on or after the fortieth-birthday timestamp, without medication information.  
    **Example:** A 41-year-old has only qualifying unmedicated results below 19, but a medicated FSH result above 19. The restricted and broader test-universe readings differ.

40. **Invalidated, corrected, or clinically unreliable results.**  
    **Text:** “Most recent” and “all prior tests,” without a validity or correction rule.  
    **Readings:** Every recorded result controls; or a withdrawn, erroneous, or superseded result is disregarded.  
    **Encoding:** Has no validity or supersession status. A retained high result after 40 fails the historical test.  
    **Example:** A result of 24 is formally corrected to 14 because of a laboratory error. An every-record reading fails; a valid-final-result reading passes.

41. **Tied most-recent results.**  
    **Text:** “Your most recent lab test,” expressed in the singular.  
    **Readings:** Accept any tied latest result, require all tied results to qualify, or select an authoritative final result.  
    **Encoding:** Requires a test with no other test at an equal or later timestamp. Two entries tied for latest therefore leave no selected most-recent test, even when both are acceptable.  
    **Example:** Two tests recorded at the same latest timestamp both show 15. An all-tied-results rule passes; the encoding cannot establish the recent-test requirement.

42. **The reference date for the FSH lookback period.**  
    **Text:** Testing must be “within the past” six or 12 months.  
    **Readings:** Measure backward from authorization, cycle initiation, each service date, or claim submission.  
    **Encoding:** Uses each claim’s service date.  
    **Example:** A test is valid when a cycle starts but becomes more than six months old before a later service in that cycle. Cycle-start assessment passes; service-date assessment fails.

43. **Calendar calculation and endpoint treatment for the lookback period.**  
    **Text:** “Within the past” six or 12 months, without a day-count or month-end convention.  
    **Readings:** Inclusive calendar-month anniversary, strict anniversary cutoff, fixed-day interval, or calendar arithmetic that clamps to the last day of a shorter month.  
    **Encoding:** Uses its custom month-difference calculation, accepts the exact same-day anniversary, and ignores test time for this comparison. It does not implement a general month-end-clamping rule.  
    **Example:** An August 31 test assessed on February 28 passes a six-calendar-month month-end convention but can fail the supplied helper.

44. **Whether “after age 40” includes the fortieth birthday.**  
    **Text:** “Tests performed after age 40.”  
    **Readings:** Tests on or after attaining 40; or only tests strictly after the boundary, with the treatment of birthday-day tests requiring a convention.  
    **Encoding:** Includes tests from midnight on the fortieth birthday.  
    **Example:** A high FSH result recorded on the fortieth birthday triggers the encoded historical exclusion but could be outside a strictly-after-birthday interpretation.

45. **Whether “all prior tests” includes the current/latest qualifying test.**  
    **Text:** “All prior tests performed after age 40.”  
    **Readings:** All tests before the coverage decision, including the latest one; or tests preceding the current assessment test, with the latest test needing a separately inferred result requirement.  
    **Encoding:** Includes the latest supplied post-40 test in the historical threshold check.  
    **Example:** Earlier post-40 results are 15, but the latest is 22. An inclusive interpretation fails; a strictly-prior-only reading without an additional current-result rule could pass.

46. **No post-40 tests yet.**  
    **Text:** An individual aged 40 or older needs a recent test and qualifying results in “all prior tests performed after age 40.”  
    **Readings:** The universal historical condition is satisfied when there are no post-40 tests, provided a recent pre-40 test exists; or at least one post-40 test is required.  
    **Encoding:** Explicitly requires at least one test on or after the fortieth birthday.  
    **Example:** A patient turns 40 today and had a result of 14 one month ago. The empty-history reading passes; the encoding requires a new test.

47. **How complete a post-40 testing history must be established.**  
    **Text:** “All prior tests,” without specifying how completeness is demonstrated or how unavailable records are handled.  
    **Readings:** A sufficiently certified supplied history is enough; or eligibility remains unestablished until all relevant outside records are obtained. This does not change which tests substantively count—it changes the evidentiary standard.  
    **Encoding:** Checks only the supplied list and requires no completeness assertion.  
    **Example:** A patient supplies one qualifying result but reports older tests at a closed clinic whose records are unavailable. Accepting the submitted history may pass; requiring a complete history does not.

## Semen analyses

48. **What makes a semen analysis “abnormal.”**  
    **Text:** “At least 2 abnormal semen analyses.”  
    **Readings:** Any out-of-range parameter suffices; a specified fertility-related parameter or threshold is required; or the clinician must conclude that the abnormality is significant for infertility.  
    **Encoding:** Accepts entries already labeled `abnormal_semen_analysis`, without measurements or criteria.  
    **Example:** Two analyses show normal count and motility but slightly abnormal viscosity. A laboratory-flag reading qualifies; a clinically significant infertility reading may not.

49. **Whether old abnormal analyses remain sufficient after normal results.**  
    **Text:** Two abnormal analyses are required, but there is no recency requirement or rule for later normalization.  
    **Readings:** Any historical qualifying pair suffices; or the analyses must establish current infertility, with later normal results potentially defeating the diagnosis.  
    **Encoding:** Accepts any qualifying pair in the supplied list, regardless of age or subsequent results.  
    **Example:** Two abnormal results from ten years ago are followed by several recent normal results. The encoded historical-pair rule passes; a current-condition reading may not.

50. **Whether two analyses require two independently obtained specimens.**  
    **Text:** “2 abnormal semen analyses obtained at least 2 weeks apart.”  
    **Readings:** Two separate specimen collections are necessary; or separately obtained analytical reports can count, including reanalysis of one stored specimen.  
    **Encoding:** Selects two list entries with different indices; it has no specimen identity or collection/report-date distinction.  
    **Example:** One specimen is analyzed initially and reanalyzed three weeks later. A report-based interpretation can pass; a separate-specimen interpretation cannot.

51. **How the two-week interval is measured.**  
    **Text:** “Obtained at least 2 weeks apart.”  
    **Readings:** Fourteen calendar dates apart; or at least 336 elapsed hours, measured from collection or another specified event.  
    **Encoding:** Converts dates to midnight timestamps and compares a 14-day interval; no collection times are represented.  
    **Example:** Samples collected at 5 p.m. on June 1 and 8 a.m. on June 15 pass the calendar-date rule but are less than 336 hours apart.

## Authorization, providers, and service scope

52. **Requesting advance approval versus receiving it.**  
    **Text:** “Your provider will request approval from us in advance.”  
    **Readings:** A timely request satisfies the stated procedural obligation; or actual approval must be obtained before treatment.  
    **Encoding:** Requires `precertification_received(C, yes)`, not merely a request.  
    **Example:** The provider requests authorization before treatment, but the insurer has not responded when treatment occurs. A request-based reading permits coverage; an approval-based reading does not.

53. **The event before which authorization must occur, and retrospective approval.**  
    **Text:** “In advance for your infertility services.”  
    **Readings:** Approval must precede cycle initiation, each individual service, or another defined treatment milestone; subsequent approval may or may not cure an initially unauthorized service.  
    **Encoding:** Checks an undated approval boolean. It cannot establish that approval preceded any particular event.  
    **Example:** Approval arrives after medications begin but before IUI. A cycle-start rule fails; an individual-IUI-service rule may pass.

54. **What qualifies someone as an “infertility specialist.”**  
    **Text:** Charges must be made “by an infertility specialist.”  
    **Readings:** A particular subspecialty certification is required; demonstrated infertility expertise is sufficient; or an appropriately designated clinic/provider qualifies.  
    **Encoding:** Checks service location but not specialist credentials or designation.  
    **Example:** A general obstetrician-gynecologist with substantial infertility experience performs IUI. An expertise-based reading may cover it; a subspecialty-certification reading may not.

55. **Whether “charges made by” concerns performance, supervision, or billing identity.**  
    **Text:** “Charges made by an infertility specialist.”  
    **Readings:** The specialist must bill directly; the specialist must personally perform the service; or services furnished under specialist supervision qualify even when billed by a clinic, laboratory, or facility.  
    **Encoding:** Does not represent billing identity, supervision, or individual performer.  
    **Example:** A nurse performs IUI under a specialist’s supervision and the clinic submits the bill. A supervised-care reading permits coverage; a direct-specialist-billing or performance reading may not.

56. **What is included in a listed infertility service.**  
    **Text:** “Ovulation induction cycle(s) with menotropins” and “intrauterine insemination.”  
    **Readings:** These encompass the clinically necessary components of the treatment episode; or they identify narrower procedures, leaving drugs, monitoring, sperm preparation, and related charges to separate benefit provisions.  
    **Encoding:** Recognizes only the two service-type atoms and supplies no component or bundling rules.  
    **Example:** A separately billed monitoring ultrasound during a covered menotropin cycle could be part of the covered cycle under one reading but require independent coverage under the other.

## Cycle accounting and treatment-course edge cases

57. **When a cycle becomes countable.**  
    **Text:** A cycle is an “attempt,” “begins with the initiation of therapy,” and has specified completion events.  
    **Readings:** It counts when initiated; only when the treatment procedure occurs; or only when completed. These choices can affect eligibility-history counts and any separately applicable cycle accounting.  
    **Encoding:** Uses supplied counts and does not distinguish started, performed, or completed cycles.  
    **Example:** A twelfth donor-insemination attempt has occurred, but pregnancy status has not yet been determined. Counting performed attempts satisfies a 12-cycle prerequisite; counting only completed cycles does not yet do so.

58. **When therapy is “initiated.”**  
    **Text:** “The cycle begins with the initiation of therapy.”  
    **Readings:** The first cycle-directed medication, baseline monitoring, ovarian stimulation, or insemination itself marks initiation, depending on the treatment type.  
    **Encoding:** Does not represent a cycle-start event.  
    **Example:** A donor-IUI episode is canceled after preparatory medication but before insemination. A preparation-based start can make it an initiated cycle; an insemination-based start cannot.

59. **Canceled or abandoned cycles without a specified ending event.**  
    **Text:** A nonpregnant cycle ends when treatment is followed by a negative pregnancy test or menstrual period.  
    **Readings:** Cancellation itself closes the cycle; the cycle remains open until a listed event; or an abandoned episode is excluded from the count.  
    **Encoding:** Does not represent cancellation, closure, or the required confirmation.  
    **Example:** Menotropins are stopped because of excessive response; the patient has neither a recorded negative test nor a subsequent recorded period. Cancellation-based accounting counts a closed cycle, while the literal endpoint rule does not establish completion.

60. **Early pregnancy loss before the six-week completion point.**  
    **Text:** In the case of pregnancy, a cycle is completed “at 6 weeks following a positive pregnancy test,” while nonpregnancy can be confirmed by a negative test or menstrual period.  
    **Readings:** Any positive test fixes completion six weeks later; an intervening loss completes the cycle sooner under the nonpregnancy rule; or the pregnancy rule applies only if pregnancy persists.  
    **Encoding:** Has no pregnancy-event or cycle-end logic.  
    **Example:** A positive test is followed by a negative test ten days later. The cycle may be complete on day ten or remain incomplete until six weeks after the positive result.

61. **Which positive pregnancy test starts the six-week clock.**  
    **Text:** “Following a positive pregnancy test.”  
    **Readings:** The first positive home test, first positive clinical test, confirmatory test, or first medically reliable positive test.  
    **Encoding:** Does not identify or date pregnancy tests.  
    **Example:** A home test is positive a week before clinical confirmation. At six weeks after the home result, one reading regards the cycle as completed and another does not.

62. **Whether eligibility is fixed for the whole cycle or reassessed for its component services.**  
    **Text:** The benefit defines a multiweek “cycle” but states eligibility and laboratory requirements without specifying whether they attach to the cycle or each charge.  
    **Readings:** Eligibility established at cycle initiation continues through completion; or every service must independently meet the then-current requirements.  
    **Encoding:** Evaluates claims separately using their service dates, with no cycle-level eligibility lock.  
    **Example:** A patient begins a qualifying cycle before turning 40 and receives a later service after that birthday without a post-40 FSH test. Cycle-level eligibility can preserve coverage; the encoded service-level assessment can fail.

---

### Matters that should not be mistaken for policy ambiguities

Several additional differences are **unsupported additions, clear omissions, or implementation defects**, rather than competing readings of unsettled wording:

- The supplied text does not establish the encoding’s **age-37 menotropin restriction**, **three-/four-cycle CPB prerequisites**, **six-attempt covered-insemination limit**, or specified **network-location restrictions**. Other policy provisions might support them, but these excerpts do not.
- The requirement that the claimant be a covered student or qualifying covered dependent is explicit; its absence from the shown eligibility rule is an omission, not an ambiguity about whether it applies.
- **FSH must be less than 19**, not equal to 19. The numerical boundary is settled.
- Prior voluntary sterilization remains relevant **despite reversal and regardless of reversal results**. That is settled.
- The age helper’s `FOBMonth`/`DOBMonth` mismatch is an apparent coding defect, not a policy interpretation.
- “Within the past” excludes future tests. The date helper’s lack of an explicit nonfuture check is likewise not a permissible competing policy reading.
- Missing medication, provider-credential, payment-source, or failure-to-conceive checks should not automatically be described as intentional broad coverage interpretations: some may simply reflect facts presumed to have been validated before the supplied claim fields are populated.