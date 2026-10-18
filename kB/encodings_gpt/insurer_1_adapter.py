import calendar
from datetime import datetime, date

ASSUMED_MET = [
    "charges_made_by_infertility_specialist",
    "covered_under_plan",
    "coverage_role",
    "condition_recognized_by_required_clinician",
    "failure_to_become_pregnant",
]


def adapt(ref_claim: dict) -> dict:
    claim = {
        "charges_made_by_infertility_specialist": True,
        "covered_under_plan": True,
        "coverage_role": "student",
        "condition_recognized_by_required_clinician": True,
        # Counts of attempts alone do not establish their outcomes.
        "failure_to_become_pregnant": True,
    }

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            return datetime.strptime(value, "%Y_%m_%d").date()
        except ValueError:
            return None

    def format_date(value):
        return f"{value.year:04d}_{value.month:02d}_{value.day:02d}"

    def yes_no(field):
        return {"yes": True, "no": False}.get(ref_claim.get(field))

    direct = {
        "date_service_received": "service_date",
        "patient_dob": "patient_birth_date",
        "sex_of_patient_trying_to_conceive": "patient_sex",
        "num_months_timed_unprotected_intercourse":
            "unprotected_timed_intercourse_months",
        "num_months_frequent_unprotected_heterosexual_intercourse":
            "frequent_unprotected_heterosexual_intercourse_months",
        "num_cycles_donor_insemination":
            "donor_insemination_cycles_not_paid_by_plan",
    }
    for source, target in direct.items():
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
        claim["partner_sex"] = {
            "female": "female",
            "male": "male",
            "no_partner": "none",
        }.get(partner, "other")

    on = parse_date(ref_claim.get("date_service_received"))
    birth = parse_date(ref_claim.get("patient_dob"))

    partner_age = ref_claim.get("age_of_patients_female_partner")
    if (
        on is not None
        and type(partner_age) is int
        and partner_age >= 0
        and 1 <= on.year - partner_age <= 9999
    ):
        # Exact DOB is unavailable. This representative DOB preserves the
        # supplied age on the service date, which is all the rule uses.
        year = on.year - partner_age
        day = min(on.day, calendar.monthrange(year, on.month)[1])
        claim["partner_birth_date"] = format_date(date(year, on.month, day))

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        claim["condition_demonstrated_to_cause_infertility"] = True
        claim["condition_documented_in_patient_or_partner_record"] = True
        claim["either_has_infertility_due_to_natural_physiologic_process"] = (
            condition in {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
        )

    patient_sterilized = yes_no("patient_has_had_voluntary_sterilization")
    partner_sterilized = yes_no("partner_has_had_voluntary_sterilization")
    no_partner = ref_claim.get("sex_of_patients_partner") == "no_partner"

    if patient_sterilized is True or (
        not no_partner and partner_sterilized is True
    ):
        claim["either_has_voluntary_sterilization_history"] = True
    elif patient_sterilized is False and (
        no_partner or partner_sterilized is False
    ):
        claim["either_has_voluntary_sterilization_history"] = False

    less_costly = yes_no(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    )
    if less_costly is not None:
        claim[
            "successful_pregnancy_unattainable_with_less_costly_covered_treatment"
        ] = not less_costly

    dysphoria = yes_no("patient_or_partner_diagnosed_with_gender_dysphoria")
    if dysphoria is not None:
        claim[
            "patient_or_partner_clinically_diagnosed_gender_dysphoria"
        ] = dysphoria

    if "day_3_fsh_tests" in ref_claim and on is not None:
        tests = []
        for level, tested_date, tested_time in ref_claim["day_3_fsh_tests"]:
            tested = parse_date(tested_date)
            if tested is not None and tested <= on:
                tests.append((tested, tested_time, level))

        if tests:
            # The reference allows duplicate timestamps. Use the highest
            # result among indistinguishably latest tests, conservatively.
            latest = max(tests, key=lambda item: (item[0], item[1], item[2]))
            claim["latest_unmedicated_day3_fsh_date"] = format_date(latest[0])
            claim["latest_unmedicated_day3_fsh_miu_ml"] = latest[2]

        if birth is not None:
            def age_on(tested):
                return tested.year - birth.year - (
                    (tested.month, tested.day) < (birth.month, birth.day)
                )

            claim[
                "all_unmedicated_day3_fsh_tests_at_or_after_40_below_19"
            ] = all(
                type(level) in (int, float) and 0 <= level < 19
                for tested, _, level in tests
                if age_on(tested) >= 40
            )

    return claim
