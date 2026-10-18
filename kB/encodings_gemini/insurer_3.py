"""
READING CHOICES:

# READING: Infertility definition for female with male partner using donor insemination.
Text: Glossary defines infertility "For a female with a male partner, after: 1 year of frequent,
unprotected heterosexual sexual intercourse if under the age of 35; 6 months... if age 35 or older"
or diagnosis of gender dysphoria. The table lists "A. 12 months or more or B. At least 12 cycles of
donor insemination". Under the reading most favourable to the insurer, donor insemination alone does
not satisfy the glossary definition of infertility for a female with a male partner unless there is a
clinical diagnosis of gender dysphoria.

# READING: Males without a female partner are not eligible for comprehensive infertility services.
Text: The table setting eligibility requirements under Comprehensive Infertility Services lists
categories only for females (with or without a male partner) and males with a female partner.
Under the reading most favourable to the insurer, satisfying the criteria in the table is an absolute
prerequisite ("Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following
criteria: [table]"). Because no criteria exist for a male without a female partner, such claims cannot
satisfy the benefit requirements and are not covered.

# READING: Gender dysphoria diagnosis does not waive text or table eligibility criteria.
Text: "You are eligible for infertility services if: ... You have met the requirement for the number
of months trying to conceive through egg and sperm contact. Your unmedicated day 3 Follicle Stimulating
Hormone (FSH) level meets the following criteria: [table]".
Glossary: "Infertile or infertility: A disease defined by the failure to become pregnant: ... For an
individual or their partner who has been clinically diagnosed with gender dysphoria".
Under the reading most favourable to the insurer, gender dysphoria establishes the threshold status
of infertility under the glossary, but does not exempt the member from any of the eligibility
requirements in the policy text, including the required duration/cycles trying to conceive and FSH testing.

# READING: FSH requirements for females age 40 and older.
Text: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40."
And Column 4 requires an unmedicated day 3 FSH test done within the past 6 months.
Under the reading most favourable to the insurer, a female claimant age 40 or older must have had a test
within the past 6 months, and every test performed after age 40 (including the most recent test) must be
strictly less than 19 mIU/mL.

# READING: Infertility specialist provider requirement.
Text: "We will cover charges made by an infertility specialist for the following infertility services..."
Under the reading most favourable to the insurer, coverage is restricted to services rendered by an
infertility specialist.

# READING: Donor insemination self-paid requirement.
Text: "Number of donor artificial insemination cycles: Self paid/not paid for by plan"
Under the reading most favourable to the insurer, donor insemination cycles only count if they were
self-paid and not paid for by the plan.

# READING: Covered services restricted to specified treatments.
Text: "We will cover charges made by an infertility specialist for the following infertility services:
• Ovulation induction cycle(s) with menotropins • Intrauterine insemination"
Under the reading most favourable to the insurer, ovulation induction cycles using medications other than
menotropins are not covered under comprehensive infertility services.
"""

