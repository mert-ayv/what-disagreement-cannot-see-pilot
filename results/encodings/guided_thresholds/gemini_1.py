def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered service
    service_type = claim.get("service_type")
    if service_type not in (
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    ):
        return False

    # 2. Infertility definition
    if not h.patient_is_infertile(claim):
        return False

    # 3. Demonstrated and documented condition causing infertility (not a natural physiologic process)
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # 4. No voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # 5. Cannot be attained through less costly treatment covered by plan
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # 6. Date service received
    date_service = claim.get("date_service_received")
    if not date_service:
        return False

    # 7. Patient sex & partner sex
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")

    patient_age = h.patient_age(claim)
    if patient_age is None:
        return False

    months_intercourse = claim.get("num_months_timed_unprotected_intercourse") or 0
    cycles_donor = claim.get("num_cycles_donor_insemination") or 0

    if patient_sex == "female":
        if partner_sex == "male":
            # A female with a male partner
            if patient_age < 37:
                if months_intercourse < 12 and cycles_donor < 12:
                    return False
                fsh_max_months = 12
            else:
                if months_intercourse < 6 and cycles_donor < 6:
                    return False
                fsh_max_months = 6
        elif partner_sex in ("female", "no_partner"):
            # A female without a male partner
            if patient_age < 37:
                if cycles_donor < 12:
                    return False
                fsh_max_months = 12
            else:
                if cycles_donor < 6:
                    return False
                fsh_max_months = 6
        else:
            return False

        # FSH test timing and results
        recent_test = h.most_recent_fsh_test(claim)
        if recent_test is None:
            return False

        level, test_date, _ = recent_test
        if not h.months_at_most(test_date, date_service, fsh_max_months):
            return False

        if patient_age < 40:
            if level >= 17:
                return False
        else:
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if not tests_since_40:
                return False
            if any(t[0] >= 17 for t in tests_since_40):
                return False

        return True

    elif patient_sex == "male":
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        if partner_age < 37:
            if months_intercourse < 12:
                return False
        else:
            if months_intercourse < 6:
                return False

        return True

    else:
        return False
