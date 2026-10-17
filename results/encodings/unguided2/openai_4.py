from calendar import monthrange
from datetime import date, timedelta
import math


SCHEMA = {
    "service_date": {
        "description": "Date of the claimed service.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "service": {
        "description": "Service for which coverage is requested.",
        "type": "str",
        "allowed_values": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provided_by_infertility_specialist": {
        "description": "Whether the charges are for services by an infertility specialist.",
        "type": "bool",
        "allowed_values": [True, False],
    },
    "coverage_relationship": {
        "description": "The patient's relationship to the covered student.",
        "type": "str",
        "allowed_values": [
            "covered_student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
            "other",
        ],
    },
    "patient_sex": {
        "description": "Female/male classification used by the policy's eligibility table.",
        "type": "str",
        "allowed_values": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date, used to determine age at service and testing.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Partner's female/male classification, or no partner.",
        "type": "str",
        "allowed_values": ["female", "male", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's birth date; required for a male patient with a female partner.",
        "type": "str | None",
        "format": "YYYY_MM_DD or None",
    },
    "infertility_causing_condition_recognized_and_documented": {
        "description": (
            "A condition demonstrated to cause infertility has been recognized by "
            "a physician or infertility specialist and documented in the patient's "
            "or partner's medical records."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_or_partner_voluntarily_sterilized": {
        "description": (
            "Either person has had voluntary sterilization, even if reversed. "
            "Tubal ligation, hysterectomy, and vasectomy count only when performed "
            "for voluntary sterilization."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "patient_or_partner_infertility_due_to_natural_physiologic_process": {
        "description": (
            "Either person's infertility is due to a natural physiologic process, "
            "including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "successful_pregnancy_possible_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy can be attained through less costly treatment "
            "covered by this plan."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "unsuccessful_intercourse_months": {
        "description": (
            "Completed months of unsuccessful attempts to conceive through frequent, "
            "unprotected, timed heterosexual intercourse for this patient/couple."
        ),
        "type": "int",
        "allowed_values": "Nonnegative integer",
    },
    "unsuccessful_donor_insemination_cycles": {
        "description": "Total completed unsuccessful donor insemination cycles.",
        "type": "int",
        "allowed_values": "Nonnegative integer",
    },
    "self_paid_unsuccessful_donor_insemination_cycles": {
        "description": (
            "Completed unsuccessful donor insemination cycles self-paid and not "
            "paid for by this plan; a subset of the total donor cycles."
        ),
        "type": "int",
        "allowed_values": "Nonnegative integer, no greater than total donor cycles",
    },
    "abnormal_semen_analysis_dates": {
        "description": (
            "Dates of abnormal semen analyses, for the male-without-female-partner "
            "glossary definition."
        ),
        "type": "list[str]",
        "format": "Each entry YYYY_MM_DD, on or before service_date",
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": (
            "The patient or their partner has been clinically diagnosed with "
            "gender dysphoria, satisfying that branch of the infertility definition."
        ),
        "type": "bool",
        "allowed_values": [True, False],
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history of the patient's unmedicated day-3 FSH tests through "
            "service_date. Required for female patients; may be empty for males."
        ),
        "type": "list[dict]",
        "format": (
            'Each entry {"date": "YYYY_MM_DD", "value_miu_ml": number}; '
            "values must be finite and nonnegative"
        ),
    },
}


def _parse_date(value):
    if (
        not isinstance(value, str)
        or len(value) != 10
        or value[4] != "_"
        or value[7] != "_"
        or not (value[:4] + value[5:7] + value[8:]).isdigit()
    ):
        raise ValueError("Invalid date format")
    return date(int(value[:4]), int(value[5:7]), int(value[8:]))


def _age_on(birth_date, on_date):
    return on_date.year - birth_date.year - (
        (on_date.month, on_date.day) < (birth_date.month, birth_date.day)
    )


def _months_before(on_date, months):
    month_index = on_date.year * 12 + on_date.month - 1 - months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    day = min(on_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def covered_under_benefit(claim: dict) -> bool:
    """Apply only the specified infertility benefit and eligibility rules."""
    if not isinstance(claim, dict):
        return False

    try:
        # Only fields declared in SCHEMA are read.
        c = {name: claim[name] for name in SCHEMA}

        for name, specification in SCHEMA.items():
            if specification["type"] == "bool" and type(c[name]) is not bool:
                return False

        for name in (
            "unsuccessful_intercourse_months",
            "unsuccessful_donor_insemination_cycles",
            "self_paid_unsuccessful_donor_insemination_cycles",
        ):
            if type(c[name]) is not int or c[name] < 0:
                return False

        total_donor = c["unsuccessful_donor_insemination_cycles"]
        self_paid_donor = c["self_paid_unsuccessful_donor_insemination_cycles"]
        intercourse_months = c["unsuccessful_intercourse_months"]
        if self_paid_donor > total_donor:
            return False

        if c["service"] not in (
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
        ):
            return False
        if not c["provided_by_infertility_specialist"]:
            return False
        if c["coverage_relationship"] not in (
            "covered_student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
        ):
            return False

        if not c["infertility_causing_condition_recognized_and_documented"]:
            return False
        if c["patient_or_partner_voluntarily_sterilized"]:
            return False
        if c["patient_or_partner_infertility_due_to_natural_physiologic_process"]:
            return False
        if c["successful_pregnancy_possible_with_less_costly_covered_treatment"]:
            return False

        sex = c["patient_sex"]
        partner_sex = c["partner_sex"]
        if sex not in ("female", "male"):
            return False
        if partner_sex not in ("female", "male", "none"):
            return False

        service_date = _parse_date(c["service_date"])
        birth_date = _parse_date(c["patient_birth_date"])
        if birth_date > service_date:
            return False
        age = _age_on(birth_date, service_date)

        partner_age = None
        if c["partner_birth_date"] is not None:
            partner_birth_date = _parse_date(c["partner_birth_date"])
            if partner_birth_date > service_date or partner_sex == "none":
                return False
            partner_age = _age_on(partner_birth_date, service_date)
        if sex == "male" and partner_sex == "female" and partner_age is None:
            return False

        semen_values = c["abnormal_semen_analysis_dates"]
        if not isinstance(semen_values, list):
            return False
        semen_dates = [_parse_date(value) for value in semen_values]
        if any(d > service_date or d < birth_date for d in semen_dates):
            return False

        fsh_values = c["unmedicated_day3_fsh_tests"]
        if not isinstance(fsh_values, list):
            return False
        fsh_tests = []
        for test in fsh_values:
            if not isinstance(test, dict):
                return False
            test_date = _parse_date(test["date"])
            value = test["value_miu_ml"]
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or value < 0
                or test_date > service_date
                or test_date < birth_date
            ):
                return False
            fsh_tests.append((test_date, value))

        # Establish infertility under the separate glossary definition.
        infertile = c[
            "patient_or_partner_clinically_diagnosed_gender_dysphoria"
        ]
        if sex == "female":
            threshold = 12 if age < 35 else 6
            if partner_sex == "male":
                infertile = infertile or intercourse_months >= threshold
            else:
                infertile = infertile or total_donor >= threshold
        elif partner_sex == "female":
            # The female partner's failure to conceive establishes couple infertility.
            threshold = 12 if partner_age < 35 else 6
            infertile = infertile or intercourse_months >= threshold
        else:
            sufficiently_separated_analyses = (
                len(semen_dates) >= 2
                and max(semen_dates) - min(semen_dates) >= timedelta(days=14)
            )
            infertile = infertile or sufficiently_separated_analyses

        if not infertile:
            return False

        # Apply the table independently: a glossary alternative does not waive it.
        if sex == "female":
            threshold = 12 if age < 35 else 6
            if partner_sex == "male":
                if (
                    intercourse_months < threshold
                    and self_paid_donor < threshold
                ):
                    return False
            elif self_paid_donor < threshold:
                return False

            if not fsh_tests:
                return False

            latest_date = max(d for d, _ in fsh_tests)
            if latest_date < _months_before(service_date, threshold):
                return False

            if age < 40:
                # If multiple results share the latest date, all must qualify.
                if any(v >= 19 for d, v in fsh_tests if d == latest_date):
                    return False
            else:
                if any(
                    v >= 19
                    for d, v in fsh_tests
                    if _age_on(birth_date, d) >= 40
                ):
                    return False

        elif partner_sex == "female":
            threshold = 12 if partner_age < 35 else 6
            if intercourse_months < threshold:
                return False

        # The table supplies no waiting-period or FSH requirement for males
        # without female partners; their glossary criterion is applied above.
        # No precertification, network, medical-necessity, plan-limit, or
        # general-exclusion checks are performed here.
        return True

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
