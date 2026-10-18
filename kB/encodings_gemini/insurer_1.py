"""
Policy Coverage Rules: Comprehensive Infertility Services
Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64

READING CHOICES & LEGAL INTERPRETATIONS:
1. # READING: Covered services and provider specialty:
   "We will cover charges made by an infertility specialist for the following infertility services:
   • Ovulation induction cycle(s) with menotropins
   • Intrauterine insemination"
   Reading chosen: Coverage is strictly limited to charges made by an infertility specialist for
   ovulation induction cycles with menotropins and intrauterine insemination (IUI). Ovulation
   induction without menotropins and other procedures (e.g., IVF) are not covered under this benefit.

2. # READING: Infertility definition for female with male partner and donor insemination:
   Under the glossary, infertility for a female with a male partner is defined strictly by failure
   to become pregnant after 1 year (<35) or 6 months (>=35) of frequent, unprotected heterosexual
   intercourse, or through a clinical diagnosis of gender dysphoria. The glossary does not list
   donor insemination for females with a male partner. Reading chosen: A female with a male partner
   cannot satisfy the glossary definition solely through donor insemination cycles unless she or her
   partner has a diagnosis of gender dysphoria.

3. # READING: Males without a female partner:
   While the glossary contains a definition of infertility for a male without a female partner
   (at least 2 abnormal semen analyses at least 2 weeks apart), the policy table provides no
   category or criteria for a male without a female partner. Reading chosen: A male without a
   female partner cannot satisfy the policy table criteria and is therefore ineligible for coverage.

4. # READING: Gender dysphoria:
   A diagnosis of gender dysphoria satisfies the glossary definition of infertility, but does not
   waive the cumulative policy text requirements (including the waiting periods/cycle requirements
   in the table and FSH testing).

5. # READING: FSH threshold:
   "Must be less than 19 mIU/mL in your most recent lab test" and "less than 19 mIU/mL in all prior
   tests performed after age 40." Reading chosen: The threshold is strictly less than (< 19.0 mIU/mL).
   A test result of exactly 19.0 mIU/mL is not covered. For individuals age 40 and older, both the
   most recent test and all prior tests performed after age 40 must be strictly less than 19.0 mIU/mL.

6. # READING: Voluntary sterilization:
   "You or your partner has not had a voluntary sterilization with or without surgical reversal..."
   Reading chosen: Any voluntary sterilization by the patient or partner permanently bars coverage,
   even if surgically reversed.
"""

from typing import Any, Dict

