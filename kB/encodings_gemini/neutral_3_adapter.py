import datetime

ASSUMED_MET = ["patient_is_covered_student_or_partner"]


def _parse_date(date_str: str) -> datetime.date:
    parts = date_str.split("_")
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))


def adapt(ref_claim: dict) -> dict:
    out = {}

    # Assumed met fields
    out["patient_is_covered_student_or_partner"] = True

    # Service type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_with_menotropins"
        else:
            out["service_type"] = st

    # Service date
    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]

    # Patient gender
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        out["patient_gender"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # Patient age derived from DOB and service date
    if "patient_dob" in ref_claim and "date_service_received" in ref_claim:
        dob = _parse_date(ref_claim["patient_dob"])
        s_date = _parse_date(ref_claim["date_service_received"])
        age = s_date.year - dob.year - ((s_date.month, s_date.day) < (dob.month, dob.day))
        out["patient_age"] = age

    # Partner info
    if "sex_of_patients_partner" in ref_claim:
        partner_sex = ref_claim["sex_of_patients_partner"]
        if partner_sex == "no_partner":
            out["has_partner"] = False
        elif partner_sex in ("male", "female"):
            out["has_partner"] = True
            out["partner_gender"] = partner_sex

    if "age_of_patients_female_partner" in ref_claim:
        out["partner_age"] = ref_claim["age_of_patients_female_partner"]

    # Voluntary sterilization
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    partner_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    has_no_partner = ref_claim.get("sex_of_patients_partner") == "no_partner"

    if p_ster == "yes" or partner_ster == "yes":
        out["has_voluntary_sterilization"] = True
    elif p_ster == "no" and (partner_ster == "no" or has_no_partner):
        out["has_voluntary_sterilization"] = False
    elif p_ster == "no" and partner_ster is None and "sex_of_patients_partner" not in ref_claim:
        out["has_voluntary_sterilization"] = False

    # Documented condition and natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        out["has_documented_condition_causing_infertility"] = True
        natural_causes = {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }
        out["infertility_due_to_natural_physiologic_process"] = cond in natural_causes

    # Less costly treatment
    if "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan" in ref_claim:
        val = ref_claim["successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"]
        if val == "yes":
            out["pregnancy_attainable_through_less_costly_covered_treatment"] = True
        elif val == "no":
            out["pregnancy_attainable_through_less_costly_covered_treatment"] = False

    # Intercourse duration
    months = []
    if "num_months_frequent_unprotected_heterosexual_intercourse" in ref_claim:
        m = ref_claim["num_months_frequent_unprotected_heterosexual_intercourse"]
        if m is not None:
            months.append(m)
    if "num_months_timed_unprotected_intercourse" in ref_claim:
        m = ref_claim["num_months_timed_unprotected_intercourse"]
        if m is not None:
            months.append(m)
    if months:
        out["months_of_unprotected_timed_intercourse"] = max(months)

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        out["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # Gender dysphoria
    if "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim:
        val = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        if val == "yes":
            out["gender_dysphoria_diagnosed"] = True
        elif val == "no":
            out["gender_dysphoria_diagnosed"] = False

    # FSH tests
    if "day_3_fsh_tests" in ref_claim and ref_claim["day_3_fsh_tests"]:
        tests = ref_claim["day_3_fsh_tests"]
        sorted_tests = sorted(tests, key=lambda x: (x[1], x[2] if len(x) > 2 else ""))
        most_recent = sorted_tests[-1]
        out["fsh_test_date"] = most_recent[1]
        out["most_recent_fsh_level"] = float(most_recent[0])
        out["fsh_test_is_unmedicated_day_3"] = True

        if "patient_dob" in ref_claim:
            dob = _parse_date(ref_claim["patient_dob"])
            prior_tests = sorted_tests[:-1]
            all_under_19 = True
            for pt in prior_tests:
                pt_date = _parse_date(pt[1])
                pt_age = pt_date.year - dob.year - ((pt_date.month, pt_date.day) < (dob.month, dob.day))
                if pt_age >= 40 and pt[0] >= 19:
                    all_under_19 = False
                    break
            out["all_prior_fsh_tests_after_40_under_19"] = all_under_19

    # Semen analyses
    if "abnormal_semen_analyses" in ref_claim:
        analyses = ref_claim["abnormal_semen_analyses"]
        out["abnormal_semen_analyses_count"] = len(analyses)
        if len(analyses) >= 2:
            dates = sorted([_parse_date(d) for d in analyses])
            out["semen_analyses_at_least_2_weeks_apart"] = (dates[-1] - dates[0]).days >= 14
        else:
            out["semen_analyses_at_least_2_weeks_apart"] = False

    return out
