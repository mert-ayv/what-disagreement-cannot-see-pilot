from datetime import date, datetime

ASSUMED_MET = ["provider_is_infertility_specialist", "coverage_role"]

_SERVICE_MAP = {
    "intrauterine_insemination": "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins": "ovulation_induction_menotropins",
}

_NATURAL_PROCESSES = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _parse(s):
    return datetime.strptime(s, "%Y_%m_%d").date()


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _years_before(d, years):
    try:
        return date(d.year - years, d.month, d.day)
    except ValueError:  # 29 February in a non-leap year
        return date(d.year - years, 2, 28)


def _yes_no(v):
    if v == "yes":
        return True
    if v == "no":
        return False
    return None


def adapt(ref_claim: dict) -> dict:
    out = {}

    # Facts not covered by the reference interface: set to the value meaning "met".
    out["provider_is_infertility_specialist"] = True
    out["coverage_role"] = "student"

    if "service_type" in ref_claim:
        out["service_type"] = _SERVICE_MAP.get(ref_claim["service_type"], "other")

    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]

    if "patient_dob" in ref_claim:
        out["patient_birth_date"] = ref_claim["patient_dob"]

    sex = ref_claim.get("sex_of_patient_trying_to_conceive")
    if sex in ("female", "male"):
        out["patient_sex"] = sex

    partner = ref_claim.get("sex_of_patients_partner")
    if partner in ("female", "male"):
        out["partner_sex"] = partner
    elif partner == "no_partner":
        out["partner_sex"] = "none"

    # Partner birth date derived from the partner's age on the service date.
    if "age_of_patients_female_partner" in ref_claim and "date_service_received" in ref_claim:
        service_date = _parse(ref_claim["date_service_received"])
        age = int(ref_claim["age_of_patients_female_partner"])
        out["partner_birth_date"] = _fmt(_years_before(service_date, age))

    gd = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if gd is not None:
        out["gender_dysphoria_diagnosis"] = gd

    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        out["condition_demonstrated_to_cause_infertility"] = True
        out["condition_recognized_and_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in _NATURAL_PROCESSES

    # Voluntary sterilization of patient or partner.
    p_ster = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    if partner == "no_partner":
        q_ster = False
    else:
        q_ster = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if p_ster is True or q_ster is True:
        out["voluntary_sterilization"] = True
    elif p_ster is False and q_ster is False:
        out["voluntary_sterilization"] = False

    less_costly = _yes_no(
        ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan")
    )
    if less_costly is not None:
        out["pregnancy_attainable_with_less_costly_covered_treatment"] = less_costly

    months = [
        ref_claim[k]
        for k in (
            "num_months_timed_unprotected_intercourse",
            "num_months_frequent_unprotected_heterosexual_intercourse",
        )
        if k in ref_claim and ref_claim[k] is not None
    ]
    if months:
        out["months_unprotected_intercourse"] = max(int(m) for m in months)

    if "num_cycles_donor_insemination" in ref_claim:
        out["donor_insemination_cycles_not_plan_paid"] = int(ref_claim["num_cycles_donor_insemination"])

    if "abnormal_semen_analyses" in ref_claim:
        out["abnormal_semen_analysis_dates"] = list(ref_claim["abnormal_semen_analyses"])

    if "day_3_fsh_tests" in ref_claim:
        tests = []
        for t in ref_claim["day_3_fsh_tests"]:
            level, d = t[0], t[1]
            tests.append({"date": d, "value_miu_ml": float(level)})
        out["fsh_tests"] = tests

    return out
