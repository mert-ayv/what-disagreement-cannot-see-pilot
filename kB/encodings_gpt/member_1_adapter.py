from datetime import datetime
from math import isfinite


ASSUMED_MET = [
    "billed_by_infertility_specialist",
    "covered_person_category",
    "condition_recognized_by_physician_or_specialist",
    "partner_has_natural_process_infertility",
]


def adapt(ref_claim: dict) -> dict:
    out = {
        "billed_by_infertility_specialist": True,
        "covered_person_category": "student",
        "condition_recognized_by_physician_or_specialist": True,
        # The reference has no separate diagnosis of the partner's
        # natural-process infertility.
        "partner_has_natural_process_infertility": False,
    }

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            result = datetime.strptime(value, "%Y_%m_%d").date()
        except ValueError:
            return None
        return result if result.strftime("%Y_%m_%d") == value else None

    def nonnegative_int(value):
        return type(value) is int and value >= 0

    def map_yes_no(source, target, invert=False):
        value = ref_claim.get(source)
        if value in ("yes", "no"):
            result = value == "yes"
            out[target] = not result if invert else result

    if "service_type" in ref_claim:
        service = ref_claim["service_type"]
        out["service_type"] = {
            "intrauterine_insemination": "intrauterine_insemination",
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
        }.get(service, "other")

    patient = ref_claim.get("sex_of_patient_trying_to_conceive")
    if patient in ("female", "male"):
        out["patient_category"] = patient

    partner = ref_claim.get("sex_of_patients_partner")
    if partner in ("female", "male", "no_partner"):
        out["partner_category"] = (
            "none" if partner == "no_partner" else partner
        )

    partner_age = ref_claim.get("age_of_patients_female_partner")
    if nonnegative_int(partner_age):
        out["female_partner_age"] = partner_age

    service_date = parse_date(ref_claim.get("date_service_received"))
    dob = parse_date(ref_claim.get("patient_dob"))

    if service_date is not None:
        out["service_date"] = service_date.strftime("%Y_%m_%d")

    if dob is not None and service_date is not None and dob <= service_date:
        out["patient_age"] = (
            service_date.year
            - dob.year
            - ((service_date.month, service_date.day) < (dob.month, dob.day))
        )

    map_yes_no(
        "patient_has_had_voluntary_sterilization",
        "patient_had_voluntary_sterilization",
    )
    map_yes_no(
        "partner_has_had_voluntary_sterilization",
        "partner_had_voluntary_sterilization",
    )
    map_yes_no(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan",
        "cannot_achieve_pregnancy_with_less_costly_covered_treatment",
        invert=True,
    )
    map_yes_no(
        "patient_or_partner_diagnosed_with_gender_dysphoria",
        "patient_or_partner_has_clinically_diagnosed_gender_dysphoria",
    )

    condition = ref_claim.get(
        "demonstrated_and_documented_condition_causing_infertility"
    )
    natural_conditions = {
        "natural_menopause",
        "natural_perimenopause",
        "natural_male_reproductive_aging",
        "other_natural_physiologic_process",
    }
    if condition in natural_conditions or condition == "other":
        out["condition_demonstrated_to_cause_infertility"] = True
        out["condition_documented_in_either_record"] = True
        out["patient_has_natural_process_infertility"] = (
            condition in natural_conditions
        )

    # The target combines the reference's timing and frequency requirements.
    timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    frequent = ref_claim.get(
        "num_months_frequent_unprotected_heterosexual_intercourse"
    )
    if nonnegative_int(timed) and nonnegative_int(frequent):
        out["unsuccessful_intercourse_months"] = min(timed, frequent)
    elif (
        (nonnegative_int(timed) and timed == 0)
        or (nonnegative_int(frequent) and frequent == 0)
    ):
        out["unsuccessful_intercourse_months"] = 0

    donor_cycles = ref_claim.get("num_cycles_donor_insemination")
    if nonnegative_int(donor_cycles):
        out["unsuccessful_donor_cycles_not_paid_by_plan"] = donor_cycles
        # This is a known subset, not necessarily the total donor-cycle
        # count. The encoding explicitly accepts the subset as evidence.

    analyses = ref_claim.get("abnormal_semen_analyses")
    if isinstance(analyses, list):
        out["abnormal_semen_analysis_dates"] = [
            value for value in analyses if parse_date(value) is not None
        ]

    tests = ref_claim.get("day_3_fsh_tests")
    if isinstance(tests, list) and service_date is not None:
        parsed_tests = []
        complete = True

        for test in tests:
            if not isinstance(test, (tuple, list)) or len(test) != 3:
                complete = False
                continue

            level, date_text, time_text = test
            test_date = parse_date(date_text)
            if test_date is None:
                complete = False
                continue
            if test_date > service_date:
                continue

            try:
                test_time = datetime.strptime(time_text, "%H_%M").time()
                if test_time.strftime("%H_%M") != time_text:
                    raise ValueError
            except (TypeError, ValueError):
                complete = False
                continue

            if (
                type(level) not in (int, float)
                or not isfinite(level)
                or level < 0
            ):
                complete = False
                continue

            parsed_tests.append((test_date, test_time, level))

        if complete and parsed_tests:
            latest_stamp = max((d, t) for d, t, _ in parsed_tests)
            out["latest_unmedicated_day3_fsh_date"] = (
                latest_stamp[0].strftime("%Y_%m_%d")
            )
            latest_values = {
                level
                for d, t, level in parsed_tests
                if (d, t) == latest_stamp
            }
            # Conflicting results at an identical timestamp do not identify
            # a unique most recent result.
            if len(latest_values) == 1:
                out["latest_unmedicated_day3_fsh_value"] = (
                    latest_values.pop()
                )

        if not tests:
            out["all_fsh_tests_at_age_40_or_older_below_19"] = True
        elif dob is not None:
            older_tests = [
                level
                for d, _, level in parsed_tests
                if (
                    d.year
                    - dob.year
                    - ((d.month, d.day) < (dob.month, dob.day))
                ) >= 40
            ]
            if any(level >= 19 for level in older_tests):
                out["all_fsh_tests_at_age_40_or_older_below_19"] = False
            elif complete:
                out["all_fsh_tests_at_age_40_or_older_below_19"] = True

    return out
