from datetime import datetime
from typing import Any, Dict

ASSUMED_MET = [
    "provider_is_infertility_specialist",
    "patient_is_covered_student_or_partner",
]


def adapt(ref_claim: dict) -> dict:
    res: Dict[str, Any] = {}

    # Assumed met fields
    res["provider_is_infertility_specialist"] = True
    res["patient_is_covered_student_or_partner"] = True

    # service_name
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "ovulation_induction_cycle_with_menotropins":
            res["service_name"] = "ovulation_induction_with_menotropins"
        elif st == "intrauterine_insemination":
            res["service_name"] = "intrauterine_insemination"
        else:
            res["service_name"] = "other"

    # has_documented_condition_causing_infertility & infertility_due_to_natural_physiologic_process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        res["has_documented_condition_causing_infertility"] = True
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        if cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        ):
            res["infertility_due_to_natural_physiologic_process"] = True
        else:
            res["infertility_due_to_natural_physiologic_process"] = False

    # has_prior_voluntary_sterilization
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    partner_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    partner_sex = ref_claim.get("sex_of_patients_partner")

    if p_ster == "yes" or partner_ster == "yes":
        res["has_prior_voluntary_sterilization"] = True
    elif p_ster == "no":
        if partner_ster == "no" or partner_sex == "no_partner":
            res["has_prior_voluntary_sterilization"] = False

    # pregnancy_attainable_through_less_costly_treatment
    if (
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        in ref_claim
    ):
        res["pregnancy_attainable_through_less_costly_treatment"] = (
            ref_claim[
                "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
            ]
            == "yes"
        )

    # patient_gender
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        res["patient_gender"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # patient_age
    if "patient_dob" in ref_claim and "date_service_received" in ref_claim:
        d_birth = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()
        d_service = datetime.strptime(
            ref_claim["date_service_received"], "%Y_%m_%d"
        ).date()
        res["patient_age"] = (
            d_service.year
            - d_birth.year
            - ((d_service.month, d_service.day) < (d_birth.month, d_birth.day))
        )

    # partner_gender
    if "sex_of_patients_partner" in ref_claim:
        p_gender = ref_claim["sex_of_patients_partner"]
        if p_gender == "no_partner":
            res["partner_gender"] = None
        else:
            res["partner_gender"] = p_gender

    # partner_age
    if "age_of_patients_female_partner" in ref_claim:
        res["partner_age"] = ref_claim["age_of_patients_female_partner"]
    elif ref_claim.get("sex_of_patients_partner") == "no_partner":
        res["partner_age"] = None

    # patient_or_partner_diagnosed_with_gender_dysphoria
    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        res["patient_or_partner_diagnosed_with_gender_dysphoria"] = (
            ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"] == "yes"
        )

    # months_of_unprotected_timed_intercourse
    m_frequent = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    m_timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    if m_frequent is not None and m_timed is not None:
        res["months_of_unprotected_timed_intercourse"] = max(m_frequent, m_timed)
    elif m_frequent is not None:
        res["months_of_unprotected_timed_intercourse"] = m_frequent
    elif m_timed is not None:
        res["months_of_unprotected_timed_intercourse"] = m_timed

    # donor_insemination_cycles
    if "num_cycles_donor_insemination" in ref_claim:
        res["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # FSH tests
    if "day_3_fsh_tests" in ref_claim:
        tests = ref_claim["day_3_fsh_tests"]
        if not tests:
            res["fsh_test_months_ago"] = None
            res["most_recent_fsh_level"] = None
            if "patient_age" in res and res.get("patient_gender") == "female":
                if res["patient_age"] >= 40:
                    res["has_fsh_level_19_or_greater_after_age_40"] = False
                else:
                    res["has_fsh_level_19_or_greater_after_age_40"] = None
            else:
                res["has_fsh_level_19_or_greater_after_age_40"] = None
        else:
            def parse_test(item):
                if isinstance(item, dict):
                    return item["level"], item["date"], item.get("time", "00_00")
                return item[0], item[1], item[2] if len(item) > 2 else "00_00"

            sorted_tests = sorted(tests, key=lambda x: (parse_test(x)[1], parse_test(x)[2]))
            most_recent = sorted_tests[-1]
            rec_lvl, rec_date_str, _ = parse_test(most_recent)
            res["most_recent_fsh_level"] = float(rec_lvl)

            if "date_service_received" in ref_claim:
                d_service = datetime.strptime(
                    ref_claim["date_service_received"], "%Y_%m_%d"
                ).date()
                d_test = datetime.strptime(rec_date_str, "%Y_%m_%d").date()
                months = (d_service.year - d_test.year) * 12 + (d_service.month - d_test.month)
                if d_service.day < d_test.day:
                    months -= 1
                res["fsh_test_months_ago"] = max(0, months)

            if "patient_dob" in ref_claim and "patient_age" in res:
                if res.get("patient_gender") == "female" and res["patient_age"] >= 40:
                    d_birth = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()
                    any_ge_19 = False
                    for item in tests:
                        lvl, d_str, _ = parse_test(item)
                        d_item = datetime.strptime(d_str, "%Y_%m_%d").date()
                        age_at_test = (
                            d_item.year
                            - d_birth.year
                            - ((d_item.month, d_item.day) < (d_birth.month, d_birth.day))
                        )
                        if age_at_test >= 40 and lvl >= 19:
                            any_ge_19 = True
                            break
                    res["has_fsh_level_19_or_greater_after_age_40"] = any_ge_19
                else:
                    res["has_fsh_level_19_or_greater_after_age_40"] = None

    return res
