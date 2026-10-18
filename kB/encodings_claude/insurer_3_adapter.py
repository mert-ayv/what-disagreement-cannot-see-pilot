from datetime import date

ASSUMED_MET = [
    "provider_is_infertility_specialist",
    "member_status",
    "failed_to_become_pregnant",
    "condition_recognized_by_physician_or_specialist",
]

_NATURAL_PROCESSES = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _parse(s):
    y, m, d = (int(p) for p in s.split("_"))
    return date(y, m, d)


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _years_before(d, years):
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        # Feb 29 on a non-leap target year: Feb 28 keeps the age at d equal to `years`.
        return date(d.year - years, 2, 28)


def _yes_no(value):
    if value == "yes":
        return True
    if value == "no":
        return False
    return None


def adapt(ref_claim: dict) -> dict:
    c = {}

    # Facts the reference interface does not cover: set to the value meaning the requirement is met.
    c["provider_is_infertility_specialist"] = True
    c["member_status"] = "student"
    c["failed_to_become_pregnant"] = True
    c["condition_recognized_by_physician_or_specialist"] = True

    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            c["service_type"] = "intrauterine_insemination"
        elif st == "ovulation_induction_cycle_with_menotropins":
            c["service_type"] = "ovulation_induction_menotropins"
        else:
            c["service_type"] = "other"

    if "date_service_received" in ref_claim:
        c["service_date"] = ref_claim["date_service_received"]

    if "patient_dob" in ref_claim:
        c["patient_birth_date"] = ref_claim["patient_dob"]

    sex = ref_claim.get("sex_of_patient_trying_to_conceive")
    if sex in ("female", "male"):
        c["patient_sex"] = sex

    partner = ref_claim.get("sex_of_patients_partner")
    if sex in ("female", "male") and partner in ("male", "female", "no_partner"):
        opposite = "male" if sex == "female" else "female"
        c["has_partner"] = partner == opposite

    if (partner == "female" and "age_of_patients_female_partner" in ref_claim
            and "date_service_received" in ref_claim):
        service = _parse(ref_claim["date_service_received"])
        age = int(ref_claim["age_of_patients_female_partner"])
        c["partner_birth_date"] = _fmt(_years_before(service, age))

    # Only months that were both timed and frequent count; the overlap is bounded by the smaller count.
    if ("num_months_timed_unprotected_intercourse" in ref_claim
            and "num_months_frequent_unprotected_heterosexual_intercourse" in ref_claim):
        c["months_frequent_unprotected_timed_intercourse"] = min(
            int(ref_claim["num_months_timed_unprotected_intercourse"]),
            int(ref_claim["num_months_frequent_unprotected_heterosexual_intercourse"]),
        )

    if "num_cycles_donor_insemination" in ref_claim:
        c["donor_insemination_cycles_self_paid"] = int(ref_claim["num_cycles_donor_insemination"])

    if "abnormal_semen_analyses" in ref_claim:
        c["semen_analyses"] = [{"date": d, "abnormal": True} for d in ref_claim["abnormal_semen_analyses"]]

    gd = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if gd is not None:
        c["gender_dysphoria_diagnosis"] = gd

    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        c["condition_demonstrated_to_cause_infertility"] = True
        c["condition_documented_in_medical_records"] = True
        c["infertility_due_to_natural_physiologic_process"] = cond in _NATURAL_PROCESSES

    ps = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    if ps is not None:
        c["patient_voluntary_sterilization"] = ps

    pps = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if pps is not None:
        c["partner_voluntary_sterilization"] = pps

    lc = _yes_no(ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"))
    if lc is not None:
        c["pregnancy_attainable_by_less_costly_covered_treatment"] = lc

    if "day_3_fsh_tests" in ref_claim:
        c["fsh_tests"] = [
            {"date": t[1], "value_miu_ml": float(t[0]), "unmedicated_day3": True}
            for t in ref_claim["day_3_fsh_tests"]
        ]

    return c
