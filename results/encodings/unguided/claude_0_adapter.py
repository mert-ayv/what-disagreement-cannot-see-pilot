from datetime import date


def _parse_date(s):
    if not s or not isinstance(s, str):
        return None
    parts = s.strip().split("_")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, TypeError):
        return None


def _yes_no_to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s == "yes":
            return True
        if s == "no":
            return False
    return None


def _dob_for_age(age, on):
    year = on.year - age
    try:
        return date(year, on.month, on.day)
    except ValueError:
        # Feb 29 on a non-leap target year
        return date(year, on.month, 28)


def adapt(ref_claim: dict) -> dict:
    out = {}
    rc = ref_claim or {}

    # service_type
    if "service_type" in rc:
        st = rc.get("service_type")
        if st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_with_menotropins"
        elif st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        else:
            out["service_type"] = "other"

    # service_date
    if "date_service_received" in rc:
        out["service_date"] = rc.get("date_service_received")

    # condition fields
    if "demonstrated_and_documented_condition_causing_infertility" in rc:
        cond = rc.get("demonstrated_and_documented_condition_causing_infertility")
        if cond is not None:
            out["infertility_condition_demonstrated"] = True
            out["condition_recognized_and_documented"] = True
            natural = {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
            out["infertility_due_to_natural_physiologic_process"] = cond in natural

    # voluntary sterilization
    if "patient_has_had_voluntary_sterilization" in rc:
        b = _yes_no_to_bool(rc.get("patient_has_had_voluntary_sterilization"))
        if b is not None:
            out["voluntary_sterilization_patient_or_partner"] = b

    # less costly treatment
    key = "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    if key in rc:
        b = _yes_no_to_bool(rc.get(key))
        if b is not None:
            out["less_costly_covered_treatment_could_succeed"] = b

    # patient sex / dob
    patient_sex = rc.get("sex_of_patient_trying_to_conceive")
    if patient_sex in ("female", "male"):
        out["patient_sex"] = patient_sex
    if "patient_dob" in rc:
        out["patient_date_of_birth"] = rc.get("patient_dob")

    # partner sex
    if "sex_of_patients_partner" in rc:
        ps = rc.get("sex_of_patients_partner")
        if ps == "no_partner":
            out["partner_sex"] = "none"
        elif ps in ("male", "female"):
            out["partner_sex"] = ps

    # partner date of birth derived from female partner's age at service date
    if "age_of_patients_female_partner" in rc:
        service_dt = _parse_date(rc.get("date_service_received"))
        try:
            age = int(rc.get("age_of_patients_female_partner"))
        except (TypeError, ValueError):
            age = None
        if service_dt is not None and age is not None and age >= 0:
            try:
                dob = _dob_for_age(age, service_dt)
                out["partner_date_of_birth"] = "%04d_%02d_%02d" % (dob.year, dob.month, dob.day)
            except (ValueError, OverflowError):
                pass

    # months of intercourse
    timed = rc.get("num_months_timed_unprotected_intercourse")
    frequent = rc.get("num_months_frequent_unprotected_heterosexual_intercourse")
    months = None
    if patient_sex == "male":
        months = frequent if frequent is not None else timed
    else:
        months = timed
    if months is not None:
        out["months_unprotected_timed_intercourse"] = months

    # donor cycles
    if "num_cycles_donor_insemination" in rc:
        out["donor_insemination_cycles_not_plan_paid"] = rc.get("num_cycles_donor_insemination")

    # FSH tests
    if "day_3_fsh_tests" in rc:
        tests = []
        raw = rc.get("day_3_fsh_tests") or []
        for t in raw:
            level = None
            d = None
            if isinstance(t, (list, tuple)):
                if len(t) >= 2:
                    level, d = t[0], t[1]
            elif isinstance(t, dict):
                level = t.get("level")
                d = t.get("date")
            else:
                continue
            try:
                val = float(level)
            except (TypeError, ValueError):
                continue
            tests.append({"date": d, "value_miu_ml": val, "unmedicated_day3": True})
        out["fsh_tests"] = tests

    return out
