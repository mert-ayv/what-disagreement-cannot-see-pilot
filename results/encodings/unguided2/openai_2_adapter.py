def adapt(ref_claim: dict) -> dict:
    result = {}

    direct_fields = {
        "date_service_received": "service_date",
        "patient_dob": "patient_birth_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "months_unprotected_timed_intercourse",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "months_frequent_unprotected_heterosexual_intercourse",
        "age_of_patients_female_partner": "partner_age",
    }
    for source, target in direct_fields.items():
        if source in ref_claim:
            result[target] = ref_claim[source]

    if "service_type" in ref_claim:
        result["service"] = {
            "intrauterine_insemination": "intrauterine_insemination",
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
        }.get(ref_claim["service_type"], "other")

    if "sex_of_patients_partner" in ref_claim:
        partner_sex = ref_claim["sex_of_patients_partner"]
        result["partner_sex"] = (
            "none" if partner_sex == "no_partner" else partner_sex
        )
        if partner_sex == "no_partner":
            result["partner_age"] = None

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        result["infertility_causing_condition_documented"] = True
        result["infertility_due_to_natural_physiologic_process"] = condition in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    sterilization = ref_claim.get("patient_has_had_voluntary_sterilization")
    if sterilization == "yes":
        result["patient_or_partner_voluntarily_sterilized"] = True
    elif (
        sterilization == "no"
        and ref_claim.get("sex_of_patients_partner") == "no_partner"
    ):
        result["patient_or_partner_voluntarily_sterilized"] = False
    # A patient's negative history does not establish the partner's history.

    less_costly_field = (
        "successful_pregnancy_can_be_attained_through_less_costly_"
        "treatment_covered_by_plan"
    )
    if ref_claim.get(less_costly_field) in ("yes", "no"):
        result["pregnancy_possible_with_less_costly_covered_treatment"] = (
            ref_claim[less_costly_field] == "yes"
        )

    if "num_cycles_donor_insemination" in ref_claim:
        result["self_paid_unsuccessful_donor_insemination_cycles"] = (
            ref_claim["num_cycles_donor_insemination"]
        )
    # The reference counts only cycles not paid for by the plan; the total
    # including plan-paid cycles cannot be determined from that count.

    if "day_3_fsh_tests" in ref_claim:
        result["unmedicated_day3_fsh_tests"] = [
            {"date": test_date, "value_miu_ml": level}
            for level, test_date, _time in ref_claim["day_3_fsh_tests"]
        ]

    # Specialist status, coverage role, abnormal semen analyses, gender
    # dysphoria, and a male partner's age have no reference counterparts.
    return result
