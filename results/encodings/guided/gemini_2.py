def covered_under_benefit(claim: dict, h) -> bool:
    # Service coverage
    covered_services = {
        "ovulation_induction_cycle_with_menotropins",
        "intrauterine_insemination",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # Infertility requirement
    if not h.patient_is_infertile(claim):
        return False

    # Condition causing infertility must be demonstrated/documented and not a natural physiologic process
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # Voluntary sterilization exclusion
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Less costly treatment requirement
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    timed_intercourse_months = claim.get("num_months_timed_unprotected_intercourse") or 0
    donor_cycles = claim.get("num_cycles_donor_insemination") or 0
    service_date = claim.get("date_service_received")

    if patient_sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False

        if partner_sex == "male":
            if age < 35:
                months_needed = 12
                cycles_needed = 12
                fsh_max_months = 12
            else:
                months_needed = 6
                cycles_needed = 6
                fsh_max_months = 6

            # Trying to conceive requirement: timed intercourse OR donor insemination
            if timed_intercourse_months < months_needed and donor_cycles < cycles_needed:
                return False
        else:
            # Female without a male partner
            if age < 35:
                cycles_needed = 12
                fsh_max_months = 12
            else:
                cycles_needed = 6
                fsh_max_months = 6

            if donor_cycles < cycles_needed:
                return False

        # FSH test requirements
        recent_fsh = h.most_recent_fsh_test(claim)
        if recent_fsh is None:
            return False

        recent_level, recent_date, _ = recent_fsh
        if not h.months_at_most(recent_date, service_date, fsh_max_months):
            return False

        if age < 40:
            if recent_level >= 19:
                return False
        else:
            if recent_level >= 19:
                return False
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if any(level >= 19 for level, _, _ in tests_since_40):
                return False

        return True

    elif patient_sex == "male":
        if partner_sex != "female":
            return False

        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

        if female_partner_age < 35:
            return timed_intercourse_months >= 12
        else:
            return timed_intercourse_months >= 6

    return False
