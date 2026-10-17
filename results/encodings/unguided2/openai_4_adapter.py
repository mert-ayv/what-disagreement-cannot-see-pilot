from calendar import monthrange
from datetime import date


def adapt(ref_claim: dict) -> dict:
    result = {}

    def copy(source, target):
        if source in ref_claim:
            result[target] = ref_claim[source]

    def yes_no(source, target):
        if source in ref_claim:
            value = ref_claim[source]
            if value == "yes":
                result[target] = True
            elif value == "no":
                result[target] = False

    copy("date_service_received", "service_date")
    copy("patient_dob", "patient_birth_date")
    copy("sex_of_patient_trying_to_conceive", "patient_sex")

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
            result["partner_birth_date"] = None

    if (
        ref_claim.get("sex_of_patients_partner") == "female"
        and "age_of_patients_female_partner" in ref_claim
        and "date_service_received" in ref_claim
    ):
        service_date = date(
            *map(int, ref_claim["date_service_received"].split("_"))
        )
        age = ref_claim["age_of_patients_female_partner"]

        # Age does not identify an exact DOB. Choose a representative birthday
        # yielding the supplied age on the service date.
        year = service_date.year - age
        day = min(service_date.day, monthrange(year, service_date.month)[1])
        result["partner_birth_date"] = (
            f"{year:04d}_{service_date.month:02d}_{day:02d}"
        )

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        result["infertility_causing_condition_recognized_and_documented"] = True
        result[
            "patient_or_partner_infertility_due_to_natural_physiologic_process"
        ] = condition in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    sterilization = ref_claim.get("patient_has_had_voluntary_sterilization")
    if sterilization == "yes":
        result["patient_or_partner_voluntarily_sterilized"] = True
    # A patient's "no" does not establish that their partner was not sterilized.
    elif sterilization == "no" and result.get("partner_sex") == "none":
        result["patient_or_partner_voluntarily_sterilized"] = False

    yes_no(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan",
        "successful_pregnancy_possible_with_less_costly_covered_treatment",
    )

    intercourse_fields = (
        "num_months_timed_unprotected_intercourse",
        "num_months_frequent_unprotected_heterosexual_intercourse",
    )
    if all(field in ref_claim for field in intercourse_fields):
        # The target combines both qualifications into a single duration.
        result["unsuccessful_intercourse_months"] = min(
            ref_claim[field] for field in intercourse_fields
        )

    if "num_cycles_donor_insemination" in ref_claim:
        cycles = ref_claim["num_cycles_donor_insemination"]
        result["unsuccessful_donor_insemination_cycles"] = cycles
        result["self_paid_unsuccessful_donor_insemination_cycles"] = cycles

    if "day_3_fsh_tests" in ref_claim:
        result["unmedicated_day3_fsh_tests"] = [
            {"date": test_date, "value_miu_ml": level}
            for level, test_date, _time in ref_claim["day_3_fsh_tests"]
        ]

    # No reference information establishes specialist status, coverage
    # relationship, semen-analysis dates, or a gender-dysphoria diagnosis.
    # Leave those fields absent rather than inventing values.
    return result
