def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # A documented condition must cause the infertility, and it must not be a
    # natural physiologic process.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex is None or partner is None:
        return False

    months = claim.get("num_months_timed_unprotected_intercourse")
    cycles = claim.get("num_cycles_donor_insemination")

    def at_least(val, n):
        return isinstance(val, int) and val >= n

    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int):
            return False
        required = 12 if partner_age < 37 else 6
        return at_least(months, required)

    if sex != "female":
        return False

    age = h.patient_age(claim)
    if age is None:
        return False

    has_male_partner = partner == "male"
    if partner not in ("male", "female", "no_partner"):
        return False

    n = 12 if age < 37 else 6

    if has_male_partner:
        if not (at_least(months, n) or at_least(cycles, n)):
            return False
    else:
        if not at_least(cycles, n):
            return False

    # FSH test requirements
    service_date = claim.get("date_service_received")
    if not service_date:
        return False
    recent = h.most_recent_fsh_test(claim)
    if recent is None:
        return False
    level, test_date, _time = recent
    if test_date > service_date:
        return False
    if not h.months_at_most(test_date, service_date, n):
        return False

    if age < 40:
        return level < 17
    else:
        since_40 = h.fsh_tests_since_age_40(claim)
        if not since_40:
            return False
        return all(t[0] < 17 for t in since_40)
