"""
READING choices:
1. Patient covered status:
   # READING: The text states "You are covered under this plan as a student or as
   # a covered dependent who is the student's legal spouse, civil union partner
   # or domestic partner". We require the patient to have this enrollment status.
2. Provider specialty:
   # READING: The text states "We will cover charges made by an infertility
   # specialist for the following infertility services...". We check that the
   # service is rendered by an infertility specialist.
3. Covered services:
   # READING: The policy lists two covered services under comprehensive
   # infertility services: "Ovulation induction cycle(s) with menotropins" and
   # "Intrauterine insemination".
4. Demonstrable condition documented in medical records:
   # READING: "There exists a condition that: Is demonstrated to cause the
   # illness of infertility. Has been recognized by your physician or infertility
   # specialist and documented in your or your partner's medical records."
5. Voluntary sterilization:
   # READING: "You or your partner has not had a voluntary sterilization with or
   # without surgical reversal, regardless of post reversal results."
6. Natural physiologic process:
   # READING: "You or your partner does not have infertility that is due to a
   # natural physiologic process such as age related ovarian insufficiency (e.g.
   # perimenopause, menopause)."
7. Less costly treatment:
   # READING: "A successful pregnancy cannot be attained through less costly
   # treatment for which coverage is available under this plan."
8. Infertility definition (Glossary):
   # READING: The glossary defines infertility as failure to become pregnant:
   # - female with male partner: 1 year (if <35) or 6 months (if >=35) of frequent,
   #   unprotected heterosexual intercourse.
   # - female without male partner: at least 12 cycles (if <35) or 6 cycles (if >=35)
   #   of donor insemination.
   # - male without female partner: at least 2 abnormal semen analyses obtained
   #   at least 2 weeks apart.
   # - individual or partner diagnosed with gender dysphoria.
   # Meeting any of these glossary definitions satisfies the glossary infertility requirement.
9. Table requirements:
   # READING: The table enumerates patient categories and requirements:
   # - Female < 35 with male partner: >= 12 months unprotected timed intercourse
   #   OR >= 12 donor insemination cycles; day 3 FSH within past 12 months < 19 mIU/mL
   #   in most recent lab test.
   # - Female < 35 without male partner: >= 12 donor insemination cycles;
   #   day 3 FSH within past 12 months < 19 mIU/mL in most recent lab test.
   # - Female >= 35 with male partner: >= 6 months unprotected timed intercourse
   #   OR >= 6 donor insemination cycles; day 3 FSH within past 6 months. If < 40,
   #   most recent < 19 mIU/mL. If >= 40, all prior tests after age 40 < 19 mIU/mL.
   # - Female >= 35 without male partner: >= 6 donor insemination cycles;
   #   day 3 FSH within past 6 months. If < 40, most recent < 19 mIU/mL.
   #   If >= 40, all prior tests after age 40 < 19 mIU/mL.
   # - Male with female partner < 35: >= 12 months unprotected timed intercourse;
   #   FSH test does not apply.
   # - Male with female partner >= 35: >= 6 months unprotected timed intercourse;
   #   FSH test does not apply.
   # - For other categories recognized by the glossary (male without female partner,
   #   or gender dysphoria cases not falling into the table's male/female partner rows),
   #   the table has no applicable criteria ("Does not apply").
"""

from typing import Any, Dict

