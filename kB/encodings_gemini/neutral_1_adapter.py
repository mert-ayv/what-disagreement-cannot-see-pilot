import calendar
from datetime import date
from typing import Any, Dict

ASSUMED_MET = [
    "covered_role",
    "provider_is_infertility_specialist",
]


def _parse_date(d_str: str) -> date:
    parts = [int(p) for p in d_str.split("_")]
    return date(parts[0], parts[1], parts[2])


def _calculate_age(dob: date, ref_date: date) -> int:
    age = ref_date.year - dob.year
    if (ref_date.month, ref_date.day) < (dob.month, dob.day):
        age -= 1
    return age


def _add_months(d: date, m: int) -> date:
    year = d.year + (d.month - 1 + m) // 12
    month = (d.month - 1 + m) % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(d.day, max_day)
    return date(year, month, day)


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def _months_ago(test_date: date, service_date: date) -> int:
    if test_date >= service_date:
        return 0
    m = 0
    while _add_months(test_date, m) < service_date:
        m += 1
    return m


def adapt(ref_claim: dict) -> dict:
    res: Dict[str, Any] = {}

    # Assumed met requirements
    res["covered_role"] = "student"
    res["provider_is_infertility_specialist"] = True

    # Service type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            res["service_type"] = "intrauterine_insemination"
        elif st in [
            "ovulation_induction_cycle_with_menotropins",
            "ovulation_induction_with_menotropins",
        ]:
            res["service_type"] = "ovulation_induction_with_menotropins"
        else:
            res["service_type"] = "other"

    # Patient sex
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        res["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # Patient age
    dob = None
    service_date = None
    if "patient_dob" in ref_claim:
        dob = _parse_date(ref_claim["patient_dob"])
    if "date_service_received" in ref_claim:
        service_date = _parse_date(ref_claim["date_service_received"])

    if dob is not None and service_date is not None:
        res["patient_age"] = _calculate_age(dob, service_date)

    # Partner presence, sex, and age
    if "sex_of_patients_partner" in ref_claim:
        partner_sex_val = ref_claim["sex_of_patients_partner"]
        if partner_sex_val in ["male", "female"]:
            res["has_partner"] = True
            res["partner_sex"] = partner_sex_val
        elif partner_sex_val == "no_partner":
            res["has_partner"] = False

    if "age_of_patients_female_partner" in ref_claim:
        res["partner_age"] = ref_claim["age_of_patients_female_partner"]
        if "has_partner" not in res:
            res["has_partner"] = True
        if "partner_sex" not in res:
            res["partner_sex"] = "female"

    # Intercourse duration
    months_intercourse = ref_claim.get("num_months_timed_unprotected_intercourse")
    if months_intercourse is None:
        months_intercourse = ref_claim.get(
            "num_months_frequent_unprotected_heterosexual_intercourse"
        )
    if months_intercourse is not None:
        res["months_unprotected_timed_intercourse"] = months_intercourse

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        res["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # Voluntary sterilization
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    partner_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    partner_sex_val = ref_claim.get("sex_of_patients_partner")

    if p_ster == "yes" or partner_ster == "yes":
        res["patient_or_partner_voluntary_sterilization"] = True
    elif p_ster == "no":
        if partner_sex_val == "no_partner" or partner_ster == "no":
            res["patient_or_partner_voluntary_sterilization"] = False

    # Condition causing infertility
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        res["condition_causes_infertility_and_documented"] = True
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        if cond in [
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        ]:
            res["infertility_due_to_natural_physiologic_process"] = True
        elif cond == "other":
            res["infertility_due_to_natural_physiologic_process"] = False

    # Less costly treatment
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

    # Day 3 FSH tests
    if "day_3_fsh_tests" in ref_claim:
        tests = ref_claim["day_3_fsh_tests"]
        if tests:
            parsed_tests = []
            for item in tests:
                if isinstance(item, (list, tuple)):
                    lvl, d_str, t_str = item[0], item[1], item[2]
                elif isinstance(item, dict):
                    lvl = item.get("level")
                    d_str = item.get("date")
                    t_str = item.get("time")
                parsed_tests.append((d_str, t_str, _parse_date(d_str), float(lvl)))

            parsed_tests.sort(key=lambda x: (x[0], x[1]))
            most_recent = parsed_tests[-1]
            res["fsh_most_recent_value"] = most_recent[3]

            if service_date is not None:
                res["fsh_test_done_within_months"] = _months_ago(
                    most_recent[2], service_date
                )

            if dob is not None:
                dob_40 = _add_years(dob, 40)
                most_recent_ts = (most_recent[0], most_recent[1])
                prior_tests = [
                    t for t in parsed_tests if (t[0], t[1]) < most_recent_ts
                ]
                prior_tests_after_40 = [t for t in prior_tests if t[2] >= dob_40]
                res["fsh_all_after_age_40_under_19"] = all(
                    t[3] < 19.0 for t in prior_tests_after_40
                )

    # Abnormal semen analyses (for male without female partner)
    if "abnormal_semen_analyses" in ref_claim:
        dates_str = ref_claim["abnormal_semen_analyses"]
        if len(dates_str) >= 2:
            dates = sorted([_parse_date(d) for d in dates_str])
            res["male_without_female_partner_abnormal_semen_analyses"] = (
                dates[-1] - dates[0]
            ).days >= 14
        else:
            res["male_without_female_partner_abnormal_semen_analyses"] = False

    # Gender dysphoria
    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        val = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        if val == "yes":
            res["patient_or_partner_diagnosed_gender_dysphoria"] = True
        elif val == "no":
            res["patient_or_partner_diagnosed_gender_dysphoria"] = False

    return res
