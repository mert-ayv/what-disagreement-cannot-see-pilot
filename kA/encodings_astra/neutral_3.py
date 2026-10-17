"""
READING choices:
- Unknown required facts do not establish eligibility.
- Neither the patient nor an existing partner may have voluntary sterilization.
- The documented condition must not be a natural physiologic process.
- Glossary infertility and the eligibility table are independent requirements.
- For a male with a female partner, glossary infertility is assessed through
  the female partner's age-based intercourse criterion.
- The table supplies the exhaustive eligibility routes; gender dysphoria
  establishes glossary infertility but does not waive table requirements.
- Frequent intercourse and timed intercourse are separate reported facts;
  donor insemination is an alternative only where expressly allowed.
- Only tests performed on or before the service date count.
- Tied most-recent FSH results must all satisfy the applicable threshold.
- At age 40 or older, the FSH threshold applies to all reported post-40 tests;
  the separate recency requirement does not require a post-40 test.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def reported_at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    # READING: Unknown facts — "You are eligible ... if" requires affirmative
    # support for each applicable condition; an absent required fact fails.
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
    # not as allowing eligibility whenever just one person has avoided it.
    # "Your partner" imposes no factual requirement when there is no partner.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # READING: Documented cause — "There exists a condition" documented in
    # "your or your partner's medical records" may be established through
    # either person. "Does not have infertility ... due to a natural
    # physiologic process" excludes every listed natural-process category.
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
    if sex == "female" and age is None:
        return False

    # READING: Independent requirements — the glossary's "A disease defined
    # by the failure to become pregnant" and the benefit's "You are eligible
    # ... if" both apply. A table alternative does not replace the glossary.
    glossary_infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not glossary_infertile:
        if sex == "female":
            required = 12 if age < 35 else 6
            if partner == "male":
                glossary_infertile = reported_at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    required,
                )
            else:
                glossary_infertile = reported_at_least(
                    "num_cycles_donor_insemination", required
                )

        elif partner == "female":
            # READING: Male with female partner — the glossary's "For a female
            # with a male partner" describes the couple's failure to conceive.
            # Apply that criterion through the female partner, consistent with
            # the table's "A male of any age with a female partner" rows.
            partner_age = claim.get("age_of_patients_female_partner")
            if partner_age is not None:
                required = 12 if partner_age < 35 else 6
                glossary_infertile = reported_at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    required,
                )

        else:
            analyses = claim.get("abnormal_semen_analyses")
            service_date = claim.get("date_service_received")
            if analyses is not None and service_date is not None:
                service_day = parse_date(service_date)
                # READING: Test timing — "after ... At least 2 abnormal semen
                # analyses" requires those analyses to precede or coincide
                # with the service, not occur later.
                prior_analyses = [
                    date for date in analyses
                    if parse_date(date) <= service_day
                ]
                if len(prior_analyses) >= 2:
                    first = min(prior_analyses, key=parse_date)
                    last = max(prior_analyses, key=parse_date)
                    glossary_infertile = h.days_between(first, last) >= 14

    if not glossary_infertile:
        return False

    # READING: Table scope — "You have met the requirement for the number of
    # months trying to conceive" followed by the "You are" table supplies
    # exhaustive eligibility routes. No route is supplied for a male without
    # a female partner. The glossary's "clinically diagnosed with gender
    # dysphoria" establishes infertility, but does not waive these requirements.
    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 35 else 6
        # The male rows expressly mark donor cycles and FSH "Does not apply".
        return reported_at_least(
            "num_months_timed_unprotected_intercourse", required
        )

    required = 12 if age < 35 else 6

    # READING: Distinct intercourse measures — the glossary says "frequent,
    # unprotected heterosexual sexual intercourse", whereas the table says
    # "unprotected timed sexual intercourse". Neither reported measure is
    # inferred from the other. The female-with-male-partner rows expressly
    # allow timed intercourse "or" donor insemination.
    donor_requirement_met = reported_at_least(
        "num_cycles_donor_insemination", required
    )
    if partner == "male":
        table_attempt_requirement_met = (
            reported_at_least(
                "num_months_timed_unprotected_intercourse", required
            )
            or donor_requirement_met
        )
    else:
        table_attempt_requirement_met = donor_requirement_met

    if not table_attempt_requirement_met:
        return False

    tests = claim.get("day_3_fsh_tests")
    service_date = claim.get("date_service_received")
    if tests is None or service_date is None:
        return False

    service_day = parse_date(service_date)

    # READING: FSH timing — "within the past" and "all prior tests" refer to
    # the service date. Future tests cannot establish or defeat this claim's
    # eligibility.
    historical_tests = []
    for level, date, time in tests:
        timestamp = datetime.strptime(date + " " + time, "%Y_%m_%d %H_%M")
        if timestamp.date() <= service_day:
            historical_tests.append((level, date, timestamp))

    if not historical_tests:
        return False

    latest_timestamp = max(test[2] for test in historical_tests)
    latest_tests = [
        test for test in historical_tests if test[2] == latest_timestamp
    ]
    if not h.months_at_most(latest_tests[0][1], service_date, required):
        return False

    if age < 40:
        # READING: Tied latest tests — "less than 19 mIU/mL in your most recent
        # lab test" requires every equally recent result to be below 19;
        # no arbitrary list-order tie breaker is used.
        return all(level < 19 for level, _, _ in latest_tests)

    # READING: Age-40 FSH rule — "less than 19 mIU/mL in all prior tests
    # performed after age 40" constrains all post-40 results, not pre-40
    # results. "A ... test done within the past ... 6 months" is separate:
    # a recent pre-40 test can satisfy recency, and the text does not require
    # a nonempty post-40 test history.
    post_40_tests = h.fsh_tests_since_age_40(claim)
    return all(
        level < 19
        for level, date, _ in post_40_tests
        if parse_date(date) <= service_day
    )
