from datetime import date, timedelta
import calendar
import math


SCHEMA = {
    "service": {
        "description": "Infertility service for which coverage is requested.",
        "type": "str",
        "allowed": ["ovulation_induction_with_menotropins", "intrauterine_insemination"],
    },
    "performed_by_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_under_plan": {
        "description": "Whether the patient is enrolled in this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_relationship": {
        "description": "Patient's relationship to the covered student.",
        "type": "str",
        "allowed": ["student", "legal_spouse", "civil_union_partner",
                    "domestic_partner", "other"],
    },
    "service_date": {
        "description": "Date on which eligibility is evaluated.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "date_of_birth": {
        "description": "Patient's birth date, used to select the policy's age band.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Patient's classification for the policy's female/male rules.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "partner_sex": {
        "description": "Partner's classification; 'none' means no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_date_of_birth": {
        "description": "Required for a male patient with a female partner.",
        "type": "str or None",
        "format": "YYYY_MM_DD, or None when not applicable",
    },
    "infertility_causing_condition": {
        "description": "A condition has been demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": (
            "That condition is recognized by a physician or infertility specialist "
            "and documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_voluntary_sterilization": {
        "description": (
            "Either has undergone voluntary sterilization, even if reversed. "
            "Include hysterectomy, tubal ligation, or vasectomy only when "
            "obtained as voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_natural_physiologic_infertility": {
        "description": (
            "Either has infertility due to a natural physiologic process, "
            "including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_can_achieve_pregnancy": {
        "description": (
            "Whether successful pregnancy can be attained through less costly "
            "treatment covered by this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "qualifying_intercourse_months": {
        "description": (
            "Completed months of frequent, unprotected, timed heterosexual "
            "intercourse trying to conceive through egg and sperm contact."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number",
    },
    "self_paid_donor_insemination_cycles": {
        "description": (
            "Completed donor artificial insemination cycles trying to conceive "
            "that were self-paid and not paid for by the plan."
        ),
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": (
            "Whether the patient or partner has a clinical gender dysphoria "
            "diagnosis, satisfying that alternative in the infertility definition."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "semen_analyses": {
        "description": (
            "Semen analyses for a male patient without a female partner. "
            "Required unless the gender-dysphoria alternative establishes "
            "infertility; otherwise may be an empty list."
        ),
        "type": "list[dict]",
        "format": (
            "Each entry: {'date': 'YYYY_MM_DD', 'abnormal': bool}. "
            "Include results obtained on or before service_date."
        ),
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history of the female patient's unmedicated day-3 FSH "
            "tests through service_date, including every such test after age 40. "
            "Not required for male patients."
        ),
        "type": "list[dict]",
        "format": (
            "Each entry: {'date': 'YYYY_MM_DD', 'value_miu_ml': number}. "
            "Values must be finite and nonnegative."
        ),
    },
}


def _date(value):
    if not isinstance(value, str):
        raise ValueError("Expected a date string")
    parsed = date.fromisoformat(value.replace("_", "-"))
    if parsed.strftime("%Y_%m_%d") != value:
        raise ValueError("Expected YYYY_MM_DD")
    return parsed


def _age(birth, when):
    if birth > when:
        raise ValueError("Birth date is after evaluation date")
    return when.year - birth.year - (
        (when.month, when.day) < (birth.month, birth.day)
    )


def _months_before(when, months):
    index = when.year * 12 + when.month - 1 - months
    year, month_index = divmod(index, 12)
    month = month_index + 1
    return date(year, month, min(when.day, calendar.monthrange(year, month)[1]))


def _nonnegative_number(value):
    if type(value) not in (int, float):
        raise ValueError("Expected a number, not a boolean")
    if not math.isfinite(value) or value < 0:
        raise ValueError("Expected a finite nonnegative number")
    return value


def covered_under_benefit(claim: dict) -> bool:
    """
    Apply only the quoted benefit's service, infertility, and eligibility rules.

    The glossary's infertility definition and the table's eligibility conditions
    are separate requirements. A gender-dysphoria diagnosis establishes
    infertility but does not waive an applicable table requirement.

    The table states no additional duration or FSH rule for a male without a
    female partner; his stated infertility pathway is the glossary's semen-
    analysis pathway (or the gender-dysphoria alternative).
    """
    try:
        if not isinstance(claim, dict):
            return False

        boolean_fields = (
            "performed_by_infertility_specialist",
            "covered_under_plan",
            "infertility_causing_condition",
            "condition_recognized_and_documented",
            "patient_or_partner_voluntary_sterilization",
            "patient_or_partner_natural_physiologic_infertility",
            "less_costly_covered_treatment_can_achieve_pregnancy",
            "patient_or_partner_clinically_diagnosed_gender_dysphoria",
        )
        if any(type(claim[field]) is not bool for field in boolean_fields):
            return False

        if claim["service"] not in (
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
        ):
            return False
        if not claim["performed_by_infertility_specialist"]:
            return False
        if not claim["covered_under_plan"]:
            return False
        if claim["covered_relationship"] not in (
            "student", "legal_spouse", "civil_union_partner", "domestic_partner"
        ):
            return False
        if not claim["infertility_causing_condition"]:
            return False
        if not claim["condition_recognized_and_documented"]:
            return False
        if claim["patient_or_partner_voluntary_sterilization"]:
            return False
        if claim["patient_or_partner_natural_physiologic_infertility"]:
            return False
        if claim["less_costly_covered_treatment_can_achieve_pregnancy"]:
            return False

        when = _date(claim["service_date"])
        birth = _date(claim["date_of_birth"])
        age = _age(birth, when)
        sex = claim["patient_sex"]
        partner_sex = claim["partner_sex"]
        if sex not in ("female", "male"):
            return False
        if partner_sex not in ("female", "male", "none"):
            return False

        dysphoria = claim[
            "patient_or_partner_clinically_diagnosed_gender_dysphoria"
        ]

        if sex == "female":
            months = _nonnegative_number(claim["qualifying_intercourse_months"])
            cycles = claim["self_paid_donor_insemination_cycles"]
            if type(cycles) is not int or cycles < 0:
                return False

            required = 12 if age < 35 else 6

            # Apply the glossary independently of the table's donor-cycle option.
            if partner_sex == "male":
                infertile = dysphoria or months >= required
                attempts_met = months >= required or cycles >= required
            else:
                infertile = dysphoria or cycles >= required
                attempts_met = cycles >= required

            if not infertile or not attempts_met:
                return False

            raw_tests = claim["unmedicated_day3_fsh_tests"]
            if not isinstance(raw_tests, list) or not raw_tests:
                return False

            tests = []
            for test in raw_tests:
                test_date = _date(test["date"])
                if test_date < birth or test_date > when:
                    return False
                value = _nonnegative_number(test["value_miu_ml"])
                tests.append((test_date, value))

            latest_date = max(test_date for test_date, _ in tests)
            lookback = 12 if age < 35 else 6
            if latest_date < _months_before(when, lookback):
                return False

            if age < 40:
                # Check every result if multiple tests share the latest date.
                if any(
                    value >= 19
                    for test_date, value in tests
                    if test_date == latest_date
                ):
                    return False
            else:
                if any(
                    value >= 19
                    for test_date, value in tests
                    if _age(birth, test_date) >= 40
                ):
                    return False

            return True

        if partner_sex == "female":
            partner_birth = _date(claim["partner_date_of_birth"])
            partner_age = _age(partner_birth, when)
            required = 12 if partner_age < 35 else 6
            months = _nonnegative_number(claim["qualifying_intercourse_months"])

            # Even with the glossary's dysphoria alternative, the male table
            # row requires the stated duration of intercourse.
            return months >= required

        if dysphoria:
            return True

        analyses = claim["semen_analyses"]
        if not isinstance(analyses, list):
            return False

        abnormal_dates = []
        for analysis in analyses:
            analysis_date = _date(analysis["date"])
            if analysis_date < birth or analysis_date > when:
                return False
            if type(analysis["abnormal"]) is not bool:
                return False
            if analysis["abnormal"]:
                abnormal_dates.append(analysis_date)

        return (
            len(abnormal_dates) >= 2
            and max(abnormal_dates) - min(abnormal_dates) >= timedelta(days=14)
        )

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
