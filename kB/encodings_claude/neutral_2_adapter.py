from datetime import date

ASSUMED_MET = ["billing_provider_is_infertility_specialist", "member_type"]

_SERVICE_MAP = {
    "intrauterine_insemination": "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins": "ovulation_induction_menotropins",
}

_NATURAL_CONDITIONS = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = value.split("_")
        return date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _sub_years(d, years):
    try:
        return d.replace(year=d.year - years)
    except ValueError:  # Feb 29 in a non-leap year
        return d.replace(year=d.year - years, month=2, day=28)


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _yes_no(value):
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def adapt(ref_claim: dict) -> dict:
    out = {}

    # Fields the reference interface does not cover: set to the value meaning the requirement is met.
    out["billing_provider_is_infertility_specialist"] = True
    out["member_type"] = "student"

    if "service_type" in ref_claim:
        out["service_type"] = _SERVICE_MAP.get(ref_claim["service_type"], "other")

    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]

    if "sex_of_patient_trying_to_conceive" in ref_claim:
        out["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    if "patient_dob" in ref_claim:
        out["patient_date_of_birth"] = ref_claim["patient_dob"]

    if "sex_of_patients_partner" in ref_claim:
        ps = ref_claim["sex_of_patients_partner"]
        out["partner_sex"] = "none" if ps == "no_partner" else ps

    # Partner date of birth derived from the female partner's age on the service date.
    if "age_of_patients_female_partner" in ref_claim:
        sd = _parse_date(ref_claim.get("date_service_received"))
        age = ref_claim["age_of_patients_female_partner"]
        if sd is not None and isinstance(age, int) and not isinstance(age, bool):
            out["partner_date_of_birth"] = _fmt(_sub_years(sd, age))

    # Condition: presence of the reference field means a condition was demonstrated and documented.
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        out["condition_demonstrated_to_cause_infertility"] = True
        out["condition_recognized_and_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in _NATURAL_CONDITIONS

    # Voluntary sterilization of patient or partner.
    pat = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    par = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if pat is True or par is True:
        out["voluntary_sterilization_patient_or_partner"] = True
    elif pat is False and par is False:
        out["voluntary_sterilization_patient_or_partner"] = False

    lc = _yes_no(ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"))
    if lc is not None:
        out["less_costly_covered_treatment_can_achieve_pregnancy"] = lc

    # Months of frequent, unprotected (timed) heterosexual intercourse.
    months = [
        ref_claim[k]
        for k in (
            "num_months_timed_unprotected_intercourse",
            "num_months_frequent_unprotected_heterosexual_intercourse",
        )
        if k in ref_claim
    ]
    if months:
        out["months_unprotected_intercourse"] = min(months)

    if "num_cycles_donor_insemination" in ref_claim:
        n = ref_claim["num_cycles_donor_insemination"]
        out["donor_insemination_cycles_total"] = n
        out["donor_insemination_cycles_not_plan_paid"] = n

    if "day_3_fsh_tests" in ref_claim:
        tests = []
        for t in ref_claim["day_3_fsh_tests"]:
            level, tdate, ttime = t[0], t[1], t[2] if len(t) > 2 else "00_00"
            tests.append((tdate, ttime, level))
        # Latest (date, time) first, so the most recent test on a date wins ties.
        tests.sort(key=lambda x: (x[0], x[1]), reverse=True)
        out["fsh_tests"] = [{"date": d, "value_miu_ml": float(v)} for d, _, v in tests]

    if "abnormal_semen_analyses" in ref_claim:
        out["semen_analyses"] = [
            {"date": d, "abnormal": True} for d in ref_claim["abnormal_semen_analyses"]
        ]

    gd = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if gd is not None:
        out["gender_dysphoria_diagnosis_patient_or_partner"] = gd

    return out
