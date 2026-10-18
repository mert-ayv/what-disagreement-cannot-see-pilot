from datetime import datetime

ASSUMED_MET = [
    "charged_by_infertility_specialist",
    "coverage_status",
    "failure_to_become_pregnant",
]


def adapt(ref_claim: dict) -> dict:
    claim = {
        "charged_by_infertility_specialist": True,
        "coverage_status": "covered_student",
        # The reference interface does not separately report pregnancy outcomes.
        "failure_to_become_pregnant": True,
    }

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "age_of_patients_female_partner": "partner_age_years",
        "num_months_timed_unprotected_intercourse":
            "months_unprotected_timed_sexual_intercourse",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "months_frequent_unprotected_heterosexual_intercourse",
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

    partner_key = "sex_of_patients_partner"
    if partner_key in ref_claim:
        partner = ref_claim[partner_key]
        claim["partner_sex"] = (
            "none" if partner == "no_partner" else partner
        )

    condition_key = "demonstrated_and_documented_condition_causing_infertility"
    if condition_key in ref_claim:
        condition = ref_claim[condition_key]
        claim["condition_demonstrated_to_cause_infertility"] = True
        claim["condition_recognized_and_documented"] = True
        claim["no_natural_physiologic_infertility_in_patient_or_partner"] = (
            condition == "other"
        )

    sterilization_keys = ["patient_has_had_voluntary_sterilization"]
    if ref_claim.get(partner_key) != "no_partner":
        sterilization_keys.append("partner_has_had_voluntary_sterilization")

    sterilization_values = [ref_claim.get(key) for key in sterilization_keys]
    sterilization_target = "no_voluntary_sterilization_in_patient_or_partner"
    if "yes" in sterilization_values:
        claim[sterilization_target] = False
    elif all(value == "no" for value in sterilization_values):
        claim[sterilization_target] = True

    yes_no_fields = {
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            ("pregnancy_unattainable_with_less_costly_covered_treatment", "no"),
        "patient_or_partner_diagnosed_with_gender_dysphoria":
            ("patient_or_partner_clinically_diagnosed_gender_dysphoria", "yes"),
    }
    for source, (target, true_value) in yes_no_fields.items():
        if source in ref_claim and ref_claim[source] in ("yes", "no"):
            claim[target] = ref_claim[source] == true_value

    def parse_date(value):
        try:
            return datetime.strptime(value, "%Y_%m_%d").date()
        except (TypeError, ValueError):
            return None

    service_date = parse_date(ref_claim.get("date_service_received"))
    birth_date = parse_date(ref_claim.get("patient_dob"))

    if "day_3_fsh_tests" in ref_claim and service_date is not None:
        tests = []
        complete = True

        for entry in ref_claim["day_3_fsh_tests"]:
            try:
                level, date_text, time_text = entry
                test_date = parse_date(date_text)
                test_time = datetime.strptime(time_text, "%H_%M").time()
                if test_date is None:
                    complete = False
                    continue
                if test_date <= service_date:
                    tests.append((test_date, test_time, level))
            except (TypeError, ValueError):
                complete = False

        if complete and tests:
            latest_timestamp = max((day, time) for day, time, _ in tests)
            latest_levels = [
                level
                for day, time, level in tests
                if (day, time) == latest_timestamp
            ]
            claim["most_recent_unmedicated_day3_fsh_date"] = (
                latest_timestamp[0].strftime("%Y_%m_%d")
            )
            # Equally timestamped results cannot be ordered further.
            # Use the highest result rather than silently discard an adverse one.
            claim["most_recent_unmedicated_day3_fsh_value"] = max(latest_levels)

        if complete and birth_date is not None and birth_date <= service_date:
            def age_on(day):
                return day.year - birth_date.year - (
                    (day.month, day.day)
                    < (birth_date.month, birth_date.day)
                )

            claim["all_unmedicated_day3_fsh_since_40_below_19"] = all(
                level < 19
                for day, _, level in tests
                if age_on(day) >= 40
            )

    # Abnormal semen analyses have no corresponding field in this SCHEMA.
    return claim
