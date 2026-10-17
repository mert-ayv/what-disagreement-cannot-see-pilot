"""
READING choices:
- Sterilization and natural-process exclusions apply to either member of the
  couple, not merely to one member selected to satisfy the wording.
- Glossary infertility and the service-specific eligibility table are cumulative.
  Gender dysphoria satisfies the glossary but does not waive the table.
- For a male with a female partner, the glossary's female-with-male-partner
  definition is applied to the couple using the female partner's age.
- The table supplies the available eligibility pathways; an unlisted pairing
  does not establish eligibility.
- Timed intercourse and frequent heterosexual intercourse are separate facts.
- Donor cycles are an alternative to timed intercourse only where stated.
- FSH evidence is evaluated as of service, with calendar-month boundaries
  inclusive. Equally recent tests must all satisfy the applicable threshold.
- At age 40 or older, the threshold applies to all tests on or after the 40th
  birthday; a recent test is still required, but need not have occurred after
  that birthday.
- Unknown required facts do not establish coverage; an unknown alternative
  does not defeat another, established alternative.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, minimum):
        value = claim.get(field)
        return isinstance(value, int) and value >= minimum

    # READING: Evidence — "You are eligible ... if" and "You have met the
    # requirement" require affirmative evidence of each applicable condition.
    # Missing facts cannot establish a requirement, but an established
    # alternative can suffice without evidence about the other alternative.
    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner_sex not in {"female", "male", "no_partner"}:
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" is read as excluding voluntary sterilization by either
    # member of the couple. A nonexistent partner needs no sterilization fact.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner_sex != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: Cause — "There exists a condition" that is demonstrated,
    # recognized and documented, and "You or your partner does not have
    # infertility ... due to a natural physiologic process" are cumulative.
    # The supplied condition field represents this requirement for the couple;
    # any listed natural-process cause fails, while "other" establishes it.
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

    dysphoria = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    # READING: Unlisted pairings — the table headed "You are" supplies the
    # service-specific pathways. Its male rows require "a female partner";
    # the glossary's male-without-female-partner definition alone supplies
    # no table pathway, even with qualifying semen analyses.
    if sex == "male":
        if partner_sex != "female":
            return False
        female_age = claim.get("age_of_patients_female_partner")
        if not isinstance(female_age, int) or female_age < 0:
            return False
        required_months = 12 if female_age < 35 else 6

        # READING: Male with female partner — "failure to become pregnant"
        # and "For a female with a male partner" describe the couple's
        # infertility. Apply that glossary criterion using the female
        # partner's age, consistent with the table's explicit male rows.
        glossary_infertile = dysphoria or at_least(
            "num_months_frequent_unprotected_heterosexual_intercourse",
            required_months,
        )

        # READING: Separate intercourse facts — the glossary says "frequent,
        # unprotected heterosexual sexual intercourse"; the table says
        # "unprotected timed sexual intercourse". Neither field establishes
        # the other. The male table rows offer no donor-cycle alternative.
        return glossary_infertile and at_least(
            "num_months_timed_unprotected_intercourse", required_months
        )

    try:
        age = h.patient_age(claim)
    except (KeyError, TypeError, ValueError, OverflowError):
        return False
    if age is None or age < 0:
        return False

    required_months = 12 if age < 35 else 6
    donor_requirement_met = at_least(
        "num_cycles_donor_insemination", required_months
    )

    # READING: Female without male partner — "without a male partner"
    # includes both no partner and a female partner.
    if partner_sex == "male":
        glossary_infertile = dysphoria or at_least(
            "num_months_frequent_unprotected_heterosexual_intercourse",
            required_months,
        )
        # READING: Table alternatives — "A. ... months ... or B. ... cycles
        # of donor insemination" allows either route for a female with a male
        # partner. It does not replace the separately required glossary test.
        table_attempt_requirement_met = (
            at_least(
                "num_months_timed_unprotected_intercourse", required_months
            )
            or donor_requirement_met
        )
    else:
        glossary_infertile = dysphoria or donor_requirement_met
        table_attempt_requirement_met = donor_requirement_met

    # READING: Gender dysphoria — "For an individual or their partner who
    # has been clinically diagnosed with gender dysphoria" is an independent
    # glossary route. It does not waive "You have met the requirement for the
    # number of months" or the FSH requirements in the service-specific table.
    if not glossary_infertile or not table_attempt_requirement_met:
        return False

    tests = claim.get("day_3_fsh_tests")
    if not isinstance(tests, list):
        return False

    try:
        service_date = parse_date(claim["date_service_received"])
        dated_tests = []
        for level, date_text, time_text in tests:
            test_date = parse_date(date_text)
            test_time = datetime.strptime(time_text, "%H_%M").time()
            if test_date <= service_date:
                dated_tests.append(
                    (datetime.combine(test_date, test_time), level, date_text)
                )
    except (KeyError, TypeError, ValueError, OverflowError):
        return False

    # READING: Timing — "within the past" and "most recent lab test" are
    # evaluated on the service date. Future tests cannot establish or defeat
    # coverage; tests on the service date count because no service time is given.
    if not dated_tests:
        return False

    latest_timestamp = max(test[0] for test in dated_tests)
    latest_tests = [
        test for test in dated_tests if test[0] == latest_timestamp
    ]
    try:
        if not h.months_at_most(
            latest_tests[0][2],
            claim["date_service_received"],
            required_months,
        ):
            return False
    except (KeyError, TypeError, ValueError, OverflowError):
        return False

    if age < 40:
        # READING: Tied latest results — "less than 19 ... in your most recent
        # lab test" is applied to every equally recent test, rather than
        # selecting a favorable result when timestamps are identical.
        return all(level < 19 for _, level, _ in latest_tests)

    # READING: Age 40 threshold — "less than 19 ... in all prior tests
    # performed after age 40" includes all tests on or after the 40th birthday
    # through service, including the latest such test. "Within the past"
    # six months remains a separate recency condition; the text does not
    # additionally require that a test have occurred after the 40th birthday.
    try:
        tests_since_40 = h.fsh_tests_since_age_40(claim)
        return all(
            level < 19
            for level, date_text, _ in tests_since_40
            if parse_date(date_text) <= service_date
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        return False
