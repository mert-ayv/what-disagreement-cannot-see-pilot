def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # A condition causing infertility must be demonstrated and documented,
    # and it must not be a natural physiologic process.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    if condition in (
        "natural_menopause",
        "natural_perimenopause",
        "natural_male_reproductive_aging",
        "other_natural_physiologic_process",
    ):
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    service_date = claim.get("date_service_received")
    if service_date is None:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
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

    required = 12 if age < 35 else 6

    # Trying-to-conceive requirement
    trying_ok = False
    if cycles is not None and cycles >= required:
        trying_ok = True
    elif partner == "male" and months is not None and months >= required:
        trying_ok = True
    if not trying_ok:
        return False

    # FSH test recency requirement
    recent = h.most_recent_fsh_test(claim)
    if recent is None:
        return False
    level, test_date, _ = recent
    if test_date > service_date:
        return False
    if not h.months_at_most(test_date, service_date, required):
        return False

    # FSH result requirement
    if age < 40:
        return level < 19
    else:
        tests = [t for t in h.fsh_tests_since_age_40(claim) if t[1] <= service_date]
        return all(t[0] < 19 for t in tests)
