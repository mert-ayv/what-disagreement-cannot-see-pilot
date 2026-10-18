import calendar
from datetime import date

ASSUMED_MET = [
    "patient_is_covered_student_or_dependent_partner",
    "provider_is_infertility_specialist",
]


def _subtract_months(d: date, months: int) -> date:
    year = d.year - (months // 12)
    month = d.month - (months % 12)
    if month <= 0:
        month += 12
        year -= 1
    max_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, max_day))


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def _calculate_age(dob: date, svc: date) -> int:
    return svc.year - dob.year - ((svc.month, svc.day) < (dob.month, dob.day))


def adapt(ref_claim: dict) -> dict:
    res = {}

    # Fields assumed to be met
    res["patient_is_covered_student_or_dependent_partner"] = True
    res["provider_is_infertility_specialist"] = True

    # Service type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            res["service_type"] = "intrauterine_insemination"
        elif st in (
            "ovulation_induction_cycle_with_menotropins",
            "ovulation_induction_with_menotropins",
        ):
            res["service_type"] = "ovulation_induction_with_menotropins"
        else:
            res["service_type"] = "other"

    # Patient sex
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        res["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # Partner sex and partner age
    has_no_partner = False
    if "sex_of_patients_partner" in ref_claim:
        p_sex = ref_claim["sex_of_patients_partner"]
        if p_sex == "no_partner":
            res["partner_sex"] = "none"
            res["partner_age"] = None
            has_no_partner = True
        elif p_sex in ("male", "female"):
            res["partner_sex"] = p_sex

    if "age_of_patients_female_partner" in ref_claim:
        res["partner_age"] = ref_claim["age_of_patients_female_partner"]

    # Patient age calculation
    patient_dob = None
    svc_date = None
    patient_age = None
    if "patient_dob" in ref_claim:
        patient_dob = date.fromisoformat(ref_claim["patient_dob"].replace("_", "-"))
    if "date_service_received" in ref_claim:
        svc_date = date.fromisoformat(
            ref_claim["date_service_received"].replace("_", "-")
        )

    if patient_dob and svc_date:
        patient_age = _calculate_age(patient_dob, svc_date)
        res["patient_age"] = patient_age

    # Condition causing infertility & natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        res["condition_causing_infertility_documented"] = True
        natural_conditions = {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }
        res["infertility_due_to_natural_physiologic_process"] = (
            cond in natural_conditions
        )

    # Prior voluntary sterilization
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    pt_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    if p_ster == "yes" or pt_ster == "yes":
        res["has_prior_voluntary_sterilization"] = True
    elif p_ster == "no" and (pt_ster == "no" or has_no_partner):
        res["has_prior_voluntary_sterilization"] = False

    # Less costly covered treatment
    if (
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        in ref_claim
    ):
        val = ref_claim[
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        ]
        if val == "yes":
            res["pregnancy_attainable_through_less_costly_covered_treatment"] = True
        elif val == "no":
            res["pregnancy_attainable_through_less_costly_covered_treatment"] = False

    # Gender dysphoria diagnosis
    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        gd = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        if gd == "yes":
            res["has_gender_dysphoria_diagnosis"] = True
        elif gd == "no":
            res["has_gender_dysphoria_diagnosis"] = False

    # Months of unprotected intercourse
    intercourse_months = [
        ref_claim[k]
        for k in (
            "num_months_frequent_unprotected_heterosexual_intercourse",
            "num_months_timed_unprotected_intercourse",
        )
        if k in ref_claim
    ]
    if intercourse_months:
        res["months_of_unprotected_timed_intercourse"] = max(intercourse_months)

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        res["donor_insemination_cycles_self_paid"] = ref_claim[
            "num_cycles_donor_insemination"
        ]

    # Abnormal semen analyses (for male without female partner)
    if "abnormal_semen_analyses" in ref_claim:
        raw_dates = ref_claim["abnormal_semen_analyses"]
        if len(raw_dates) < 2:
            res["male_has_two_abnormal_semen_analyses_two_weeks_apart"] = False
        else:
            dates = sorted(
                date.fromisoformat(d.replace("_", "-")) for d in raw_dates
            )
            res["male_has_two_abnormal_semen_analyses_two_weeks_apart"] = (
                dates[-1] - dates[0]
            ).days >= 14

    # FSH tests (for female patients)
    if "day_3_fsh_tests" in ref_claim:
        raw_tests = ref_claim["day_3_fsh_tests"]
        parsed_tests = []
        for t in raw_tests:
            if isinstance(t, dict):
                lvl = t["level"]
                d = date.fromisoformat(t["date"].replace("_", "-"))
                tm = t.get("time", "00_00").replace("_", ":")
            else:
                lvl = t[0]
                d = date.fromisoformat(t[1].replace("_", "-"))
                tm = t[2].replace("_", ":") if len(t) > 2 else "00:00"
            parsed_tests.append({"level": lvl, "date": d, "time": tm})

        if parsed_tests:
            parsed_tests.sort(key=lambda x: (x["date"], x["time"]))
            res["most_recent_fsh_level"] = float(parsed_tests[-1]["level"])

        if svc_date and patient_age is not None:
            if patient_age < 35:
                cutoff = _subtract_months(svc_date, 12)
            else:
                cutoff = _subtract_months(svc_date, 6)
            res["fsh_test_done_within_required_timeframe"] = any(
                cutoff <= t["date"] <= svc_date for t in parsed_tests
            )

        if patient_age is not None and patient_age >= 40 and patient_dob:
            bday_40 = _add_years(patient_dob, 40)
            tests_after_40 = [t for t in parsed_tests if t["date"] >= bday_40]
            res["all_fsh_tests_after_age_40_under_19"] = all(
                t["level"] < 19 for t in tests_after_40
            )

    return res