SCHEMA: Dict[str, Any] = {
    "service_type": {
        "description": "The specific infertility service billed.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the provider billing the service is an infertility specialist.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_is_student_or_covered_dependent_partner": {
        "description": "Whether the patient is covered under the plan as a student or as a covered dependent spouse/partner.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "has_documented_infertility_causing_condition": {
        "description": "Whether a condition demonstrated to cause infertility has been recognized by a physician/specialist and documented in medical records.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_or_partner_has_voluntary_sterilization": {
        "description": "Whether the patient or partner has had a voluntary sterilization (with or without surgical reversal).",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Whether infertility is due to a natural physiologic process such as age-related ovarian insufficiency (e.g. perimenopause, menopause).",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": "Whether a successful pregnancy can be attained through less costly treatment covered under this plan.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_sex": {
        "description": "Legal/biological sex of the patient.",
        "type": "str",
        "allowed_values": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of the patient in completed years.",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "partner_sex": {
        "description": "Sex of the patient's spouse/partner, or 'none' if no partner.",
        "type": "str",
        "allowed_values": ["female", "male", "none"],
    },
    "partner_age": {
        "description": "Age of the partner in completed years (required if patient is male with female partner).",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "diagnosed_with_gender_dysphoria": {
        "description": "Whether the patient or their partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of frequent, unprotected timed heterosexual intercourse trying to conceive.",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "donor_insemination_cycles": {
        "description": "Number of donor artificial insemination cycles completed that were self-paid / not paid for by the plan.",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "abnormal_semen_analyses_count": {
        "description": "Number of abnormal semen analyses obtained at least 2 weeks apart.",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "unmedicated_day3_fsh_test_months_ago": {
        "description": "Number of months ago the most recent unmedicated day 3 FSH test was performed.",
        "type": "int",
        "allowed_values": ">= 0",
    },
    "unmedicated_day3_fsh_most_recent_value": {
        "description": "FSH level in mIU/mL from the most recent unmedicated day 3 FSH test.",
        "type": "float",
        "allowed_values": ">= 0.0",
    },
    "all_prior_fsh_tests_after_40_under_19": {
        "description": "For patients age 40 and older, whether all prior unmedicated day 3 FSH tests performed after age 40 were < 19 mIU/mL.",
        "type": "bool",
        "allowed_values": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    # 1. Covered Service & Provider Specialty
    # READING: Covered services and specialist provider:
    # Only ovulation induction with menotropins or intrauterine insemination, billed by an infertility specialist.
    service = claim.get("service_type")
    if service not in ["ovulation_induction_with_menotropins", "intrauterine_insemination"]:
        return False

    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # 2. Plan Member Eligibility
    if claim.get("patient_is_student_or_covered_dependent_partner") is not True:
        return False

    # 3. Documented Condition Causing Infertility
    if claim.get("has_documented_infertility_causing_condition") is not True:
        return False

    # 4. Voluntary Sterilization Exclusion
    # READING: Voluntary sterilization: Bars coverage regardless of reversal.
    if claim.get("patient_or_partner_has_voluntary_sterilization") is not False:
        return False

    # 5. Natural Physiologic Process Exclusion
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False

    # 6. Less Costly Treatment Exclusion
    if claim.get("pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    patient_sex = claim.get("patient_sex")
    patient_age = claim.get("patient_age")
    partner_sex = claim.get("partner_sex")

    if patient_sex not in ["female", "male"]:
        return False
    if not isinstance(patient_age, (int, float)):
        return False
    if partner_sex not in ["female", "male", "none"]:
        return False

    months_intercourse = claim.get("months_unprotected_timed_intercourse", 0)
    if not isinstance(months_intercourse, (int, float)):
        months_intercourse = 0

    donor_cycles = claim.get("donor_insemination_cycles", 0)
    if not isinstance(donor_cycles, (int, float)):
        donor_cycles = 0

    has_gender_dysphoria = claim.get("diagnosed_with_gender_dysphoria") is True

    # 7. Glossary Definition of Infertility Check
    # READING: Glossary infertility definition:
    # Must meet one of the glossary prongs. For female with male partner, donor insemination alone
    # does not establish glossary infertility unless gender dysphoria is present.
    glossary_infertile = False
    if has_gender_dysphoria:
        glossary_infertile = True
    elif patient_sex == "female" and partner_sex == "male":
        if patient_age < 35 and months_intercourse >= 12:
            glossary_infertile = True
        elif patient_age >= 35 and months_intercourse >= 6:
            glossary_infertile = True
    elif patient_sex == "female" and partner_sex != "male":
        if patient_age < 35 and donor_cycles >= 12:
            glossary_infertile = True
        elif patient_age >= 35 and donor_cycles >= 6:
            glossary_infertile = True
    elif patient_sex == "male" and partner_sex == "female":
        partner_age = claim.get("partner_age")
        if isinstance(partner_age, (int, float)):
            if partner_age < 35 and months_intercourse >= 12:
                glossary_infertile = True
            elif partner_age >= 35 and months_intercourse >= 6:
                glossary_infertile = True
    elif patient_sex == "male" and partner_sex != "female":
        semen_count = claim.get("abnormal_semen_analyses_count", 0)
        if isinstance(semen_count, (int, float)) and semen_count >= 2:
            glossary_infertile = True

    if not glossary_infertile:
        return False

    # 8. Policy Text Table Requirements
    # READING: Gender dysphoria does not exempt claimant from table requirements.
    # READING: Males without a female partner are not covered in the table.
    fsh_months = claim.get("unmedicated_day3_fsh_test_months_ago")
    fsh_value = claim.get("unmedicated_day3_fsh_most_recent_value")

    # Helper for female FSH check
    def fsh_meets_criteria(max_months: int) -> bool:
        if not isinstance(fsh_months, (int, float)) or fsh_months > max_months:
            return False
        # READING: FSH threshold must be strictly less than 19.0 mIU/mL
        if not isinstance(fsh_value, (int, float)) or fsh_value >= 19.0:
            return False
        # READING: FSH testing for females age 40 and older
        if patient_age >= 40:
            if claim.get("all_prior_fsh_tests_after_40_under_19") is not True:
                return False
        return True

    # Row 1: Female under 35 with male partner
    if patient_sex == "female" and patient_age < 35 and partner_sex == "male":
        conception_req_met = (months_intercourse >= 12) or (donor_cycles >= 12)
        if not conception_req_met:
            return False
        return fsh_meets_criteria(max_months=12)

    # Row 2: Female under 35 without male partner
    if patient_sex == "female" and patient_age < 35 and partner_sex != "male":
        if donor_cycles < 12:
            return False
        return fsh_meets_criteria(max_months=12)

    # Row 3: Female 35 or older with male partner
    if patient_sex == "female" and patient_age >= 35 and partner_sex == "male":
        conception_req_met = (months_intercourse >= 6) or (donor_cycles >= 6)
        if not conception_req_met:
            return False
        return fsh_meets_criteria(max_months=6)

    # Row 4: Female 35 or older without male partner
    if patient_sex == "female" and patient_age >= 35 and partner_sex != "male":
        if donor_cycles < 6:
            return False
        return fsh_meets_criteria(max_months=6)

    # Row 5: Male of any age with female partner under 35
    if patient_sex == "male" and partner_sex == "female":
        partner_age = claim.get("partner_age")
        if not isinstance(partner_age, (int, float)):
            return False
        if partner_age < 35:
            return months_intercourse >= 12
        else:
            # Row 6: Male of any age with female partner 35 or older
            return months_intercourse >= 6

    # Male without a female partner is not provided for in the table.
    return False
