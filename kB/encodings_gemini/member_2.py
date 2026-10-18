"""
Policy coverage rules for Cardinal Care (2023-2024), pp. 62-64:
Comprehensive Infertility Services.

READING choices made in member's favor:
1. READING: Covered services
   "We will cover charges made by an infertility specialist for the following infertility services:
    - Ovulation induction cycle(s) with menotropins
    - Intrauterine insemination"
   Reading: Only these two specific services are covered under the comprehensive infertility benefit.
   The provider rendering the service must be an infertility specialist (or the charge made by one).

2. READING: Definition of infertility (Glossary vs. Eligibility table)
   Under the Glossary, "infertile or infertility" can be met by:
   - female with male partner: 1 year (if < 35) or 6 months (if >= 35) of frequent, unprotected heterosexual intercourse;
   - female without male partner: at least 12 cycles (< 35) or 6 cycles (>= 35) of donor insemination;
   - male without female partner: at least 2 abnormal semen analyses obtained at least 2 weeks apart;
   - an individual or their partner clinically diagnosed with gender dysphoria.
   In the policy text table, a female with a male partner can also satisfy the requirement by either timed
   intercourse OR donor insemination cycles (e.g., if using donor sperm). To advocate for the member,
   we interpret the glossary and policy criteria harmoniously: meeting either the standard intercourse
   duration or donor insemination cycle count (or having a clinical diagnosis of gender dysphoria, or
   male semen analysis criteria where applicable) satisfies the infertility definition, and the table's
   specific criteria for trying to conceive / donor insemination are applied based on the category.

3. READING: "You or your partner" voluntary sterilization exclusion
   "You or your partner has not had a voluntary sterilization with or without surgical reversal,
   regardless of post reversal results. This includes tubal ligation, hysterectomy and vasectomy only if
   obtained as a form of voluntary sterilization."
   Reading: Sterilization only disqualifies the claim if it was voluntary (i.e. obtained as a form of
   voluntary sterilization). Involuntary/medically necessary procedures (e.g. non-elective hysterectomy
   for cancer or trauma) do not disqualify coverage.

4. READING: Less costly treatment
   "A successful pregnancy cannot be attained through less costly treatment for which coverage is available under this plan."
   Reading: Unless it is established that pregnancy could be attained through a less costly covered treatment,
   this requirement is considered met.

5. READING: FSH test requirement timing and levels
   - For female < 35 (with or without male partner): unmedicated day 3 FSH test must be done within the past
     12 months, and most recent result must be < 19 mIU/mL.
   - For female >= 35 and < 40 (with or without male partner): unmedicated day 3 FSH test must be done within the
     past 6 months, and most recent result must be < 19 mIU/mL.
   - For female >= 40 (with or without male partner): unmedicated day 3 FSH test must be done within the past 6 months,
     and all prior tests performed after age 40 must be < 19 mIU/mL.
   - For male with female partner: FSH test "Does not apply".
"""

from typing import Any, Dict, List, Optional

SCHEMA: Dict[str, str] = {
    "covered_person_role": (
        "Role under the plan of the person for whom coverage is sought: "
        "'student', 'spouse', 'civil_union_partner', 'domestic_partner', or 'other'"
    ),
    "service_type": (
        "The comprehensive infertility service requested: "
        "'ovulation_induction_with_menotropins', 'intrauterine_insemination', or 'other'"
    ),
    "provider_is_infertility_specialist": (
        "Whether charges are made by an infertility specialist (bool)"
    ),
    "has_documented_infertility_condition": (
        "Whether there exists a condition demonstrated to cause infertility, "
        "recognized by a physician or infertility specialist and documented in medical records (bool)"
    ),
    "voluntary_sterilization_history": (
        "Whether the member or their partner had a voluntary sterilization (tubal ligation, "
        "hysterectomy, or vasectomy obtained as a form of voluntary sterilization) (bool)"
    ),
    "infertility_due_to_natural_physiologic_process": (
        "Whether infertility is due to a natural physiologic process such as age-related "
        "ovarian insufficiency (perimenopause, menopause) (bool)"
    ),
    "successful_pregnancy_attainable_through_less_costly_covered_treatment": (
        "Whether a successful pregnancy can be attained through a less costly covered treatment under this plan (bool)"
    ),
    "patient_gender": (
        "Gender/sex category of the patient receiving the service: 'female' or 'male'"
    ),
    "patient_age": (
        "Age of the patient at the time of service in years (int)"
    ),
    "partner_gender": (
        "Gender/sex category of the partner, if applicable: 'female', 'male', or None"
    ),
    "partner_age": (
        "Age of the partner in years, if applicable (int or None)"
    ),
    "has_gender_dysphoria_diagnosis": (
        "Whether the individual or their partner has been clinically diagnosed with gender dysphoria (bool)"
    ),
    "months_unprotected_intercourse": (
        "Number of months of frequent, unprotected heterosexual/timed sexual intercourse trying to conceive (int)"
    ),
    "donor_insemination_cycles": (
        "Number of donor artificial insemination cycles completed (int)"
    ),
    "male_abnormal_semen_analyses_count": (
        "For a male without a female partner, number of abnormal semen analyses obtained at least 2 weeks apart (int)"
    ),
    "fsh_test_performed_within_months": (
        "Number of months prior to the request that the unmedicated day 3 FSH test was performed (int or None)"
    ),
    "fsh_most_recent_result": (
        "Result in mIU/mL of the most recent unmedicated day 3 FSH test (float or None)"
    ),
    "fsh_all_tests_after_40_under_19": (
        "If female age 40 or older, whether all prior unmedicated day 3 FSH tests performed after age 40 were < 19 mIU/mL (bool or None)"
    ),
}


