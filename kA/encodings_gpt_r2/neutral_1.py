"""Encode comprehensive infertility-services coverage.

READING choices:
- The glossary and the services eligibility table are cumulative requirements.
- The table's listed patient/partner categories are exhaustive.
- For a male with a female partner, the glossary's heterosexual-intercourse
  definition is applied using the female partner's age.
- Gender dysphoria independently satisfies the glossary, not the other criteria.
- Both members of an existing partnership must satisfy the sterilization rule.
- A patient without a partner has no partner sterilization requirement.
- The documented-condition field represents the condition required by the policy;
  only "other" avoids the natural-physiologic-process exclusion.
- Donor insemination is an alternative to timed intercourse in the female table
  rows, but does not replace the separate glossary requirement.
- FSH recency is inclusive; future tests are disregarded.
- Equally recent FSH results must all pass when the latest result governs.
- At age 40 or older, the result threshold applies to all tests on or after the
  40th birthday; a recent pre-40 test may still satisfy the recency requirement.
- Unknown facts do not establish a requirement, but a known alternative can.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, threshold):
        value = claim.get(field)
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            and value >= threshold
        )

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"} or partner not in {
        "female", "male", "no_partner"
    }:
        return False

    # READING: "You or your partner has not had a voluntary sterilization"
    # excludes a voluntary sterilization of either member, rather than allowing
    # coverage whenever just one member has not been sterilized.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # READING: "your partner" imposes no partner-specific requirement when
    # there is no partner; otherwise the partner's status must be known.
    if (
        partner != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: "There exists a condition" that is demonstrated and documented,
    # together with "does not have infertility ... due to a natural physiologic
    # process", is represented by the supplied condition field. Only "other"
    # establishes a documented condition outside the listed natural processes.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    age = h.patient_age(claim) if sex == "female" else None
    if sex == "female" and (age is None or age < 0):
        return False

    female_partner_age = claim.get("age_of_patients_female_partner")
    if sex == "male" and partner == "female":
        if (
            not isinstance(female_partner_age, int)
            or isinstance(female_partner_age, bool)
            or female_partner_age < 0
        ):
            return False

    # READING: "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" is an independent glossary route only;
    # it does not waive "You have met" the table's trying-to-conceive criteria.
    glossary_satisfied = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if sex == "female":
        required = 12 if age < 35 else 6
        if partner == "male":
            glossary_satisfied |= at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )
        else:
            glossary_satisfied |= at_least(
                "num_cycles_donor_insemination", required
            )
    elif partner == "female":
        # READING: The glossary's "For a female with a male partner" and the
        # table's "A male of any age with a female partner" describe the same
        # reproductive pairing. Apply the glossary intercourse duration using
        # the female partner's age, rather than excluding all such male claims.
        required = 12 if female_partner_age < 35 else 6
        glossary_satisfied |= at_least(
            "num_months_frequent_unprotected_heterosexual_intercourse",
            required,
        )
    else:
        analyses = claim.get("abnormal_semen_analyses")
        if analyses:
            dates = [parse_date(value) for value in analyses]
            glossary_satisfied |= any(
                h.days_between(a.strftime("%Y_%m_%d"),
                               b.strftime("%Y_%m_%d")) >= 14
                for a in dates
                for b in dates
            )

    # READING: "the patient is infertile under the glossary" and "You are
    # eligible ... if" make glossary infertility and table eligibility
    # cumulative, even where their routes differ.
    if not glossary_satisfied:
        return False

    if sex == "male":
        # READING: The table lists males only "with a female partner".
        # Treat the table as exhaustive: semen analyses or gender dysphoria
        # establish glossary infertility but do not supply an omitted table row.
        if partner != "female":
            return False
        return at_least(
            "num_months_timed_unprotected_intercourse", required
        )

    # READING: The female rows say "A. ... or B." and "without a male partner".
    # Donor cycles are a table alternative for females with a male partner;
    # females with a female partner or no partner must use donor cycles.
    table_attempts_satisfied = at_least(
        "num_cycles_donor_insemination", required
    )
    if partner == "male":
        table_attempts_satisfied |= at_least(
            "num_months_timed_unprotected_intercourse", required
        )
    if not table_attempts_satisfied:
        return False

    tests = claim.get("day_3_fsh_tests")
    service_date_text = claim.get("date_service_received")
    if not tests or service_date_text is None:
        return False

    service_date = parse_date(service_date_text)

    # READING: "within the past" excludes future tests and includes the exact
    # 12- or 6-calendar-month boundary.
    tests = [test for test in tests if parse_date(test[1]) <= service_date]
    if not tests:
        return False

    def timestamp(test):
        return datetime.strptime(
            test[1] + " " + test[2], "%Y_%m_%d %H_%M"
        )

    latest_timestamp = max(timestamp(test) for test in tests)
    latest_tests = [
        test for test in tests if timestamp(test) == latest_timestamp
    ]
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(
        latest_tests[0][1], service_date_text, recency_months
    ):
        return False

    if age < 40:
        # READING: "less than 19 ... in your most recent lab test" applies
        # strictly. If multiple results share the latest date and time,
        # all must pass; the text supplies no way to prefer one tied result.
        return all(test[0] < 19 for test in latest_tests)

    # READING: "less than 19 ... in all prior tests performed after age 40"
    # includes all tests on/after the 40th birthday through service, including
    # the latest such test. Recency is separate: a recent pre-40 test can meet
    # it, and no post-40 tests means no post-40 threshold violations.
    post_40_tests = [
        test
        for test in h.fsh_tests_since_age_40(claim)
        if parse_date(test[1]) <= service_date
    ]
    return all(test[0] < 19 for test in post_40_tests)
