"""
Policy Coverage Rules: Comprehensive Infertility Services
Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64, Glossary

READING CHOICES:
1. Covered Services:
   # READING: The text covers "Ovulation induction cycle(s) with menotropins" and
   # "Intrauterine insemination". Other procedures (e.g. IVF, ICSI, or ovulation
   # induction without menotropins) are not covered comprehensive infertility services.
2. Infertility Specialist Provider:
   # READING: "charges made by an infertility specialist" is read as an affirmative
   # benefit eligibility requirement that the service be rendered by an infertility specialist.
3. Harmonization of Glossary and Table on Donor Insemination for Female with Male Partner:
   # READING: The glossary defines infertility for a female with a male partner by
   # heterosexual sexual intercourse, whereas the benefit table explicitly allows either
   # timed intercourse OR donor insemination cycles (at least 12 cycles if under 35,
   # 6 cycles if 35 or older). To avoid rendering Option B of the table inoperative,
   # we read the table's explicit donor insemination path as satisfying the conception
   # effort / infertility requirement under this benefit.
4. Gender Dysphoria and Benefit Criteria:
   # READING: Under the glossary, a diagnosis of gender dysphoria establishes infertility
   # without a waiting period of failed conception. However, the operative text makes each
   # bullet an eligibility condition ("You are eligible for infertility services if: ...").
   # Therefore, an individual or partner with gender dysphoria must still meet the table's
   # conception attempt and FSH test criteria.
5. Male Without Female Partner:
   # READING: The glossary defines infertility for a male without a female partner (2 abnormal
   # semen analyses at least 2 weeks apart). However, the comprehensive infertility services
   # table provides no category or criteria for males without a female partner, and the covered
   # services (ovulation induction and IUI) cannot be performed without a female partner.
   # Thus, claims for a male without a female partner are not eligible under this benefit.
6. FSH Results for Age 40 and Older:
   # READING: "must be less than 19 mIU/mL in all prior tests performed after age 40" means
   # that for a female age 40 or older, every unmedicated day 3 FSH test performed after age 40
   # (including the test performed within the past 6 months) must have a result < 19 mIU/mL.
   # If any test performed after age 40 was >= 19 mIU/mL, the criterion is not met.
"""

from typing import Any, Dict

