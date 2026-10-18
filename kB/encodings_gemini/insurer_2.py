"""
Policy Coverage Decision Module: Comprehensive Infertility Services
Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64, and Glossary

READING CHOICES:
1. READING: Covered services scope.
   "We will cover charges made by an infertility specialist for the following infertility services:
   • Ovulation induction cycle(s) with menotropins
   • Intrauterine insemination"
   Coverage is strictly confined to ovulation induction with menotropins and intrauterine
   insemination, rendered by an infertility specialist. Other services or non-specialist providers
   are not covered.

2. READING: Eligible beneficiary status.
   "You are covered under this plan as a student or as a covered dependent who is the student’s legal
   spouse, civil union partner or domestic partner"
   Only a student or their covered legal spouse/civil union partner/domestic partner is eligible.
   Child dependents are not eligible.

3. READING: Infertility definition for female with male partner vs. table criteria.
   "A disease defined by the failure to become pregnant: For a female with a male partner, after:
   1 year of frequent, unprotected heterosexual sexual intercourse if under the age of 35;
   6 months ... if age 35 or older"
   Under the glossary definition, infertility for a female with a male partner is defined strictly
   by failure to become pregnant after frequent, unprotected heterosexual intercourse (or gender
   dysphoria). Although the table lists donor insemination as an alternative to meet the
   egg-and-sperm contact requirement, under the insurer-favorable reading, a female with a male
   partner must independently satisfy the glossary definition of infertility (requiring the
   specified duration of heterosexual intercourse or a gender dysphoria diagnosis).

4. READING: Male without a female partner.
   "• Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following criteria: [table]"
   The policy table explicitly enumerates six categories. A male without a female partner is not
   listed in the table, cannot satisfy the table's mandatory criteria, and is therefore ineligible.

5. READING: FSH threshold standard.
   "Must be less than 19 mIU/mL"
   "Less than 19" requires a level strictly less than 19.0 mIU/mL. A test result of exactly
   19.0 mIU/mL does not satisfy the requirement.

6. READING: Age 40+ FSH history.
   "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40."
   For a female claimant aged 40 or older, every test performed after reaching age 40 (both prior
   tests and the most recent test) must be strictly less than 19.0 mIU/mL. If any test after age 40
   was 19.0 mIU/mL or higher, coverage is barred.

7. READING: Impact of gender dysphoria diagnosis.
   "For an individual or their partner who has been clinically diagnosed with gender dysphoria"
   A clinical diagnosis of gender dysphoria establishes infertility under the glossary, but does
   not exempt the claimant from the separate eligibility requirements in the policy text, including
   the table's requirements for months of egg/sperm contact or donor insemination and FSH testing.

8. READING: Voluntary sterilization disqualification.
   "You or your partner has not had a voluntary sterilization with or without surgical reversal,
   regardless of post reversal results."
   Any voluntary sterilization of either partner (tubal ligation, hysterectomy, vasectomy), even
   if surgically reversed, permanently bars eligibility under this benefit.
"""

