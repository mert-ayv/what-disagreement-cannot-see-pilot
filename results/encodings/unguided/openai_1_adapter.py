from calendar import monthrange
from datetime import datetime


def adapt(ref_claim: dict) -> dict:
    claim = {}

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "completed_months_unprotected_timed_intercourse",
        "num_cycles_donor_insemination":
            "self_paid_donor_insemination_cycles",
    }
    for source, target in direct_fields.items():
        if source in ref_claim:
            claim[target] = ref_claim[source]

    if "service_type" in ref_claim:
        claim["service"] = {
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
            "intrauterine_insemination": "intrauterine_insemination",
        }.get(ref_claim["service_type"], "other")

    if "sex_of_patients_partner" in ref_claim:
        partner_sex = ref_claim["sex_of_patients_partner"]
        claim["partner_sex"] = (
            None if partner_sex == "no_partner" else partner_sex
        )
        if partner_sex != "female":
            claim["partner_birth_date"] = None

    # An age does not determine an exact DOB. This representative DOB
    # preserves the reported completed age on the service date, which is
    # all the encoding uses for a female partner.
    if (
        ref_claim.get("sex_of_patients_partner") == "female"
        and "age_of_patients_female_partner" in ref_claim
        and "date_service_received" in ref_claim
    ):
        age = ref_claim["age_of_patients_female_partner"]
        if type(age) is int and age >= 0:
            try:
                service_date = datetime.strptime(
                    ref_claim["date_service_received"], "%Y_%m_%d"
                ).date()
                year = service_date.year - age
                if 1 <= year <= 9999:
                    month = service_date.month
                    day = min(service_date.day, monthrange(year, month)[1])
                    claim["partner_birth_date"] = (
                        f"{year:04d}_{month:02d}_{day:02d}"
                    )
            except (TypeError, ValueError, OverflowError):
                pass

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        known_conditions = {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
            "other",
        }
        if condition in known_conditions:
            claim["condition_demonstrated_to_cause_infertility"] = True
            claim["condition_documented_in_patient_or_partner_records"] = True
            claim[
                "patient_or_partner_infertility_due_to_natural_physiologic_process"
            ] = condition != "other"

    # A patient's positive history establishes the aggregate positive.
    # A patient's negative history does not rule out partner sterilization.
    if ref_claim.get("patient_has_had_voluntary_sterilization") == "yes":
        claim["patient_or_partner_had_voluntary_sterilization"] = True

    less_costly_field = (
        "successful_pregnancy_can_be_attained_through_less_costly_"
        "treatment_covered_by_plan"
    )
    if less_costly_field in ref_claim:
        value = ref_claim[less_costly_field]
        if value in ("yes", "no"):
            claim[
                "successful_pregnancy_attainable_with_less_costly_covered_treatment"
            ] = value == "yes"

    if "day_3_fsh_tests" in ref_claim:
        claim["unmedicated_day3_fsh_tests"] = [
            {"test_date": test_date, "fsh_miu_ml": level}
            for level, test_date, _time in ref_claim["day_3_fsh_tests"]
        ]

    # Frequent intercourse is not necessarily timed intercourse.
    # Provider specialty, coverage relationship, and physician recognition
    # have no reference counterparts and cannot be inferred.
    return claim