SCHEMA: Dict[str, Dict[str, Any]] = {
    "service_name": {
        "description": "Name of the infertility service requested or rendered.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_is_covered_student_or_partner": {
        "description": (
            "Whether the patient is covered under the plan as a student or as a "
            "covered dependent who is the student's legal spouse, civil union "
            "partner, or domestic partner."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_documented_condition_causing_infertility": {
        "description": (
            "Whether there exists a condition demonstrated to cause the illness of "
            "infertility, recognized by a physician or infertility specialist and "
            "documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_prior_voluntary_sterilization": {
        "description": (
            "Whether the patient or partner has had a voluntary sterilization "
            "(e.g., tubal ligation, hysterectomy, vasectomy) with or without "
            "surgical reversal."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": (
            "Whether the infertility of the patient or partner is due to a natural "
            "physiologic process such as age-related ovarian insufficiency "
            "(e.g., perimenopause, menopause)."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "pregnancy_attainable_through_less_costly_treatment": {
        "description": (
            "Whether a successful pregnancy can be attained through less costly "
            "treatment for which coverage is available under this plan."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_gender": {
        "description": "Biological or administrative sex/gender of the patient.",
        "type": "str",
        "allowed_values": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of the patient in years.",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "partner_gender": {
        "description": "Gender of the patient's partner, or None if no partner.",
        "type": "str",
        "allowed_values": ["female", "male", None],
    },
    "partner_age": {
        "description": "Age of the patient's partner in years, if applicable.",
        "type": "int",
        "allowed_values": ">= 0 or None",
    },
    "patient_or_partner_diagnosed_with_gender_dysphoria": {
        "description": (
            "Whether the patient or their partner has been clinically diagnosed "
            "with gender dysphoria."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "months_of_unprotected_timed_intercourse": {
        "description": (
            "Number of months of frequent, unprotected timed heterosexual "
            "intercourse trying to conceive."
        ),
        "type": "int",
        "allowed_values": ">= 0 or None",
    },
    "donor_insemination_cycles": {
        "description": (
            "Number of donor artificial insemination cycles completed that were "
            "self-paid / not paid for by the plan."
        ),
        "type": "int",
        "allowed_values": ">= 0 or None",
    },
    "fsh_test_months_ago": {
        "description": (
            "Number of months elapsed since the most recent unmedicated day 3 "
            "FSH test was performed. None if never performed."
        ),
        "type": "int",
        "allowed_values": ">= 0 or None",
    },
    "most_recent_fsh_level": {
        "description": (
            "Result of the most recent unmedicated day 3 FSH test in mIU/mL."
        ),
        "type": "float",
        "allowed_values": ">= 0.0 or None",
    },
    "has_fsh_level_19_or_greater_after_age_40": {
        "description": (
            "For a female age 40 or older, whether any unmedicated day 3 FSH "
            "test performed after age 40 had a result of 19 mIU/mL or greater."
        ),
        "type": "bool",
        "allowed_values": [True, False, None],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """
    Determines whether a claim is covered under the Comprehensive Infertility
    Services benefit of the Cardinal Care Certificate of Coverage.
    """
    # 1. Covered service check
    # READING: Only ovulation induction with menotropins and intrauterine insemination are covered.
    service_name = claim.get("service_name")
    covered_services = {
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    }
    if service_name not in covered_services:
        return False

    # 2. Rendering provider check
    # READING: Service must be provided by an infertility specialist.
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # 3. Patient coverage eligibility
    if claim.get("patient_is_covered_student_or_partner") is not True:
        return False

    # 4. Documented condition causing infertility
    if claim.get("has_documented_condition_causing_infertility") is not True:
        return False

    # 5. Prior voluntary sterilization exclusion
    if claim.get("has_prior_voluntary_sterilization") is not False:
        return False

    # 6. Natural physiologic process exclusion
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False

    # 7. Less costly treatment availability
    if claim.get("pregnancy_attainable_through_less_costly_treatment") is not False:
        return False

    # Demographics
    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    partner_gender = claim.get("partner_gender")
    partner_age = claim.get("partner_age")

    if patient_gender not in ("female", "male"):
        return False
    if patient_age is None or not isinstance(patient_age, (int, float)):
        return False

    months_intercourse = claim.get("months_of_unprotected_timed_intercourse")
    donor_cycles = claim.get("donor_insemination_cycles")
    fsh_months_ago = claim.get("fsh_test_months_ago")
    most_recent_fsh = claim.get("most_recent_fsh_level")

    # Helper for intercourse threshold
    def has_intercourse_months(min_months: int) -> bool:
        return isinstance(months_intercourse, (int, float)) and months_intercourse >= min_months

    # Helper for donor insemination threshold
    def has_donor_cycles(min_cycles: int) -> bool:
        return isinstance(donor_cycles, (int, float)) and donor_cycles >= min_cycles

    # 8. Category-specific criteria from the benefit table
    if patient_gender == "female":
        if fsh_months_ago is None or not isinstance(fsh_months_ago, (int, float)):
            return False
        if most_recent_fsh is None or not isinstance(most_recent_fsh, (int, float)):
            return False

        if patient_age < 35:
            # FSH timing: within past 12 months; result < 19 mIU/mL
            if fsh_months_ago > 12 or most_recent_fsh >= 19.0:
                return False

            if partner_gender == "male":
                # Row 1: Female < 35 with male partner: 12+ months intercourse OR 12+ donor cycles
                # READING: Donor insemination option harmonizes with glossary definition.
                if not (has_intercourse_months(12) or has_donor_cycles(12)):
                    return False
            else:
                # Row 2: Female < 35 without male partner: at least 12 donor cycles
                if not has_donor_cycles(12):
                    return False

        else:
            # Female 35 years of age or older
            # FSH timing: within past 6 months
            if fsh_months_ago > 6:
                return False

            # FSH results:
            if patient_age < 40:
                if most_recent_fsh >= 19.0:
                    return False
            else:
                # Age 40 and older: most recent < 19 AND all prior tests after 40 < 19
                # READING: Any prior test >= 19 mIU/mL after age 40 disqualifies.
                if most_recent_fsh >= 19.0:
                    return False
                if claim.get("has_fsh_level_19_or_greater_after_age_40") is not False:
                    return False

            if partner_gender == "male":
                # Row 3: Female >= 35 with male partner: 6+ months intercourse OR 6+ donor cycles
                if not (has_intercourse_months(6) or has_donor_cycles(6)):
                    return False
            else:
                # Row 4: Female >= 35 without male partner: at least 6 donor cycles
                if not has_donor_cycles(6):
                    return False

    elif patient_gender == "male":
        # Rows 5 & 6: Male of any age with female partner
        # READING: Males without a female partner cannot meet table criteria.
        if partner_gender != "female":
            return False
        if partner_age is None or not isinstance(partner_age, (int, float)):
            return False

        if partner_age < 35:
            # Row 5: Male with female partner under 35: 12+ months intercourse
            if not has_intercourse_months(12):
                return False
        else:
            # Row 6: Male with female partner 35 or older: 6+ months intercourse
            if not has_intercourse_months(6):
                return False
    else:
        return False

    return True
