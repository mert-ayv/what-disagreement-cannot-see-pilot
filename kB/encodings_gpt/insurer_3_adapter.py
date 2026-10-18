from datetime import date

ASSUMED_MET = [
    "billed_by_infertility_specialist",
    "covered_role",
    "condition_recognized_by_physician_or_specialist",
    "partner_infertility_due_to_natural_process",
    "failed_to_become_pregnant_during_qualifying_attempts",
]


def adapt(ref_claim: dict) -> dict:
    claim = {
        "billed_by_infertility_specialist": True,
        "covered_role": "student",
        "condition_recognized_by_physician_or_specialist": True,
        # The reference condition describes the patient's infertility;
        # it supplies no separate natural-process history for the partner.
        "partner_infertility_due_to_natural_process": False,
        # Attempt counts do not separately report pregnancy outcomes.
        "failed_to_become_pregnant_during_qualifying_attempts": True,
    }

    def parse_date(value):
        return date(*(int(part) for part in value.split("_")))

    def format_date(value):
        return f"{value.year:04d}_{value.month:02d}_{value.day:02d}"

    def copy_field(source, target):
        if source in ref_claim:
            claim[target] = ref_claim[source]

    def copy_yes_no(source, target, invert=False):
        if source in ref_claim:
            value = ref_claim[source]
            if value in ("yes", "no"):
                answer = value == "yes"
                claim[target] = not answer if invert else answer

    if "service_type" in ref_claim:
        claim["service"] = {
            "intrauterine_insemination": "intrauterine_insemination",
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
        }.get(ref_claim["service_type"], "other")

    copy_field("sex_of_patient_trying_to_conceive", "patient_category")

    if "sex_of_patients_partner" in ref_claim:
        partner = ref_claim["sex_of_patients_partner"]
        claim["partner_category"] = (
            "none" if partner == "no_partner" else partner
        )

    copy_field("age_of_patients_female_partner", "partner_age")
    copy_field("date_service_received", "service_date")
    copy_field(
        "num_months_timed_unprotected_intercourse",
        "months_unprotected_timed_sexual_intercourse",
    )
    copy_field(
        "num_months_frequent_unprotected_heterosexual_intercourse",
        "months_frequent_unprotected_heterosexual_intercourse",
    )
    # The reference reports donor cycles, rather than initiated treatments,
    # and specifies that these cycles are self-paid/not plan-paid.
    copy_field(
        "num_cycles_donor_insemination",
        "completed_self_paid_donor_insemination_cycles",
    )

    copy_yes_no(
        "patient_has_had_voluntary_sterilization",
        "patient_voluntary_sterilization",
    )
    copy_yes_no(
        "partner_has_had_voluntary_sterilization",
        "partner_voluntary_sterilization",
    )
    copy_yes_no(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan",
        "successful_pregnancy_unattainable_through_less_costly_covered_treatment",
        invert=True,
    )
    copy_yes_no(
        "patient_or_partner_diagnosed_with_gender_dysphoria",
        "patient_or_partner_clinically_diagnosed_gender_dysphoria",
    )

    condition_field = "demonstrated_and_documented_condition_causing_infertility"
    if condition_field in ref_claim:
        condition = ref_claim[condition_field]
        claim["condition_demonstrated_to_cause_infertility"] = True
        claim["condition_documented_in_patient_or_partner_records"] = True
        claim["patient_infertility_due_to_natural_process"] = condition in {
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        }

    service_date = None
    if "date_service_received" in ref_claim:
        service_date = parse_date(ref_claim["date_service_received"])

    dob = None
    if "patient_dob" in ref_claim:
        dob = parse_date(ref_claim["patient_dob"])

    if dob is not None and service_date is not None:
        claim["patient_age"] = (
            service_date.year
            - dob.year
            - ((service_date.month, service_date.day) < (dob.month, dob.day))
        )

    if "day_3_fsh_tests" in ref_claim and service_date is not None:
        tests = [
            (parse_date(test_date), test_time, level)
            for level, test_date, test_time in ref_claim["day_3_fsh_tests"]
        ]
        applicable_tests = [
            test for test in tests if test[0] <= service_date
        ]

        if applicable_tests:
            # If timestamps tie, use the highest result rather than hiding
            # an adverse result behind an arbitrary input ordering.
            latest_date, _, latest_value = max(
                applicable_tests,
                key=lambda test: (test[0], test[1], test[2]),
            )
            claim["latest_unmedicated_day3_fsh_date"] = format_date(latest_date)
            claim["latest_unmedicated_day3_fsh_value"] = latest_value

        if dob is not None:
            # Comparing month/day tuples also handles a leap-day birthday
            # without inventing a February 28 anniversary.
            fortieth_year = dob.year + 40
            birthday_key = (fortieth_year, dob.month, dob.day)
            claim[
                "all_unmedicated_day3_fsh_tests_at_or_after_40_below_19"
            ] = all(
                level < 19
                for test_date, _, level in applicable_tests
                if (test_date.year, test_date.month, test_date.day)
                >= birthday_key
            )

    # Abnormal semen analyses do not establish any additional SCHEMA fact.
    return claim
