"""
READING choices:
- Apply the glossary and the eligibility table cumulatively.
- Apply glossary categories to the patient, without imputing a partner's status.
- Treat gender dysphoria as an alternative glossary definition, not a waiver.
- Require an expressly applicable table row.
- Exclude voluntary sterilization of either member of an existing couple.
- Exclude all identified natural physiologic causes.
- Require both glossary intercourse and table contact requirements where applicable.
- Count only tests performed by the service date.
- Resolve tied most-recent FSH results against coverage.
- At age 40 or older, test every post-40 result, including the latest.
"""


def covered_under_benefit(claim: dict, h) -> bool:
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
    # requires neither member of an existing couple to have undergone it;
    # one unsterilized member is insufficient. An absent partner needs no finding.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # READING: "a natural physiologic process such as age related ovarian
    # insufficiency" is illustrative, not limited to ovarian aging.
    # The supplied "other" category establishes a documented non-natural cause.
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

    age = h.patient_age(claim) if sex == "female" else None
    if sex == "female" and age is None:
        return False

    def enough(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    # READING: The glossary's "For an individual or their partner who has been
    # clinically diagnosed with gender dysphoria" supplies an alternative
    # glossary route. It does not waive "You are eligible ... if" or the table.
    glossary_satisfied = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not glossary_satisfied:
        if sex == "female":
            required = 12 if age < 35 else 6
            if partner == "male":
                # READING: The glossary's "frequent, unprotected heterosexual
                # sexual intercourse" and the table's "unprotected timed sexual
                # intercourse" are separate requirements; neither proves the
                # other. The table's donor alternative does not erase the
                # glossary's intercourse requirement for this category.
                glossary_satisfied = enough(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    required,
                )
            else:
                glossary_satisfied = enough(
                    "num_cycles_donor_insemination", required
                )
        elif partner != "female":
            service_date = claim.get("date_service_received")
            analyses = claim.get("abnormal_semen_analyses")
            if service_date is not None and analyses is not None:
                # READING: Analyses "obtained" must already exist when the
                # service is received; future analyses cannot establish status.
                prior = sorted(d for d in analyses if d <= service_date)
                glossary_satisfied = (
                    len(prior) >= 2
                    and h.days_between(prior[0], prior[-1]) >= 14
                )
        else:
            # READING: "For a female with a male partner" describes a female
            # patient, not her male partner. The glossary supplies no ordinary
            # male-with-female-partner branch. Do not impute the female
            # partner's infertility to the patient; a table row alone does not
            # establish the separately required glossary definition.
            glossary_satisfied = False

    if not glossary_satisfied:
        return False

    # READING: "You have met the requirement for the number of months" and
    # "FSH level meets the following criteria" make the table mandatory.
    # No listed row for a male without a female partner means no table-based
    # eligibility, even if semen analyses or gender dysphoria meet the glossary.
    if sex == "male":
        if partner != "female":
            return False
        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False
        required = 12 if female_partner_age < 35 else 6
        return enough("num_months_timed_unprotected_intercourse", required)

    required = 12 if age < 35 else 6
    donor_requirement_met = enough("num_cycles_donor_insemination", required)
    if partner == "male":
        contact_requirement_met = (
            enough("num_months_timed_unprotected_intercourse", required)
            or donor_requirement_met
        )
    else:
        contact_requirement_met = donor_requirement_met

    if not contact_requirement_met:
        return False

    service_date = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date is None or tests is None:
        return False

    # READING: A test "done within the past" must be on or before the service
    # date. Later tests neither establish recency nor disqualify an earlier claim.
    prior_tests = [test for test in tests if test[1] <= service_date]
    if not prior_tests:
        return False

    latest_key = max((test[1], test[2]) for test in prior_tests)
    latest_tests = [
        test for test in prior_tests
        if (test[1], test[2]) == latest_key
    ]
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(latest_key[0], service_date, recency_months):
        return False

    if age < 40:
        # READING: "less than 19 ... in your most recent lab test" requires
        # every equally most-recent result to pass when timestamps tie;
        # an adverse tied result cannot be discarded.
        return all(test[0] < 19 for test in latest_tests)

    # READING: "less than 19 ... in all prior tests performed after age 40"
    # includes the latest test and tests on the 40th birthday, but not tests
    # before that birthday. The separate recent-test requirement still applies;
    # the text does not require an additional post-birthday test.
    post_40_tests = h.fsh_tests_since_age_40(claim)
    return all(
        test[0] < 19
        for test in post_40_tests
        if test[1] <= service_date
    )
