from datetime import date
import calendar


def _parse(d):
    if not d or not isinstance(d, str):
        return None
    try:
        y, m, dd = d.split("_")
        return date(int(y), int(m), int(dd))
    except Exception:
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _sub_years(d, years):
    y = d.year - years
    day = min(d.day, calendar.monthrange(y, d.month)[1])
    return date(y, d.month, day)


def adapt(ref_claim: dict) -> dict:
    out = {}

    # service_type
    st = ref_claim.get("service_type")
    if st is not None:
        if st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_menotropins"
        elif st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        else:
            out["service_type"] = "other"

    # dates
    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]
    if "patient_dob" in ref_claim:
        out["patient_date_of_birth"] = ref_claim["patient_dob"]

    # sexes
    sex = ref_claim.get("sex_of_patient_trying_to_conceive")
    if sex in ("female", "male"):
        out["patient_sex"] = sex

    psex = ref_claim.get("sex_of_patients_partner")
    if psex is not None:
        if psex == "no_partner":
            out["partner_sex"] = "none"
        elif psex in ("female", "male"):
            out["partner_sex"] = psex

    # partner date of birth derived from partner age at service date
    page = ref_claim.get("age_of_patients_female_partner")
    sdate = _parse(ref_claim.get("date_service_received"))
    if page is not None and sdate is not None:
        try:
            out["partner_date_of_birth"] = _fmt(_sub_years(sdate, int(page)))
        except Exception:
            pass

    # condition
    cond = ref_claim.get("demonstrated_and_documented_condition_causing_infertility")
    if cond is not None:
        out["infertility_causing_condition_exists"] = True
        out["condition_recognized_and_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        )

    # sterilization
    ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    if ster in ("yes", "no"):
        out["patient_or_partner_voluntary_sterilization"] = ster == "yes"

    # less costly treatment
    lc = ref_claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    )
    if lc in ("yes", "no"):
        out["pregnancy_attainable_with_less_costly_covered_treatment"] = lc == "yes"

    # months of intercourse (schema requires frequent AND timed)
    timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    freq = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    vals = [int(v) for v in (timed, freq) if v is not None]
    if vals:
        out["months_unprotected_intercourse_without_pregnancy"] = max(0, min(vals))

    # donor insemination cycles
    di = ref_claim.get("num_cycles_donor_insemination")
    if di is not None:
        out["donor_insemination_cycles_without_pregnancy"] = max(0, int(di))

    # FSH tests
    fsh = ref_claim.get("day_3_fsh_tests")
    if fsh is not None:
        tests = []
        for t in fsh:
            level = None
            tdate = None
            if isinstance(t, dict):
                level = t.get("level")
                tdate = t.get("date")
            elif isinstance(t, (list, tuple)):
                if len(t) > 0:
                    level = t[0]
                if len(t) > 1:
                    tdate = t[1]
            if level is None or tdate is None:
                continue
            try:
                val = float(level)
            except Exception:
                continue
            tests.append({"date": tdate, "value_miu_ml": val, "unmedicated_day3": True})
        out["fsh_tests"] = tests

    return out