SCHEMA = {
    "patient_is_covered_student_or_dependent_partner": {
        "description": "Whether the patient is covered under the plan as a student or as an eligible dependent partner (legal spouse, civil union partner, or domestic partner).",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "condition_causing_infertility_documented": {
        "description": "Whether there exists a condition demonstrated to cause infertility, recognized by a physician or infertility specialist, and documented in medical records.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_prior_voluntary_sterilization": {
        "description": "Whether the patient or their partner has had a voluntary sterilization (e.g. tubal ligation, hysterectomy, vasectomy obtained as voluntary sterilization), with or without surgical reversal.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Whether the infertility of the patient or partner is due to a natural physiologic process such as age-related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": "Whether a successful pregnancy can be attained through less costly treatment for which coverage is available under this plan.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "service_type": {
        "description": "The specific comprehensive infertility service for which coverage is claimed.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the provider rendering the service is an infertility specialist.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_sex": {
        "description": "Biological sex of the patient.",
        "type": "str",
        "allowed_values": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of the patient in years at the time of service.",
        "type": "int",
        "allowed_values": "integer >= 0",
    },
    "partner_sex": {
        "description": "Biological sex of the patient's partner, or 'none' if the patient has no partner.",
        "type": "str",
        "allowed_values": ["male", "female", "none"],
    },
    "partner_age": {
        "description": "Age of the patient's partner in years at the time of service, if applicable.",
        "type": "int",
        "allowed_values": "integer >= 0 or None",
    },
    "has_gender_dysphoria_diagnosis": {
        "description": "Whether the patient or their partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "months_of_unprotected_timed_intercourse": {
        "description": "Number of months of frequent, unprotected timed heterosexual sexual intercourse trying to conceive.",
        "type": "int",
        "allowed_values": "integer >= 0",
    },
    "donor_insemination_cycles_self_paid": {
        "description": "Number of donor artificial insemination cycles completed that were self-paid and not paid for by the plan.",
        "type": "int",
        "allowed_values": "integer >= 0",
    },
    "male_has_two_abnormal_semen_analyses_two_weeks_apart": {
        "description": "For a male without a female partner, whether at least 2 abnormal semen analyses were obtained at least 2 weeks apart.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "fsh_test_done_within_required_timeframe": {
        "description": "Whether an unmedicated day 3 FSH test was performed within the required period (past 12 months if female patient is under 35; past 6 months if female patient is 35 or older).",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "most_recent_fsh_level": {
        "description": "The result of the female patient's most recent unmedicated day 3 FSH test in mIU/mL.",
        "type": "float",
        "allowed_values": "float >= 0.0",
    },
    "all_fsh_tests_after_age_40_under_19": {
        "description": "For female patients age 40 or older, whether all prior and current unmedicated day 3 FSH tests performed after age 40 were strictly less than 19 mIU/mL.",
        "type": "bool",
        "allowed_values": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    # 1. Plan eligibility and general benefit exclusions
    if claim.get("patient_is_covered_student_or_dependent_partner") is not True:
        return False
    if claim.get("condition_causing_infertility_documented") is not True:
        return False
    if claim.get("has_prior_voluntary_sterilization") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    # 2. Covered services and provider type
    if claim.get("provider_is_infertility_specialist") is not True:
        return False
    covered_services = {
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    }
    if claim.get("service_type") not in covered_services:
        return False

    patient_sex = claim.get("patient_sex")
    patient_age = claim.get("patient_age")
    partner_sex = claim.get("partner_sex")
    partner_age = claim.get("partner_age")

    if patient_sex not in {"female", "male"} or patient_age is None or partner_sex is None:
        return False

    has_gd = claim.get("has_gender_dysphoria_diagnosis", False)
    months_intercourse = claim.get("months_of_unprotected_timed_intercourse", 0)
    donor_cycles = claim.get("donor_insemination_cycles_self_paid", 0)

    # 3. Infertility definition under Glossary & Table criteria evaluation
    if patient_sex == "female":
        has_male_partner = partner_sex == "male"

        if patient_age < 35:
            # Glossary check
            if has_male_partner:
                # READING: female with male partner requires 1 year intercourse or GD for glossary infertility
                is_infertile = has_gd or (months_intercourse >= 12)
            else:
                is_infertile = has_gd or (donor_cycles >= 12)

            if not is_infertile:
                return False

            # Table criteria check
            if has_male_partner:
                trying_met = (months_intercourse >= 12) or (donor_cycles >= 12)
            else:
                trying_met = donor_cycles >= 12

            if not trying_met:
                return False

            # FSH test requirements (under 35: within past 12 months, < 19 mIU/mL)
            if claim.get("fsh_test_done_within_required_timeframe") is not True:
                return False
            fsh_level = claim.get("most_recent_fsh_level")
            if fsh_level is None or fsh_level >= 19.0:
                return False

        else:  # patient_age >= 35
            # Glossary check
            if has_male_partner:
                # READING: female with male partner requires 6 months intercourse or GD for glossary infertility
                is_infertile = has_gd or (months_intercourse >= 6)
            else:
                is_infertile = has_gd or (donor_cycles >= 6)

            if not is_infertile:
                return False

            # Table criteria check
            if has_male_partner:
                trying_met = (months_intercourse >= 6) or (donor_cycles >= 6)
            else:
                trying_met = donor_cycles >= 6

            if not trying_met:
                return False

            # FSH test requirements (35 and older: within past 6 months)
            if claim.get("fsh_test_done_within_required_timeframe") is not True:
                return False
            fsh_level = claim.get("most_recent_fsh_level")
            if fsh_level is None or fsh_level >= 19.0:
                return False

            if patient_age >= 40:
                # READING: all prior and current tests after age 40 must be < 19 mIU/mL
                if claim.get("all_fsh_tests_after_age_40_under_19") is not True:
                    return False

        return True

    else:  # patient_sex == "male"
        # READING: Males without a female partner are not eligible as they have no table criteria
        if partner_sex != "female":
            return False

        if partner_age is None:
            return False

        if partner_age < 35:
            # Glossary check (female partner under 35 needs 1 year heterosexual intercourse or GD)
            is_infertile = has_gd or (months_intercourse >= 12)
            if not is_infertile:
                return False

            # Table criteria check (Row 5: 12 months or more intercourse, FSH does not apply)
            if months_intercourse < 12:
                return False

            return True

        else:  # partner_age >= 35
            # Glossary check (female partner 35 or older needs 6 months heterosexual intercourse or GD)
            is_infertile = has_gd or (months_intercourse >= 6)
            if not is_infertile:
                return False

            # Table criteria check (Row 6: 6 months or more intercourse, FSH does not apply)
            if months_intercourse < 6:
                return False

            return True
