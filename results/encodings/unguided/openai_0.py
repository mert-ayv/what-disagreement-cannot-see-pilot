import calendar
import math
from datetime import date


SCHEMA = {
    "service": {
        "description": "The infertility service for which coverage is requested.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provided_by_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "service_date": {
        "description": "Date of the claimed service; eligibility is evaluated on this date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "covered_role": {
        "description": "Patient's covered status under this plan.",
        "type": "str",
        "allowed_values": [
            "student",
            "student_legal_spouse",
            "student_civil_union_partner",
            "student_domestic_partner",
            "other_or_not_covered",
        ],
    },
    "patient_is_infertile": {
        "description": "Whether the patient has the illness of infertility.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "infertility_causing_condition_demonstrated": {
        "description": "Whether a condition is demonstrated to cause the infertility.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": (
            "Whether that condition is recognized by the physician or infertility "
            "specialist and documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "either_partner_voluntarily_sterilized": {
        "description": (
            "Whether the patient or partner ever had voluntary sterilization, "
            "regardless of reversal or its results. Tubal ligation, hysterectomy, "
            "and vasectomy count only when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "either_partner_infertility_due_to_natural_process": {
        "description": (
            "Whether the patient or partner has infertility due to a natural "
            "physiologic process, including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": (
            "Whether successful pregnancy can be attained through less costly "
            "treatment covered by this plan."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_sex": {
        "description": "Patient's sex for selecting the policy's eligibility-table row.",
        "type": "str",
        "allowed_values": ["female", "male", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Partner's sex, or no partner, for selecting the table row.",
        "type": "str",
        "allowed_values": ["female", "male", "other", "none"],
    },
    "partner_birth_date": {
        "description": "Required for a male patient with a female partner; otherwise unused.",
        "type": "str or None",
        "format": "YYYY_MM_DD or None",
    },
    "unprotected_timed_intercourse_months": {
        "description": (
            "Completed months trying to conceive through unprotected timed "
            "sexual intercourse involving egg and sperm contact."
        ),
        "type": "int",
        "allowed_values": "Nonnegative integer",
    },
    "self_paid_donor_insemination_cycles": {
        "description": (
            "Completed donor artificial insemination cycles trying to conceive "
            "that were self-paid and not paid for by the plan."
        ),
        "type": "int",
        "allowed_values": "Nonnegative integer",
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history, through the service date, of unmedicated day-3 "
            "FSH tests. Required for female patients; unused for male patients."
        ),
        "type": "list[dict]",
        "format": (
            "Each entry is {'date': 'YYYY_MM_DD', 'level_miu_ml': number}; "
            "level_miu_ml must be finite and nonnegative."
        ),
    },
}


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("Date must be a string")
    parsed = date.fromisoformat(value.replace("_", "-"))
    if value != (
        f"{parsed.year:04d}_{parsed.month:02d}_{parsed.day:02d}"
    ):
        raise ValueError("Date must have format YYYY_MM_DD")
    return parsed


def _birthday(birth, years):
    year = birth.year + years
    day = min(birth.day, calendar.monthrange(year, birth.month)[1])
    return date(year, birth.month, day)


def _months_before(day, months):
    month_index = day.year * 12 + day.month - 1 - months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    return date(
        year, month, min(day.day, calendar.monthrange(year, month)[1])
    )


def _nonnegative_integer(value):
    return type(value) is int and value >= 0


def covered_under_benefit(claim: dict) -> bool:
    """Missing or invalid required facts do not establish coverage."""
    if not isinstance(claim, dict):
        return False

    try:
        if claim["service"] not in {
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
        }:
            return False

        if claim["covered_role"] not in {
            "student",
            "student_legal_spouse",
            "student_civil_union_partner",
            "student_domestic_partner",
        }:
            return False

        required_true = (
            "provided_by_infertility_specialist",
            "patient_is_infertile",
            "infertility_causing_condition_demonstrated",
            "condition_recognized_and_documented",
        )
        required_false = (
            "either_partner_voluntarily_sterilized",
            "either_partner_infertility_due_to_natural_process",
            "pregnancy_attainable_through_less_costly_covered_treatment",
        )
        if any(claim[field] is not True for field in required_true):
            return False
        if any(claim[field] is not False for field in required_false):
            return False

        service_date = _parse_date(claim["service_date"])
        birth = _parse_date(claim["patient_birth_date"])
        if birth > service_date:
            return False

        sex = claim["patient_sex"]
        partner_sex = claim["partner_sex"]
        if partner_sex not in {"female", "male", "other", "none"}:
            return False

        if sex == "male":
            # The table supplies male eligibility only with a female partner.
            if partner_sex != "female":
                return False
            partner_birth = _parse_date(claim["partner_birth_date"])
            if partner_birth > service_date:
                return False
            required_months = (
                12 if service_date < _birthday(partner_birth, 35) else 6
            )
            months = claim["unprotected_timed_intercourse_months"]
            return (
                _nonnegative_integer(months)
                and months >= required_months
            )

        if sex != "female":
            return False

        under_35 = service_date < _birthday(birth, 35)
        required_attempts = 12 if under_35 else 6

        cycles = claim["self_paid_donor_insemination_cycles"]
        if not _nonnegative_integer(cycles):
            return False
        attempts_met = cycles >= required_attempts

        if partner_sex == "male":
            months = claim["unprotected_timed_intercourse_months"]
            if not _nonnegative_integer(months):
                return False
            attempts_met = attempts_met or months >= required_attempts

        # Without a male partner, only donor insemination satisfies the table.
        if not attempts_met:
            return False

        history = claim["unmedicated_day3_fsh_tests"]
        if not isinstance(history, list) or not history:
            return False

        tests = []
        for entry in history:
            if not isinstance(entry, dict):
                return False
            test_date = _parse_date(entry["date"])
            level = entry["level_miu_ml"]
            if (
                type(level) not in (int, float)
                or not math.isfinite(level)
                or level < 0
                or not birth <= test_date <= service_date
            ):
                return False
            tests.append((test_date, level))

        latest_date = max(test_date for test_date, _ in tests)
        if latest_date < _months_before(service_date, required_attempts):
            return False

        fortieth_birthday = _birthday(birth, 40)
        if service_date < fortieth_birthday:
            # Every result on the most recent test date must meet the threshold.
            return all(
                level < 19
                for test_date, level in tests
                if test_date == latest_date
            )

        # At age 40 or older, the stated threshold applies to all tests
        # performed at age 40 or older, rather than only the latest result.
        return all(
            level < 19
            for test_date, level in tests
            if test_date >= fortieth_birthday
        )

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
