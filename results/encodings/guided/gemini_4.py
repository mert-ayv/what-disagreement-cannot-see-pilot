def covered_under_benefit(claim: dict, h) -> bool:
    # Service must be one of the covered comprehensive infertility services
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # Patient must meet the plan's definition of infertility
    if not h.patient_is_infertile(claim):
        return False

    # Condition causing infertility must be demonstrated/documented and not due to
    # a natural physiologic process (e.g. menopause, perimenopause, aging)
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # Patient has not had voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Pregnancy cannot be attained through less costly covered treatment
    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    timed_months = claim.get("num_months_timed_unprotected_intercourse") or 0
    donor_cycles = claim.get("num_cycles_donor_insemination") or 0

    if patient_sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False

        has_male_partner = partner_sex == "male"

        if age < 35:
            if has_male_partner:
                if timed_months < 12 and donor_cycles < 12:
                    return False
            else:
                if donor_cycles < 12:
                    return False
            fsh_window_months = 12
        else:
            if has_male_partner:
                if timed_months < 6 and donor_cycles < 6:
                    return False
            else:
                if donor_cycles < 6:
                    return False
            fsh_window_months = 6

        # Check day 3 FSH requirements
        date_service = claim.get("date_service_received")
        if not date_service:
            return False

        most_recent_fsh = h.most_recent_fsh_test(claim)
        if not most_recent_fsh:
            return False

        level, test_date, _ = most_recent_fsh
        if not h.months_at_most(test_date, date_service, fsh_window_months):
            return False

        if level >= 19:
            return False

        if age >= 40:
            tests_after_40 = h.fsh_tests_since_age_40(claim)
            if any(t[0] >= 19 for t in tests_after_40):
                return False

        return True

    elif patient_sex == "male":
        # Policy table only provides coverage for males with a female partner
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        if partner_age < 35:
            if timed_months < 12:
                return False
        else:
            if timed_months < 6:
                return False

        return True

    return False
