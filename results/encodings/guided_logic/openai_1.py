def covered_under_benefit(claim: dict, h) -> bool:
    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    if not h.patient_is_infertile(claim):
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")

    def at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    if sex == "male":
        if partner_sex != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required_months = 12 if partner_age < 35 else 6
        return at_least(
            "num_months_timed_unprotected_intercourse", required_months
        )

    if sex != "female" or partner_sex not in {"male", "female", "no_partner"}:
        return False

    age = h.patient_age(claim)
    if age is None:
        return False

    required_attempts = 12 if age < 35 else 6

    # The table requires both intercourse and donor cycles with a male partner.
    if partner_sex == "male" and not at_least(
        "num_months_timed_unprotected_intercourse", required_attempts
    ):
        return False

    if not at_least("num_cycles_donor_insemination", required_attempts):
        return False

    latest_test = h.most_recent_fsh_test(claim)
    service_date = claim.get("date_service_received")
    if latest_test is None or service_date is None:
        return False

    level, test_date, _ = latest_test
    recency_months = 9 if age < 35 else 6

    if test_date > service_date:
        return False
    if not h.months_at_most(test_date, service_date, recency_months):
        return False

    if age < 40:
        return level < 19

    return all(
        test_level < 19
        for test_level, _, _ in h.fsh_tests_since_age_40(claim)
    )
