def covered_under_benefit(claim: dict, h) -> bool:
    # Service must be one of the covered comprehensive infertility services
    if claim.get("service_type") not in (
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    ):
        return False

    # Patient must meet the plan's glossary definition of infertility
    if not h.patient_is_infertile(claim):
        return False

    # Cannot have had voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Condition causing infertility must exist and be documented, and cannot be a natural physiologic process
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    # Successful pregnancy cannot be attained through less costly covered treatment
    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    dos = claim.get("date_service_received")
    if not dos:
        return False

    if patient_sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False

        # FSH test requirements
        fsh_test = h.most_recent_fsh_test(claim)
        if fsh_test is None:
            return False
        level, test_date, _ = fsh_test

        if age < 35:
            # FSH test within past 9 months, level < 19
            if not h.months_at_most(test_date, dos, 9):
                return False
            if level >= 19:
                return False

            if partner_sex == "male":
                timed = claim.get("num_months_timed_unprotected_intercourse")
                donor = claim.get("num_cycles_donor_insemination")
                if timed is None or timed < 12:
                    return False
                if donor is None or donor < 12:
                    return False
            elif partner_sex in ("female", "no_partner"):
                donor = claim.get("num_cycles_donor_insemination")
                if donor is None or donor < 12:
                    return False
            else:
                return False

        else:  # age >= 35
            # FSH test within past 6 months
            if not h.months_at_most(test_date, dos, 6):
                return False

            if age < 40:
                if level >= 19:
                    return False
            else:  # age >= 40
                if level >= 19:
                    return False
                tests_after_40 = h.fsh_tests_since_age_40(claim)
                if any(t[0] >= 19 for t in tests_after_40):
                    return False

            if partner_sex == "male":
                timed = claim.get("num_months_timed_unprotected_intercourse")
                donor = claim.get("num_cycles_donor_insemination")
                if timed is None or timed < 6:
                    return False
                if donor is None or donor < 6:
                    return False
            elif partner_sex in ("female", "no_partner"):
                donor = claim.get("num_cycles_donor_insemination")
                if donor is None or donor < 6:
                    return False
            else:
                return False

    elif patient_sex == "male":
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        timed = claim.get("num_months_timed_unprotected_intercourse")
        if timed is None:
            return False

        if partner_age < 35:
            if timed < 12:
                return False
        else:  # partner_age >= 35
            if timed < 6:
                return False

    else:
        return False

    return True
