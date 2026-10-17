def covered_under_benefit(claim: dict, h) -> bool:
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    if not h.patient_is_infertile(claim):
        return False

    # Infertility must come from a documented condition that is not a
    # natural physiologic process (e.g. menopause or perimenopause).
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    if condition in (
        "natural_menopause",
        "natural_perimenopause",
        "natural_male_reproductive_aging",
        "other_natural_physiologic_process",
    ):
        return False

    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    service_date = claim.get("date_service_received")
    timed_months = claim.get("num_months_timed_unprotected_intercourse", 0) or 0
    donor_cycles = claim.get("num_cycles_donor_insemination", 0) or 0

    if sex == "male":
        # Only the rows for a male with a female partner apply.
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        required = 12 if partner_age < 35 else 6
        return timed_months >= required

    if sex != "female":
        return False

    age = h.patient_age(claim)
    if age is None or service_date is None:
        return False

    required = 12 if age < 35 else 6

    # Months trying to conceive: timed intercourse counts only with a male
    # partner; donor insemination cycles count in every female row.
    trying_ok = donor_cycles >= required
    if partner == "male" and timed_months >= required:
        trying_ok = True
    if not trying_ok:
        return False

    # FSH test must have been done within the past `required` months.
    def in_window(test):
        d = test[1]
        return d <= service_date and h.months_at_most(d, service_date, required)

    if age < 40:
        recent = h.most_recent_fsh_test(claim)
        if recent is None:
            return False
        if not in_window(recent):
            return False
        return recent[0] < 19

    # Age 40 and older.
    tests = claim.get("day_3_fsh_tests") or []
    if not any(in_window(t) for t in tests):
        return False
    since_40 = [t for t in h.fsh_tests_since_age_40(claim) if t[1] <= service_date]
    return all(t[0] < 19 for t in since_40)
