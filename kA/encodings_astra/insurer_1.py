"""
READING choices:
- Unknown facts do not establish an applicable eligibility requirement.
- Both the patient and any partner must be free of voluntary sterilization.
- Natural-physiologic infertility is excluded, including reproductive aging.
- The glossary and eligibility table impose cumulative requirements; gender
  dysphoria satisfies the glossary but does not waive the table.
- Table categories are exhaustive. The glossary's female categories are not
  extended to male patients with female partners.
- Timed intercourse and frequent heterosexual intercourse are distinct facts.
- FSH recency includes the calendar-month boundary. Tied latest results must
  all qualify. At age 40 or older, every service-date-or-earlier test on or
  after the 40th birthday must qualify, including the latest such test.
- A recent pre-40 FSH test can satisfy recency at age 40; no additional
  post-40 test is required where no such test has yet occurred.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    # READING: Proof of eligibility — "You are eligible ... if" makes each
    # applicable requirement mandatory. An unknown fact cannot establish it.
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
    # sterilization" excludes a claim if either member has had one; it is not
    # enough that one member has not. A nonexistent partner needs no finding.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: Physiologic cause — "You or your partner does not have
    # infertility that is due to a natural physiologic process such as age
    # related ovarian insufficiency" excludes all natural physiologic causes,
    # not merely the illustrative ovarian conditions.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    def at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    # READING: Exhaustive table — "You have met the requirement for the number
    # of months" and the table's "You are" categories require an applicable
    # row. The glossary does not supply omitted eligibility-table rows.
    age = None
    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        required = 12 if age < 35 else 6
        donor_requirement_met = at_least(
            "num_cycles_donor_insemination", required
        )
        if partner == "male":
            table_requirement_met = (
                at_least("num_months_timed_unprotected_intercourse", required)
                or donor_requirement_met
            )
        else:
            # "Without a male partner" includes a female partner.
            table_requirement_met = donor_requirement_met
    else:
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 35 else 6
        table_requirement_met = at_least(
            "num_months_timed_unprotected_intercourse", required
        )

    if not table_requirement_met:
        return False

    # READING: Cumulative glossary and table — "A disease defined by the
    # failure to become pregnant" defines infertility separately from
    # "You are eligible ... if". The table's donor-insemination alternative
    # does not waive an applicable glossary intercourse requirement.
    #
    # READING: Distinct intercourse facts — "frequent, unprotected
    # heterosexual sexual intercourse" in the glossary and "unprotected
    # timed sexual intercourse" in the table must each be established when
    # applicable; neither claim field is substituted for the other.
    #
    # READING: Gender dysphoria — "For an individual or their partner who has
    # been clinically diagnosed with gender dysphoria" independently satisfies
    # the glossary, but does not waive "You have met the requirement" or FSH.
    glossary_met = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )
    if sex == "female":
        if partner == "male":
            glossary_met = glossary_met or at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )
        else:
            glossary_met = glossary_met or at_least(
                "num_cycles_donor_insemination", required
            )
    else:
        # READING: Literal glossary categories — "For a female with a male
        # partner" is not extended to a male claimant with a female partner.
        # The male-specific alternative, "For a male without a female
        # partner", does not apply here. Thus a male who passed the table
        # needs the glossary's gender-dysphoria alternative. Abnormal semen
        # analyses cannot substitute for that alternative in this category.
        pass

    if not glossary_met:
        return False

    # The male table rows expressly say FSH testing "Does not apply".
    if sex == "male":
        return True

    service_date_text = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date_text is None or not tests:
        return False

    service_date = datetime.strptime(service_date_text, "%Y_%m_%d").date()

    def test_timestamp(test):
        return datetime.strptime(test[1] + " " + test[2], "%Y_%m_%d %H_%M")

    # READING: Temporal scope — "within the past" and "prior tests" refer to
    # the service date. Future tests neither establish nor defeat this claim.
    available_tests = [
        (test_timestamp(test), test)
        for test in tests
        if test_timestamp(test).date() <= service_date
    ]
    if not available_tests:
        return False

    latest_timestamp = max(timestamp for timestamp, _ in available_tests)
    latest_tests = [
        test
        for timestamp, test in available_tests
        if timestamp == latest_timestamp
    ]

    # READING: Recency boundary — "within the past" 12 or 6 months includes
    # exactly that many calendar months, and requires a test in that window.
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(
        latest_tests[0][1], service_date_text, recency_months
    ):
        return False

    if age < 40:
        # READING: Latest-result ties — "less than 19 ... in your most recent
        # lab test" requires every result tied for most recent to be below 19;
        # a favorable tied result cannot displace an unfavorable one.
        return all(test[0] < 19 for test in latest_tests)

    # READING: Age-40 history — "age 40 and older" and "all prior tests
    # performed after age 40" include tests on or after the 40th birthday,
    # including the latest test available by the service date. Any result
    # at or above 19 in that history defeats eligibility.
    post_40_tests = [
        test
        for test in h.fsh_tests_since_age_40(claim)
        if test_timestamp(test).date() <= service_date
    ]

    # READING: No additional test requirement — "test done within the past"
    # six months can be satisfied by a pre-40 test; "all prior tests performed
    # after age 40" does not require a post-40 test to exist or impose its
    # threshold on a pre-40 result.
    return all(test[0] < 19 for test in post_40_tests)
