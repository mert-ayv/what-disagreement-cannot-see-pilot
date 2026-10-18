"""
Policy Reading Choices:

1. READING: Covered comprehensive infertility services
   Text: "We will cover charges made by an infertility specialist for the following
   infertility services: • Ovulation induction cycle(s) with menotropins • Intrauterine
   insemination"
   Reading: Only ovulation induction with menotropins and intrauterine insemination performed
   by an infertility specialist are covered comprehensive infertility services under this
   benefit.

2. READING: Clinical diagnosis of gender dysphoria
   Text: Glossary: "Infertile or infertility: A disease defined by the failure to become pregnant:
   ... • For an individual or their partner who has been clinically diagnosed with gender dysphoria"
   Reading: Reading most favorably to the member, a documented clinical diagnosis of gender
   dysphoria in the individual or their partner establishes infertility and satisfies the
   requirement for trying to conceive through egg and sperm contact without requiring a waiting
   period of timed intercourse or donor insemination. For female patients receiving treatment,
   the objective day 3 FSH test requirement still applies to confirm ovarian reserve.

3. READING: Donor insemination for females with male partners
   Text: Table: "A female under 35 years of age with a male partner: A. 12 months or more or
   B. At least 12 cycles of donor insemination" (and 6 months / 6 cycles for age 35 or older).
   Glossary: "For a female with a male partner, after: 1 year of frequent, unprotected
   heterosexual sexual intercourse if under the age of 35 [6 months if 35 or older]".
   Reading: Reading the policy and glossary harmoniously and most favorably to the member,
   donor artificial insemination cycles satisfy the requirement for establishing infertility
   and egg/sperm contact for a female with a male partner (e.g., in cases of male factor
   infertility), matching the explicit criteria in the coverage table.

4. READING: Definition of "without a male partner"
   Text: Table: "A female under 35 years of age without a male partner" / "A female 35 years
   of age or older without a male partner".
   Reading: "Without a male partner" applies both to single females and to females with a
   female or non-male partner.

5. READING: FSH test criteria for females age 40 and older
   Text: Table: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests
   performed after age 40."
   Reading: Reading most favorably to the member, this requires that the most recent test
   performed within the past 6 months must be less than 19 mIU/mL, and any prior tests
   performed after age 40 (if any were performed) must also have been less than 19 mIU/mL.
   If no tests prior to the current one were performed after age 40, the condition is satisfied
   as long as the current test is less than 19 mIU/mL.
"""

