def adapt(ref_claim: dict) -> dict:
    import calendar
    from datetime import datetime

    claim = {}

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "timed_unprotected_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "frequent_unprotected_intercourse_months",
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
        partner = ref_claim["sex_of_patients_partner"]
        claim["partner_sex"] = None if partner == "no_partner" else partner

        if partner == "no_partner":
            claim["partner_birth_date"] = None
        elif (
            partner == "female"
            and "age_of_patients_female_partner" in ref_claim
            and "date_service_received" in ref_claim
        ):
            # Age does not identify an exact DOB. Use a representative DOB
            # that preserves the partner's age on the service date.
            service_date = datetime.strptime(
                ref_claim["date_service_received"], "%Y_%m_%d"
            ).date()
            year = (
                service_date.year
                - ref_claim["age_of_patients_female_partner"]
            )
            day = min(
                service_date.day,
                calendar.monthrange(year, service_date.month)[1],
            )
            claim["partner_birth_date"] = (
                f"{year:04d}_{service_date.month:02d}_{day:02d}"
            )

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        claim["infertility_causing_condition_demonstrated"] = True
        claim["condition_recognized_and_documented"] = True
        claim["patient_or_partner_infertility_due_to_natural_process"] = (
            condition in {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
        )

    sterilization = ref_claim.get("patient_has_had_voluntary_sterilization")
    if sterilization == "yes":
        claim["patient_or_partner_voluntarily_sterilized"] = True
    # A patient-only "no" does not establish that the partner was not
    # voluntarily sterilized. With no partner, it does establish the result.
    elif (
        sterilization == "no"
        and ref_claim.get("sex_of_patients_partner") == "no_partner"
    ):
        claim["patient_or_partner_voluntarily_sterilized"] = False

    cheaper_field = (
        "successful_pregnancy_can_be_attained_through_less_costly_"
        "treatment_covered_by_plan"
    )
    if cheaper_field in ref_claim:
        value = ref_claim[cheaper_field]
        if value in ("yes", "no"):
            claim[
                "pregnancy_attainable_through_less_costly_covered_treatment"
            ] = value == "yes"

    if "num_cycles_donor_insemination" in ref_claim:
        cycles = ref_claim["num_cycles_donor_insemination"]
        claim["donor_insemination_cycles"] = cycles
        claim["self_paid_donor_insemination_cycles"] = cycles

    if "day_3_fsh_tests" in ref_claim:
        claim["unmedicated_day3_fsh_tests"] = [
            {"date": test_date, "value_miu_ml": level}
            for level, test_date, _time in ref_claim["day_3_fsh_tests"]
        ]

    # Enrollment role, semen-analysis dates, and gender-dysphoria diagnosis
    # have no reference counterparts and cannot be inferred.
    return claim
