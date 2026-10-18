from datetime import date

ASSUMED_MET = ["provider_is_infertility_specialist", "patient_coverage_status"]


def _parse_date(d_str: str) -> date:
    parts = d_str.split("_")
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


def _calc_age(dob: date, current: date) -> int:
    return (
        current.year
        - dob.year
        - ((current.month, current.day) < (dob.month, dob.day))
    )


def adapt(ref_claim: dict) -> dict:
    adapted = {}

    # Assumed met fields
    adapted["provider_is_infertility_specialist"] = True
    adapted["patient_coverage_status"] = "student"

    # Service type
    if "service_type" in ref_claim and ref_claim["service_type"] is not None:
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

    # Dates and Patient Age
    service_date = None
    if (
        "date_service_received" in ref_claim
        and ref_claim["date_service_received"] is not None
    ):
        adapted["service_date"] = ref_claim["date_service_received"]
        try:
            service_date = _parse_date(ref_claim["date_service_received"])
        except (ValueError, IndexError):
            service_date = None

    if (
        "patient_dob" in ref_claim
        and ref_claim["patient_dob"] is not None
        and service_date is not None
    ):
        try:
            dob = _parse_date(ref_claim["patient_dob"])
            adapted["patient_age"] = _calc_age(dob, service_date)
        except (ValueError, IndexError):
            pass

    # Patient Gender
    if (
        "sex_of_patient_trying_to_conceive" in ref_claim
        and ref_claim["sex_of_patient_trying_to_conceive"] is not None
    ):
        adapted["patient_gender"] = ref_claim[
            "sex_of_patient_trying_to_conceive"
        ]

    # Partner Gender
    if (
        "sex_of_patients_partner" in ref_claim
        and ref_claim["sex_of_patients_partner"] is not None
    ):
        p_sex = ref_claim["sex_of_patients_partner"]
        if p_sex == "no_partner":
            adapted["partner_gender"] = "none"
        elif p_sex in ("male", "female"):
            adapted["partner_gender"] = p_sex

    # Partner Age
    if (
        "age_of_patients_female_partner" in ref_claim
        and ref_claim["age_of_patients_female_partner"] is not None
    ):
        adapted["partner_age"] = ref_claim["age_of_patients_female_partner"]

    # Voluntary Sterilization
    p_ster = ref_claim.get("patient_has_had_voluntary_sterilization")
    partner_ster = ref_claim.get("partner_has_had_voluntary_sterilization")
    no_partner = ref_claim.get("sex_of_patients_partner") == "no_partner"

    if p_ster == "yes" or partner_ster == "yes":
        adapted["has_had_voluntary_sterilization"] = True
    elif p_ster == "no" and (partner_ster == "no" or no_partner):
        adapted["has_had_voluntary_sterilization"] = False

    # Condition Causing Infertility
    if (
        "demonstrated_and_documented_condition_causing_infertility" in ref_claim
        and ref_claim[
            "demonstrated_and_documented_condition_causing_infertility"
        ]
        is not None
    ):
        cond = ref_claim[
            "demonstrated_and_documented_condition_causing_infertility"
        ]
        adapted["condition_demonstrated_to_cause_infertility"] = True
        adapted["condition_documented_in_medical_records"] = True
        if cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        ):
            adapted["infertility_due_to_natural_physiologic_process"] = True
        else:
            adapted["infertility_due_to_natural_physiologic_process"] = False

    # Less Costly Covered Treatment
    if (
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        in ref_claim
        and ref_claim[
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        ]
        is not None
    ):
        val = ref_claim[
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        ]
        if val == "yes":
            adapted[
                "pregnancy_attainable_through_less_costly_covered_treatment"
            ] = True
        elif val == "no":
            adapted[
                "pregnancy_attainable_through_less_costly_covered_treatment"
            ] = False

    # Gender Dysphoria
    if (
        "patient_or_partner_diagnosed_with_gender_dysphoria" in ref_claim
        and ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        is not None
    ):
        val = ref_claim["patient_or_partner_diagnosed_with_gender_dysphoria"]
        if val == "yes":
            adapted["clinical_diagnosis_of_gender_dysphoria"] = True
        elif val == "no":
            adapted["clinical_diagnosis_of_gender_dysphoria"] = False

    # Months of Intercourse
    m_timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    m_freq = ref_claim.get(
        "num_months_frequent_unprotected_heterosexual_intercourse"
    )
    if m_timed is not None and m_freq is not None:
        adapted["months_of_unprotected_timed_intercourse"] = min(
            m_timed, m_freq
        )
    elif m_timed is not None:
        adapted["months_of_unprotected_timed_intercourse"] = m_timed
    elif m_freq is not None:
        adapted["months_of_unprotected_timed_intercourse"] = m_freq

    # Donor Insemination Cycles
    if (
        "num_cycles_donor_insemination" in ref_claim
        and ref_claim["num_cycles_donor_insemination"] is not None
    ):
        adapted["donor_insemination_cycles_self_paid"] = ref_claim[
            "num_cycles_donor_insemination"
        ]

    # Day 3 FSH Tests
    if (
        "day_3_fsh_tests" in ref_claim
        and ref_claim["day_3_fsh_tests"] is not None
    ):
        tests = ref_claim["day_3_fsh_tests"]
        if len(tests) > 0:
            sorted_tests = sorted(tests, key=lambda t: (t[1], t[2], t[0]))
            most_recent = sorted_tests[-1]
            adapted["most_recent_fsh_test_date"] = most_recent[1]
            adapted["most_recent_fsh_level"] = float(most_recent[0])
            adapted["fsh_test_is_unmedicated_day_3"] = True

            if (
                "patient_dob" in ref_claim
                and ref_claim["patient_dob"] is not None
            ):
                try:
                    dob = _parse_date(ref_claim["patient_dob"])
                    prior_levels = []
                    for t in sorted_tests[:-1]:
                        t_date = _parse_date(t[1])
                        if _calc_age(dob, t_date) >= 40:
                            prior_levels.append(float(t[0]))
                    adapted["prior_fsh_levels_after_age_40"] = prior_levels
                except (ValueError, IndexError):
                    pass

    return adapted