import calendar
from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The specific comprehensive infertility service requested.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_coverage_status": {
        "description": "Enrollment status of the patient under the Cardinal Care plan.",
        "type": "str",
        "allowed": ["student", "covered_dependent_partner", "other"],
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "Whether there exists a condition demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_medical_records": {
        "description": "Whether the condition has been recognized by a physician or infertility specialist and documented in medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "has_had_voluntary_sterilization": {
        "description": "Whether the patient or their partner has had a voluntary sterilization (e.g., tubal ligation, vasectomy, elective hysterectomy), regardless of reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Whether infertility is due to a natural physiologic process such as age-related ovarian insufficiency, perimenopause, or menopause.",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": "Whether a successful pregnancy can be attained through less costly treatment covered under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_gender": {
        "description": "Gender of the patient.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_age": {
        "description": "Age of the patient in whole years at the date of service.",
        "type": "int",
        "allowed": "Integer >= 0",
    },
    "partner_gender": {
        "description": "Gender of the patient's legal spouse, civil union partner, or domestic partner, or 'none' if patient has no partner.",
        "type": "str",
        "allowed": ["male", "female", "none"],
    },
    "partner_age": {
        "description": "Age of the patient's partner in whole years at the date of service (required if partner is female).",
        "type": "int",
        "allowed": "Integer >= 0",
    },
    "clinical_diagnosis_of_gender_dysphoria": {
        "description": "Whether the patient or their partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_of_unprotected_timed_intercourse": {
        "description": "Number of completed months trying to conceive through frequent, unprotected timed heterosexual intercourse.",
        "type": "int",
        "allowed": "Integer >= 0",
    },
    "donor_insemination_cycles_self_paid": {
        "description": "Number of donor artificial insemination cycles completed that were self-paid / not paid for by the plan.",
        "type": "int",
        "allowed": "Integer >= 0",
    },
    "service_date": {
        "description": "Date of service in 'YYYY_MM_DD' format.",
        "type": "str",
        "allowed": "String matching YYYY_MM_DD",
    },
    "most_recent_fsh_test_date": {
        "description": "Date of the most recent unmedicated day 3 FSH test in 'YYYY_MM_DD' format.",
        "type": "str",
        "allowed": "String matching YYYY_MM_DD",
    },
    "fsh_test_is_unmedicated_day_3": {
        "description": "Whether the most recent FSH test was an unmedicated day 3 test.",
        "type": "bool",
        "allowed": [True, False],
    },
    "most_recent_fsh_level": {
        "description": "Result of the most recent unmedicated day 3 FSH test in mIU/mL.",
        "type": "float",
        "allowed": "Float >= 0.0",
    },
    "prior_fsh_levels_after_age_40": {
        "description": "List of results in mIU/mL of all other prior FSH tests performed after reaching age 40 (empty list if none).",
        "type": "list",
        "allowed": "List of floats >= 0.0",
    },
}


def _parse_date(d_str: str) -> date:
    parts = d_str.split("_")
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


def _subtract_months(d: date, months: int) -> date:
    year = d.year
    month = d.month - months
    while month <= 0:
        month += 12
        year -= 1
    max_days = calendar.monthrange(year, month)[1]
    day = min(d.day, max_days)
    return date(year, month, day)


def covered_under_benefit(claim: dict) -> bool:
    # 1. Covered services verification
    service_type = claim.get("service_type")
    if service_type not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False

    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # 2. Beneficiary eligibility
    coverage_status = claim.get("patient_coverage_status")
    if coverage_status not in ("student", "covered_dependent_partner"):
        return False

    # 3. Documented condition demonstrated to cause infertility
    if claim.get("condition_demonstrated_to_cause_infertility") is not True:
        return False
    if claim.get("condition_documented_in_medical_records") is not True:
        return False

    # 4. Mandatory exclusions (sterilization, natural physiologic process, less costly treatment)
    if claim.get("has_had_voluntary_sterilization") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if (
        claim.get("pregnancy_attainable_through_less_costly_covered_treatment")
        is not False
    ):
        return False

    # 5. Demographics validation
    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    if patient_gender not in ("female", "male"):
        return False
    if patient_age is None or not isinstance(patient_age, int) or patient_age < 0:
        return False

    partner_gender = claim.get("partner_gender")
    if partner_gender not in ("male", "female", "none"):
        return False

    has_gender_dysphoria = (
        claim.get("clinical_diagnosis_of_gender_dysphoria") is True
    )
    months_intercourse = claim.get("months_of_unprotected_timed_intercourse")
    donor_cycles = claim.get("donor_insemination_cycles_self_paid")

    # 6. Evaluation by patient category
    if patient_gender == "female":
        has_male_partner = partner_gender == "male"

        # Check Glossary definition of Infertile / Infertility
        if has_gender_dysphoria:
            glossary_infertile = True
        elif has_male_partner:
            if months_intercourse is None or not isinstance(
                months_intercourse, int
            ):
                return False
            if patient_age < 35:
                glossary_infertile = months_intercourse >= 12
            else:
                glossary_infertile = months_intercourse >= 6
        else:
            # Female without male partner
            if donor_cycles is None or not isinstance(donor_cycles, int):
                return False
            if patient_age < 35:
                glossary_infertile = donor_cycles >= 12
            else:
                glossary_infertile = donor_cycles >= 6

        if not glossary_infertile:
            return False

        # Check Table criteria: Months trying to conceive / donor insemination
        if has_male_partner:
            if patient_age < 35:
                intercourse_ok = (
                    months_intercourse is not None
                    and isinstance(months_intercourse, int)
                    and months_intercourse >= 12
                )
                donor_ok = (
                    donor_cycles is not None
                    and isinstance(donor_cycles, int)
                    and donor_cycles >= 12
                )
            else:
                intercourse_ok = (
                    months_intercourse is not None
                    and isinstance(months_intercourse, int)
                    and months_intercourse >= 6
                )
                donor_ok = (
                    donor_cycles is not None
                    and isinstance(donor_cycles, int)
                    and donor_cycles >= 6
                )
            if not (intercourse_ok or donor_ok):
                return False
        else:
            if donor_cycles is None or not isinstance(donor_cycles, int):
                return False
            required_cycles = 12 if patient_age < 35 else 6
            if donor_cycles < required_cycles:
                return False

        # Check Table criteria: FSH test timing and results
        if claim.get("fsh_test_is_unmedicated_day_3") is not True:
            return False

        service_date_str = claim.get("service_date")
        fsh_date_str = claim.get("most_recent_fsh_test_date")
        if not service_date_str or not fsh_date_str:
            return False

        try:
            service_date = _parse_date(service_date_str)
            fsh_test_date = _parse_date(fsh_date_str)
        except (ValueError, IndexError):
            return False

        if fsh_test_date > service_date:
            return False

        max_lookback_months = 12 if patient_age < 35 else 6
        earliest_date = _subtract_months(service_date, max_lookback_months)
        if fsh_test_date < earliest_date:
            return False

        most_recent_fsh = claim.get("most_recent_fsh_level")
        if most_recent_fsh is None or not isinstance(
            most_recent_fsh, (int, float)
        ):
            return False
        if most_recent_fsh >= 19.0:
            return False

        if patient_age >= 40:
            prior_levels = claim.get("prior_fsh_levels_after_age_40")
            if prior_levels is None or not isinstance(prior_levels, list):
                return False
            for lvl in prior_levels:
                if lvl is None or not isinstance(lvl, (int, float)):
                    return False
                if lvl >= 19.0:
                    return False

        return True

    else:
        # patient_gender == "male"
        # Males without a female partner are not included in the table and cannot meet table criteria
        if partner_gender != "female":
            return False

        partner_age = claim.get("partner_age")
        if (
            partner_age is None
            or not isinstance(partner_age, int)
            or partner_age < 0
        ):
            return False

        required_intercourse_months = 12 if partner_age < 35 else 6

        # Check Glossary definition of Infertile / Infertility
        if has_gender_dysphoria:
            glossary_infertile = True
        else:
            if months_intercourse is None or not isinstance(
                months_intercourse, int
            ):
                return False
            glossary_infertile = months_intercourse >= required_intercourse_months

        if not glossary_infertile:
            return False

        # Check Table criteria: Months of unprotected timed sexual intercourse
        if months_intercourse is None or not isinstance(
            months_intercourse, int
        ):
            return False
        if months_intercourse < required_intercourse_months:
            return False

        # For males, the table specifies that donor insemination and FSH testing do not apply
        return True
