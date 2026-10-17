def covered_under_benefit(claim: dict, h) -> bool:
    # Covered services
    if claim.get("service_type") not in (
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    ):
        return False

    # Patient must be infertile
    if not h.patient_is_infertile(claim):
        return False

    # A documented condition demonstrated to cause infertility, not due to a
    # natural physiologic process
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # No voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Pregnancy cannot be attained through less costly covered treatment
    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex is None or partner is None:
        return False

    months = claim.get("num_months_timed_unprotected_intercourse")
    cycles = claim.get("num_cycles_donor_insemination")

    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None or months is None:
            return False
        required = 12 if partner_age < 35 else 6
        return months >= required

    if sex != "female":
        return False

    age = h.patient_age(claim)
    if age is None:
        return False

    if age < 35:
        req_months, req_cycles, window = 12, 12, 9
    else:
        req_months, req_cycles, window = 6, 6, 6

    # Trying-to-conceive requirements
    if cycles is None or cycles < req_cycles:
        return False
    if partner == "male":
        if months is None or months < req_months:
            return False

    # FSH test requirements
    service_date = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date is None or not tests:
        return False

    # Test must have been done within the required window
    if not any(h.months_at_most(t[1], service_date, window) for t in tests):
        return False

    if age < 40:
        recent = h.most_recent_fsh_test(claim)
        if recent is None:
            return False
        if not h.months_at_most(recent[1], service_date, window):
            return False
        return recent[0] < 19
    else:
        since_40 = h.fsh_tests_since_age_40(claim)
        return all(t[0] < 19 for t in since_40)
