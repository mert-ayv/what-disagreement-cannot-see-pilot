from datetime import date


def _parse_date(s):
    try:
        y, m, d = str(s).split("_")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _sub_years(d, years):
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        return d.replace(year=d.year - years, day=28)


def _to_bool_yes_no(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s == "yes":
            return True
        if s == "no":
            return False
    return None


def adapt(ref_claim: dict) -> dict:
    out = {}
    rc = ref_claim or {}

    # service_type
    if "service_type" in rc:
        st = rc.get("service_type")
        mapping = {
            "ovulation_induction_cycle_with_menotropins": "ovulation_induction_with_menotropins",
            "ovulation_induction_with_menotropins": "ovulation_induction_with_menotropins",
            "intrauterine_insemination": "intrauterine_insemination",
        }
        out["service_type"] = mapping.get(st, "other")

    # service_date
    if "date_service_received" in rc and rc["date_service_received"] is not None:
        out["service_date"] = rc["date_service_received"]

    # patient_birth_date
    if "patient_dob" in rc and rc["patient_dob"] is not None:
        out["patient_birth_date"] = rc["patient_dob"]

    # patient_sex
    ps = rc.get("sex_of_patient_trying_to_conceive")
    if ps in ("female", "male"):
        out["patient_sex"] = ps

    # partner_sex
    psx = rc.get("sex_of_patients_partner")
    if psx in ("male", "female"):
        out["partner_sex"] = psx
    elif psx == "no_partner":
        out["partner_sex"] = "none"

    # partner_birth_date: derived from partner age on the service date
    if psx in ("male", "no_partner"):
        out["partner_birth_date"] = None
    elif psx == "female" and "age_of_patients_female_partner" in rc:
        svc = _parse_date(rc.get("date_service_received"))
        try:
            p_age = int(rc["age_of_patients_female_partner"])
        except (TypeError, ValueError):
            p_age = None
        if svc is not None and p_age is not None:
            out["partner_birth_date"] = _fmt(_sub_years(svc, p_age))

    # Condition-related fields
    if "demonstrated_and_documented_condition_causing_infertility" in rc:
        cond = rc.get("demonstrated_and_documented_condition_causing_infertility")
        if cond is not None:
            out["infertility_condition_documented"] = True
            natural = {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
            out["infertility_due_to_natural_physiologic_process"] = cond in natural

    # Voluntary sterilization
    if "patient_has_had_voluntary_sterilization" in rc:
        b = _to_bool_yes_no(rc["patient_has_had_voluntary_sterilization"])
        if b is not None:
            out["patient_or_partner_voluntary_sterilization"] = b

    # Less costly treatment
    k = "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    if k in rc:
        b = _to_bool_yes_no(rc[k])
        if b is not None:
            out["less_costly_covered_treatment_can_achieve_pregnancy"] = b

    # Months of intercourse: must be both timed and frequent -> min of known values
    vals = []
    for key in ("num_months_timed_unprotected_intercourse",
                "num_months_frequent_unprotected_heterosexual_intercourse"):
        if key in rc and rc[key] is not None:
            try:
                vals.append(int(rc[key]))
            except (TypeError, ValueError):
                pass
    if vals:
        out["months_unprotected_timed_intercourse"] = max(0, min(vals))

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in rc and rc["num_cycles_donor_insemination"] is not None:
        try:
            out["donor_insemination_cycles_self_paid"] = max(0, int(rc["num_cycles_donor_insemination"]))
        except (TypeError, ValueError):
            pass

    # FSH tests
    if "day_3_fsh_tests" in rc and rc["day_3_fsh_tests"] is not None:
        tests = []
        for t in rc["day_3_fsh_tests"] or []:
            level = dt = None
            if isinstance(t, dict):
                level = t.get("level", t.get("value_miu_ml"))
                dt = t.get("date")
            elif isinstance(t, (list, tuple)) and len(t) >= 2:
                level, dt = t[0], t[1]
            if level is None or dt is None:
                continue
            try:
                tests.append({"date": str(dt), "value_miu_ml": float(level)})
            except (TypeError, ValueError):
                continue
        out["unmedicated_day3_fsh_tests"] = tests

    return out
