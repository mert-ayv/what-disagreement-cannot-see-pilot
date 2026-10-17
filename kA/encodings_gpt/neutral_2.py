"""
READING choices:
- Treat the claim as belonging to a covered student or eligible covered partner;
  the interface provides no field for verifying that enrollment category.
- Require neither the patient nor an existing partner to have undergone voluntary
  sterilization, and exclude every listed natural physiologic cause.
- Apply the glossary and the service-specific eligibility table cumulatively.
  Gender dysphoria satisfies the glossary, but does not waive table requirements.
- For a male with a female partner, use the female partner's age and the couple's
  intercourse history to apply the glossary's pregnancy-failure definition.
- Treat the table's population categories as exhaustive; it supplies no qualifying
  route for a male without a female partner.
- Read the table's intercourse and donor-insemination alternatives literally.
- Require a recent FSH test for female patients only. Before age 40, all tests tied
  for most recent must satisfy the threshold. From age 40, apply the threshold to
  every test on or after the 40th birthday, without requiring a post-40 test.
- Evaluate histories as of the service date; later tests do not count.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Enrollment scope — "covered under this plan as a student or as a
    # covered dependent" is treated as the input population. The supplied
    # interface cannot independently establish or distinguish enrollment status.

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner_sex not in {"male", "female", "no_partner"}:
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" means neither person has had one, rather than allowing one
    # person's negative history to overcome the other's sterilization.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner_sex != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: Natural causes — "does not have infertility that is due to a
    # natural physiologic process such as" excludes all supplied natural-process
    # categories, not merely the examples of menopause and perimenopause.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    # READING: Table scope — "You have met the requirement for the number of
    # months trying to conceive" followed by the table makes its categories
    # mandatory. Although the glossary recognizes males without female partners,
    # no table route is provided for them; do not invent an exemption.
    if sex == "male" and partner_sex != "female":
        return False

    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        relevant_female_age = age
    else:
        relevant_female_age = claim.get("age_of_patients_female_partner")
        if relevant_female_age is None:
            return False

    required_duration = 12 if relevant_female_age < 35 else 6

    frequent_months = claim.get(
        "num_months_frequent_unprotected_heterosexual_intercourse"
    )
    timed_months = claim.get("num_months_timed_unprotected_intercourse")
    donor_cycles = claim.get("num_cycles_donor_insemination")

    frequent_ok = (
        frequent_months is not None
        and frequent_months >= required_duration
    )
    timed_ok = (
        timed_months is not None
        and timed_months >= required_duration
    )
    donor_ok = (
        donor_cycles is not None
        and donor_cycles >= required_duration
    )

    # READING: Male with female partner — the glossary's "For a female with a
    # male partner" pregnancy-failure definition is applied to the couple when
    # the claimant is male, consistently with the table's male/female-partner
    # rows. The female partner's age determines the required duration.
    if sex == "male":
        ordinary_glossary_infertility = frequent_ok
    elif partner_sex == "male":
        ordinary_glossary_infertility = frequent_ok
    else:
        ordinary_glossary_infertility = donor_ok

    # READING: Cumulative definitions — "For an individual or their partner who
    # has been clinically diagnosed with gender dysphoria" independently
    # satisfies the glossary, but "You have met the requirement" still requires
    # the applicable table route. Unknown dysphoria does not establish it.
    glossary_infertility = (
        ordinary_glossary_infertility
        or claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )
    if not glossary_infertility:
        return False

    # READING: Table alternatives — "A. ... or B." permits either timed
    # intercourse or self-paid donor cycles for a female with a male partner.
    # "Does not apply" supplies no donor-cycle alternative for a male claimant.
    # The glossary's separate frequent-intercourse requirement remains separate.
    if sex == "male":
        table_attempts_ok = timed_ok
    elif partner_sex == "male":
        table_attempts_ok = timed_ok or donor_ok
    else:
        table_attempts_ok = donor_ok

    if not table_attempts_ok:
        return False

    # READING: FSH applicability — the male rows say "Does not apply" for both
    # FSH columns; no FSH result is required from a male or his female partner.
    if sex == "male":
        return True

    service_date = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date is None or not tests:
        return False

    # READING: Evaluation date — "within the past" and "prior tests" refer to
    # the service date. With no service time supplied, tests on that date count.
    # The specified fixed-width date and time strings sort chronologically.
    prior_tests = [test for test in tests if test[1] <= service_date]
    if not prior_tests:
        return False

    latest_timestamp = max((test[1], test[2]) for test in prior_tests)
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(
        latest_timestamp[0], service_date, recency_months
    ):
        return False

    if age < 40:
        # READING: Simultaneous results — "less than 19 mIU/mL in your most
        # recent lab test" requires every result tied for the latest timestamp
        # to be below 19; do not arbitrarily select a favorable tied result.
        latest_tests = [
            test for test in prior_tests
            if (test[1], test[2]) == latest_timestamp
        ]
        return all(test[0] < 19 for test in latest_tests)

    # READING: Age-40 rule — "all prior tests performed after age 40" includes
    # tests on or after the 40th birthday. A recent test is still required, but
    # the text does not require that recent test to have occurred after turning
    # 40 or impose the under-40 threshold on a pre-40 test.
    post_40_tests = [
        test for test in h.fsh_tests_since_age_40(claim)
        if test[1] <= service_date
    ]
    return all(test[0] < 19 for test in post_40_tests)
