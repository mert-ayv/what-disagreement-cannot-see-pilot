"""Encode comprehensive infertility-service coverage.

READING choices:
- Negative eligibility conditions exclude a disqualifying history in either partner.
- The eligibility table supplies the permitted patient/partner configurations.
- The glossary and eligibility table are cumulative, not alternatives.
- A male with a female partner may establish glossary infertility through that pair.
- Gender dysphoria satisfies the glossary but does not waive eligibility requirements.
- Table alternatives and FSH age boundaries are applied literally.
- Equally recent FSH results must all satisfy an applicable latest-result limit.
- Unknown required facts do not establish eligibility.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    # READING: Unknown facts — "You are eligible ... if" and "You have met
    # the requirement" require affirmative evidence of each applicable
    # condition; an absent field does not establish that condition.
    def at_least(field, minimum):
        value = claim.get(field)
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            and value >= minimum
        )

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner not in {"female", "male", "no_partner"}:
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" is read as neither person having had one, not as allowing
    # a sterilized person to qualify because the other person has not.
    # With "no_partner", there is no partner history to establish.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: Physiologic infertility — "You or your partner does not have
    # infertility that is due to a natural physiologic process" excludes such
    # a cause in either person. The combined documented-condition field must
    # establish a non-natural cause; missing information is insufficient.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    # READING: Table scope — "You have met the requirement for the number of
    # months trying to conceive" followed by "You are [table categories]" is
    # read as requiring an applicable table row. There is no row for a male
    # without a female partner. The glossary's "2 abnormal semen analyses"
    # can establish infertility, but cannot supply a missing eligibility row.
    if sex == "male" and partner != "female":
        return False

    if sex == "female":
        age = h.patient_age(claim)
        if age is None or age < 0:
            return False
        threshold = 12 if age < 35 else 6
    else:
        partner_age = claim.get("age_of_patients_female_partner")
        if (
            not isinstance(partner_age, int)
            or isinstance(partner_age, bool)
            or partner_age < 0
        ):
            return False
        threshold = 12 if partner_age < 35 else 6

    # READING: Glossary/table relationship — the glossary's "frequent,
    # unprotected heterosexual sexual intercourse" and the table's
    # "unprotected timed sexual intercourse" are separate requirements.
    # In particular, the table's donor-cycle alternative for a female with
    # a male partner does not itself replace her glossary intercourse test.
    #
    # READING: Male with female partner — "A disease defined by the failure
    # to become pregnant" and "For a female with a male partner" are read
    # as establishing infertility for either member of that pair using the
    # female partner's age and the pair's intercourse history. This gives
    # effect to the table's explicit male-with-female-partner rows.
    if sex == "female" and partner != "male":
        ordinary_glossary_infertility = at_least(
            "num_cycles_donor_insemination", threshold
        )
    else:
        ordinary_glossary_infertility = at_least(
            "num_months_frequent_unprotected_heterosexual_intercourse",
            threshold,
        )

    # READING: Gender dysphoria — "For an individual or their partner who
    # has been clinically diagnosed with gender dysphoria" independently
    # satisfies the glossary definition, but does not waive the separately
    # stated eligibility conditions, table waiting periods, or FSH criteria.
    if not (
        ordinary_glossary_infertility
        or claim.get("patient_or_partner_diagnosed_with_gender_dysphoria")
        == "yes"
    ):
        return False

    timed_intercourse_met = at_least(
        "num_months_timed_unprotected_intercourse", threshold
    )
    donor_cycles_met = at_least("num_cycles_donor_insemination", threshold)

    # READING: Table alternatives — "A. ... or B." permits either timed
    # intercourse or the stated self-paid donor cycles for a female with
    # a male partner. For females without a male partner, only donor cycles
    # count. For males with female partners, donor cycles "Does not apply".
    if sex == "female":
        if partner == "male":
            if not (timed_intercourse_met or donor_cycles_met):
                return False
        elif not donor_cycles_met:
            return False
    elif not timed_intercourse_met:
        return False

    # The male rows explicitly make FSH testing and results inapplicable.
    if sex == "male":
        return True

    service_date_text = claim.get("date_service_received")
    if service_date_text is None:
        return False
    service_date = datetime.strptime(service_date_text, "%Y_%m_%d").date()

    tests = claim.get("day_3_fsh_tests")
    if not isinstance(tests, list) or not tests:
        return False

    # READING: Test chronology — "within the past" and "prior tests" refer
    # to tests on or before the service date; future tests cannot establish
    # eligibility for this claim.
    available_tests = []
    for level, date_text, time_text in tests:
        test_date = datetime.strptime(date_text, "%Y_%m_%d").date()
        test_time = datetime.strptime(time_text, "%H_%M").time()
        if test_date <= service_date:
            available_tests.append(
                (level, date_text, test_date, test_time)
            )

    if not available_tests:
        return False

    latest_key = max((test[2], test[3]) for test in available_tests)
    latest_tests = [
        test for test in available_tests
        if (test[2], test[3]) == latest_key
    ]
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(
        latest_tests[0][1], service_date_text, recency_months
    ):
        return False

    if age < 40:
        # READING: Tied latest results — "less than 19 mIU/mL in your most
        # recent lab test" requires every result tied for the latest date
        # and time to be below 19; no arbitrary tie-breaking is warranted.
        return all(test[0] < 19 for test in latest_tests)

    # READING: Age-40 boundary — "less than 19 mIU/mL in all prior tests
    # performed after age 40" includes the latest test and, using the
    # supplied helper, tests on the 40th birthday. All such results must
    # pass. The separate "within the past ... 6 months" requirement still
    # applies, but the text does not require a new test on turning 40:
    # a recent pre-40 test can establish recency, and its result is outside
    # this age-specific result restriction.
    for level, date_text, time_text in h.fsh_tests_since_age_40(claim):
        test_date = datetime.strptime(date_text, "%Y_%m_%d").date()
        if test_date <= service_date and level >= 19:
            return False

    return True
