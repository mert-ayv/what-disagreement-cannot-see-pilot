from datetime import datetime, date


def adapt(ref_claim: dict) -> dict:
    out = {}

    # service_type
    st = ref_claim.get("service_type")
    if st is not None:
        if st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        elif st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_menotropins"
        else:
            out["service_type"] = "other"

    # service_date
    sd = ref_claim.get("date_service_received")
    if sd is not None:
        out["service_date"] = sd

    # patient_sex
    ps = ref_claim.get("sex_of_patient_trying_to_conceive")
    if ps in ("female", "male"):
        out["patient_sex"] = ps

    # patient_birth_date
    dob = ref_claim.get("patient_dob")
    if dob is not None:
        out["patient_birth_date"] = dob

    # partner_sex
    psx = ref_claim.get("sex_of_patients_partner")
    if psx is not None:
        if psx == "no_partner":
            out["partner_sex"] = "none"
        elif psx in ("male", "female"):
            out["partner_sex"] = psx

    # partner_birth_date: derived from partner's age at service date
    page = ref_claim.get("age_of_patients_female_partner")
    if page is not None and sd is not None and psx == "female":
        try:
            svc = datetime.strptime(sd, "%Y_%m_%d").date()
            y = svc.year - int(page)
            try:
                b = date(y, svc.month, svc.day)
            except ValueError:
                b = date(y, 2, 28)
            out["partner_birth_date"] = b.strftime("%Y_%m_%d")
        except (ValueError, TypeError):
            pass

    # condition documentation / natural physiologic process
    cond = ref_claim.get("demonstrated_and_documented_condition_causing_infertility")
    if cond is not None:
        out["infertility_condition_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        )

    # voluntary sterilization
    vs = ref_claim.get("patient_has_had_voluntary_sterilization")
    if vs in ("yes", "no"):
        out["voluntary_sterilization_patient_or_partner"] = vs == "yes"

    # less costly treatment
    lc = ref_claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    )
    if lc in ("yes", "no"):
        out["pregnancy_attainable_by_less_costly_covered_treatment"] = lc == "yes"

    # months of frequent, unprotected, timed heterosexual intercourse
    m1 = ref_claim.get("num_months_timed_unprotected_intercourse")
    m2 = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    vals = [int(m) for m in (m1, m2) if m is not None]
    if vals:
        out["months_unprotected_timed_intercourse"] = max(0, min(vals))

    # donor insemination cycles
    dc = ref_claim.get("num_cycles_donor_insemination")
    if dc is not None:
        out["donor_insemination_cycles_not_plan_paid"] = int(dc)

    # FSH tests
    fsh = ref_claim.get("day_3_fsh_tests")
    if fsh is not None:
        tests = []
        for t in fsh:
            if isinstance(t, dict):
                level = t.get("level")
                d = t.get("date")
            else:
                level = t[0] if len(t) > 0 else None
                d = t[1] if len(t) > 1 else None
            try:
                tests.append({"date": d, "value_miu_ml": float(level)})
            except (TypeError, ValueError):
                tests.append({"date": d, "value_miu_ml": level})
        out["fsh_tests"] = tests

    return out
