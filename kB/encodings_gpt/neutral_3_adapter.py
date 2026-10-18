ASSUMED_MET = [
    "charged_by_infertility_specialist",
    "coverage_role",
    "failure_to_become_pregnant",
]


def adapt(ref_claim: dict) -> dict:
    claim = {
        "charged_by_infertility_specialist": True,
        "coverage_role": "covered_student",
        # The reference interface does not separately report pregnancy outcomes.
        "failure_to_become_pregnant": True,
    }

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_category",
        "age_of_patients_female_partner": "female_partner_age_years",
        "num_months_timed_unprotected_intercourse":
            "timed_unprotected_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "frequent_unprotected_intercourse_months",
        "num_cycles_donor_insemination":
            "self_paid_donor_insemination_cycles",
    }
    for source, target in direct_fields.items():
        if source in ref_claim:
            claim[target] = ref_claim[source]

    if "service_type" in ref_claim:
        claim["service"] = {
            "intrauterine_insemination": "intrauterine_insemination",
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
        }.get(ref_claim["service_type"], "other")

    if "sex_of_patients_partner" in ref_claim:
        claim["partner_category"] = {
            "female": "female",
            "male": "male",
            "no_partner": "none_or_other",
        }[ref_claim["sex_of_patients_partner"]]

    condition_field = (
        "demonstrated_and_documented_condition_causing_infertility"
    )
    if condition_field in ref_claim:
        claim["condition_demonstrated_to_cause_infertility"] = True
        claim["condition_recognized_and_documented"] = True
        claim["patient_or_partner_infertility_due_to_natural_process"] = (
            ref_claim[condition_field] in {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
        )

    sterilization = [
        ref_claim.get("patient_has_had_voluntary_sterilization"),
        ref_claim.get("partner_has_had_voluntary_sterilization"),
    ]
    if "yes" in sterilization:
        claim["patient_or_partner_voluntarily_sterilized"] = True
    elif sterilization == ["no", "no"]:
        claim["patient_or_partner_voluntarily_sterilized"] = False

    yes_no_fields = {
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            "pregnancy_attainable_with_less_costly_covered_treatment",
        "patient_or_partner_diagnosed_with_gender_dysphoria":
            "patient_or_partner_clinically_diagnosed_gender_dysphoria",
    }
    for source, target in yes_no_fields.items():
        if source in ref_claim:
            claim[target] = ref_claim[source] == "yes"

    service_date = ref_claim.get("date_service_received")

    if "abnormal_semen_analyses" in ref_claim:
        claim["abnormal_semen_analysis_dates"] = [
            test_date
            for test_date in ref_claim["abnormal_semen_analyses"]
            if service_date is None or test_date <= service_date
        ]

    if "day_3_fsh_tests" in ref_claim:
        # Preserve every qualifying result, including same-day duplicates.
        # The target schema has no time-of-day field.
        claim["fsh_tests"] = [
            {"date": test_date, "value_miu_ml": level}
            for level, test_date, _time in ref_claim["day_3_fsh_tests"]
            if service_date is None or test_date <= service_date
        ]

    return claim
