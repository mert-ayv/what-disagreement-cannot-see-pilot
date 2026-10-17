from datetime import date
import calendar


def adapt(ref_claim: dict) -> dict:
    result = {}

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "unprotected_timed_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "frequent_unprotected_intercourse_months",
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
        result["partner_sex"] = (
            "none" if partner == "no_partner" else partner
        )
        if partner == "no_partner":
            result["partner_birth_date"] = None

    if (
        ref_claim.get("sex_of_patients_partner") == "female"
        and "age_of_patients_female_partner" in ref_claim
        and "date_service_received" in ref_claim
    ):
        on = date(
            *map(int, ref_claim["date_service_received"].split("_"))
        )
        age = ref_claim["age_of_patients_female_partner"]
        year = on.year - age
        day = min(on.day, calendar.monthrange(year, on.month)[1])

        # Exact DOB is unknown. This representative DOB reproduces the
        # reported age on the service date, which is all the encoding uses.
        result["partner_birth_date"] = (
            f"{year:04d}_{on.month:02d}_{day:02d}"
        )

    if "num_cycles_donor_insemination" in ref_claim:
        cycles = ref_claim["num_cycles_donor_insemination"]
        # The reference count includes only self-paid / non-plan-paid cycles.
        result["donor_insemination_cycles"] = cycles
        result["self_paid_donor_insemination_cycles"] = cycles

    yes_no_fields = {
        "patient_has_had_voluntary_sterilization":
            "either_has_voluntary_sterilization",
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            "pregnancy_attainable_with_less_costly_covered_treatment",
    }
    for source, target in yes_no_fields.items():
        if source in ref_claim:
            value = ref_claim[source]
            if value in ("yes", "no"):
                result[target] = value == "yes"

    condition_field = (
        "demonstrated_and_documented_condition_causing_infertility"
    )
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        result["infertility_causing_condition_demonstrated"] = True
        result["condition_physician_recognized_and_documented"] = True
        result["either_has_natural_physiologic_infertility"] = condition in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    if "day_3_fsh_tests" in ref_claim:
        result["unmedicated_day3_fsh_tests"] = [
            {"date": tested_on, "level_miu_ml": level}
            for level, tested_on, _time in ref_claim["day_3_fsh_tests"]
        ]

    # Plan coverage, covered role, pregnancy failure, abnormal semen
    # analyses, and gender dysphoria cannot be inferred from this interface.
    return result
