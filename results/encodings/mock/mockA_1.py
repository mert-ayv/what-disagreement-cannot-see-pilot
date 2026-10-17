# Pipeline test only: off-by-one at 35, from a hand-written encoding.
def covered_under_benefit(claim, h):
    if claim.get("service_type") not in ("intrauterine_insemination", "ovulation_induction_cycle_with_menotropins"):
        return False
    if not h.patient_is_infertile(claim):
        return False
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    cond = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if cond is None or cond.startswith("natural") or cond == "other_natural_physiologic_process":
        return False
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False
    sex, partner = claim.get("sex_of_patient_trying_to_conceive"), claim.get("sex_of_patients_partner")
    timed = claim.get("num_months_timed_unprotected_intercourse", 0)
    donor = claim.get("num_cycles_donor_insemination", 0)
    if sex == "male" and partner == "female":
        pa = claim.get("age_of_patients_female_partner")
        return pa is not None and timed >= (12 if pa < 35 else 6)
    if sex != "female":
        return False
    age = h.patient_age(claim)
    if age is None:
        return False
    need = 12 if age <= 35 else 6
    contact = donor >= need or (partner == "male" and timed >= need)
    recent = h.most_recent_fsh_test(claim)
    if not contact or recent is None or not h.months_at_most(recent[1], claim["date_service_received"], need):
        return False
    if age < 40:
        return recent[0] < 19
    tests = h.fsh_tests_since_age_40(claim)
    return bool(tests) and all(t[0] < 19 for t in tests)
