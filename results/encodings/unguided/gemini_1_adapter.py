from datetime import datetime


def adapt(ref_claim: dict) -> dict:
    adapted = {}

    # Service type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "ovulation_induction_cycle_with_menotropins":
            adapted["service_type"] = "ovulation_induction_with_menotropins"
        elif st == "intrauterine_insemination":
            adapted["service_type"] = "intrauterine_insemination"
        else:
            adapted["service_type"] = "other"

    # Patient and service dates -> Patient age
    patient_dob = None
    date_service = None
    if "patient_dob" in ref_claim:
        try:
            patient_dob = datetime.strptime(ref_claim["patient_dob"], "%Y_%m_%d").date()
        except Exception:
            pass

    if "date_service_received" in ref_claim:
        try:
            date_service = datetime.strptime(ref_claim["date_service_received"], "%Y_%m_%d").date()
        except Exception:
            pass

    if patient_dob is not None and date_service is not None:
        age = (
            date_service.year
            - patient_dob.year
            - ((date_service.month, date_service.day) < (patient_dob.month, patient_dob.day))
        )
        adapted["patient_age"] = age

    # Patient gender
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        adapted["patient_gender"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # Partner gender
    if "sex_of_patients_partner" in ref_claim:
        pg = ref_claim["sex_of_patients_partner"]
        if pg == "no_partner":
            adapted["partner_gender"] = "none"
        elif pg in ("female", "male"):
            adapted["partner_gender"] = pg

    # Partner age
    if "age_of_patients_female_partner" in ref_claim:
        adapted["partner_age"] = ref_claim["age_of_patients_female_partner"]
    elif ref_claim.get("sex_of_patients_partner") == "no_partner":
        adapted["partner_age"] = None

    # Months of unprotected intercourse
    timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    frequent = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    if timed is not None and frequent is not None:
        adapted["months_unprotected_intercourse"] = max(timed, frequent)
    elif timed is not None:
        adapted["months_unprotected_intercourse"] = timed
    elif frequent is not None:
        adapted["months_unprotected_intercourse"] = frequent

    # Donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim:
        adapted["donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # Voluntary sterilization
    if "patient_has_had_voluntary_sterilization" in ref_claim:
        val = ref_claim["patient_has_had_voluntary_sterilization"]
        adapted["voluntary_sterilization"] = str(val).lower() == "yes"

    # Infertility condition and natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        adapted["has_infertility_condition"] = bool(cond and cond != "none")
        adapted["infertility_due_to_natural_physiologic_process"] = cond in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    # Less costly treatment
    if "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan" in ref_claim:
        val = ref_claim["successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"]
        adapted["pregnancy_attainable_through_less_costly_treatment"] = str(val).lower() == "yes"

    # FSH tests
    if "day_3_fsh_tests" in ref_claim:
        raw_tests = ref_claim["day_3_fsh_tests"]
        if raw_tests is None or len(raw_tests) == 0:
            adapted["fsh_test_months_ago"] = None
            adapted["fsh_most_recent_result"] = None
            if adapted.get("patient_gender") == "female" and adapted.get("patient_age", 0) >= 40:
                adapted["all_fsh_tests_after_40_under_19"] = None
        else:
            parsed_tests = []
            for t in raw_tests:
                if isinstance(t, (list, tuple)):
                    level = t[0]
                    d_str = t[1]
                    tm_str = t[2] if len(t) > 2 else "00_00"
                elif isinstance(t, dict):
                    level = t.get("level")
                    d_str = t.get("date")
                    tm_str = t.get("time", "00_00")
                else:
                    continue

                try:
                    dt = datetime.strptime(f"{d_str}_{tm_str}", "%Y_%m_%d_%H_%M")
                except Exception:
                    try:
                        dt = datetime.strptime(d_str, "%Y_%m_%d")
                    except Exception:
                        continue
                parsed_tests.append((dt, level))

            if parsed_tests:
                parsed_tests.sort(key=lambda x: x[0])
                recent_dt, recent_level = parsed_tests[-1]
                adapted["fsh_most_recent_result"] = recent_level

                if date_service is not None:
                    test_date = recent_dt.date()
                    if date_service < test_date:
                        adapted["fsh_test_months_ago"] = 0.0
                    else:
                        diff_months = (
                            (date_service.year - test_date.year) * 12
                            + (date_service.month - test_date.month)
                            + (date_service.day - test_date.day) / 30.0
                        )
                        adapted["fsh_test_months_ago"] = max(0.0, diff_months)

                # all_fsh_tests_after_40_under_19
                p_gender = adapted.get("patient_gender")
                p_age = adapted.get("patient_age", 0)
                if p_gender == "female" and p_age >= 40:
                    if patient_dob is not None:
                        tests_after_40 = []
                        for dt, lvl in parsed_tests:
                            t_date = dt.date()
                            age_at_test = (
                                t_date.year
                                - patient_dob.year
                                - ((t_date.month, t_date.day) < (patient_dob.month, patient_dob.day))
                            )
                            if age_at_test >= 40:
                                tests_after_40.append(lvl)
                        if tests_after_40:
                            adapted["all_fsh_tests_after_40_under_19"] = all(lvl < 19 for lvl in tests_after_40)
                        else:
                            adapted["all_fsh_tests_after_40_under_19"] = True
                elif p_gender == "female" and p_age < 40:
                    adapted["all_fsh_tests_after_40_under_19"] = None
                elif p_gender == "male":
                    adapted["all_fsh_tests_after_40_under_19"] = None

    return adapted
