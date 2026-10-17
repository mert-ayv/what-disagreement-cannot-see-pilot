from datetime import date


def _parse_date(s):
    try:
        y, m, d = (int(p) for p in str(s).split("_"))
        return date(y, m, d)
    except Exception:
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
    rc = ref_claim or {}

    # service_type
    if "service_type" in rc:
        st = rc["service_type"]
        if st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        elif st in ("ovulation_induction_cycle_with_menotropins", "ovulation_induction_menotropins"):
            out["service_type"] = "ovulation_induction_menotropins"
        else:
            out["service_type"] = "other"

    # dates
    if "date_service_received" in rc:
        out["service_date"] = rc["date_service_received"]
    if "patient_dob" in rc:
        out["patient_birth_date"] = rc["patient_dob"]

    # sexes
    if "sex_of_patient_trying_to_conceive" in rc:
        out["patient_sex"] = rc["sex_of_patient_trying_to_conceive"]
    partner = rc.get("sex_of_patients_partner")
    if partner is not None:
        if partner == "no_partner":
            out["partner_sex"] = "none"
        else:
            out["partner_sex"] = partner

    # partner birth date (derived from partner age on the service date)
    if partner == "no_partner":
        out["partner_birth_date"] = None
    elif "age_of_patients_female_partner" in rc:
        sd = _parse_date(rc.get("date_service_received"))
        try:
            page = int(rc["age_of_patients_female_partner"])
        except Exception:
            page = None
        if sd is not None and page is not None:
            try:
                pb = sd.replace(year=sd.year - page)
            except ValueError:
                pb = sd.replace(year=sd.year - page, day=28)
            out["partner_birth_date"] = _fmt(pb)

    # months of frequent, unprotected, timed heterosexual intercourse
    vals = []
    for k in ("num_months_timed_unprotected_intercourse",
              "num_months_frequent_unprotected_heterosexual_intercourse"):
        if k in rc and rc[k] is not None:
            try:
                vals.append(int(rc[k]))
            except Exception:
                pass
    if vals:
        out["months_unprotected_intercourse_without_pregnancy"] = min(vals)

    # donor insemination cycles
    if "num_cycles_donor_insemination" in rc:
        try:
            out["donor_insemination_cycles_self_paid"] = int(rc["num_cycles_donor_insemination"])
        except Exception:
            out["donor_insemination_cycles_self_paid"] = rc["num_cycles_donor_insemination"]

    # FSH tests
    if "day_3_fsh_tests" in rc:
        tests = []
        for t in rc.get("day_3_fsh_tests") or []:
            level = dt = None
            if isinstance(t, dict):
                level = t.get("level", t.get("value_miu_ml"))
                dt = t.get("date")
            elif isinstance(t, (list, tuple)):
                if len(t) >= 1:
                    level = t[0]
                if len(t) >= 2:
                    dt = t[1]
            try:
                val = float(level)
            except Exception:
                val = level
            tests.append({"date": dt, "value_miu_ml": val})
        out["fsh_tests"] = tests

    # condition demonstrated / documented, natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in rc:
        cond = rc["demonstrated_and_documented_condition_causing_infertility"]
        out["infertility_condition_demonstrated"] = True
        out["condition_recognized_and_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        )

    # voluntary sterilization
    if "patient_has_had_voluntary_sterilization" in rc:
        v = _yes_no(rc["patient_has_had_voluntary_sterilization"])
        if v is not None:
            out["voluntary_sterilization"] = v

    # less costly treatment
    k = "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    if k in rc:
        v = _yes_no(rc[k])
        if v is not None:
            out["less_costly_covered_treatment_can_achieve_pregnancy"] = v

    return out
