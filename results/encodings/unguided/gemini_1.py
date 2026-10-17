SCHEMA = {
    "is_student_or_eligible_dependent": (
        "Whether the patient is covered under the plan as a student or as an "
        "eligible dependent (legal spouse, civil union partner, or domestic partner).",
        bool,
        [True, False],
    ),
    "service_type": (
        "The type of infertility service requested.",
        str,
        ["ovulation_induction_with_menotropins", "intrauterine_insemination", "other"],
    ),
    "provider_is_infertility_specialist": (
        "Whether the service charges are made by an infertility specialist.",
        bool,
        [True, False],
    ),
    "has_infertility_condition": (
        "Whether there exists a condition demonstrated to cause infertility, "
        "recognized by a physician or infertility specialist and documented in medical records.",
        bool,
        [True, False],
    ),
    "voluntary_sterilization": (
        "Whether the patient or partner has had a voluntary sterilization "
        "(e.g., tubal ligation, hysterectomy, vasectomy) with or without surgical reversal.",
        bool,
        [True, False],
    ),
    "infertility_due_to_natural_physiologic_process": (
        "Whether infertility is due to a natural physiologic process such as "
        "age-related ovarian insufficiency (e.g., perimenopause, menopause).",
        bool,
        [True, False],
    ),
    "pregnancy_attainable_through_less_costly_treatment": (
        "Whether a successful pregnancy can be attained through less costly "
        "treatment for which coverage is available under this plan.",
        bool,
        [True, False],
    ),
    "patient_gender": (
        "Gender of the patient.",
        str,
        ["female", "male"],
    ),
    "patient_age": (
        "Age of the patient in years.",
        int,
        "non-negative integer",
    ),
    "partner_gender": (
        "Gender of the patient's partner, or 'none' if the patient does not have a partner.",
        str,
        ["female", "male", "none"],
    ),
    "partner_age": (
        "Age of the partner in years, or None if not applicable.",
        (int, type(None)),
        "non-negative integer or None",
    ),
    "months_unprotected_intercourse": (
        "Number of months of timed unprotected sexual intercourse trying to conceive.",
        int,
        "non-negative integer",
    ),
    "donor_insemination_cycles": (
        "Number of donor artificial insemination cycles (self-paid/not paid for by plan).",
        int,
        "non-negative integer",
    ),
    "fsh_test_months_ago": (
        "Number of months since the most recent unmedicated day 3 FSH test was performed, or None if not tested.",
        (int, float, type(None)),
        "non-negative number or None",
    ),
    "fsh_most_recent_result": (
        "Result of the most recent unmedicated day 3 FSH test in mIU/mL, or None if not tested.",
        (int, float, type(None)),
        "non-negative number or None",
    ),
    "all_fsh_tests_after_40_under_19": (
        "For females age 40 and older, whether all prior unmedicated day 3 FSH tests performed after age 40 are < 19 mIU/mL.",
        (bool, type(None)),
        [True, False, None],
    ),
}


def covered_under_benefit(claim: dict) -> bool:
    # Coverage status
    if not claim.get("is_student_or_eligible_dependent", False):
        return False

    # Service must be a covered comprehensive infertility service by an infertility specialist
    covered_services = {
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    }
    if claim.get("service_type") not in covered_services:
        return False
    if not claim.get("provider_is_infertility_specialist", False):
        return False

    # Medical eligibility criteria
    if not claim.get("has_infertility_condition", False):
        return False
    if claim.get("voluntary_sterilization", False):
        return False
    if claim.get("infertility_due_to_natural_physiologic_process", False):
        return False
    if claim.get("pregnancy_attainable_through_less_costly_treatment", False):
        return False

    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age", 0)
    partner_gender = claim.get("partner_gender", "none")
    partner_age = claim.get("partner_age")
    months_intercourse = claim.get("months_unprotected_intercourse", 0)
    donor_cycles = claim.get("donor_insemination_cycles", 0)
    fsh_months_ago = claim.get("fsh_test_months_ago")
    fsh_recent_result = claim.get("fsh_most_recent_result")
    all_fsh_after_40_under_19 = claim.get("all_fsh_tests_after_40_under_19")

    # Table categories evaluation
    if patient_gender == "female":
        has_male_partner = partner_gender == "male"

        if patient_age < 35:
            # Trying to conceive requirement
            if has_male_partner:
                if not (months_intercourse >= 12 or donor_cycles >= 12):
                    return False
            else:
                if not (donor_cycles >= 12):
                    return False

            # FSH test recency: within the past 12 months
            if fsh_months_ago is None or fsh_months_ago > 12:
                return False

            # FSH test result: most recent < 19 mIU/mL
            if fsh_recent_result is None or fsh_recent_result >= 19:
                return False

            return True

        else:  # Female 35 years of age or older
            # Trying to conceive requirement
            if has_male_partner:
                if not (months_intercourse >= 6 or donor_cycles >= 6):
                    return False
            else:
                if not (donor_cycles >= 6):
                    return False

            # FSH test recency: within the past 6 months
            if fsh_months_ago is None or fsh_months_ago > 6:
                return False

            # FSH test results based on age
            if patient_age < 40:
                if fsh_recent_result is None or fsh_recent_result >= 19:
                    return False
            else:  # Age 40 and older
                if not all_fsh_after_40_under_19:
                    return False

            return True

    elif patient_gender == "male":
        # Male of any age with a female partner
        if partner_gender != "female" or partner_age is None:
            return False

        if partner_age < 35:
            return months_intercourse >= 12
        else:  # Female partner 35 or older
            return months_intercourse >= 6

    return False
