from datetime import date
import calendar


def adapt(ref_claim: dict) -> dict:
    result = {}

    direct_fields = {
        "patient_dob": "date_of_birth",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_cycles_donor_insemination": "self_paid_donor_insemination_cycles",
    }
    for source, target in direct_fields.items():
        if source in ref_claim:
            result[target] = ref_claim[source]

    if "service_type" in ref_claim:
        service = ref_claim["service_type"]
        result["service"] = {
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
        }.get(service, service)

    if "sex_of_patients_partner" in ref_claim:
        partner = ref_claim["sex_of_patients_partner"]
        result["partner_sex"] = "none" if partner == "no_partner" else partner

    yes_no_fields = {
        "patient_has_had_voluntary_sterilization":
            "patient_or_partner_voluntary_sterilization",
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            "less_costly_covered_treatment_can_achieve_pregnancy",
    }
    for source, target in yes_no_fields.items():
        if source in ref_claim:
            value = ref_claim[source]
            if value in ("yes", "no"):
                result[target] = value == "yes"

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        natural_conditions = {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }
        if condition in natural_conditions or condition == "other":
            result["infertility_causing_condition"] = True
            result["condition_recognized_and_documented"] = True
            result["patient_or_partner_natural_physiologic_infertility"] = (
                condition in natural_conditions
            )

    # When both duration measures are available, do not claim more qualifying
    # months than either measure supports.
    durations = [
        ref_claim[field]
        for field in (
            "num_months_timed_unprotected_intercourse",
            "num_months_frequent_unprotected_heterosexual_intercourse",
        )
        if field in ref_claim
    ]
    if durations:
        result["qualifying_intercourse_months"] = min(durations)

    if result.get("partner_sex") in ("male", "none"):
        result["partner_date_of_birth"] = None
    elif (
        result.get("partner_sex") == "female"
        and "age_of_patients_female_partner" in ref_claim
        and "service_date" in result
    ):
        # Exact DOB is unavailable. A birthday on the service date reproduces
        # the supplied completed age, which is all the encoding uses.
        try:
            when = date.fromisoformat(result["service_date"].replace("_", "-"))
            age = ref_claim["age_of_patients_female_partner"]
            if type(age) is int and age >= 0:
                year = when.year - age
                day = min(when.day, calendar.monthrange(year, when.month)[1])
                birth = date(year, when.month, day)
                result["partner_date_of_birth"] = birth.strftime("%Y_%m_%d")
        except (ValueError, TypeError, AttributeError, OverflowError):
            pass

    if "day_3_fsh_tests" in ref_claim:
        tests = []
        service_date = result.get("service_date")
        for level, test_date, _time in ref_claim["day_3_fsh_tests"]:
            # Canonical YYYY_MM_DD strings sort chronologically.
            if service_date is None or test_date <= service_date:
                tests.append({"date": test_date, "value_miu_ml": level})
        result["unmedicated_day3_fsh_tests"] = tests

    # No reference fields establish specialist status, plan enrollment,
    # covered relationship, gender dysphoria, or semen-analysis results.
    return result
