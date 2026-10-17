def covered_under_benefit(claim: dict, h) -> bool:
    # Check covered service types
    covered_services = {
        "ovulation_induction_cycle_with_menotropins",
        "intrauterine_insemination",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # Check whether patient is infertile under the plan's definition
    if not h.patient_is_infertile(claim):
        return False

    # Patient has not had voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Demonstrated and documented condition, not due to a natural physiologic process
    natural_processes = {
        "natural_menopause",
        "natural_perimenopause",
        "natural_male_reproductive_aging",
        "other_natural_physiologic_process",
    }
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if not condition or condition in natural_processes:
        return False

    # Cannot be attained through less costly covered treatment
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    patient_age = h.patient_age(claim)
    if patient_age is None:
        return False

    dos = claim.get("date_service_received")
    if not dos:
        return False

    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")

    timed_intercourse_months = claim.get("num_months_timed_unprotected_intercourse") or 0
    donor_cycles = claim.get("num_cycles_donor_insemination") or 0

    if patient_sex == "female":
        has_male_partner = (partner_sex == "male")

        # Check conception attempt requirements and FSH lookback limit
        if patient_age < 35:
            if has_male_partner:
                if timed_intercourse_months < 12 and donor_cycles < 12:
                    return False
            else:
                if donor_cycles < 12:
                    return False
            fsh_lookback_months = 12
        else:
            if has_male_partner:
                if timed_intercourse_months < 6 and donor_cycles < 6:
                    return False
            else:
                if donor_cycles < 6:
                    return False
            fsh_lookback_months = 6

        # Check FSH test within required months
        recent_test = h.most_recent_fsh_test(claim)
        if recent_test is None:
            return False

        level, test_date, _ = recent_test
        if not h.months_at_most(test_date, dos, fsh_lookback_months):
            return False

        # Check FSH test results
        if patient_age < 40:
            if level >= 19:
                return False
        else:
            prior_tests_after_40 = h.fsh_tests_since_age_40(claim)
            if not prior_tests_after_40:
                return False
            if any(lvl >= 19 for lvl, _, _ in prior_tests_after_40):
                return False

        return True

    elif patient_sex == "male":
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        if partner_age < 35:
            if timed_intercourse_months < 12:
                return False
        else:
            if timed_intercourse_months < 6:
                return False

        return True

    return False