SCHEMA: Dict[str, Dict[str, Any]] = {
    "covered_role": {
        "description": "Patient coverage category under the plan",
        "type": "str",
        "allowed": ["student", "spouse_or_partner", "other"],
    },
    "service_type": {
        "description": "Type of infertility service being claimed",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether charges are made by an infertility specialist",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_causes_infertility_and_documented": {
        "description": (
            "Condition demonstrated to cause infertility recognized by physician/specialist "
            "and documented in patient's or partner's medical records"
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_voluntary_sterilization": {
        "description": "Whether patient or partner has had voluntary sterilization",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": (
            "Whether infertility is due to natural physiologic process such as age-related "
            "ovarian insufficiency (perimenopause/menopause)"
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": (
            "Whether successful pregnancy can be attained through less costly treatment "
            "for which coverage is available under this plan"
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_sex": {
        "description": "Biological/legal sex of patient relevant to clinical table",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of patient in years",
        "type": "int",
        "allowed": ">= 0",
    },
    "has_partner": {
        "description": "Whether patient has a partner",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_sex": {
        "description": "Biological/legal sex of partner (if applicable)",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "partner_age": {
        "description": "Age of partner in years (if applicable)",
        "type": "int",
        "allowed": ">= 0",
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of frequent, unprotected timed heterosexual intercourse",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles": {
        "description": "Number of donor artificial insemination cycles (self-paid/not paid by plan)",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_test_done_within_months": {
        "description": "Months ago that unmedicated day 3 FSH test was performed",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_most_recent_value": {
        "description": "Result of most recent unmedicated day 3 FSH test in mIU/mL",
        "type": "float",
        "allowed": ">= 0.0",
    },
    "fsh_all_after_age_40_under_19": {
        "description": (
            "Whether all prior unmedicated day 3 FSH tests performed after age 40 "
            "were less than 19 mIU/mL"
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "male_without_female_partner_abnormal_semen_analyses": {
        "description": (
            "Whether male without female partner has at least 2 abnormal semen analyses "
            "obtained at least 2 weeks apart"
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_diagnosed_gender_dysphoria": {
        "description": "Whether patient or partner has clinically diagnosed gender dysphoria",
        "type": "bool",
        "allowed": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    # 1. Covered status
    if claim.get("covered_role") not in ["student", "spouse_or_partner"]:
        return False

    # 2. Service type
    allowed_services = [
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ]
    if claim.get("service_type") not in allowed_services:
        return False

    # 3. Provider specialty
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # 4. Underlying condition documented
    if claim.get("condition_causes_infertility_and_documented") is not True:
        return False

    # 5. No voluntary sterilization
    if claim.get("patient_or_partner_voluntary_sterilization") is not False:
        return False

    # 6. Not due to natural physiologic process
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False

    # 7. Cannot be attained through less costly treatment
    if claim.get("pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    # 8. Check glossary definition of infertility
    sex = claim.get("patient_sex")
    age = claim.get("patient_age")
    has_partner = claim.get("has_partner")
    partner_sex = claim.get("partner_sex")
    partner_age = claim.get("partner_age")
    months_intercourse = claim.get("months_unprotected_timed_intercourse", 0)
    donor_cycles = claim.get("donor_insemination_cycles", 0)

    if age is None or sex not in ["female", "male"]:
        return False

    is_female_with_male = (sex == "female" and has_partner is True and partner_sex == "male")
    is_female_without_male = (sex == "female" and (has_partner is False or partner_sex != "male"))
    is_male_with_female = (sex == "male" and has_partner is True and partner_sex == "female")
    is_male_without_female = (sex == "male" and (has_partner is False or partner_sex != "female"))

    glossary_infertile = False

    # Female with male partner: failure to become pregnant after 1 yr (<35) or 6 mo (>=35)
    if is_female_with_male:
        if age < 35 and months_intercourse >= 12:
            glossary_infertile = True
        elif age >= 35 and months_intercourse >= 6:
            glossary_infertile = True

    # Female without male partner: donor insemination >= 12 cycles (<35) or >= 6 cycles (>=35)
    if is_female_without_male:
        if age < 35 and donor_cycles >= 12:
            glossary_infertile = True
        elif age >= 35 and donor_cycles >= 6:
            glossary_infertile = True

    # Male with female partner: glossary covers heterosexual couple via female definition;
    # also check if the couple has had intercourse meeting the duration:
    if is_male_with_female:
        if partner_age is not None:
            if partner_age < 35 and months_intercourse >= 12:
                glossary_infertile = True
            elif partner_age >= 35 and months_intercourse >= 6:
                glossary_infertile = True

    # Male without female partner: at least 2 abnormal semen analyses at least 2 weeks apart
    if is_male_without_female:
        if claim.get("male_without_female_partner_abnormal_semen_analyses") is True:
            glossary_infertile = True

    # Gender dysphoria
    if claim.get("patient_or_partner_diagnosed_gender_dysphoria") is True:
        glossary_infertile = True

    if not glossary_infertile:
        return False

    # 9. Table requirements: Months trying / donor cycles and FSH testing
    fsh_within = claim.get("fsh_test_done_within_months")
    fsh_val = claim.get("fsh_most_recent_value")
    fsh_all_40 = claim.get("fsh_all_after_age_40_under_19")

    if is_female_with_male:
        if age < 35:
            # Intercourse >= 12 mo OR donor >= 12 cycles
            if months_intercourse < 12 and donor_cycles < 12:
                return False
            # FSH within 12 months, most recent < 19
            if fsh_within is None or fsh_within > 12:
                return False
            if fsh_val is None or fsh_val >= 19.0:
                return False
        else:
            # age >= 35
            # Intercourse >= 6 mo OR donor >= 6 cycles
            if months_intercourse < 6 and donor_cycles < 6:
                return False
            # FSH within 6 months
            if fsh_within is None or fsh_within > 6:
                return False
            if age < 40:
                if fsh_val is None or fsh_val >= 19.0:
                    return False
            else:
                # age >= 40: must be less than 19 in all prior tests after age 40
                if fsh_val is None or fsh_val >= 19.0:
                    return False
                if fsh_all_40 is not True:
                    return False

    elif is_female_without_male:
        if age < 35:
            # Donor >= 12 cycles
            if donor_cycles < 12:
                return False
            # FSH within 12 months, most recent < 19
            if fsh_within is None or fsh_within > 12:
                return False
            if fsh_val is None or fsh_val >= 19.0:
                return False
        else:
            # age >= 35
            # Donor >= 6 cycles
            if donor_cycles < 6:
                return False
            # FSH within 6 months
            if fsh_within is None or fsh_within > 6:
                return False
            if age < 40:
                if fsh_val is None or fsh_val >= 19.0:
                    return False
            else:
                # age >= 40
                if fsh_val is None or fsh_val >= 19.0:
                    return False
                if fsh_all_40 is not True:
                    return False

    elif is_male_with_female:
        if partner_age is None:
            return False
        if partner_age < 35:
            if months_intercourse < 12:
                return False
        else:
            if months_intercourse < 6:
                return False
        # FSH does not apply to male

    # If all requirements met
    return True
