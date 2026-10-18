from datetime import date

ASSUMED_MET = ["billed_by_infertility_specialist", "member_status"]

_SERVICE_MAP = {
    "intrauterine_insemination": "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins": "ovulation_induction_menotropins",
}

_PARTNER_SEX_MAP = {"male": "male", "female": "female", "no_partner": "none"}

_NATURAL_CONDITIONS = {
    "natural_menopause": "female",
    "natural_perimenopause": "female",
    "natural_male_reproductive_aging": "male",
    "other_natural_physiologic_process": None,
}


def _parse_date(value):
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


def adapt(ref_claim: dict) -> dict:
    out = {}

    # Service type
    if "service_type" in ref_claim:
        out["service_type"] = _SERVICE_MAP.get(ref_claim["service_type"], "other")

    # Facts outside the reference interface: set to the value meaning the requirement is met.
    out["billed_by_infertility_specialist"] = True
    out["member_status"] = "student"

    # Dates
    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]
    if "patient_dob" in ref_claim:
        out["patient_birth_date"] = ref_claim["patient_dob"]

    # Sexes
    patient_sex = ref_claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex in ("female", "male"):
        out["patient_sex"] = patient_sex
    elif patient_sex is not None:
        out["patient_sex"] = "other"

    partner_sex_ref = ref_claim.get("sex_of_patients_partner")
    if partner_sex_ref is not None:
        out["partner_sex"] = _PARTNER_SEX_MAP.get(partner_sex_ref, "other")
    partner_sex = out.get("partner_sex")

    # Partner birth date derived from the female partner's age on the service date.
    partner_age = ref_claim.get("age_of_patients_female_partner")
    service = _parse_date(ref_claim.get("date_service_received"))
    if isinstance(partner_age, int) and not isinstance(partner_age, bool) and service is not None:
        try:
            birth = service.replace(year=service.year - partner_age)
        except ValueError:  # 29 February
            birth = service.replace(year=service.year - partner_age, day=28)
        out["partner_birth_date"] = _fmt(birth)

    # Documented condition and natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        condition = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        out["infertility_condition_documented"] = True
        if condition in _NATURAL_CONDITIONS:
            condition_sex = _NATURAL_CONDITIONS[condition]
            if (
                condition_sex is not None
                and patient_sex != condition_sex
                and partner_sex == condition_sex
            ):
                out["partner_infertility_natural_process"] = True
            else:
                out["patient_infertility_natural_process"] = True
        else:
            out["patient_infertility_natural_process"] = False
            out["partner_infertility_natural_process"] = False

    # Sterilization
    v = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    if v is not None:
        out["patient_voluntary_sterilization"] = v
    v = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if v is not None:
        out["partner_voluntary_sterilization"] = v

    # Less costly treatment
    v = _yes_no(ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"))
    if v is not None:
        out["less_costly_covered_treatment_could_succeed"] = v

    # Months of unprotected intercourse (timed and frequent are one count in the encoding)
    months = [
        ref_claim[k]
        for k in (
            "num_months_timed_unprotected_intercourse",
            "num_months_frequent_unprotected_heterosexual_intercourse",
        )
        if isinstance(ref_claim.get(k), int) and not isinstance(ref_claim.get(k), bool)
    ]
    if months:
        out["months_unprotected_intercourse"] = max(months)

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        out["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # FSH tests (all reference tests are unmedicated day 3 tests); order by date and time
    if "day_3_fsh_tests" in ref_claim:
        tests = []
        for t in ref_claim["day_3_fsh_tests"] or []:
            try:
                level, d, tm = t[0], t[1], t[2]
            except (TypeError, IndexError, KeyError):
                continue
            tests.append((str(d), str(tm), level))
        tests.sort(key=lambda x: (x[0], x[1]))
        out["fsh_tests"] = [
            {"date": d, "value_miu_ml": float(level), "unmedicated_day3": True}
            for d, _, level in tests
        ]

    # Semen analyses (reference lists abnormal analyses only)
    if "abnormal_semen_analyses" in ref_claim:
        out["semen_analyses"] = [
            {"date": d, "abnormal": True} for d in (ref_claim["abnormal_semen_analyses"] or [])
        ]

    # Gender dysphoria (patient or partner)
    v = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if v is True:
        out["patient_gender_dysphoria_diagnosis"] = True
    elif v is False:
        out["patient_gender_dysphoria_diagnosis"] = False
        out["partner_gender_dysphoria_diagnosis"] = False

    return out
