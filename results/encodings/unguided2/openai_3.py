import calendar
import math
from datetime import date, timedelta


SCHEMA = {
    "service": {
        "description": "Service for which coverage is requested.",
        "type": "str",
        "allowed": ["ovulation_induction_with_menotropins", "intrauterine_insemination"],
    },
    "service_date": {
        "description": "Date on which eligibility is evaluated.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "covered_under_plan": {
        "description": "Whether the patient is covered under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_role": {
        "description": "Patient's relationship to the covered student.",
        "type": "str",
        "allowed": [
            "student", "dependent_legal_spouse",
            "dependent_civil_union_partner", "dependent_domestic_partner",
            "other",
        ],
    },
    "patient_sex": {
        "description": "Patient's classification for applying the policy's sex-specific criteria.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Partner's classification for applying the policy's partner-specific criteria.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's birth date; required for a male patient with a female partner.",
        "type": "str or None",
        "format": "YYYY_MM_DD or None",
    },
    "infertility_causing_condition_demonstrated": {
        "description": "A condition in the patient or partner is demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_physician_recognized_and_documented": {
        "description": "That condition is recognized by a physician or infertility specialist and documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "either_has_voluntary_sterilization": {
        "description": "Patient or partner has ever had voluntary sterilization, regardless of reversal or its results; procedures for other purposes do not count.",
        "type": "bool",
        "allowed": [True, False],
    },
    "either_has_natural_physiologic_infertility": {
        "description": "Patient or partner has infertility due to a natural physiologic process, including age-related ovarian insufficiency.",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through a less costly treatment covered by this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "failure_to_become_pregnant": {
        "description": "Failure to become pregnant during the reported intercourse or donor-insemination attempts.",
        "type": "bool",
        "allowed": [True, False],
    },
    "frequent_unprotected_intercourse_months": {
        "description": "Completed months of frequent, unprotected heterosexual intercourse, for the glossary definition.",
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "unprotected_timed_intercourse_months": {
        "description": "Completed months of unprotected timed intercourse, for the eligibility table.",
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "donor_insemination_cycles": {
        "description": "Completed donor-insemination cycles, regardless of payer, for the glossary definition.",
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "self_paid_donor_insemination_cycles": {
        "description": "Completed donor-insemination cycles self-paid and not paid for by the plan, for the eligibility table.",
        "type": "int",
        "allowed": "Nonnegative integer, no greater than donor_insemination_cycles",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of abnormal semen analyses obtained by the male patient, for the glossary definition.",
        "type": "list[str]",
        "format": 'List of dates in "YYYY_MM_DD" format',
    },
    "either_clinically_diagnosed_gender_dysphoria": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "unmedicated_day3_fsh_tests": {
        "description": "Complete history of the female patient's unmedicated day-3 FSH tests through the service date, including all such tests at age 40 or older.",
        "type": "list[dict]",
        "format": 'Each item: {"date": "YYYY_MM_DD", "level_miu_ml": nonnegative finite number}',
    },
}


def _date(value):
    if not isinstance(value, str):
        raise ValueError("Date must be a string")
    parts = value.split("_")
    if len(parts) != 3 or [len(p) for p in parts] != [4, 2, 2]:
        raise ValueError("Invalid date format")
    if not all(p.isascii() and p.isdigit() for p in parts):
        raise ValueError("Invalid date format")
    return date(*(int(p) for p in parts))


def _age(birth, on):
    if birth > on:
        raise ValueError("Birth date is in the future")
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _months_before(on, months):
    month_index = on.year * 12 + on.month - 1 - months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    return date(year, month, min(on.day, calendar.monthrange(year, month)[1]))


def covered_under_benefit(claim: dict) -> bool:
    """Evaluate only the supplied benefit criteria; other claim checks are external."""
    if not isinstance(claim, dict):
        return False

    try:
        boolean_fields = [
            "covered_under_plan",
            "infertility_causing_condition_demonstrated",
            "condition_physician_recognized_and_documented",
            "either_has_voluntary_sterilization",
            "either_has_natural_physiologic_infertility",
            "pregnancy_attainable_with_less_costly_covered_treatment",
            "failure_to_become_pregnant",
            "either_clinically_diagnosed_gender_dysphoria",
        ]
        for field in boolean_fields:
            if type(claim[field]) is not bool:
                return False

        count_fields = [
            "frequent_unprotected_intercourse_months",
            "unprotected_timed_intercourse_months",
            "donor_insemination_cycles",
            "self_paid_donor_insemination_cycles",
        ]
        for field in count_fields:
            if type(claim[field]) is not int or claim[field] < 0:
                return False

        if claim["service"] not in (
            "ovulation_induction_with_menotropins", "intrauterine_insemination"
        ):
            return False
        if not claim["covered_under_plan"] or claim["covered_role"] not in (
            "student", "dependent_legal_spouse",
            "dependent_civil_union_partner", "dependent_domestic_partner",
        ):
            return False
        if not (
            claim["infertility_causing_condition_demonstrated"]
            and claim["condition_physician_recognized_and_documented"]
        ):
            return False
        if (
            claim["either_has_voluntary_sterilization"]
            or claim["either_has_natural_physiologic_infertility"]
            or claim["pregnancy_attainable_with_less_costly_covered_treatment"]
        ):
            return False

        on = _date(claim["service_date"])
        birth = _date(claim["patient_birth_date"])
        age = _age(birth, on)
        sex = claim["patient_sex"]
        partner = claim["partner_sex"]
        if sex not in ("female", "male", "other"):
            return False
        if partner not in ("female", "male", "other", "none"):
            return False

        frequent = claim["frequent_unprotected_intercourse_months"]
        timed = claim["unprotected_timed_intercourse_months"]
        donor = claim["donor_insemination_cycles"]
        self_paid = claim["self_paid_donor_insemination_cycles"]
        if self_paid > donor:
            return False

        partner_age = None
        if sex == "male" and partner == "female":
            partner_age = _age(_date(claim["partner_birth_date"]), on)

        # Apply the glossary independently of the eligibility table.
        infertile = claim["either_clinically_diagnosed_gender_dysphoria"]
        if claim["failure_to_become_pregnant"]:
            if sex == "female":
                required = 12 if age < 35 else 6
                if partner == "male":
                    infertile |= frequent >= required
                else:
                    infertile |= donor >= required
            elif sex == "male" and partner == "female":
                # The female partner's age determines the couple's threshold.
                infertile |= frequent >= (12 if partner_age < 35 else 6)

        if sex == "male" and partner != "female":
            analyses = claim["abnormal_semen_analysis_dates"]
            if not isinstance(analyses, list):
                return False
            dates = sorted(_date(d) for d in analyses)
            if any(d < birth or d > on for d in dates):
                return False
            infertile |= (
                len(dates) >= 2
                and dates[-1] - dates[0] >= timedelta(days=14)
            )

        if not infertile:
            return False

        # Gender dysphoria establishes glossary infertility; it does not waive
        # any eligibility-table requirement applicable to this patient.
        if sex == "female":
            required = 12 if age < 35 else 6
            if partner == "male":
                if timed < required and self_paid < required:
                    return False
            elif self_paid < required:
                return False

            tests = claim["unmedicated_day3_fsh_tests"]
            if not isinstance(tests, list) or not tests:
                return False
            parsed = []
            for test in tests:
                tested_on = _date(test["date"])
                level = test["level_miu_ml"]
                if (
                    type(level) not in (int, float)
                    or not math.isfinite(level)
                    or level < 0
                    or tested_on < birth
                    or tested_on > on
                ):
                    return False
                parsed.append((tested_on, level))

            latest_date = max(d for d, _ in parsed)
            if latest_date < _months_before(on, required):
                return False

            if age < 40:
                if any(level >= 19 for d, level in parsed if d == latest_date):
                    return False
            else:
                if any(
                    level >= 19
                    for d, level in parsed
                    if _age(birth, d) >= 40
                ):
                    return False

        elif sex == "male" and partner == "female":
            if timed < (12 if partner_age < 35 else 6):
                return False

        # The supplied table specifies no intercourse, donor-cycle, or FSH
        # threshold for other categories; do not invent additional thresholds.
        return True

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
