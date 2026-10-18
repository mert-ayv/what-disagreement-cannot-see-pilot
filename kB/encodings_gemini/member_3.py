"""
Policy Coverage Decision Module: Cardinal Care Comprehensive Infertility Services

READING CHOICES & INTERPRETATIONS:
1. READING: Covered Services
   Text: "We will cover charges made by an infertility specialist for the following infertility services:
   • Ovulation induction cycle(s) with menotropins
   • Intrauterine insemination"
   Interpretation: Coverage under this specific benefit is restricted to either an ovulation induction
   cycle with menotropins or intrauterine insemination (IUI). Provider specialty and network status are
   handled separately as noted in the prompt instructions, but the service rendered must match one of
   these two eligible types.

2. READING: Infertility under Glossary
   Text: "Infertile or infertility: A disease defined by the failure to become pregnant:
   • For a female with a male partner, after: 1 year / 6 months...
   • For a female without a male partner, after: 12 cycles / 6 cycles...
   • For a male without a female partner, after: At least 2 abnormal semen analyses obtained at least 2 weeks apart
   • For an individual or their partner who has been clinically diagnosed with gender dysphoria"
   Interpretation: An individual qualifies as infertile under the glossary if they meet ANY applicable category:
   - A clinical diagnosis of gender dysphoria in either the patient or their partner immediately qualifies them as infertile.
   - For a male without a female partner, having at least 2 abnormal semen analyses at least 2 weeks apart qualifies them.
   - For a female with a male partner, reaching the threshold of intercourse (12 months if <35, 6 months if >=35) qualifies them.
   - For a female without a male partner, reaching the donor insemination cycles (12 cycles if <35, 6 cycles if >=35) qualifies them.
   In favor of the member, if a female with a male partner qualifies via donor insemination or gender dysphoria, that satisfies the glossary definition as well.

3. READING: Table Eligibility vs Male Without a Female Partner
   Text: The table explicitly lists rows for:
   - A female under 35 with a male partner
   - A female under 35 without a male partner
   - A female 35 or older with a male partner
   - A female 35 or older without a male partner
   - A male of any age with a female partner under 35
   - A male of any age with a female partner 35 or older
   Interpretation: The table does not specify FSH or trying-to-conceive requirements for a male without a female partner.
   In favor of the member, a male without a female partner (e.g., qualifying under the glossary via abnormal semen analyses
   or gender dysphoria) is not barred by the table, and has no FSH or intercourse requirements under the table ("Does not apply").

4. READING: Documentation of Condition Causing Infertility
   Text: "There exists a condition that: Is demonstrated to cause the illness of infertility. Has been recognized by your
   physician or infertility specialist and documented in your or your partner's medical records."
   Interpretation: The member meets this criterion if either the member or their partner has a documented recognized
   condition demonstrated to cause infertility, OR if infertility itself (as defined under the policy/glossary) is the documented
   recognized condition diagnosed by a physician/specialist.

5. READING: Natural Physiologic Process
   Text: "You or your partner does not have infertility that is due to a natural physiologic process such as age related
   ovarian insufficiency (e.g. perimenopause, menopause)."
   Interpretation: Only disqualified if the infertility is caused by a natural physiologic process such as perimenopause/menopause.
   If the cause is not attributed to such a natural physiologic process, this requirement is satisfied.

6. READING: Voluntary Sterilization
   Text: "You or your partner has not had a voluntary sterilization with or without surgical reversal, regardless of post reversal results.
   This includes tubal ligation, hysterectomy and vasectomy only if obtained as a form of voluntary sterilization."
   Interpretation: A hysterectomy, tubal ligation, or vasectomy performed for medical indications (not as voluntary elective sterilization)
   does not disqualify the member. Only voluntary elective sterilization disqualifies.

7. READING: Unmedicated Day 3 FSH Test Timing and Results
   Text:
   - Female < 35: FSH test done within past 12 months; most recent lab test < 19 mIU/mL.
   - Female 35-39: FSH test done within past 6 months; most recent lab test < 19 mIU/mL.
   - Female 40+: FSH test done within past 6 months; all prior tests performed after age 40 must be < 19 mIU/mL.
   Interpretation: The test must be an unmedicated day 3 FSH test. For females under 40, the most recent test within the lookback window
   must be strictly less than 19 mIU/mL. For females 40 and older, all tests performed after age 40 must be strictly less than 19 mIU/mL,
   and at least one valid test must have occurred within the past 6 months.
"""

