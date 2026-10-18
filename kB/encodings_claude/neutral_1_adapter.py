import calendar
import datetime

ASSUMED_MET = [
    "rendering_provider_is_infertility_specialist",
    "patient_coverage_status",
]

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
    parts = value.split("_")
    if len(parts) != 3:
        return None
    try:
        return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _yes_no(value):
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def _birth_date_for_age(age, on):
    # A birth date such that the person is exactly `age` on date `on`.
    year = on.year - age
    day = min(on.day, calendar.monthrange(year, on.month)[1])
    return datetime.date(year, on.month, day)


def adapt(ref_claim: dict) -> dict:
    out = {}

    # Fields the reference interface does not cover: set to "requirement met".
    out["rendering_provider_is_infertility_specialist"] = True
    out["patient_coverage_status"] = "student"

    if "service_type" in ref_claim:
        out["service_type"] = _SERVICE_MAP.get(ref_claim["service_type"], "other")

    if "sex_of_patient_trying_to_conceive" in ref_claim:
        out["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    if "sex_of_patients_partner" in ref_claim:
        p = ref_claim["sex_of_patients_partner"]
        out["partner_sex"] = "none" if p == "no_partner" else p

    if "patient_dob" in ref_claim:
        out["patient_birth_date"] = ref_claim["patient_dob"]

    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]

    # Partner birth date derived from the female partner's age on the service date.
    partner_age = ref_claim.get("age_of_patients_female_partner")
    service_date = _parse_date(ref_claim.get("date_service_received"))
    if isinstance(partner_age, int) and not isinstance(partner_age, bool) and service_date:
        out["partner_birth_date"] = _fmt(_birth_date_for_age(partner_age, service_date))

    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        out["infertility_condition_demonstrated"] = True
        out["condition_recognized_and_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in _NATURAL_CONDITIONS

    pat_ster = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    par_ster = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if pat_ster is True or par_ster is True:
        out["voluntary_sterilization_patient_or_partner"] = True
    elif pat_ster is False and par_ster is False:
        out["voluntary_sterilization_patient_or_partner"] = False

    less_costly = _yes_no(
        ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan")
    )
    if less_costly is not None:
        out["pregnancy_attainable_through_less_costly_covered_treatment"] = less_costly

    dysphoria = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if dysphoria is not None:
        out["gender_dysphoria_diagnosis_patient_or_partner"] = dysphoria

    # The encoding uses one month count for both the timed (table) and the frequent
    # heterosexual (glossary) intercourse requirement; when both are known, the smaller
    # count is used so that both requirements must hold.
    month_values = [
        ref_claim[k]
        for k in (
            "num_months_timed_unprotected_intercourse",
            "num_months_frequent_unprotected_heterosexual_intercourse",
        )
        if k in ref_claim
    ]
    if month_values:
        out["months_unprotected_intercourse_without_pregnancy"] = min(month_values)

    if "num_cycles_donor_insemination" in ref_claim:
        cycles = ref_claim["num_cycles_donor_insemination"]
        out["donor_insemination_cycles_not_plan_paid_without_pregnancy"] = cycles
        out["donor_insemination_cycles_without_pregnancy"] = cycles

    if "abnormal_semen_analyses" in ref_claim:
        out["abnormal_semen_analysis_dates"] = list(ref_claim["abnormal_semen_analyses"])

    if "day_3_fsh_tests" in ref_claim:
        tests = []
        for t in ref_claim["day_3_fsh_tests"]:
            level, date, time = t[0], t[1], t[2]
            tests.append((date, time if isinstance(time, str) else "", level))
        # Latest (date, time) first, so the encoding's first-maximum-by-date pick is
        # the most recent test when several share a date.
        tests.sort(key=lambda x: (x[0], x[1]), reverse=True)
        out["fsh_tests"] = [
            {"date": date, "value_miu_per_ml": float(level)} for date, _time, level in tests
        ]

    return out
