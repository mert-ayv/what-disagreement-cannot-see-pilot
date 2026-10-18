from datetime import datetime

ASSUMED_MET = [
    "charged_by_infertility_specialist",
    "covered_role",
]


def adapt(ref_claim: dict) -> dict:
    claim = {
        "charged_by_infertility_specialist": True,
        "covered_role": "student",
    }

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_table_sex",
        "age_of_patients_female_partner": "female_partner_age",
        "num_months_timed_unprotected_intercourse":
            "failed_unprotected_timed_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "failed_frequent_unprotected_intercourse_months",
        "num_cycles_donor_insemination":
            "failed_donor_insemination_cycles_not_paid_by_plan",
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
        claim["partner_category"] = {
            "male": "male",
            "female": "female",
            "no_partner": "none",
        }.get(partner, "other")

    yes_no_fields = {
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            "successful_pregnancy_possible_with_less_costly_covered_treatment",
        "patient_or_partner_diagnosed_with_gender_dysphoria":
            "either_clinically_diagnosed_gender_dysphoria",
    }
    for source, target in yes_no_fields.items():
        if ref_claim.get(source) in ("yes", "no"):
            claim[target] = ref_claim[source] == "yes"

    patient_sterilized = ref_claim.get(
        "patient_has_had_voluntary_sterilization"
    )
    partner_sterilized = ref_claim.get(
        "partner_has_had_voluntary_sterilization"
    )
    no_partner = ref_claim.get("sex_of_patients_partner") == "no_partner"

    if patient_sterilized == "yes" or partner_sterilized == "yes":
        claim["either_has_voluntary_sterilization_history"] = True
    elif patient_sterilized == "no" and (
        partner_sterilized == "no" or no_partner
    ):
        claim["either_has_voluntary_sterilization_history"] = False

    condition_field = (
        "demonstrated_and_documented_condition_causing_infertility"
    )
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        claim["condition_demonstrated_to_cause_infertility"] = True
        claim["condition_recognized_and_documented"] = True
        claim["either_has_natural_physiologic_infertility"] = condition in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    if "day_3_fsh_tests" in ref_claim:
        service_date = None
        if "date_service_received" in ref_claim:
            try:
                service_date = datetime.strptime(
                    ref_claim["date_service_received"], "%Y_%m_%d"
                ).date()
            except (TypeError, ValueError):
                pass

        tests = []
        for level, test_date, _time in ref_claim["day_3_fsh_tests"]:
            # The target history is assessed only through the service date.
            if service_date is not None:
                try:
                    parsed_date = datetime.strptime(
                        test_date, "%Y_%m_%d"
                    ).date()
                except (TypeError, ValueError):
                    parsed_date = None
                if parsed_date is not None and parsed_date > service_date:
                    continue

            # Preserve every test, including coincident measurements.
            tests.append({
                "date": test_date,
                "value_miu_ml": level,
            })

        claim["unmedicated_day3_fsh_tests"] = tests
        # The reference's supplied test history has no partial-history marker.
        claim["fsh_history_complete_since_age_40"] = True

    return claim
