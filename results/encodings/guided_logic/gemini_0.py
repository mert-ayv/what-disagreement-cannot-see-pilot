def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered service check
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # 2. Patient must meet the plan's definition of infertility
    if not h.patient_is_infertile(claim):
        return False

    # 3. Demonstrated and documented condition causing infertility,
    # and not due to a natural physiologic process
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # 4. No voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # 5. Cannot be attained through less costly treatment
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # 6. Table requirements based on patient and partner demographics
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")

    if patient_sex == "male":
        # Table only provides coverage for male of any age with a female partner
        if partner_sex != "female":
            return False

        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

        months_intercourse = claim.get("num_months_timed_unprotected_intercourse")
        if months_intercourse is None:
            return False

        if female_partner_age < 35:
            if months_intercourse < 12:
                return False
        else:
            if months_intercourse < 6:
                return False

        # Donor insemination and FSH tests do not apply to males
        return True

    elif patient_sex == "female":
        patient_age = h.patient_age(claim)
        if patient_age is None:
            return False

        service_date = claim.get("date_service_received")
        if not service_date:
            return False

        if partner_sex == "male":
            months_intercourse = claim.get("num_months_timed_unprotected_intercourse")
            cycles_donor = claim.get("num_cycles_donor_insemination")

            if patient_age < 35:
                if months_intercourse is None or months_intercourse < 12:
                    return False
                if cycles_donor is None or cycles_donor < 12:
                    return False
            else:
                if months_intercourse is None or months_intercourse < 6:
                    return False
                if cycles_donor is None or cycles_donor < 6:
                    return False

        elif partner_sex in {"female", "no_partner"}:
            cycles_donor = claim.get("num_cycles_donor_insemination")

            if patient_age < 35:
                if cycles_donor is None or cycles_donor < 12:
                    return False
            else:
                if cycles_donor is None or cycles_donor < 6:
                    return False
        else:
            return False

        # FSH test requirements for females
        most_recent_fsh = h.most_recent_fsh_test(claim)
        if most_recent_fsh is None:
            return False

        test_level, test_date, _ = most_recent_fsh

        if patient_age < 35:
            if not h.months_at_most(test_date, service_date, 9):
                return False
            if test_level >= 19:
                return False
        else:
            if not h.months_at_most(test_date, service_date, 6):
                return False
            if patient_age < 40:
                if test_level >= 19:
                    return False
            else:
                if test_level >= 19:
                    return False
                tests_after_40 = h.fsh_tests_since_age_40(claim)
                if any(test[0] >= 19 for test in tests_after_40):
                    return False

        return True

    return False
