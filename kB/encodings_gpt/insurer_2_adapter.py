import calendar
from datetime import date


ASSUMED_MET = [
    "charged_by_infertility_specialist",
    "plan_relationship",
    "same_condition_recognized_by_physician_or_specialist",
    "failure_to_become_pregnant",
]


def adapt(ref_claim: dict) -> dict:
    result = {
        "charged_by_infertility_specialist": True,
        "plan_relationship": "covered_student",
        "same_condition_recognized_by_physician_or_specialist": True,
        # Counts of intercourse or inseminations do not, by themselves,
        # establish whether pregnancy occurred.
        "failure_to_become_pregnant": True,
    }

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value.replace("_", "-"))
        except ValueError:
            return None

    def format_date(value):
        return value.isoformat().replace("-", "_")

    def yes_no(field):
        value = ref_claim.get(field)
        if value == "yes":
            return True
        if value == "no":
            return False
        return None

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_table_category",
        "sex_of_patients_partner": "partner_category",
        "num_months_timed_unprotected_intercourse":
            "unprotected_timed_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "frequent_unprotected_heterosexual_intercourse_months",
        "num_cycles_donor_insemination":
            "donor_insemination_cycles_not_paid_by_plan",
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

    condition_field = (
        "demonstrated_and_documented_condition_causing_infertility"
    )
    if condition_field in ref_claim:
        result["condition_demonstrated_to_cause_infertility"] = True
        result[
            "same_condition_documented_in_patient_or_partner_records"
        ] = True
        result["either_person_infertility_due_to_natural_physiology"] = (
            ref_claim[condition_field] in {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
        )

    boolean_fields = {
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            "successful_pregnancy_attainable_with_less_costly_covered_treatment",
        "patient_or_partner_diagnosed_with_gender_dysphoria":
            "patient_or_partner_clinically_diagnosed_gender_dysphoria",
    }
    for source, target in boolean_fields.items():
        value = yes_no(source)
        if value is not None:
            result[target] = value

    patient_sterilized = yes_no("patient_has_had_voluntary_sterilization")
    if ref_claim.get("sex_of_patients_partner") == "no_partner":
        partner_sterilized = False
    else:
        partner_sterilized = yes_no("partner_has_had_voluntary_sterilization")

    if patient_sterilized is True or partner_sterilized is True:
        result["either_person_had_voluntary_sterilization"] = True
    elif patient_sterilized is False and partner_sterilized is False:
        result["either_person_had_voluntary_sterilization"] = False

    service_date = parse_date(ref_claim.get("date_service_received"))
    birth_date = parse_date(ref_claim.get("patient_dob"))

    # Only the female partner's attained age matters to the encoding.
    # Use a representative birthday giving exactly that age on the service date.
    partner_age = ref_claim.get("age_of_patients_female_partner")
    if (
        ref_claim.get("sex_of_patients_partner") == "female"
        and service_date is not None
        and type(partner_age) is int
        and partner_age >= 0
    ):
        year = service_date.year - partner_age
        if 1 <= year <= 9999:
            day = min(
                service_date.day,
                calendar.monthrange(year, service_date.month)[1],
            )
            result["female_partner_birth_date"] = format_date(
                date(year, service_date.month, day)
            )

    if "day_3_fsh_tests" in ref_claim:
        tests = ref_claim["day_3_fsh_tests"]

        if not tests:
            result["all_unmedicated_day3_fsh_tests_at_age_40_or_older"] = []

        if service_date is not None:
            eligible_tests = []
            for level, test_date_string, test_time in tests:
                test_date = parse_date(test_date_string)
                if test_date is not None and test_date <= service_date:
                    eligible_tests.append(
                        (test_date, test_time, level, test_date_string)
                    )

            if eligible_tests:
                latest_key = max(
                    (test_date, time)
                    for test_date, time, _, _ in eligible_tests
                )
                latest_candidates = [
                    test
                    for test in eligible_tests
                    if test[:2] == latest_key
                ]

                # Different results with identical timestamps do not identify
                # which result was actually the most recent.
                level = latest_candidates[0][2]
                if all(test[2] == level for test in latest_candidates):
                    result["latest_unmedicated_day3_fsh_test"] = {
                        "date": latest_candidates[0][3],
                        "value": level,
                    }

            if birth_date is not None:
                history = []
                for test_date, _, level, test_date_string in eligible_tests:
                    age = (
                        test_date.year
                        - birth_date.year
                        - (
                            (test_date.month, test_date.day)
                            < (birth_date.month, birth_date.day)
                        )
                    )
                    if age >= 40:
                        history.append({
                            "date": test_date_string,
                            "value": level,
                        })
                result[
                    "all_unmedicated_day3_fsh_tests_at_age_40_or_older"
                ] = history

    return result
