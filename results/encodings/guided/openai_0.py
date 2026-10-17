def covered_under_benefit(claim: dict, h) -> bool:
    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    if not h.patient_is_infertile(claim):
        return False

    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    intercourse_months = claim.get("num_months_timed_unprotected_intercourse", 0)
    donor_cycles = claim.get("num_cycles_donor_insemination", 0)

    if sex == "male":
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None or partner_age < 0:
            return False

        required_months = 12 if partner_age < 35 else 6
        return intercourse_months >= required_months

    if sex != "female" or partner_sex not in {"male", "female", "no_partner"}:
        return False

    age = h.patient_age(claim)
    if age is None or age < 0:
        return False

    required_months_or_cycles = 12 if age < 35 else 6
    if partner_sex == "male":
        if not (
            intercourse_months >= required_months_or_cycles
            or donor_cycles >= required_months_or_cycles
        ):
            return False
    elif donor_cycles < required_months_or_cycles:
        return False

    latest_test = h.most_recent_fsh_test(claim)
    service_date = claim.get("date_service_received")
    if latest_test is None or service_date is None:
        return False

    level, test_date, _ = latest_test
    if test_date > service_date:
        return False

    if not h.months_at_most(test_date, service_date, required_months_or_cycles):
        return False

    if age < 40:
        return level < 19

    return all(
        test_level < 19
        for test_level, _, _ in h.fsh_tests_since_age_40(claim)
    )
