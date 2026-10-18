from datetime import datetime

ASSUMED_MET = ["is_covered_student_or_partner"]


def adapt(ref_claim: dict) -> dict:
    res = {}

    # Plan enrollment (assumed met)
    res["is_covered_student_or_partner"] = True

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

    # Evaluation date / current date
    if "date_service_received" in ref_claim:
        res["current_date"] = ref_claim["date_service_received"]

    # Patient demographics
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        res["patient_gender"] = ref_claim["sex_of_patient_trying_to_conceive"]

    if "patient_dob" in ref_claim and "date_service_received" in ref_claim:
        try:
            dob = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d")
            srv = datetime.strptime(ref_claim["date_service_received"], "%Y_%m_%d")
            res["patient_age"] = srv.year - dob.year - ((srv.month, srv.day) < (dob.month, dob.day))
        except Exception:
            pass

    # Partner demographics
    if "sex_of_patients_partner" in ref_claim:
        p_sex = ref_claim["sex_of_patients_partner"]
        if p_sex == "no_partner":
            res["partner_gender"] = "none"
        else:
            res["partner_gender"] = p_sex

    if "age_of_patients_female_partner" in ref_claim:
        res["partner_age"] = ref_claim["age_of_patients_female_partner"]

    # Medical history & disqualifiers
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        res["documented_infertility_condition"] = True
        natural_causes = {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }
        res["infertility_due_to_natural_physiologic_process"] = cond in natural_causes

    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    pr_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    if p_ster is not None or pr_ster is not None:
        if p_ster == "yes" or pr_ster == "yes":
            res["has_voluntary_sterilization"] = True
        else:
            res["has_voluntary_sterilization"] = False

    if "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan" in ref_claim:
        val = ref_claim["successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"]
        res["less_costly_treatment_available"] = (val == "yes")

    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        val = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        res["gender_dysphoria_diagnosed"] = (val == "yes")

    # Conception attempts
    months_timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    months_freq = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    if months_timed is not None or months_freq is not None:
        vals = [m for m in [months_timed, months_freq] if m is not None]
        res["months_trying_conception_intercourse"] = max(vals)

    if "num_cycles_donor_insemination" in ref_claim:
        res["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # Semen analyses
    if "abnormal_semen_analyses" in ref_claim:
        dates = []
        for d in ref_claim["abnormal_semen_analyses"]:
            try:
                dates.append(datetime.strptime(d, "%Y_%m_%d"))
            except Exception:
                pass
        dates.sort()
        count = 0
        last_d = None
        for d in dates:
            if last_d is None or (d - last_d).days >= 14:
                count += 1
                last_d = d
        res["male_abnormal_semen_analyses_count"] = count

    # FSH tests
    if "day_3_fsh_tests" in ref_claim:
        tests = ref_claim["day_3_fsh_tests"]
        if tests:
            sorted_tests = sorted(tests, key=lambda t: (t[1], t[2]))
            most_recent = sorted_tests[-1]
            res["most_recent_day3_fsh_level"] = float(most_recent[0])
            res["fsh_test_date"] = most_recent[1]

            if "patient_dob" in ref_claim:
                try:
                    dob = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d")
                    post_40_tests = []
                    for t in sorted_tests:
                        t_date = datetime.strptime(t[1], "%Y_%m_%d")
                        age_at_test = t_date.year - dob.year - ((t_date.month, t_date.day) < (dob.month, dob.day))
                        if age_at_test >= 40:
                            post_40_tests.append(t)
                    res["all_post_40_fsh_levels_under_19"] = all(float(t[0]) < 19.0 for t in post_40_tests)
                except Exception:
                    pass

    return res
