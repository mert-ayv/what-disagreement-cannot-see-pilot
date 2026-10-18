from datetime import datetime

ASSUMED_MET = [
    "enrollment",
    "charged_by_infertility_specialist",
    "partner_natural_process_infertility",
]


def adapt(ref_claim: dict) -> dict:
    result = {
        "enrollment": "covered_student",
        "charged_by_infertility_specialist": True,
        # The reference does not separately describe the partner's cause
        # of infertility.
        "partner_natural_process_infertility": False,
    }

    def known(name):
        return name in ref_claim and ref_claim[name] is not None

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            return datetime.strptime(value, "%Y_%m_%d").date()
        except ValueError:
            return None

    def age_on(dob, day):
        return (
            day.year
            - dob.year
            - ((day.month, day.day) < (dob.month, dob.day))
        )

    def copy_field(source, target):
        if known(source):
            result[target] = ref_claim[source]

    def copy_yes_no(source, target):
        value = ref_claim.get(source)
        if value in ("yes", "no"):
            result[target] = value == "yes"

    copy_field("date_service_received", "assessment_date")
    copy_field("sex_of_patient_trying_to_conceive", "patient_sex")
    copy_field("age_of_patients_female_partner", "partner_age")
    copy_field("num_cycles_donor_insemination",
               "nonplan_donor_insemination_cycles")

    if known("sex_of_patients_partner"):
        partner = ref_claim["sex_of_patients_partner"]
        result["partner_sex"] = (
            "none" if partner == "no_partner" else partner
        )

    if known("service_type"):
        result["service"] = {
            "intrauterine_insemination": "intrauterine_insemination",
            "ovulation_induction_cycle_with_menotropins":
                "ovulation_induction_with_menotropins",
        }.get(ref_claim["service_type"], "other")

    dob = parse_date(ref_claim.get("patient_dob"))
    assessment = parse_date(ref_claim.get("date_service_received"))
    if dob is not None and assessment is not None and dob <= assessment:
        result["patient_age"] = age_on(dob, assessment)

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
        "covered_less_costly_treatment_can_achieve_pregnancy",
    )

    condition_field = (
        "demonstrated_and_documented_condition_causing_infertility"
    )
    if known(condition_field):
        result["qualifying_condition"] = True
        result["patient_natural_process_infertility"] = (
            ref_claim[condition_field] in {
                "natural_menopause",
                "natural_perimenopause",
                "natural_male_reproductive_aging",
                "other_natural_physiologic_process",
            }
        )

    # Both descriptions contribute to the encoding's combined intercourse
    # requirement. A missing counter does not establish that requirement.
    intercourse_fields = (
        "num_months_timed_unprotected_intercourse",
        "num_months_frequent_unprotected_heterosexual_intercourse",
    )
    counts = [ref_claim[name] for name in intercourse_fields if known(name)]
    if len(counts) == 2:
        result["unsuccessful_intercourse_months"] = min(counts)
    elif counts and counts[0] == 0:
        result["unsuccessful_intercourse_months"] = 0

    dysphoria = ref_claim.get(
        "patient_or_partner_diagnosed_with_gender_dysphoria"
    )
    if dysphoria == "no":
        result["patient_gender_dysphoria_diagnosed"] = False
        result["partner_gender_dysphoria_diagnosed"] = False
    elif dysphoria == "yes":
        # The source supplies only a disjunction, not the person's identity.
        # The encoding only uses these fields disjunctively, so carry that
        # aggregate attestation through its patient-side representative.
        result["patient_gender_dysphoria_diagnosed"] = True

    if known("abnormal_semen_analyses"):
        result["abnormal_semen_analysis_dates"] = list(
            ref_claim["abnormal_semen_analyses"]
        )

    if known("day_3_fsh_tests"):
        tests = []
        for level, date_string, _time in ref_claim["day_3_fsh_tests"]:
            tested = parse_date(date_string)
            if (
                assessment is not None
                and tested is not None
                and tested > assessment
            ):
                continue

            test = {"date": date_string}
            if level is not None:
                test["result_miu_ml"] = level
            if dob is not None and tested is not None and dob <= tested:
                test["age_at_test"] = age_on(dob, tested)
            tests.append(test)

        result["fsh_tests"] = tests

    return result
