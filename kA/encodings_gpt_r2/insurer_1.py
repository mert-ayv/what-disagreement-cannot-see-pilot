"""
READING choices:
- The glossary and eligibility table impose cumulative, independent requirements.
- Glossary categories are applied literally; a female partner's glossary category
  is not substituted for that of a male patient.
- Gender dysphoria satisfies the glossary, not the separate eligibility table.
- Neither the patient nor an existing partner may have voluntary sterilization.
- All listed natural physiologic causes are disqualifying.
- Donor cycles substitute for intercourse only where expressly permitted.
- FSH testing is evaluated as of service, with inclusive calendar-month windows.
- All results tied for the most recent FSH test must satisfy its threshold.
- At age 40 or older, all post-40 FSH results must satisfy the threshold;
  pre-40 results are not subject to that threshold.
- Unknown required facts do not establish coverage.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def enough(field, minimum):
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

    # READING: "You or your partner has not had a voluntary sterilization"
    # excludes sterilization of either person, rather than requiring only one
    # person to be unsterilized. With no partner, only the patient is tested.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # READING: "a natural physiologic process such as age related ovarian
    # insufficiency" is illustrative, not limited to ovarian aging. Every
    # supplied natural-process category is excluded.
    # READING: "There exists a condition" that is demonstrated, recognized and
    # documented requires affirmative evidence; an absent field is not proof.
    if claim.get(
        "demonstrated_and_documented_condition_causing_infertility"
    ) != "other":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    age = None
    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        minimum = 12 if age < 35 else 6
    elif partner == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        minimum = 12 if partner_age < 35 else 6
    else:
        # READING: "You have met the requirement" and the table's male rows,
        # both "with a female partner", provide no eligibility row for a male
        # without a female partner, even if the glossary calls him infertile.
        return False

    # READING: The table and "A disease defined by" the glossary are cumulative.
    # The glossary's "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" is an alternative glossary route, not a
    # waiver of the table or other eligibility requirements.
    glossary_met = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not glossary_met:
        if sex == "female" and partner == "male":
            glossary_met = enough(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                minimum,
            )
        elif sex == "female":
            glossary_met = enough("num_cycles_donor_insemination", minimum)
        else:
            # READING: The glossary says "For a female with a male partner"
            # and "For a male without a female partner". It supplies no
            # intercourse-based route for a male with a female partner.
            # Do not transfer the female partner's category to the patient.
            glossary_met = False

    if not glossary_met:
        return False

    # READING: The female-with-male-partner rows expressly say intercourse
    # "or" donor insemination. The male rows instead say donor cycles
    # "Does not apply"; donor cycles cannot replace their intercourse minimum.
    if sex == "female" and partner == "male":
        table_met = (
            enough("num_months_timed_unprotected_intercourse", minimum)
            or enough("num_cycles_donor_insemination", minimum)
        )
    elif sex == "female":
        table_met = enough("num_cycles_donor_insemination", minimum)
    else:
        table_met = enough(
            "num_months_timed_unprotected_intercourse", minimum
        )

    if not table_met:
        return False

    if sex == "male":
        # The male rows expressly mark FSH testing "Does not apply".
        return True

    service_value = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_value is None or not tests:
        return False

    service_date = parse_date(service_value)

    # READING: A test "done within the past" must have occurred on or before
    # service; later tests cannot establish eligibility for this claim.
    tests_as_of_service = [
        test for test in tests if parse_date(test[1]) <= service_date
    ]
    if not tests_as_of_service:
        return False

    def test_timestamp(test):
        return datetime.strptime(
            test[1] + " " + test[2], "%Y_%m_%d %H_%M"
        )

    latest_timestamp = max(map(test_timestamp, tests_as_of_service))
    latest_tests = [
        test for test in tests_as_of_service
        if test_timestamp(test) == latest_timestamp
    ]

    window = 12 if age < 35 else 6

    # READING: "within the past" 12 or 6 months includes the exact calendar-
    # month boundary; the most recent test must fall inside that window.
    if not h.months_at_most(
        latest_tests[0][1], service_value, window
    ):
        return False

    if age < 40:
        # READING: "less than 19 ... in your most recent lab test" is strict.
        # When tests tie for most recent, all tied results must qualify,
        # rather than selecting the most favorable result.
        return all(test[0] < 19 for test in latest_tests)

    # READING: "If you are age 40 and older" replaces the most-recent-result
    # threshold with "less than 19 ... in all prior tests performed after
    # age 40". Apply that threshold to every post-40 test through service,
    # including the latest, but not to pre-40 tests. The separate recent-test
    # requirement remains; the text does not require an additional post-40
    # test when the recent test predates the 40th birthday.
    historical_claim = dict(claim)
    historical_claim["day_3_fsh_tests"] = tests_as_of_service
    post_40_tests = h.fsh_tests_since_age_40(historical_claim)
    return all(test[0] < 19 for test in post_40_tests)
