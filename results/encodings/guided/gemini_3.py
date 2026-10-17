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

    # Condition causing infertility must be demonstrated and documented,
    # and not due to a natural physiologic process
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # Must not have had voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Successful pregnancy cannot be attained through less costly treatment covered by plan
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    sex_of_patient = claim.get("sex_of_patient_trying_to_conceive")
    sex_of_partner = claim.get("sex_of_patients_partner")

    if sex_of_patient == "male":
        # Policy table only provides coverage for males with a female partner
        if sex_of_partner != "female":
            return False

        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

        timed_months = claim.get("num_months_timed_unprotected_intercourse")
        if timed_months is None:
            return False

        if female_partner_age < 35:
            if timed_months < 12:
                return False
        else:
            if timed_months < 6:
                return False

        return True

    elif sex_of_patient == "female":
        patient_age = h.patient_age(claim)
        if patient_age is None:
            return False

        if sex_of_partner not in ("male", "female", "no_partner"):
            return False

        has_male_partner = (sex_of_partner == "male")
        timed_months = claim.get("num_months_timed_unprotected_intercourse")
        donor_cycles = claim.get("num_cycles_donor_insemination")

        if patient_age < 35:
            if has_male_partner:
                met_timed = timed_months is not None and timed_months >= 12
                met_donor = donor_cycles is not None and donor_cycles >= 12
                if not (met_timed or met_donor):
                    return False
            else:
                if donor_cycles is None or donor_cycles < 12:
                    return False
            fsh_window_months = 12
        else:
            if has_male_partner:
                met_timed = timed_months is not None and timed_months >= 6
                met_donor = donor_cycles is not None and donor_cycles >= 6
                if not (met_timed or met_donor):
                    return False
            else:
                if donor_cycles is None or donor_cycles < 6:
                    return False
            fsh_window_months = 6

        # Check FSH test timing and results
        dos = claim.get("date_service_received")
        if not dos:
            return False

        recent_test = h.most_recent_fsh_test(claim)
        if recent_test is None:
            return False

        recent_level, recent_date, _ = recent_test

        # Must have an unmedicated day 3 FSH test done within the past window
        if not (recent_date <= dos and h.months_at_most(recent_date, dos, fsh_window_months)):
            return False

        # FSH level criteria
        if patient_age < 40:
            if recent_level >= 19:
                return False
        else:
            if recent_level >= 19:
                return False
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if any(test[0] >= 19 for test in tests_since_40):
                return False

        return True

    else:
        return False
