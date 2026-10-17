def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # A condition causing infertility must be demonstrated and documented,
    # and it must not be a natural physiologic process.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # No voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    # Pregnancy cannot be attained through less costly covered treatment
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    service_date = claim.get("date_service_received")
    if sex is None or partner is None or service_date is None:
        return False

    months_timed = claim.get("num_months_timed_unprotected_intercourse")
    donor_cycles = claim.get("num_cycles_donor_insemination")
    months_timed = months_timed if isinstance(months_timed, int) else 0
    donor_cycles = donor_cycles if isinstance(donor_cycles, int) else 0

    def test_in_window(test, n):
        if test is None:
            return False
        date = test[1]
        if date > service_date:
            return False
        return h.months_at_most(date, service_date, n)

    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 35 else 6
        return months_timed >= required

    if sex != "female":
        return False

    age = h.patient_age(claim)
    if age is None:
        return False

    with_male = partner == "male"
    threshold = 12 if age < 35 else 6

    # Trying-to-conceive requirement
    if with_male:
        if not (months_timed >= threshold or donor_cycles >= threshold):
            return False
    else:
        if donor_cycles < threshold:
            return False

    # FSH requirement
    if age < 40:
        recent = h.most_recent_fsh_test(claim)
        if recent is None:
            return False
        if not test_in_window(recent, threshold):
            return False
        return recent[0] < 19
    else:
        tests_40 = [t for t in h.fsh_tests_since_age_40(claim) if t[1] <= service_date]
        if not tests_40:
            return False
        if not any(test_in_window(t, threshold) for t in tests_40):
            return False
        return all(t[0] < 19 for t in tests_40)
