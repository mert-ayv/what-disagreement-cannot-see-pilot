"""
READING choices:
- The eligibility table is exhaustive; glossary qualification does not waive it.
- Glossary categories apply literally to the patient, not by substituting a partner.
- The glossary and eligibility table impose cumulative requirements.
- Neither the patient nor an existing partner may have voluntary sterilization.
- Natural physiologic causes are excluded, including male reproductive aging.
- Female applicants without a male partner use the donor-insemination route.
- FSH recency includes the calendar-month boundary and excludes future tests.
- Tied most-recent FSH results must all satisfy the threshold.
- At age 40 or older, every supplied FSH test from the 40th birthday through
  service must satisfy the threshold; the text does not separately require
  that a test have occurred after the 40th birthday.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    def at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner not in {"female", "male", "no_partner"}:
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" is read as excluding sterilization of either person,
    # rather than permitting coverage whenever just one person is unsterilized.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: Natural causes — "You or your partner does not have infertility
    # that is due to a natural physiologic process such as age related ovarian
    # insufficiency" excludes natural causes for either person; "such as"
    # supplies examples, not an ovarian-only limitation.
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

    # READING: Exhaustive table — "You have met the requirement for the number
    # of months trying to conceive" followed by the "You are" categories makes
    # a listed table category necessary. The only male categories are "A male
    # of any age with a female partner"; semen analyses or gender dysphoria
    # do not create an additional eligibility-table category.
    if sex == "male":
        if partner != "female":
            return False
        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False
        required_attempts = 12 if female_partner_age < 35 else 6
        age = None
    else:
        age = h.patient_age(claim)
        if age is None:
            return False
        required_attempts = 12 if age < 35 else 6

    # READING: Literal glossary categories — "For a female with a male
    # partner" describes a female patient, not a male patient through his
    # partner. The glossary's male category is "For a male without a female
    # partner". Thus a male with a female partner must qualify through
    # "an individual or their partner who has been clinically diagnosed with
    # gender dysphoria"; the table alone does not establish glossary infertility.
    glossary_infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )
    if sex == "female":
        if partner == "male":
            glossary_infertile = glossary_infertile or at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required_attempts,
            )
        else:
            # READING: Without a male partner — "A female ... without a male
            # partner" includes both no partner and a female partner; neither
            # situation permits substituting intercourse for donor cycles.
            glossary_infertile = glossary_infertile or at_least(
                "num_cycles_donor_insemination", required_attempts
            )

    if not glossary_infertile:
        return False

    # READING: Cumulative requirements — glossary "frequent, unprotected
    # heterosexual sexual intercourse" and table "unprotected timed sexual
    # intercourse" are separate requirements. The table's donor alternative
    # does not waive the glossary, and its requirements remain applicable
    # even when glossary infertility rests on gender dysphoria.
    if sex == "male":
        if not at_least(
            "num_months_timed_unprotected_intercourse", required_attempts
        ):
            return False
    elif partner == "male":
        if not (
            at_least(
                "num_months_timed_unprotected_intercourse", required_attempts
            )
            or at_least("num_cycles_donor_insemination", required_attempts)
        ):
            return False
    elif not at_least("num_cycles_donor_insemination", required_attempts):
        return False

    # The male table rows expressly make FSH testing inapplicable.
    if sex == "male":
        return True

    service_date = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date is None or not tests:
        return False

    # READING: FSH timing — "done within the past" excludes tests after service.
    # "12 months" and "6 months" include the exact calendar-month boundary.
    prior_tests = [
        test
        for test in tests
        if h.days_between(test[1], service_date) >= 0
    ]
    if not prior_tests:
        return False

    latest_timestamp = max((test[1], test[2]) for test in prior_tests)
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(
        latest_timestamp[0], service_date, recency_months
    ):
        return False

    if age < 40:
        # READING: Tied latest results — "less than 19 mIU/mL in your most
        # recent lab test" requires every result tied for most recent to pass;
        # a claimant cannot select only the favorable tied result.
        return all(
            test[0] < 19
            for test in prior_tests
            if (test[1], test[2]) == latest_timestamp
        )

    # READING: Age-40 history — "If you are age 40 and older" and "all prior
    # tests performed after age 40" include tests on the 40th birthday and
    # the latest test through service. A later low result cannot cure a high
    # result in that history. The separate recent-test requirement still
    # applies, but neither clause requires an additional post-birthday test
    # when a recent pre-birthday test exists.
    tests_since_40 = [
        test
        for test in h.fsh_tests_since_age_40(claim)
        if h.days_between(test[1], service_date) >= 0
    ]
    return all(test[0] < 19 for test in tests_since_40)