from datetime import datetime
from typing import Optional

SCHEMA = {
    # Plan enrollment
    "is_covered_student_or_partner": {
        "description": "Patient is covered under this plan as a student or as a covered legal spouse, civil union partner, or domestic partner.",
        "type": "bool",
    },
    # Service
    "service_type": {
        "description": "The specific infertility service requested: 'ovulation_induction_with_menotropins' or 'intrauterine_insemination'.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    # Medical history & disqualifiers
    "documented_infertility_condition": {
        "description": "There exists a condition demonstrated to cause infertility, recognized by a physician/specialist and documented in medical records.",
        "type": "bool",
    },
    "has_voluntary_sterilization": {
        "description": "Whether the patient or their partner had a voluntary sterilization (e.g., tubal ligation, vasectomy, hysterectomy as elective sterilization).",
        "type": "bool",
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Whether infertility is due to a natural physiologic process such as age-related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
    },
    "less_costly_treatment_available": {
        "description": "Whether a successful pregnancy can be attained through less costly treatment for which coverage is available under this plan.",
        "type": "bool",
    },
    # Demographic & relationship characteristics
    "patient_gender": {
        "description": "Gender of the patient receiving or seeking treatment ('female' or 'male').",
        "type": "str",
        "allowed_values": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of the patient in years at the time of claim/service.",
        "type": "int",
    },
    "partner_gender": {
        "description": "Gender of the partner, if any ('female', 'male', or None/omitted if no partner).",
        "type": "str",
        "allowed_values": ["female", "male", "none"],
    },
    "partner_age": {
        "description": "Age of the partner in years, if partner exists.",
        "type": "int",
    },
    "gender_dysphoria_diagnosed": {
        "description": "Whether the patient or their partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
    },
    # Conception attempts
    "months_trying_conception_intercourse": {
        "description": "Number of months of frequent, unprotected timed heterosexual intercourse trying to conceive.",
        "type": "int",
    },
    "donor_insemination_cycles": {
        "description": "Number of self-paid / not paid for by plan donor artificial insemination cycles completed.",
        "type": "int",
    },
    "male_abnormal_semen_analyses_count": {
        "description": "For male without female partner, count of abnormal semen analyses obtained at least 2 weeks apart.",
        "type": "int",
    },
    # FSH test details (for female patients)
    "fsh_test_date": {
        "description": "Date of the most recent unmedicated day 3 FSH test ('YYYY_MM_DD').",
        "type": "str",
    },
    "current_date": {
        "description": "Date of the request or service evaluation ('YYYY_MM_DD').",
        "type": "str",
    },
    "most_recent_day3_fsh_level": {
        "description": "Result of the most recent unmedicated day 3 FSH test in mIU/mL.",
        "type": "float",
    },
    "all_post_40_fsh_levels_under_19": {
        "description": "For female patients age 40 and older, whether all prior unmedicated day 3 FSH tests performed after age 40 were < 19 mIU/mL.",
        "type": "bool",
    },
}


def covered_under_benefit(claim: dict) -> bool:
    # 1. Plan enrollment check
    if not claim.get("is_covered_student_or_partner"):
        return False

    # 2. Covered services check
    allowed_services = [
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ]
    if claim.get("service_type") not in allowed_services:
        return False

    # 3. Medical exclusions and conditions
    if claim.get("has_voluntary_sterilization") is True:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is True:
        return False
    if claim.get("less_costly_treatment_available") is True:
        return False
    if not claim.get("documented_infertility_condition"):
        return False

    # Patient demographics
    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    partner_gender = claim.get("partner_gender")
    partner_age = claim.get("partner_age")

    if patient_gender not in ["female", "male"] or patient_age is None:
        return False

    has_male_partner = partner_gender == "male"
    has_female_partner = partner_gender == "female"

    # Months trying and donor cycles
    months_intercourse = claim.get("months_trying_conception_intercourse", 0)
    donor_cycles = claim.get("donor_insemination_cycles", 0)
    semen_analyses = claim.get("male_abnormal_semen_analyses_count", 0)
    has_gender_dysphoria = claim.get("gender_dysphoria_diagnosed", False)

    # 4. Glossary Infertility Determination
    # Definition of infertile under glossary:
    # - Gender dysphoria clinically diagnosed in individual or partner
    # - Female with male partner: >= 12 months intercourse if < 35, >= 6 months if >= 35
    # - Female without male partner: >= 12 cycles donor insemination if < 35, >= 6 cycles if >= 35
    # - Male without female partner: >= 2 abnormal semen analyses at least 2 weeks apart
    # In member's favor, female with male partner may also qualify via donor insemination or gender dysphoria.
    glossary_infertile = False
    if has_gender_dysphoria:
        glossary_infertile = True
    elif patient_gender == "female":
        if has_male_partner:
            if patient_age < 35:
                if months_intercourse >= 12 or donor_cycles >= 12:
                    glossary_infertile = True
            else:
                if months_intercourse >= 6 or donor_cycles >= 6:
                    glossary_infertile = True
        else:
            # Female without male partner
            if patient_age < 35:
                if donor_cycles >= 12:
                    glossary_infertile = True
            else:
                if donor_cycles >= 6:
                    glossary_infertile = True
    elif patient_gender == "male":
        if not has_female_partner:
            if semen_analyses >= 2:
                glossary_infertile = True
        else:
            # Male with female partner
            if partner_age is not None:
                if partner_age < 35 and months_intercourse >= 12:
                    glossary_infertile = True
                elif partner_age >= 35 and months_intercourse >= 6:
                    glossary_infertile = True

    if not glossary_infertile:
        return False

    # 5. Table Requirements (Months trying / Donor cycles & FSH testing)
    # Check FSH timing helper
    def months_between(d_earlier: str, d_later: str) -> Optional[float]:
        try:
            dt1 = datetime.strptime(d_earlier, "%Y_%m_%d")
            dt2 = datetime.strptime(d_later, "%Y_%m_%d")
            # Calculate calendar difference in months (approx 365.25 / 12 days per month)
            days = (dt2 - dt1).days
            if days < 0:
                return None
            return days / (365.25 / 12)
        except Exception:
            return None

    # Check rows of the table:
    if patient_gender == "female":
        # Check months / donor cycles
        if has_male_partner:
            if patient_age < 35:
                if not (months_intercourse >= 12 or donor_cycles >= 12):
                    return False
                fsh_window_months = 12
            else:
                if not (months_intercourse >= 6 or donor_cycles >= 6):
                    return False
                fsh_window_months = 6
        else:
            # Female without male partner
            if patient_age < 35:
                if donor_cycles < 12:
                    return False
                fsh_window_months = 12
            else:
                if donor_cycles < 6:
                    return False
                fsh_window_months = 6

        # Check FSH test date window
        test_date = claim.get("fsh_test_date")
        curr_date = claim.get("current_date")
        if not test_date or not curr_date:
            return False

        diff_months = months_between(test_date, curr_date)
        if diff_months is None or diff_months > fsh_window_months:
            return False

        # Check FSH level
        fsh_level = claim.get("most_recent_day3_fsh_level")
        if fsh_level is None or fsh_level >= 19.0:
            return False

        # If age 40 and older, all prior tests performed after age 40 must be < 19 mIU/mL
        if patient_age >= 40:
            if claim.get("all_post_40_fsh_levels_under_19") is not True:
                return False

    elif patient_gender == "male":
        if has_female_partner:
            if partner_age is None:
                return False
            if partner_age < 35:
                if months_intercourse < 12:
                    return False
            else:
                if months_intercourse < 6:
                    return False
        else:
            # Male without female partner: table specifies "Does not apply" / no row
            pass

    return True
