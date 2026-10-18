"""
Comprehensive infertility services coverage encoder.

READING choices:
1. The service list limits this benefit to the two expressly named treatments.
2. The glossary and benefit-specific eligibility requirements apply cumulatively.
3. The table supplies the available eligibility pathways; unlisted configurations
   do not establish eligibility under this benefit.
4. Neither the patient nor an existing partner may have the specified voluntary
   sterilization or natural-physiologic infertility.
5. Required donor cycles must be self-paid and not paid for by the plan.
6. For patients age 40 or older, all unmedicated day-3 FSH tests on or after
   the 40th birthday must be below 19, including the latest such test.
   The policy does not independently require a test after that birthday.
7. Test recency uses inclusive calendar-month lookbacks, and age is determined
   on the service date.
8. Charges must be made by an infertility specialist. Advance approval and the
   other checks assigned elsewhere are not encoded.

Missing or invalid facts cannot establish a required condition. Facts irrelevant
to an otherwise established pathway need not be supplied.
"""

import calendar
import math
from datetime import date


SCHEMA = {
    "service": {
        "description": "Treatment being claimed.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "charged_by_infertility_specialist": {
        "description": "Whether an infertility specialist makes the charge.",
        "type": "bool",
        "allowed": [True, False],
    },
    "coverage_status": {
        "description": "Patient's covered relationship to the student.",
        "type": "str",
        "allowed": [
            "covered_student",
            "covered_legal_spouse",
            "covered_civil_union_partner",
            "covered_domestic_partner",
            "other_or_not_covered",
        ],
    },
    "service_date": {
        "description": "Date on which coverage is being evaluated.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_birth_date": {
        "description": "Patient's birth date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Patient's category for applying the policy's sex-specific rules.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_sex": {
        "description": "Existing partner's category, or absence of a partner.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "partner_age_years": {
        "description": "Partner's completed age on the service date; needed for a male patient.",
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "An existing condition is demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": (
            "That condition is recognized by the physician or infertility specialist "
            "and documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "no_voluntary_sterilization_in_patient_or_partner": {
        "description": (
            "Neither patient nor existing partner has had voluntary sterilization, "
            "regardless of reversal or its results. Tubal ligation, hysterectomy, "
            "and vasectomy count here only when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "no_natural_physiologic_infertility_in_patient_or_partner": {
        "description": (
            "Neither patient nor existing partner has infertility due to a natural "
            "physiologic process, including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_unattainable_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy cannot be attained through less costly treatment "
            "covered under this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "failure_to_become_pregnant": {
        "description": (
            "Failure to become pregnant during the reported intercourse attempts "
            "or donor insemination cycles."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "months_frequent_unprotected_heterosexual_intercourse": {
        "description": "Months of attempts meeting the glossary's intercourse wording.",
        "type": "int or float",
        "allowed": "Finite nonnegative number; excludes bool.",
    },
    "months_unprotected_timed_sexual_intercourse": {
        "description": "Months of attempts meeting the table's timed-intercourse wording.",
        "type": "int or float",
        "allowed": "Finite nonnegative number; excludes bool.",
    },
    "self_paid_donor_insemination_cycles": {
        "description": "Completed donor artificial insemination cycles self-paid, not plan-paid.",
        "type": "int",
        "allowed": "Nonnegative integer; excludes bool.",
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": "Patient or existing partner has a clinical gender-dysphoria diagnosis.",
        "type": "bool",
        "allowed": [True, False],
    },
    "most_recent_unmedicated_day3_fsh_date": {
        "description": (
            "Date of the actual most recent unmedicated day-3 FSH test "
            "on or before the service date."
        ),
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "most_recent_unmedicated_day3_fsh_value": {
        "description": "That test's result in mIU/mL; needed when the patient is under 40.",
        "type": "int or float",
        "allowed": "Finite nonnegative number; excludes bool.",
    },
    "all_unmedicated_day3_fsh_since_40_below_19": {
        "description": (
            "Complete-history fact: every unmedicated day-3 FSH test performed "
            "on or after the patient's 40th birthday through the service date, "
            "including the latest applicable test, was below 19 mIU/mL. "
            "True also when there were no tests in that interval."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
}


def _parse_date(value):
    if not isinstance(value, str):
        return None
    parts = value.split("_")
    if (
        len(parts) != 3
        or tuple(map(len, parts)) != (4, 2, 2)
        or any(not p.isascii() or not p.isdigit() for p in parts)
    ):
        return None
    try:
        return date(*(int(p) for p in parts))
    except ValueError:
        return None


def _nonnegative_number(value):
    if type(value) is int:
        return value >= 0
    return type(value) is float and math.isfinite(value) and value >= 0


def _at_least(value, minimum):
    return _nonnegative_number(value) and value >= minimum


def _subtract_calendar_months(day, months):
    month_index = day.year * 12 + day.month - 1 - months
    year, month_zero = divmod(month_index, 12)
    if year < 1:
        return date.min
    month = month_zero + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def covered_under_benefit(claim: dict) -> bool:
    if not isinstance(claim, dict):
        return False

    # READING: Scope — "for the following infertility services" names only
    # ovulation induction with menotropins and intrauterine insemination.
    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False

    # READING: Provider — "charges made by an infertility specialist" is a
    # provider-specialty requirement, not a provider-network requirement.
    if claim.get("charged_by_infertility_specialist") is not True:
        return False

    if claim.get("coverage_status") not in (
        "covered_student",
        "covered_legal_spouse",
        "covered_civil_union_partner",
        "covered_domestic_partner",
    ):
        return False

    # READING: Shared exclusions — "You or your partner has not had" and
    # "You or your partner does not have" mean neither person may have
    # the disqualifying history or cause; reversal does not cure sterilization.
    required_true = (
        "condition_demonstrated_to_cause_infertility",
        "condition_recognized_and_documented",
        "no_voluntary_sterilization_in_patient_or_partner",
        "no_natural_physiologic_infertility_in_patient_or_partner",
        "pregnancy_unattainable_with_less_costly_covered_treatment",
    )
    if any(claim.get(field) is not True for field in required_true):
        return False

    service_date = _parse_date(claim.get("service_date"))
    birth_date = _parse_date(claim.get("patient_birth_date"))
    if service_date is None or birth_date is None or birth_date > service_date:
        return False

    # READING: Timing — "under 35", "age 40 and older", and "within the past"
    # are evaluated on the service date; month lookbacks are inclusive calendar
    # months, clamping to the last day when the corresponding day does not exist.
    age = service_date.year - birth_date.year - (
        (service_date.month, service_date.day)
        < (birth_date.month, birth_date.day)
    )

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if partner_sex not in ("female", "male", "other", "none"):
        return False

    donor_cycles = claim.get("self_paid_donor_insemination_cycles")
    valid_donor_count = type(donor_cycles) is int and donor_cycles >= 0
    timed_months = claim.get("months_unprotected_timed_sexual_intercourse")
    glossary_months = claim.get(
        "months_frequent_unprotected_heterosexual_intercourse"
    )

    # READING: Table pathways — "You have met the requirement for the number
    # of months" and "meets the following criteria" make the table's listed
    # configurations the eligibility pathways. The glossary's male-without-
    # female-partner and gender-dysphoria definitions do not create missing
    # table pathways or waive the table.
    if sex == "female":
        threshold = 12 if age < 35 else 6

        # READING: Donor payment — "Self paid/not paid for by plan" qualifies
        # donor cycles used to satisfy the table, including its "or" alternatives.
        donor_ok = valid_donor_count and donor_cycles >= threshold
        table_attempts_ok = donor_ok or (
            partner_sex == "male" and _at_least(timed_months, threshold)
        )
        ordinary_glossary_ok = (
            _at_least(glossary_months, threshold)
            if partner_sex == "male"
            else donor_ok
        )

        test_date = _parse_date(
            claim.get("most_recent_unmedicated_day3_fsh_date")
        )
        if (
            test_date is None
            or test_date < birth_date
            or test_date > service_date
            or test_date < _subtract_calendar_months(service_date, threshold)
        ):
            return False

        if age < 40:
            result = claim.get("most_recent_unmedicated_day3_fsh_value")
            if not _nonnegative_number(result) or result >= 19:
                return False
        else:
            # READING: Older-patient FSH — "less than 19 mIU/mL in all prior
            # tests performed after age 40" includes the latest applicable
            # unmedicated day-3 test and tests on the 40th birthday. It does
            # not independently require a post-40 test if a recent pre-40
            # test satisfies the six-month recency requirement.
            if claim.get("all_unmedicated_day3_fsh_since_40_below_19") is not True:
                return False

    elif sex == "male" and partner_sex == "female":
        partner_age = claim.get("partner_age_years")
        if type(partner_age) is not int or partner_age < 0:
            return False
        threshold = 12 if partner_age < 35 else 6
        table_attempts_ok = _at_least(timed_months, threshold)
        # The female partner's failure to become pregnant establishes the
        # couple's ordinary intercourse-based infertility pathway.
        ordinary_glossary_ok = _at_least(glossary_months, threshold)
        # The male rows expressly mark FSH as "Does not apply".
    else:
        return False

    if not table_attempts_ok:
        return False

    # READING: Cumulative definitions — "Infertile or infertility" defines
    # the disease, while "You are eligible ... if" supplies additional
    # requirements. A donor alternative in the table does not replace the
    # glossary's intercourse requirement for a female with a male partner.
    # "For an individual or their partner ... diagnosed with gender dysphoria"
    # independently satisfies the glossary, but not the table.
    glossary_ok = (
        claim.get("patient_or_partner_clinically_diagnosed_gender_dysphoria")
        is True
    ) or (
        claim.get("failure_to_become_pregnant") is True
        and ordinary_glossary_ok
    )

    return bool(glossary_ok)
