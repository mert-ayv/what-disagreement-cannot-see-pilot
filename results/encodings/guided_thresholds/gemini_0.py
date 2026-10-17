def covered_under_benefit(claim: dict, h) -> bool:
    # Check covered service type
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # Patient must meet glossary definition of infertility
    if not h.patient_is_infertile(claim):
        return False

    # Condition causing infertility must be demonstrated and documented,
    # and not due to a natural physiologic process (e.g., menopause, perimenopause, aging)
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    # Voluntary sterilization exclusion
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

    # Patient age and sex
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    patient_age = h.patient_age(claim)
    if patient_age is None:
        return False

    partner_sex = claim.get("sex_of_patients_partner")
    timed_months = claim.get("num_months_timed_unprotected_intercourse", 0)
    donor_cycles = claim.get("num_cycles_donor_insemination", 0)

    if patient_sex == "female":
        has_male_partner = partner_sex == "male"
        without_male_partner = partner_sex in ("female", "no_partner")
        if not (has_male_partner or without_male_partner):
            return False

        # Check intercourse/donor cycle requirements and FSH timeframe
        if patient_age < 37:
            max_fsh_months = 12
            if has_male_partner:
                if timed_months < 12 and donor_cycles < 12:
                    return False
            else:
                if donor_cycles < 12:
                    return False
        else:
            max_fsh_months = 6
            if has_male_partner:
                if timed_months < 6 and donor_cycles < 6:
                    return False
            else:
                if donor_cycles < 6:
                    return False

        # FSH test requirements
        service_date = claim.get("date_service_received")
        if not service_date:
            return False

        most_recent = h.most_recent_fsh_test(claim)
        if most_recent is None:
            return False

        level, test_date, _ = most_recent
        if test_date > service_date:
            return False
        if not h.months_at_most(test_date, service_date, max_fsh_months):
            return False

        if patient_age < 40:
            if level >= 17:
                return False
        else:
            # Age 40 and older: must be less than 17 in all prior tests performed after age 40
            if level >= 17:
                return False
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if not all(t[0] < 17 for t in tests_since_40):
                return False

        return True

    elif patient_sex == "male":
        # Male patient is only eligible if they have a female partner
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        if partner_age < 37:
            if timed_months < 12:
                return False
        else:
            if timed_months < 6:
                return False

        return True

    return False
