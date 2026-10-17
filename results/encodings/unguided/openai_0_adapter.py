import calendar
from datetime import date


def adapt(ref_claim: dict) -> dict:
    claim = {}

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "unprotected_timed_intercourse_months",
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
        partner_sex = ref_claim["sex_of_patients_partner"]
        claim["partner_sex"] = (
            "none" if partner_sex == "no_partner" else partner_sex
        )
        if partner_sex == "no_partner":
            claim["partner_birth_date"] = None

    less_costly = (
        "successful_pregnancy_can_be_attained_through_less_costly_"
        "treatment_covered_by_plan"
    )
    if ref_claim.get(less_costly) in ("yes", "no"):
        claim["pregnancy_attainable_through_less_costly_covered_treatment"] = (
            ref_claim[less_costly] == "yes"
        )

    # A positive patient history establishes the either-partner exclusion.
    # A negative patient history does not establish the partner's history.
    sterilization = ref_claim.get("patient_has_had_voluntary_sterilization")
    if sterilization == "yes":
        claim["either_partner_voluntarily_sterilized"] = True
    elif sterilization == "no" and claim.get("partner_sex") == "none":
        claim["either_partner_voluntarily_sterilized"] = False

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        recognized_conditions = {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
            "other",
        }
        if condition in recognized_conditions:
            claim["patient_is_infertile"] = True
            claim["infertility_causing_condition_demonstrated"] = True
            claim["condition_recognized_and_documented"] = True

            if condition != "other":
                claim["either_partner_infertility_due_to_natural_process"] = True
            elif claim.get("partner_sex") == "none":
                claim["either_partner_infertility_due_to_natural_process"] = False

    if "day_3_fsh_tests" in ref_claim:
        claim["unmedicated_day3_fsh_tests"] = [
            {"date": test_date, "level_miu_ml": level}
            for level, test_date, _time in ref_claim["day_3_fsh_tests"]
        ]

    # Exact partner DOB is unavailable. This representative DOB preserves
    # the supplied completed age on the service date, which is all the
    # encoding uses for the female partner's eligibility threshold.
    if (
        claim.get("partner_sex") == "female"
        and "age_of_patients_female_partner" in ref_claim
        and "service_date" in claim
    ):
        age = ref_claim["age_of_patients_female_partner"]
        if type(age) is int and age >= 0:
            try:
                service_date = date.fromisoformat(
                    claim["service_date"].replace("_", "-")
                )
                year = service_date.year - age
                day = min(
                    service_date.day,
                    calendar.monthrange(year, service_date.month)[1],
                )
                birth = date(year, service_date.month, day)
                claim["partner_birth_date"] = (
                    f"{birth.year:04d}_{birth.month:02d}_{birth.day:02d}"
                )
            except (AttributeError, TypeError, ValueError, OverflowError):
                pass

    # Specialist status and covered role cannot be inferred.
    # Frequent intercourse alone does not establish timed intercourse.
    return claim
