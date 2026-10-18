from datetime import datetime
from calendar import monthrange

ASSUMED_MET = [
    "charged_by_infertility_specialist",
    "covered_capacity",
    "partner_natural_process_infertility",
]


def adapt(ref_claim: dict) -> dict:
    claim = {
        "charged_by_infertility_specialist": True,
        "covered_capacity": "student",
        # The reference does not separately describe the partner's cause.
        "partner_natural_process_infertility": False,
    }

    direct_fields = {
        "patient_dob": "patient_birth_date",
        "date_service_received": "service_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "unsuccessful_timed_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "unsuccessful_frequent_intercourse_months",
        "num_cycles_donor_insemination":
            "nonplan_unsuccessful_donor_insemination_cycles",
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
        claim["partner_sex"] = (
            "none" if partner == "no_partner" else partner
        )

    boolean_fields = {
        "patient_has_had_voluntary_sterilization":
            "patient_voluntary_sterilization",
        "partner_has_had_voluntary_sterilization":
            "partner_voluntary_sterilization",
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan":
            "pregnancy_attainable_with_less_costly_covered_treatment",
        "patient_or_partner_diagnosed_with_gender_dysphoria":
            "clinical_gender_dysphoria_patient_or_partner",
    }
    for source, target in boolean_fields.items():
        if source in ref_claim:
            claim[target] = {"yes": True, "no": False}[ref_claim[source]]

    condition_field = (
        "demonstrated_and_documented_condition_causing_infertility"
    )
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        claim["documented_infertility_causing_condition"] = True
        claim["patient_natural_process_infertility"] = condition in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    if (
        "age_of_patients_female_partner" in ref_claim
        and "date_service_received" in ref_claim
    ):
        service_day = datetime.strptime(
            ref_claim["date_service_received"], "%Y_%m_%d"
        ).date()
        year = (
            service_day.year
            - ref_claim["age_of_patients_female_partner"]
        )
        day = min(
            service_day.day,
            monthrange(year, service_day.month)[1],
        )
        # Representative DOB preserving the known age on the service date;
        # the partner's actual birthday is not supplied.
        claim["partner_birth_date"] = (
            f"{year:04d}_{service_day.month:02d}_{day:02d}"
        )

    if "day_3_fsh_tests" in ref_claim:
        # Keep every result, including results tied on the same date.
        claim["unmedicated_day3_fsh_tests"] = [
            {"date": date, "value": level}
            for level, date, time in ref_claim["day_3_fsh_tests"]
        ]

    if "abnormal_semen_analyses" in ref_claim:
        claim["abnormal_semen_analysis_dates"] = list(
            ref_claim["abnormal_semen_analyses"]
        )

    # The reference supplies only nonplan donor cycles, not the total across
    # all payers. Leave the total unknown; the encoding uses the known subset
    # as a lower bound when evaluating glossary infertility.
    return claim
