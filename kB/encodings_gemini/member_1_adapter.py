from datetime import datetime

ASSUMED_MET = [
    "patient_is_covered_student_or_partner",
    "provider_is_infertility_specialist",
]


def adapt(ref_claim: dict) -> dict:
    res = {
        "patient_is_covered_student_or_partner": True,
        "provider_is_infertility_specialist": True,
    }

    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "ovulation_induction_cycle_with_menotropins":
            res["service_type"] = "ovulation_induction_with_menotropins"
        elif st == "intrauterine_insemination":
            res["service_type"] = "intrauterine_insemination"
        else:
            res["service_type"] = "other"

    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        res["has_documented_infertility_condition"] = True
        if cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        ):
            res["infertility_due_to_natural_physiologic_process"] = True
        elif cond == "other":
            res["infertility_due_to_natural_physiologic_process"] = False
    elif ref_claim.get("abnormal_semen_analyses"):
        res["has_documented_infertility_condition"] = True
        res["infertility_due_to_natural_physiologic_process"] = False
    elif ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes":
        res["has_documented_infertility_condition"] = True
        res["infertility_due_to_natural_physiologic_process"] = False

    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    part_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    partner_sex = ref_claim.get("sex_of_patients_partner")

    if p_ster == "yes" or part_ster == "yes":
        res["has_voluntary_sterilization"] = True
    elif p_ster == "no":
        if partner_sex == "no_partner" or part_ster == "no":
            res["has_voluntary_sterilization"] = False

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

    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        val = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        if val == "yes":
            res["has_gender_dysphoria_diagnosis"] = True
        elif val == "no":
            res["has_gender_dysphoria_diagnosis"] = False

    if "sex_of_patient_trying_to_conceive" in ref_claim:
        sex = ref_claim["sex_of_patient_trying_to_conceive"]
        if sex in ("female", "male"):
            res["patient_gender"] = sex

    if "patient_dob" in ref_claim and "date_service_received" in ref_claim:
        dob = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()
        dos = datetime.strptime(ref_claim["date_service_received"], "%Y_%m_%d").date()
        age = dos.year - dob.year - ((dos.month, dos.day) < (dob.month, dob.day))
        res["patient_age"] = age

    if "sex_of_patients_partner" in ref_claim:
        p_sex = ref_claim["sex_of_patients_partner"]
        if p_sex in ("female", "male"):
            res["partner_gender"] = p_sex
        elif p_sex == "no_partner":
            res["partner_gender"] = "none"

    if "age_of_patients_female_partner" in ref_claim:
        res["partner_age"] = ref_claim["age_of_patients_female_partner"]

    intercourse_vals = []
    if "num_months_frequent_unprotected_heterosexual_intercourse" in ref_claim:
        intercourse_vals.append(
            ref_claim["num_months_frequent_unprotected_heterosexual_intercourse"]
        )
    if "num_months_timed_unprotected_intercourse" in ref_claim:
        intercourse_vals.append(
            ref_claim["num_months_timed_unprotected_intercourse"]
        )
    if intercourse_vals:
        res["months_unprotected_timed_intercourse"] = max(intercourse_vals)

    if "num_cycles_donor_insemination" in ref_claim:
        res["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    if "day_3_fsh_tests" in ref_claim:
        tests = ref_claim["day_3_fsh_tests"]
        if tests:
            sorted_tests = sorted(tests, key=lambda t: (t[1], t[2]))
            most_recent = sorted_tests[-1]
            res["most_recent_fsh_level"] = float(most_recent[0])

            if "date_service_received" in ref_claim:
                dos = datetime.strptime(
                    ref_claim["date_service_received"], "%Y_%m_%d"
                ).date()
                test_date = datetime.strptime(most_recent[1], "%Y_%m_%d").date()
                months = (dos.year - test_date.year) * 12 + (dos.month - test_date.month)
                if dos.day < test_date.day:
                    months -= 1
                res["fsh_test_done_within_months"] = max(0, months)

            if "patient_dob" in ref_claim:
                dob = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()
                prior_tests = sorted_tests[:-1]
                all_under_19 = True
                for pt in prior_tests:
                    pt_date = datetime.strptime(pt[1], "%Y_%m_%d").date()
                    pt_age = (
                        pt_date.year
                        - dob.year
                        - ((pt_date.month, pt_date.day) < (dob.month, dob.day))
                    )
                    if pt_age >= 40:
                        if pt[0] >= 19:
                            all_under_19 = False
                            break
                res["all_prior_fsh_levels_after_40_under_19"] = all_under_19

    return res
