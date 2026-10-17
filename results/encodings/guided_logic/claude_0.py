def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # A condition demonstrated to cause infertility must be recognized and documented,
    # and must not be a natural physiologic process.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    if condition in {
        "natural_menopause",
        "natural_perimenopause",
        "natural_male_reproductive_aging",
        "other_natural_physiologic_process",
    }:
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    service_date = claim.get("date_service_received")
    if sex is None or partner is None or service_date is None:
        return False

    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        under_35 = age < 35
        required = 12 if under_35 else 6
        fsh_window = 9 if under_35 else 6

        cycles = claim.get("num_cycles_donor_insemination")
        if cycles is None or cycles < required:
            return False

        if partner == "male":
            months = claim.get("num_months_timed_unprotected_intercourse")
            if months is None or months < required:
                return False
        elif partner not in ("female", "no_partner"):
            return False

        recent = h.most_recent_fsh_test(claim)
        if recent is None:
            return False
        level, test_date, _time = recent
        if test_date > service_date:
            return False
        if not h.months_at_most(test_date, service_date, fsh_window):
            return False

        if age < 40:
            if not level < 19:
                return False
        else:
            tests_40 = h.fsh_tests_since_age_40(claim)
            for t in tests_40:
                if not t[0] < 19:
                    return False
        return True

    elif sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 35 else 6
        months = claim.get("num_months_timed_unprotected_intercourse")
        if months is None or months < required:
            return False
        return True

    return False
