from datetime import date
import calendar

SCHEMA = {
    "service_date": {
        "description": "Date of the claimed service; reference date for ages and test recency.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "service": {
        "description": "Infertility service being claimed.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provided_by_infertility_specialist": {
        "description": "Whether the charge is for services provided by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "coverage_role": {
        "description": "Patient's covered relationship to the student.",
        "type": "str",
        "allowed": [
            "student",
            "covered_legal_spouse",
            "covered_civil_union_partner",
            "covered_domestic_partner",
            "other_or_not_covered",
        ],
    },
    "patient_sex": {
        "description": "Patient's sex category for the policy's infertility criteria.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's reproductive partner, if any.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_age": {
        "description": "Partner's age in completed years on the service date.",
        "type": "int or None",
        "allowed": "Nonnegative integer; None when partner_sex is 'none'.",
    },
    "infertility_causing_condition_documented": {
        "description": (
            "A condition demonstrated to cause infertility has been recognized "
            "by a physician or infertility specialist and documented in the "
            "patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_voluntarily_sterilized": {
        "description": (
            "Either person has undergone voluntary sterilization, with or without "
            "reversal. Count tubal ligation, hysterectomy, or vasectomy only when "
            "obtained as voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": (
            "Either person's infertility is due to a natural physiologic process, "
            "such as age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_possible_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy can be attained through a less costly "
            "treatment covered by the plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "months_frequent_unprotected_heterosexual_intercourse": {
        "description": (
            "Completed months of unsuccessful attempts through frequent, "
            "unprotected heterosexual intercourse, for the glossary definition."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "months_unprotected_timed_intercourse": {
        "description": (
            "Completed months of unsuccessful attempts through unprotected "
            "timed intercourse, for the eligibility table."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "unsuccessful_donor_insemination_cycles": {
        "description": "Total completed unsuccessful donor insemination cycles.",
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "self_paid_unsuccessful_donor_insemination_cycles": {
        "description": (
            "Completed unsuccessful donor insemination cycles self-paid and "
            "not paid for by the plan."
        ),
        "type": "int",
        "allowed": (
            "Nonnegative integer no greater than "
            "unsuccessful_donor_insemination_cycles."
        ),
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of abnormal semen analyses obtained by the patient.",
        "type": "list[str]",
        "allowed": "List of YYYY_MM_DD dates on or before service_date.",
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": "Either person has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history of the patient's unmedicated day-3 FSH tests "
            "through the service date, including tests before age 40."
        ),
        "type": "list[dict]",
        "allowed": (
            "Each item has exactly 'date' (YYYY_MM_DD) and 'value_miu_ml' "
            "(nonnegative finite int or float)."
        ),
    },
}


def _date(value):
    if not isinstance(value, str):
        raise ValueError("Expected a date string.")
    parsed = date.fromisoformat(value.replace("_", "-"))
    if parsed.strftime("%Y_%m_%d") != value:
        raise ValueError("Expected YYYY_MM_DD.")
    return parsed


def _months_before(day, months):
    year, month_zero = divmod(day.year * 12 + day.month - 1 - months, 12)
    month = month_zero + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def _age_on(birth, day):
    return day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))


def covered_under_benefit(claim: dict) -> bool:
    """Evaluate this benefit only; missing or malformed required facts return False."""
    try:
        c = {field: claim[field] for field in SCHEMA}

        for field, specification in SCHEMA.items():
            if specification["type"] == "bool" and type(c[field]) is not bool:
                return False
            if isinstance(specification["allowed"], list):
                if c[field] not in specification["allowed"]:
                    return False

        service_date = _date(c["service_date"])
        birth_date = _date(c["patient_birth_date"])
        if birth_date > service_date:
            return False
        age = _age_on(birth_date, service_date)

        count_fields = (
            "months_frequent_unprotected_heterosexual_intercourse",
            "months_unprotected_timed_intercourse",
            "unsuccessful_donor_insemination_cycles",
            "self_paid_unsuccessful_donor_insemination_cycles",
        )
        if any(type(c[f]) is not int or c[f] < 0 for f in count_fields):
            return False
        donor_cycles = c["unsuccessful_donor_insemination_cycles"]
        self_paid_cycles = c["self_paid_unsuccessful_donor_insemination_cycles"]
        if self_paid_cycles > donor_cycles:
            return False

        partner_sex = c["partner_sex"]
        partner_age = c["partner_age"]
        if partner_sex == "none":
            if partner_age is not None:
                return False
        elif type(partner_age) is not int or partner_age < 0:
            return False

        if not isinstance(c["abnormal_semen_analysis_dates"], list):
            return False
        semen_dates = sorted(_date(d) for d in c["abnormal_semen_analysis_dates"])
        if any(d > service_date for d in semen_dates):
            return False

        import math

        if not isinstance(c["unmedicated_day3_fsh_tests"], list):
            return False
        fsh_tests = []
        for test in c["unmedicated_day3_fsh_tests"]:
            if not isinstance(test, dict) or set(test) != {"date", "value_miu_ml"}:
                return False
            test_date = _date(test["date"])
            value = test["value_miu_ml"]
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or value < 0
                or not birth_date <= test_date <= service_date
            ):
                return False
            fsh_tests.append((test_date, value))

        if c["service"] not in {
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
        }:
            return False
        if not c["provided_by_infertility_specialist"]:
            return False
        if c["coverage_role"] == "other_or_not_covered":
            return False
        if not c["infertility_causing_condition_documented"]:
            return False
        if c["patient_or_partner_voluntarily_sterilized"]:
            return False
        if c["infertility_due_to_natural_physiologic_process"]:
            return False
        if c["pregnancy_possible_with_less_costly_covered_treatment"]:
            return False

        female = c["patient_sex"] == "female"
        frequent_months = c["months_frequent_unprotected_heterosexual_intercourse"]
        timed_months = c["months_unprotected_timed_intercourse"]

        # Establish infertility separately from the table's eligibility tests.
        infertile = c["patient_or_partner_clinically_diagnosed_gender_dysphoria"]
        if female:
            threshold = 12 if age < 35 else 6
            if partner_sex == "male":
                infertile = infertile or frequent_months >= threshold
            else:
                infertile = infertile or donor_cycles >= threshold
        elif partner_sex == "female":
            # Failure to conceive with a female partner uses her age threshold.
            threshold = 12 if partner_age < 35 else 6
            infertile = infertile or frequent_months >= threshold
        else:
            infertile = infertile or (
                len(semen_dates) >= 2
                and (semen_dates[-1] - semen_dates[0]).days >= 14
            )
        if not infertile:
            return False

        # A gender-dysphoria diagnosis does not waive an applicable table row.
        if female:
            threshold = 12 if age < 35 else 6
            if partner_sex == "male":
                if timed_months < threshold and self_paid_cycles < threshold:
                    return False
            elif self_paid_cycles < threshold:
                return False

            recency_months = 12 if age < 35 else 6
            if not fsh_tests:
                return False
            latest_date = max(d for d, _ in fsh_tests)
            if latest_date < _months_before(service_date, recency_months):
                return False

            if age < 40:
                # All results on the latest date must satisfy the strict cutoff.
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
            if timed_months < threshold:
                return False

        # The table specifies no additional waiting-period or FSH criterion
        # for a male without a female partner; the glossary still applies.
        return True

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