SCHEMA = {
    "patient_is_covered_student_or_partner": {
        "description": "Whether the patient is covered under the plan as a student or as an eligible covered partner (spouse, civil union partner, or domestic partner)",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "service_type": {
        "description": "The specific infertility service being claimed",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the charges are made by a recognized infertility specialist",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_documented_infertility_condition": {
        "description": "Whether a condition demonstrated to cause infertility has been recognized by a physician/specialist and documented in medical records",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_voluntary_sterilization": {
        "description": "Whether the patient or partner has had a voluntary sterilization (e.g., tubal ligation, vasectomy, hysterectomy as sterilization) with or without reversal",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Whether infertility is due to a natural physiologic process such as age-related ovarian insufficiency (e.g., perimenopause, menopause)",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": "Whether a successful pregnancy can be attained through less costly treatment for which coverage is available under the plan",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_gender_dysphoria_diagnosis": {
        "description": "Whether the patient or their partner has been clinically diagnosed with gender dysphoria",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_gender": {
        "description": "Legal/clinical gender of the patient receiving the service",
        "type": "str",
        "allowed_values": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of the patient in years at the time of service",
        "type": "int",
        "allowed_values": "non-negative integer",
    },
    "partner_gender": {
        "description": "Gender of the patient's partner, or 'none' if the patient does not have a partner",
        "type": "str",
        "allowed_values": ["male", "female", "none"],
    },
    "partner_age": {
        "description": "Age of the partner in years, if applicable",
        "type": "int",
        "allowed_values": "non-negative integer",
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of frequent, unprotected timed heterosexual intercourse trying to conceive",
        "type": "int",
        "allowed_values": "non-negative integer",
    },
    "donor_insemination_cycles": {
        "description": "Number of self-paid donor artificial insemination cycles not paid for by the plan",
        "type": "int",
        "allowed_values": "non-negative integer",
    },
    "fsh_test_done_within_months": {
        "description": "Number of months prior to the request that the most recent unmedicated day 3 FSH test was performed",
        "type": "int",
        "allowed_values": "non-negative integer",
    },
    "most_recent_fsh_level": {
        "description": "Result of the most recent unmedicated day 3 FSH test in mIU/mL",
        "type": "float",
        "allowed_values": "non-negative float",
    },
    "all_prior_fsh_levels_after_40_under_19": {
        "description": "For females age 40 and older, whether all prior unmedicated day 3 FSH tests performed after age 40 were < 19 mIU/mL (True if all prior tests were < 19 mIU/mL or if no prior tests were performed after age 40)",
        "type": "bool",
        "allowed_values": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    # Check enrollment as student or covered partner
    if claim.get("patient_is_covered_student_or_partner") is not True:
        return False

    # READING: Covered comprehensive infertility services
    # Charges must be for covered services by an infertility specialist
    covered_services = {
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    }
    if claim.get("service_type") not in covered_services:
        return False
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # Documented condition demonstrated to cause infertility
    if claim.get("has_documented_infertility_condition") is not True:
        return False

    # Exclusion: voluntary sterilization
    if claim.get("has_voluntary_sterilization") is not False:
        return False

    # Exclusion: natural physiologic process (e.g. perimenopause, menopause)
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False

    # Exclusion: pregnancy attainable through less costly covered treatment
    if claim.get("pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    if patient_gender not in ("female", "male") or patient_age is None:
        return False

    # READING: Clinical diagnosis of gender dysphoria
    # If diagnosed with gender dysphoria, infertility definition is met without waiting period
    has_gd = claim.get("has_gender_dysphoria_diagnosis") is True

    if patient_gender == "female":
        # Check FSH test requirements for females
        fsh_months = claim.get("fsh_test_done_within_months")
        fsh_level = claim.get("most_recent_fsh_level")
        if fsh_months is None or fsh_level is None:
            return False

        if patient_age < 35:
            if fsh_months > 12 or fsh_level >= 19.0:
                return False
        else:
            # Female 35 or older: test within past 6 months
            if fsh_months > 6 or fsh_level >= 19.0:
                return False
            # READING: FSH test criteria for females age 40 and older
            if patient_age >= 40:
                if claim.get("all_prior_fsh_levels_after_40_under_19") is not True:
                    return False

        # Check conception attempt / infertility duration requirements
        if not has_gd:
            partner_gender = claim.get("partner_gender")
            if partner_gender not in ("male", "female", "none"):
                return False

            intercourse_months = claim.get("months_unprotected_timed_intercourse") or 0
            donor_cycles = claim.get("donor_insemination_cycles") or 0

            if partner_gender == "male":
                # READING: Donor insemination for females with male partners
                if patient_age < 35:
                    if intercourse_months < 12 and donor_cycles < 12:
                        return False
                else:
                    if intercourse_months < 6 and donor_cycles < 6:
                        return False
            else:
                # READING: Definition of "without a male partner"
                if patient_age < 35:
                    if donor_cycles < 12:
                        return False
                else:
                    if donor_cycles < 6:
                        return False

        return True

    elif patient_gender == "male":
        # For a male patient under the policy table, coverage requires a female partner
        partner_gender = claim.get("partner_gender")
        partner_age = claim.get("partner_age")
        if partner_gender != "female" or partner_age is None:
            return False

        # Conception attempt requirements for male with female partner
        if not has_gd:
            intercourse_months = claim.get("months_unprotected_timed_intercourse") or 0
            donor_cycles = claim.get("donor_insemination_cycles") or 0
            # READING: Donor insemination for female partner also accepted
            if partner_age < 35:
                if intercourse_months < 12 and donor_cycles < 12:
                    return False
            else:
                if intercourse_months < 6 and donor_cycles < 6:
                    return False

        # FSH testing does not apply to males under the table
        return True

    return False
