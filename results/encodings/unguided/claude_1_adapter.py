from datetime import date


def _parse_date(s):
    if not isinstance(s, str):
        return None
    parts = s.split("_")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, TypeError):
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _yes_no(v):
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
    if not isinstance(ref_claim, dict):
        return out
    r = ref_claim

    # service_type
    if "service_type" in r:
        st = r.get("service_type")
        if st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        elif st in ("ovulation_induction_cycle_with_menotropins",
                    "ovulation_induction_with_menotropins"):
            out["service_type"] = "ovulation_induction_with_menotropins"
        else:
            out["service_type"] = "other"

    # condition-related fields
    if "demonstrated_and_documented_condition_causing_infertility" in r:
        cond = r.get("demonstrated_and_documented_condition_causing_infertility")
        if isinstance(cond, str) and cond:
            out["infertility_condition_demonstrated"] = True
            out["condition_documented_in_patient_or_partner_records"] = True
            out["infertility_due_to_natural_physiologic_process"] = cond in (
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            )

    # sterilization
    if "patient_has_had_voluntary_sterilization" in r:
        b = _yes_no(r.get("patient_has_had_voluntary_sterilization"))
        if b is not None:
            out["patient_had_voluntary_sterilization"] = b

    # less costly treatment
    key = "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    if key in r:
        b = _yes_no(r.get(key))
        if b is not None:
            out["pregnancy_attainable_through_less_costly_covered_treatment"] = b

    # sexes
    if "sex_of_patient_trying_to_conceive" in r:
        s = r.get("sex_of_patient_trying_to_conceive")
        if s in ("female", "male"):
            out["patient_sex"] = s

    partner_sex = None
    if "sex_of_patients_partner" in r:
        ps = r.get("sex_of_patients_partner")
        if ps in ("female", "male"):
            partner_sex = ps
        elif ps in ("no_partner", "none"):
            partner_sex = "none"
        if partner_sex is not None:
            out["partner_sex"] = partner_sex
            if partner_sex == "none":
                out["partner_had_voluntary_sterilization"] = False

    # dates
    if "patient_dob" in r:
        out["patient_birth_date"] = r.get("patient_dob")
    if "date_service_received" in r:
        out["service_date"] = r.get("date_service_received")

    # partner birth date derived from partner age at service date
    svc = _parse_date(r.get("date_service_received"))
    page = r.get("age_of_patients_female_partner")
    if partner_sex == "female":
        if isinstance(page, int) and not isinstance(page, bool) and svc is not None and page >= 0:
            y = svc.year - page
            try:
                pb = svc.replace(year=y)
            except ValueError:  # Feb 29 on a non-leap year
                pb = date(y, 2, 28)
            out["partner_birth_date"] = _fmt(pb)
    elif partner_sex in ("male", "none"):
        out["partner_birth_date"] = None

    # counts
    if "num_months_timed_unprotected_intercourse" in r:
        v = r.get("num_months_timed_unprotected_intercourse")
        if isinstance(v, int) and not isinstance(v, bool):
            out["months_unprotected_timed_intercourse"] = v
    if "num_cycles_donor_insemination" in r:
        v = r.get("num_cycles_donor_insemination")
        if isinstance(v, int) and not isinstance(v, bool):
            out["self_paid_donor_insemination_cycles"] = v

    # FSH tests
    if "day_3_fsh_tests" in r:
        tests = r.get("day_3_fsh_tests")
        lst = []
        if isinstance(tests, (list, tuple)):
            for t in tests:
                level = d = None
                if isinstance(t, (list, tuple)) and len(t) >= 2:
                    level, d = t[0], t[1]
                elif isinstance(t, dict):
                    level = t.get("level", t.get("value_miu_per_ml"))
                    d = t.get("date")
                else:
                    continue
                if isinstance(level, bool) or not isinstance(level, (int, float)):
                    continue
                lst.append({
                    "date": d,
                    "value_miu_per_ml": float(level),
                    "unmedicated": True,
                })
        out["fsh_tests"] = lst

    return out
