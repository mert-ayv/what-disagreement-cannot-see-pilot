def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # A demonstrated, documented condition causing infertility that is not a
    # natural physiologic process.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition != "other":
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    service_date = claim.get("date_service_received")
    if not service_date:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex is None or partner is None:
        return False

    months_timed = claim.get("num_months_timed_unprotected_intercourse")
    donor_cycles = claim.get("num_cycles_donor_insemination")
    months_timed = months_timed if isinstance(months_timed, int) else 0
    donor_cycles = donor_cycles if isinstance(donor_cycles, int) else 0

    def in_window(test, n):
        if test is None:
            return False
        tdate = test[1]
        return tdate <= service_date and h.months_at_most(tdate, service_date, n)

    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 37 else 6
        return months_timed >= required

    if sex != "female":
        return False

    age = h.patient_age(claim)
    if age is None:
        return False

    has_male_partner = partner == "male"
    if partner not in ("male", "female", "no_partner"):
        return False

    if age < 37:
        n = 12
    else:
        n = 6

    # Trying-to-conceive requirement
    if has_male_partner:
        if not (months_timed >= n or donor_cycles >= n):
            return False
    else:
        if not (donor_cycles >= n):
            return False

    # FSH requirement
    tests = claim.get("day_3_fsh_tests") or []
    if age < 40:
        recent = h.most_recent_fsh_test(claim)
        if recent is None:
            return False
        if not in_window(recent, n):
            return False
        if not (recent[0] < 17):
            return False
        return True
    else:
        if not any(in_window(t, n) for t in tests):
            return False
        since_40 = h.fsh_tests_since_age_40(claim) or []
        for t in since_40:
            if not (t[0] < 17):
                return False
        return True
