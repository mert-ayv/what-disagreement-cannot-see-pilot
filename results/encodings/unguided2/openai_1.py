import calendar
import math
from datetime import date, datetime


SCHEMA = {
    "service": {
        "description": "Service for which coverage is requested.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "service_date": {
        "description": "Date on which eligibility is evaluated.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "covered_role": {
        "description": "Patient's enrollment status under this plan.",
        "type": "str",
        "allowed": [
            "student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
            "other",
        ],
    },
    "patient_sex": {
        "description": "Patient's female/male category for the policy's criteria.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Partner's category; null means no partner.",
        "type": "str or None",
        "allowed": ["female", "male", None],
    },
    "partner_birth_date": {
        "description": "Required for a male patient with a female partner; otherwise may be null.",
        "type": "str or None",
        "format": "YYYY_MM_DD or null",
    },
    "infertility_causing_condition_demonstrated": {
        "description": "A condition has been demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": (
            "A physician or infertility specialist recognized that condition "
            "and documented it in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_voluntarily_sterilized": {
        "description": (
            "Either person underwent voluntary sterilization, regardless of "
            "reversal or its outcome. Tubal ligation, hysterectomy and vasectomy "
            "count only when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_infertility_due_to_natural_process": {
        "description": (
            "Either person's infertility is due to a natural physiologic process, "
            "including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy can be attained through a less costly "
            "treatment covered by this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "frequent_unprotected_intercourse_months": {
        "description": (
            "Completed months of unsuccessful frequent, unprotected heterosexual "
            "intercourse, for the glossary definition."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number",
    },
    "timed_unprotected_intercourse_months": {
        "description": (
            "Completed months of unsuccessful unprotected timed intercourse, "
            "for the eligibility table."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number",
    },
    "donor_insemination_cycles": {
        "description": "Completed unsuccessful donor insemination cycles, regardless of payer.",
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "self_paid_donor_insemination_cycles": {
        "description": (
            "Completed unsuccessful donor insemination cycles self-paid and "
            "not paid for by the plan; a subset of donor_insemination_cycles."
        ),
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "abnormal_semen_analysis_dates": {
        "description": (
            "Dates of abnormal semen analyses; used for a male without a female partner."
        ),
        "type": "list[str]",
        "format": 'List of "YYYY_MM_DD" dates on or before service_date',
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": "The patient or partner has a clinical diagnosis of gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history of the patient's unmedicated day-3 FSH tests, "
            "including all such tests after age 40. Use [] when not applicable."
        ),
        "type": "list[dict]",
        "format": (
            '[{"date": "YYYY_MM_DD", "value_miu_ml": finite nonnegative number}, ...]; '
            "dates must be distinct and on or before service_date"
        ),
    },
}


def _parse_date(value):
    if not isinstance(value, str):
        raise ValueError("Expected a date string")
    result = datetime.strptime(value, "%Y_%m_%d").date()
    if result.strftime("%Y_%m_%d") != value:
        raise ValueError("Expected YYYY_MM_DD")
    return result


def _age(birth_date, on_date):
    if birth_date > on_date:
        raise ValueError("Birth date is in the future")
    return (
        on_date.year
        - birth_date.year
        - ((on_date.month, on_date.day) < (birth_date.month, birth_date.day))
    )


def _months_before(on_date, months):
    month_index = on_date.year * 12 + on_date.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    return date(
        year,
        month,
        min(on_date.day, calendar.monthrange(year, month)[1]),
    )


def _nonnegative_number(value):
    return (
        type(value) in (int, float)
        and math.isfinite(value)
        and value >= 0
    )


def covered_under_benefit(claim: dict) -> bool:
    """Apply only the quoted benefit, infertility definition and eligibility rules."""
    try:
        if any(field not in claim for field in SCHEMA):
            return False

        boolean_fields = (
            "infertility_causing_condition_demonstrated",
            "condition_recognized_and_documented",
            "patient_or_partner_voluntarily_sterilized",
            "patient_or_partner_infertility_due_to_natural_process",
            "pregnancy_attainable_through_less_costly_covered_treatment",
            "patient_or_partner_clinically_diagnosed_gender_dysphoria",
        )
        if any(type(claim[field]) is not bool for field in boolean_fields):
            return False

        if claim["service"] not in (
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
        ):
            return False
        if claim["covered_role"] not in (
            "student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
        ):
            return False
        if not (
            claim["infertility_causing_condition_demonstrated"]
            and claim["condition_recognized_and_documented"]
        ):
            return False
        if (
            claim["patient_or_partner_voluntarily_sterilized"]
            or claim["patient_or_partner_infertility_due_to_natural_process"]
            or claim["pregnancy_attainable_through_less_costly_covered_treatment"]
        ):
            return False

        today = _parse_date(claim["service_date"])
        birth = _parse_date(claim["patient_birth_date"])
        age = _age(birth, today)
        sex = claim["patient_sex"]
        partner_sex = claim["partner_sex"]
        if sex not in ("female", "male"):
            return False
        if partner_sex not in ("female", "male", None):
            return False

        partner_age = None
        if claim["partner_birth_date"] is not None:
            partner_age = _age(_parse_date(claim["partner_birth_date"]), today)
        if sex == "male" and partner_sex == "female" and partner_age is None:
            return False

        frequent = claim["frequent_unprotected_intercourse_months"]
        timed = claim["timed_unprotected_intercourse_months"]
        if not _nonnegative_number(frequent) or not _nonnegative_number(timed):
            return False

        donor = claim["donor_insemination_cycles"]
        self_paid = claim["self_paid_donor_insemination_cycles"]
        if (
            type(donor) is not int
            or type(self_paid) is not int
            or not 0 <= self_paid <= donor
        ):
            return False

        semen_input = claim["abnormal_semen_analysis_dates"]
        if not isinstance(semen_input, list):
            return False
        semen_dates = sorted(_parse_date(d) for d in semen_input)
        if any(d > today for d in semen_dates):
            return False
        qualifying_semen_analyses = (
            len(semen_dates) >= 2
            and (semen_dates[-1] - semen_dates[0]).days >= 14
        )

        tests_input = claim["unmedicated_day3_fsh_tests"]
        if not isinstance(tests_input, list):
            return False
        fsh_tests = []
        for test in tests_input:
            test_date = _parse_date(test["date"])
            value = test["value_miu_ml"]
            if (
                not birth <= test_date <= today
                or not _nonnegative_number(value)
            ):
                return False
            fsh_tests.append((test_date, value))
        fsh_tests.sort()
        if len({d for d, _ in fsh_tests}) != len(fsh_tests):
            return False

        # The glossary and the eligibility table are separate requirements.
        # In particular, donor cycles alone do not satisfy the glossary's
        # female-with-male-partner intercourse definition.
        infertile = claim[
            "patient_or_partner_clinically_diagnosed_gender_dysphoria"
        ]
        if sex == "female":
            required = 12 if age < 35 else 6
            if partner_sex == "male":
                infertile = infertile or frequent >= required
            else:
                infertile = infertile or donor >= required
        elif partner_sex == "female":
            # Apply the female partner's age-based failure-to-conceive period.
            required = 12 if partner_age < 35 else 6
            infertile = infertile or frequent >= required
        else:
            infertile = infertile or qualifying_semen_analyses

        if not infertile:
            return False

        if sex == "female":
            required = 12 if age < 35 else 6
            contact_requirement_met = self_paid >= required
            if partner_sex == "male":
                contact_requirement_met = (
                    contact_requirement_met or timed >= required
                )
            if not contact_requirement_met or not fsh_tests:
                return False

            latest_date, latest_value = fsh_tests[-1]
            if latest_date < _months_before(today, required):
                return False

            if age < 40:
                if latest_value >= 19:
                    return False
            else:
                # The age-40 rule covers every test performed at age 40+,
                # not merely the most recent test.
                if any(
                    value >= 19
                    for test_date, value in fsh_tests
                    if _age(birth, test_date) >= 40
                ):
                    return False

        elif partner_sex == "female":
            required = 12 if partner_age < 35 else 6
            if timed < required:
                return False

        # No table row supplies an intercourse, donor-cycle or FSH requirement
        # for a male without a female partner. The glossary's semen-analysis
        # or gender-dysphoria criterion applies without inventing a table row.
        return True

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
