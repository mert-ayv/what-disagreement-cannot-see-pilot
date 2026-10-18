import datetime

ASSUMED_MET = ["rendered_by_infertility_specialist", "member_status"]

_SERVICE_MAP = {
    "intrauterine_insemination": "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins": "ovulation_induction_menotropins",
}

_PARTNER_MAP = {"male": "male", "female": "female", "no_partner": "none"}

_NATURAL = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _yes_no(value):
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def _parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = (int(p) for p in value.split("_"))
        return datetime.date(y, m, d)
    except (ValueError, TypeError):
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _birth_date_for_age(on, age):
    # A birth date such that the age on `on` is exactly `age`.
    try:
        return on.replace(year=on.year - age)
    except ValueError:  # 29 February
        return datetime.date(on.year - age, 2, 28)


def adapt(ref_claim: dict) -> dict:
    claim = {}

    # Facts the reference interface does not cover: set to "requirement met".
    claim["rendered_by_infertility_specialist"] = True
    claim["member_status"] = "student"

    if "service_type" in ref_claim:
        claim["service_type"] = _SERVICE_MAP.get(ref_claim["service_type"], "other")

    if "date_service_received" in ref_claim:
        claim["service_date"] = ref_claim["date_service_received"]

    if "sex_of_patient_trying_to_conceive" in ref_claim:
        claim["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    if "patient_dob" in ref_claim:
        claim["patient_birth_date"] = ref_claim["patient_dob"]

    if "sex_of_patients_partner" in ref_claim:
        mapped = _PARTNER_MAP.get(ref_claim["sex_of_patients_partner"])
        if mapped is not None:
            claim["partner_sex"] = mapped

    # Derive a partner birth date from the female partner's age at the service date.
    if "age_of_patients_female_partner" in ref_claim:
        service = _parse_date(ref_claim.get("date_service_received"))
        age = ref_claim["age_of_patients_female_partner"]
        if service is not None and isinstance(age, int) and not isinstance(age, bool):
            claim["partner_birth_date"] = _fmt(_birth_date_for_age(service, age))

    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        condition = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        claim["infertility_condition_documented"] = True
        claim["infertility_due_to_natural_physiologic_process"] = condition in _NATURAL

    for ref_key, key in (
        ("patient_or_partner_diagnosed_with_gender_dysphoria", "gender_dysphoria_diagnosed"),
        ("patient_has_had_voluntary_sterilization", "patient_voluntary_sterilization"),
        ("partner_has_had_voluntary_sterilization", "partner_voluntary_sterilization"),
        ("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan",
         "less_costly_covered_treatment_would_succeed"),
    ):
        if ref_key in ref_claim:
            value = _yes_no(ref_claim[ref_key])
            if value is not None:
                claim[key] = value

    # Timed or frequent unprotected intercourse both count; use the larger count.
    months = [
        ref_claim[k]
        for k in ("num_months_timed_unprotected_intercourse",
                  "num_months_frequent_unprotected_heterosexual_intercourse")
        if k in ref_claim
    ]
    if months:
        claim["months_unprotected_intercourse"] = float(max(months))

    if "num_cycles_donor_insemination" in ref_claim:
        claim["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    if "abnormal_semen_analyses" in ref_claim:
        claim["semen_analyses"] = [
            {"date": d, "abnormal": True} for d in ref_claim["abnormal_semen_analyses"]
        ]

    if "day_3_fsh_tests" in ref_claim:
        tests = []
        for test in ref_claim["day_3_fsh_tests"]:
            level, date = test[0], test[1]
            tests.append({"date": date, "value_miu_ml": float(level), "unmedicated_day3": True})
        claim["fsh_tests"] = tests

    return claim
