def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # A demonstrated, documented condition must exist, and infertility must not
    # be due to a natural physiologic process.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition != "other":
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    months = claim.get("num_months_timed_unprotected_intercourse")
    donor_cycles = claim.get("num_cycles_donor_insemination")
    service_date = claim.get("date_service_received")

    def ge(value, n):
        return value is not None and value >= n

    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 35 else 6
        return ge(months, required)

    if sex != "female":
        return False

    age = h.patient_age(claim)
    if age is None or service_date is None or partner is None:
        return False

    n = 12 if age < 35 else 6

    # Months trying to conceive / donor insemination requirement
    if partner == "male":
        if not (ge(months, n) or ge(donor_cycles, n)):
            return False
    else:
        if not ge(donor_cycles, n):
            return False

    # FSH test must have been done within the past n months
    tests = claim.get("day_3_fsh_tests") or []
    prior_tests = [t for t in tests if t[1] <= service_date]
    if not any(h.months_at_most(t[1], service_date, n) for t in prior_tests):
        return False

    most_recent = h.most_recent_fsh_test(claim)

    if age < 40:
        if most_recent is None:
            return False
        if not h.months_at_most(most_recent[1], service_date, n):
            return False
        return most_recent[0] < 19

    # Age 40 and older: all tests performed after age 40 must be < 19
    since_40 = h.fsh_tests_since_age_40(claim)
    if since_40:
        return all(t[0] < 19 for t in since_40)
    # No tests after age 40: fall back to the most recent test
    if most_recent is None:
        return False
    return most_recent[0] < 19
