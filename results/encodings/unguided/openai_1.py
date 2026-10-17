from calendar import monthrange
from datetime import datetime, date
from math import isfinite

SCHEMA = {
    "service": {
        "description": "The service for which coverage is requested.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the service is furnished by an infertility specialist.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "coverage_relationship": {
        "description": "The patient's status under this plan.",
        "type": "str",
        "allowed_values": [
            "covered_student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
            "other",
        ],
    },
    "service_date": {
        "description": "Date of the claimed service and eligibility assessment.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Patient's category for application of the eligibility table.",
        "type": "str",
        "allowed_values": ["female", "male", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Partner's category; null if the patient has no partner.",
        "type": "str | None",
        "allowed_values": ["female", "male", "other", None],
    },
    "partner_birth_date": {
        "description": (
            "Partner's birth date; required for a male patient with a female "
            "partner. Otherwise may be null."
        ),
        "type": "str | None",
        "format": "YYYY_MM_DD or null",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "Whether a condition is demonstrated to cause infertility.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "condition_recognized_by_physician_or_infertility_specialist": {
        "description": (
            "Whether that condition has been recognized by the patient's "
            "physician or infertility specialist."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "condition_documented_in_patient_or_partner_records": {
        "description": (
            "Whether that same condition is documented in the patient's "
            "or partner's medical records."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_or_partner_had_voluntary_sterilization": {
        "description": (
            "Whether either has undergone voluntary sterilization, regardless "
            "of reversal or its results. Count tubal ligation, hysterectomy, "
            "or vasectomy here only when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_or_partner_infertility_due_to_natural_physiologic_process": {
        "description": (
            "Whether either has infertility due to a natural physiologic "
            "process, including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "successful_pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": (
            "Whether successful pregnancy can be attained through less costly "
            "treatment covered under this plan."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "completed_months_unprotected_timed_intercourse": {
        "description": (
            "Completed months trying to conceive through unprotected timed "
            "sexual intercourse involving egg and sperm contact."
        ),
        "type": "int",
        "allowed_values": "Nonnegative integer",
    },
    "self_paid_donor_insemination_cycles": {
        "description": (
            "Completed donor artificial insemination cycles used to try to "
            "conceive, self-paid and not paid for by the plan."
        ),
        "type": "int",
        "allowed_values": "Nonnegative integer",
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history of the patient's unmedicated day-3 FSH tests "
            "through the service date, including all such tests after age 40. "
            "May be empty for male patients, for whom FSH testing does not apply."
        ),
        "type": "list[dict]",
        "format": (
            "Each record is {'test_date': 'YYYY_MM_DD', "
            "'fsh_miu_ml': nonnegative finite number}."
        ),
    },
}


def _date(value):
    if not isinstance(value, str):
        raise ValueError("Date must be a string")
    result = datetime.strptime(value, "%Y_%m_%d").date()
    if result.strftime("%Y_%m_%d") != value:
        raise ValueError("Date must use YYYY_MM_DD")
    return result


def _age(birth_date, on_date):
    return (
        on_date.year
        - birth_date.year
        - ((on_date.month, on_date.day) < (birth_date.month, birth_date.day))
    )


def _months_before(on_date, months):
    absolute_month = on_date.year * 12 + on_date.month - 1 - months
    year, month_index = divmod(absolute_month, 12)
    month = month_index + 1
    return date(year, month, min(on_date.day, monthrange(year, month)[1]))


def covered_under_benefit(claim: dict) -> bool:
    """Evaluate this benefit only; other plan-wide checks are not encoded."""
    try:
        if claim["service"] not in {
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
        }:
            return False

        if claim["coverage_relationship"] not in {
            "covered_student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
        }:
            return False

        required_true = (
            "provider_is_infertility_specialist",
            "condition_demonstrated_to_cause_infertility",
            "condition_recognized_by_physician_or_infertility_specialist",
            "condition_documented_in_patient_or_partner_records",
        )
        required_false = (
            "patient_or_partner_had_voluntary_sterilization",
            "patient_or_partner_infertility_due_to_natural_physiologic_process",
            "successful_pregnancy_attainable_with_less_costly_covered_treatment",
        )
        if any(claim[field] is not True for field in required_true):
            return False
        if any(claim[field] is not False for field in required_false):
            return False

        service_date = _date(claim["service_date"])
        birth_date = _date(claim["patient_birth_date"])
        if birth_date > service_date:
            return False

        patient_sex = claim["patient_sex"]
        partner_sex = claim["partner_sex"]
        if partner_sex not in {"male", "female", "other", None}:
            return False

        intercourse_months = claim["completed_months_unprotected_timed_intercourse"]
        donor_cycles = claim["self_paid_donor_insemination_cycles"]
        if any(
            type(value) is not int or value < 0
            for value in (intercourse_months, donor_cycles)
        ):
            return False

        if patient_sex == "male":
            if partner_sex != "female":
                return False
            partner_birth_date = _date(claim["partner_birth_date"])
            if partner_birth_date > service_date:
                return False
            required_months = (
                12 if _age(partner_birth_date, service_date) < 35 else 6
            )
            # The male rows allow intercourse only; donor cycles and FSH
            # requirements do not apply.
            return intercourse_months >= required_months

        if patient_sex != "female":
            return False

        patient_age = _age(birth_date, service_date)
        required_duration = 12 if patient_age < 35 else 6

        if partner_sex == "male":
            if (
                intercourse_months < required_duration
                and donor_cycles < required_duration
            ):
                return False
        elif donor_cycles < required_duration:
            return False

        records = claim["unmedicated_day3_fsh_tests"]
        if not isinstance(records, list) or not records:
            return False

        tests = []
        for record in records:
            test_date = _date(record["test_date"])
            value = record["fsh_miu_ml"]
            if (
                type(value) not in (int, float)
                or not isfinite(value)
                or value < 0
                or not birth_date <= test_date <= service_date
            ):
                return False
            tests.append((test_date, value))

        latest_date = max(test_date for test_date, _ in tests)
        if latest_date < _months_before(service_date, required_duration):
            return False

        if patient_age < 40:
            return all(
                value < 19
                for test_date, value in tests
                if test_date == latest_date
            )

        # At age 40 or older, every test performed at age 40 or older
        # must satisfy the strict threshold, not merely the latest test.
        return all(
            value < 19
            for test_date, value in tests
            if _age(birth_date, test_date) >= 40
        )

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