def covered_under_benefit(claim: dict) -> bool:
    # 1. Covered role: student, legal spouse, civil union partner, or domestic partner
    role = claim.get("covered_person_role")
    if role not in {"student", "spouse", "civil_union_partner", "domestic_partner"}:
        return False

    # 2. Service must be one of the comprehensive infertility services covered by Cardinal Care
    service = claim.get("service_type")
    if service not in {"ovulation_induction_with_menotropins", "intrauterine_insemination"}:
        return False

    # 3. Provider must be an infertility specialist
    if not claim.get("provider_is_infertility_specialist", False):
        return False

    # 4. Infertility condition recognized and documented in medical records
    if not claim.get("has_documented_infertility_condition", False):
        return False

    # 5. No voluntary sterilization with or without reversal (involuntary/medically necessary procedures do not bar)
    if claim.get("voluntary_sterilization_history", False):
        return False

    # 6. Not due to a natural physiologic process (e.g. perimenopause, menopause)
    if claim.get("infertility_due_to_natural_physiologic_process", False):
        return False

    # 7. Cannot be attained through less costly treatment
    if claim.get("successful_pregnancy_attainable_through_less_costly_covered_treatment", False):
        return False

    # Patient & partner demographics
    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    partner_gender = claim.get("partner_gender")
    partner_age = claim.get("partner_age")

    if patient_gender not in {"female", "male"} or patient_age is None:
        return False

    months_intercourse = claim.get("months_unprotected_intercourse", 0)
    donor_cycles = claim.get("donor_insemination_cycles", 0)
    has_gd = claim.get("has_gender_dysphoria_diagnosis", False)

    # 8. Glossary definition of infertility check
    # Infertility is defined by failure to become pregnant after timed intercourse / donor cycles / semen analysis / GD
    infertile_by_glossary = False
    if has_gd:
        infertile_by_glossary = True
    elif patient_gender == "female":
        if partner_gender == "male":
            if (patient_age < 35 and (months_intercourse >= 12 or donor_cycles >= 12)) or \
               (patient_age >= 35 and (months_intercourse >= 6 or donor_cycles >= 6)):
                infertile_by_glossary = True
        else:
            if (patient_age < 35 and donor_cycles >= 12) or \
               (patient_age >= 35 and donor_cycles >= 6):
                infertile_by_glossary = True
    elif patient_gender == "male":
        if partner_gender == "female":
            fem_age = partner_age if partner_age is not None else 30
            if (fem_age < 35 and months_intercourse >= 12) or \
               (fem_age >= 35 and months_intercourse >= 6):
                infertile_by_glossary = True
        else:
            # Male without female partner
            if claim.get("male_abnormal_semen_analyses_count", 0) >= 2:
                infertile_by_glossary = True

    if not infertile_by_glossary:
        return False

    # 9. Table requirements: Months trying / donor cycles & Day 3 FSH requirements
    # Table categories:
    if patient_gender == "female":
        if partner_gender == "male":
            if patient_age < 35:
                # 12 months or more timed intercourse OR at least 12 cycles donor insemination
                if not (months_intercourse >= 12 or donor_cycles >= 12 or has_gd):
                    return False
                # FSH test within past 12 months, most recent < 19
                fsh_months = claim.get("fsh_test_performed_within_months")
                fsh_recent = claim.get("fsh_most_recent_result")
                if fsh_months is None or fsh_months > 12:
                    return False
                if fsh_recent is None or fsh_recent >= 19.0:
                    return False
            else:
                # Age 35 or older with male partner
                if not (months_intercourse >= 6 or donor_cycles >= 6 or has_gd):
                    return False
                # FSH test within past 6 months
                fsh_months = claim.get("fsh_test_performed_within_months")
                fsh_recent = claim.get("fsh_most_recent_result")
                if fsh_months is None or fsh_months > 6:
                    return False
                if patient_age < 40:
                    if fsh_recent is None or fsh_recent >= 19.0:
                        return False
                else:
                    # Age 40 and older: must be < 19 in all prior tests performed after age 40
                    if not claim.get("fsh_all_tests_after_40_under_19", False):
                        return False

        else:
            # Female without male partner
            if patient_age < 35:
                if not (donor_cycles >= 12 or has_gd):
                    return False
                fsh_months = claim.get("fsh_test_performed_within_months")
                fsh_recent = claim.get("fsh_most_recent_result")
                if fsh_months is None or fsh_months > 12:
                    return False
                if fsh_recent is None or fsh_recent >= 19.0:
                    return False
            else:
                if not (donor_cycles >= 6 or has_gd):
                    return False
                fsh_months = claim.get("fsh_test_performed_within_months")
                fsh_recent = claim.get("fsh_most_recent_result")
                if fsh_months is None or fsh_months > 6:
                    return False
                if patient_age < 40:
                    if fsh_recent is None or fsh_recent >= 19.0:
                        return False
                else:
                    if not claim.get("fsh_all_tests_after_40_under_19", False):
                        return False

    elif patient_gender == "male":
        # A male of any age with a female partner
        if partner_gender == "female":
            fem_age = partner_age if partner_age is not None else 30
            if fem_age < 35:
                if not (months_intercourse >= 12 or has_gd):
                    return False
            else:
                if not (months_intercourse >= 6 or has_gd):
                    return False
            # FSH does not apply to male
        else:
            # Male without female partner: glossary covers with 2 abnormal semen analyses or GD,
            # but table has no row restricting FSH or donor cycles.
            pass

    return True
