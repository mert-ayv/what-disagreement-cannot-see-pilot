from datetime import datetime

ASSUMED_MET = [
    "provider_is_infertility_specialist",
    "patient_is_student_or_covered_dependent_partner",
]


def adapt(ref_claim: dict) -> dict:
    claim = {}

    # Assumed met fields
    claim["provider_is_infertility_specialist"] = True
    claim["patient_is_student_or_covered_dependent_partner"] = True

    # service_type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            claim["service_type"] = "intrauterine_insemination"
        elif st in [
            "ovulation_induction_cycle_with_menotropins",
            "ovulation_induction_with_menotropins",
        ]:
            claim["service_type"] = "ovulation_induction_with_menotropins"
        else:
            claim["service_type"] = "other"

    # patient_sex
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        claim["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # partner_sex
    if "sex_of_patients_partner" in ref_claim:
        ps = ref_claim["sex_of_patients_partner"]
        if ps == "no_partner":
            claim["partner_sex"] = "none"
        else:
            claim["partner_sex"] = ps

    # partner_age
    if "age_of_patients_female_partner" in ref_claim:
        claim["partner_age"] = ref_claim["age_of_patients_female_partner"]

    # patient_age (from patient_dob and date_service_received)
    dos_date = None
    if "date_service_received" in ref_claim:
        dos_date = datetime.strptime(ref_claim["date_service_received"], "%Y_%m_%d").date()

    dob_date = None
    if "patient_dob" in ref_claim:
        dob_date = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()

    if dos_date is not None and dob_date is not None:
        age = dos_date.year - dob_date.year - ((dos_date.month, dos_date.day) < (dob_date.month, dob_date.day))
        claim["patient_age"] = age

    # documented infertility causing condition & natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        claim["has_documented_infertility_causing_condition"] = True
        if cond in [
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        ]:
            claim["infertility_due_to_natural_physiologic_process"] = True
        else:
            claim["infertility_due_to_natural_physiologic_process"] = False

    # voluntary sterilization
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    part_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    partner_sex = ref_claim.get("sex_of_patients_partner")

    if p_ster == "yes" or part_ster == "yes":
        claim["patient_or_partner_has_voluntary_sterilization"] = True
    elif p_ster == "no":
        if partner_sex == "no_partner" or part_ster == "no":
            claim["patient_or_partner_has_voluntary_sterilization"] = False

    # less costly treatment
    if "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan" in ref_claim:
        val = ref_claim["successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"]
        claim["pregnancy_attainable_through_less_costly_covered_treatment"] = (val == "yes")

    # gender dysphoria
    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        val = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        claim["diagnosed_with_gender_dysphoria"] = (val == "yes")

    # months unprotected timed intercourse
    intercourse_months = None
    if "num_months_timed_unprotected_intercourse" in ref_claim:
        intercourse_months = ref_claim["num_months_timed_unprotected_intercourse"]
    if "num_months_frequent_unprotected_heterosexual_intercourse" in ref_claim:
        v = ref_claim["num_months_frequent_unprotected_heterosexual_intercourse"]
        if intercourse_months is None or v > intercourse_months:
            intercourse_months = v
    if intercourse_months is not None:
        claim["months_unprotected_timed_intercourse"] = intercourse_months

    # donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        claim["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # abnormal semen analyses count (at least 2 weeks apart)
    if "abnormal_semen_analyses" in ref_claim:
        dates = sorted([datetime.strptime(d, "%Y_%m_%d").date() for d in ref_claim["abnormal_semen_analyses"]])
        count = 0
        last_date = None
        for d in dates:
            if last_date is None or (d - last_date).days >= 14:
                count += 1
                last_date = d
        claim["abnormal_semen_analyses_count"] = count

    # FSH tests
    if "day_3_fsh_tests" in ref_claim and ref_claim["day_3_fsh_tests"]:
        tests = ref_claim["day_3_fsh_tests"]
        # Sort tests chronologically by date and time
        sorted_tests = sorted(tests, key=lambda t: (t[1], t[2]))
        most_recent = sorted_tests[-1]
        claim["unmedicated_day3_fsh_most_recent_value"] = float(most_recent[0])

        if dos_date is not None:
            most_recent_date = datetime.strptime(most_recent[1], "%Y_%m_%d").date()
            days_diff = (dos_date - most_recent_date).days
            claim["unmedicated_day3_fsh_test_months_ago"] = max(0, round(days_diff / 30.4375))

        if dob_date is not None:
            all_under_19 = True
            for test in sorted_tests[:-1]:
                t_date = datetime.strptime(test[1], "%Y_%m_%d").date()
                age_at_test = t_date.year - dob_date.year - ((t_date.month, t_date.day) < (dob_date.month, dob_date.day))
                if age_at_test >= 40 and test[0] >= 19:
                    all_under_19 = False
                    break
            claim["all_prior_fsh_tests_after_40_under_19"] = all_under_19

    return claim
