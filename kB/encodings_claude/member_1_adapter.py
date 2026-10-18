from datetime import date, timedelta

ASSUMED_MET = [
    "billed_by_infertility_specialist",
    "covered_as",
    "partner_covered_under_plan",
    "approval_request_date",
]

_NATURAL = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _parse(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = value.split("_")
        return date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _yes_no(value):
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def _dob_from_age(age, on):
    # A date of birth that gives exactly `age` completed years on `on`, about half a year past the birthday.
    try:
        anniv = on.replace(year=on.year - age)
    except ValueError:  # 29 February
        anniv = date(on.year - age, 2, 28)
    return anniv - timedelta(days=182)


def adapt(ref_claim: dict) -> dict:
    r = ref_claim
    out = {}

    # Service type
    st = r.get("service_type")
    if st is not None:
        if st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        elif st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_menotropins"
        elif isinstance(st, str) and "ovulation_induction" in st:
            out["service_type"] = "ovulation_induction_other"
        else:
            out["service_type"] = "other"

    # Facts the reference interface does not cover: set to the value meaning the requirement is met.
    out["billed_by_infertility_specialist"] = True
    out["covered_as"] = "student"
    out["partner_covered_under_plan"] = True

    # Sex
    sex = r.get("sex_of_patient_trying_to_conceive")
    if sex in ("female", "male"):
        out["patient_sex"] = sex
    psex = r.get("sex_of_patients_partner")
    if psex in ("female", "male"):
        out["partner_sex"] = psex
    elif psex == "no_partner":
        out["partner_sex"] = "none"

    # Dates
    if "patient_dob" in r:
        out["patient_date_of_birth"] = r["patient_dob"]
    service_date = r.get("date_service_received")
    if service_date is not None:
        out["service_date"] = service_date
        # Assessment as of the service date only, as in the reference interface.
        out["approval_request_date"] = service_date

    # Partner date of birth derived from the female partner's age at the service date
    page = r.get("age_of_patients_female_partner")
    sd = _parse(service_date)
    if isinstance(page, int) and not isinstance(page, bool) and sd is not None:
        out["partner_date_of_birth"] = _fmt(_dob_from_age(page, sd))

    # Months of unprotected intercourse (timed and frequent are one count in the encoding)
    months = [
        r[k]
        for k in ("num_months_timed_unprotected_intercourse", "num_months_frequent_unprotected_heterosexual_intercourse")
        if k in r and isinstance(r[k], (int, float)) and not isinstance(r[k], bool)
    ]
    if months:
        out["months_unprotected_intercourse"] = max(months)

    if "num_cycles_donor_insemination" in r:
        out["donor_insemination_cycles"] = r["num_cycles_donor_insemination"]

    # Semen analyses
    if "abnormal_semen_analyses" in r:
        out["semen_analyses"] = [{"date": d, "abnormal": True} for d in (r["abnormal_semen_analyses"] or [])]

    # FSH tests: ordered latest (date, time) first so the encoding's "most recent" pick is the latest test
    if "day_3_fsh_tests" in r:
        tests = list(r["day_3_fsh_tests"] or [])
        tests_sorted = sorted(
            tests,
            key=lambda t: (str(t[1]) if len(t) > 1 else "", str(t[2]) if len(t) > 2 else ""),
            reverse=True,
        )
        out["fsh_tests"] = [{"date": t[1], "value_miu_ml": t[0]} for t in tests_sorted]

    # Gender dysphoria (patient or partner; either satisfies the prong)
    gd = _yes_no(r.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if gd is True:
        out["patient_gender_dysphoria_diagnosis"] = True
    elif gd is False:
        out["patient_gender_dysphoria_diagnosis"] = False
        out["partner_gender_dysphoria_diagnosis"] = False

    # Documented condition and natural physiologic process
    cond = r.get("demonstrated_and_documented_condition_causing_infertility")
    if cond is not None:
        out["infertility_condition_documented"] = True
        if cond in _NATURAL:
            out["patient_infertility_due_to_natural_physiologic_process"] = True
        else:
            out["patient_infertility_due_to_natural_physiologic_process"] = False
            out["partner_infertility_due_to_natural_physiologic_process"] = False

    # Voluntary sterilization
    ps = _yes_no(r.get("patient_has_had_voluntary_sterilization"))
    if ps is not None:
        out["patient_voluntary_sterilization"] = ps
    pts = _yes_no(r.get("partner_has_had_voluntary_sterilization"))
    if pts is not None:
        out["partner_voluntary_sterilization"] = pts

    # Less costly covered treatment
    lc = _yes_no(r.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"))
    if lc is not None:
        out["less_costly_covered_treatment_could_achieve_pregnancy"] = lc

    return out
