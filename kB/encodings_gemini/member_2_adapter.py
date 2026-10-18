import calendar
from datetime import date, datetime
from typing import Any, Dict

ASSUMED_MET = ["covered_person_role", "provider_is_infertility_specialist"]


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(d.day, max_day)
    return date(year, month, day)


def adapt(ref_claim: dict) -> dict:
    adapted: Dict[str, Any] = {}

    # Assumed met fields
    adapted["covered_person_role"] = "student"
    adapted["provider_is_infertility_specialist"] = True

    # Service type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            adapted["service_type"] = "intrauterine_insemination"
        elif st in (
            "ovulation_induction_cycle_with_menotropins",
            "ovulation_induction_with_menotropins",
        ):
            adapted["service_type"] = "ovulation_induction_with_menotropins"
        else:
            adapted["service_type"] = "other"

    # Infertility condition and natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim[
            "demonstrated_and_documented_condition_causing_infertility"
        ]
        adapted["has_documented_infertility_condition"] = True
        if cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        ):
            adapted["infertility_due_to_natural_physiologic_process"] = True
        elif cond == "other":
            adapted["infertility_due_to_natural_physiologic_process"] = False

    # Voluntary sterilization history
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    part_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    no_partner = ref_claim.get("sex_of_patients_partner") == "no_partner"

    if p_ster == "yes" or part_ster == "yes":
        adapted["voluntary_sterilization_history"] = True
    elif p_ster == "no" and (part_ster == "no" or no_partner):
        adapted["voluntary_sterilization_history"] = False

    # Less costly treatment
    if (
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        in ref_claim
    ):
        adapted[
            "successful_pregnancy_attainable_through_less_costly_covered_treatment"
        ] = (
            ref_claim[
                "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
            ]
            == "yes"
        )

    # Patient demographics
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        adapted["patient_gender"] = ref_claim[
            "sex_of_patient_trying_to_conceive"
        ]

    dob: date | None = None
    if "patient_dob" in ref_claim:
        dob = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()

    dos: date | None = None
    if "date_service_received" in ref_claim:
        dos = datetime.strptime(
            ref_claim["date_service_received"], "%Y_%m_%d"
        ).date()

    if dob is not None and dos is not None:
        patient_age = (
            dos.year - dob.year - ((dos.month, dos.day) < (dob.month, dob.day))
        )
        adapted["patient_age"] = patient_age
    else:
        patient_age = None

    # Partner demographics
    if "sex_of_patients_partner" in ref_claim:
        part_sex = ref_claim["sex_of_patients_partner"]
        if part_sex == "no_partner":
            adapted["partner_gender"] = None
        elif part_sex in ("female", "male"):
            adapted["partner_gender"] = part_sex

    if "age_of_patients_female_partner" in ref_claim:
        adapted["partner_age"] = ref_claim["age_of_patients_female_partner"]

    # Gender dysphoria diagnosis
    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        adapted["has_gender_dysphoria_diagnosis"] = (
            ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
            == "yes"
        )

    # Months trying / intercourse
    intercourse_vals = []
    if "num_months_timed_unprotected_intercourse" in ref_claim:
        intercourse_vals.append(
            ref_claim["num_months_timed_unprotected_intercourse"]
        )
    if "num_months_frequent_unprotected_heterosexual_intercourse" in ref_claim:
        intercourse_vals.append(
            ref_claim["num_months_frequent_unprotected_heterosexual_intercourse"]
        )
    if intercourse_vals:
        adapted["months_unprotected_intercourse"] = max(intercourse_vals)

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        adapted["donor_insemination_cycles"] = ref_claim[
            "num_cycles_donor_insemination"
        ]

    # Abnormal semen analyses (male without female partner)
    if "abnormal_semen_analyses" in ref_claim:
        raw_dates = ref_claim["abnormal_semen_analyses"]
        parsed_dates = sorted(
            [datetime.strptime(d, "%Y_%m_%d").date() for d in raw_dates]
        )
        count = 0
        last_d = None
        for d in parsed_dates:
            if last_d is None or (d - last_d).days >= 14:
                count += 1
                last_d = d
        adapted["male_abnormal_semen_analyses_count"] = count

    # Day 3 FSH tests
    if "day_3_fsh_tests" in ref_claim:
        fsh_tests = ref_claim["day_3_fsh_tests"]
        if not fsh_tests:
            adapted["fsh_test_performed_within_months"] = None
            adapted["fsh_most_recent_result"] = None
            adapted["fsh_all_tests_after_40_under_19"] = None
        else:

            def parse_fsh_dt(item):
                lvl, d_str, t_str = item
                return datetime.strptime(
                    f"{d_str}_{t_str}", "%Y_%m_%d_%H_%M"
                )

            sorted_tests = sorted(fsh_tests, key=parse_fsh_dt)
            most_recent_test = sorted_tests[-1]
            most_recent_level = float(most_recent_test[0])
            adapted["fsh_most_recent_result"] = most_recent_level

            most_recent_date = datetime.strptime(
                most_recent_test[1], "%Y_%m_%d"
            ).date()
            if dos is not None:
                m = 0
                while _add_months(most_recent_date, m) < dos:
                    m += 1
                adapted["fsh_test_performed_within_months"] = m

            patient_gender = adapted.get("patient_gender")
            if (
                patient_gender == "female"
                and patient_age is not None
                and patient_age >= 40
                and dob is not None
            ):
                tests_after_40 = []
                for lvl, d_str, _ in sorted_tests:
                    t_d = datetime.strptime(d_str, "%Y_%m_%d").date()
                    age_at_t = (
                        t_d.year
                        - dob.year
                        - ((t_d.month, t_d.day) < (dob.month, dob.day))
                    )
                    if age_at_t >= 40:
                        tests_after_40.append(lvl)

                all_after_40_under_19 = (
                    all(lvl < 19 for lvl in tests_after_40)
                    if tests_after_40
                    else (most_recent_level < 19)
                )
                adapted["fsh_all_tests_after_40_under_19"] = (
                    all_after_40_under_19
                )

    return adapted
