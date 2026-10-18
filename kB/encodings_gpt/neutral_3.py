"""
Encode comprehensive infertility-service coverage.

READING choices:
1. Only the two expressly listed services are covered by this rule.
2. Coverage must be as a student or a covered dependent in a listed relationship.
3. Either person's voluntary sterilization or physiologic infertility disqualifies.
4. Glossary infertility and the service-specific eligibility requirements both apply.
5. For a male with a female partner, use the female partner's glossary threshold.
6. A gender-dysphoria diagnosis satisfies the glossary, not the other requirements.
7. Table requirements apply to the categories actually described in the table;
   no additional table thresholds are invented for unlisted categories.
8. The table's donor cycles must be self-paid/not paid by the plan.
9. Frequent intercourse and timed intercourse are separately established facts.
10. FSH history means unmedicated day-3 tests; use calendar-month lookback windows.
11. At age 40 or older, every available result from age 40 onward must be below
    19, and a recent test is still required.
12. Charges must be made by an infertility specialist.

Precertification, network status, medical necessity, plan limits, and general
exclusions are deliberately outside this function. Unknown facts do not establish
eligibility, but an unknown fact is not required when another applicable route
already establishes the requirement.
"""

import calendar
import math
from datetime import date, datetime


# READING: Covered services — "the following infertility services" lists
# "Ovulation induction cycle(s) with menotropins" and "Intrauterine insemination".
# Treat that list as exhaustive for this rule.
#
# READING: Insured status — "covered under this plan as a student or as a covered
# dependent who is the student's legal spouse, civil union partner or domestic
# partner". The coverage_role field includes both coverage and relationship.
#
# READING: Either-person exclusions — "You or your partner has not had a voluntary
# sterilization" and "You or your partner does not have infertility that is due to
# a natural physiologic process". Read these as excluding a claim if either
# person has the specified disqualifying history or cause, not as permitting
# coverage merely because the other person does not.
#
# READING: Cumulative tests — "You are eligible ... if" and the glossary's
# "A disease defined by the failure to become pregnant" both apply. The table's
# donor-cycle alternative does not itself replace the glossary's intercourse
# criterion for a female with a male partner.
#
# READING: Male with female partner — the glossary describes "a female with a
# male partner", while the table expressly includes "A male of any age with a
# female partner". Apply that female partner's age-dependent glossary
# intercourse threshold to their shared failure to achieve pregnancy.
#
# READING: Gender dysphoria — "For an individual or their partner who has been
# clinically diagnosed with gender dysphoria" independently satisfies the
# glossary definition; it does not waive "every" service eligibility condition.
#
# READING: Unlisted table categories — "Your unmedicated day 3 ... level meets
# the following criteria" is followed by category-specific rows, including
# "Does not apply" for males with female partners. Apply thresholds only where
# the table supplies a row. For a male without a female partner, use the
# glossary's semen-analysis route without inventing months or FSH requirements.
# An otherwise unlisted category can satisfy the glossary through dysphoria,
# but receives no invented table thresholds.
#
# READING: Donor payment — the donor column says "Self paid/not paid for by
# plan". Count only such cycles toward the table threshold. Those cycles also
# count toward the glossary's donor-cycle requirement.
#
# READING: Intercourse measures — the glossary says "frequent, unprotected"
# intercourse, while the table says "unprotected timed sexual intercourse".
# Record these separately rather than assuming that either implies the other.
#
# READING: FSH timing and history — "unmedicated day 3", "within the past"
# 12 or 6 months, and "most recent lab test" refer to the history of qualifying
# unmedicated day-3 tests through the service date. Use inclusive calendar-month
# windows, with month-end clamping.
#
# READING: FSH age 40 — "age 40 and older" and "all prior tests performed after
# age 40" mean all qualifying tests on or after the 40th birthday, including
# the latest test. A recent test remains necessary. No extra result threshold
# is imposed on a test performed before the 40th birthday.
#
# READING: Specialist — "cover charges made by an infertility specialist"
# requires specialist billing; this is distinct from provider-network status.


SCHEMA = {
    "service": {
        "description": "Service for which coverage is being decided.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "charged_by_infertility_specialist": {
        "description": "Whether the charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "coverage_role": {
        "description": "Patient's actual covered status under this plan.",
        "type": "str",
        "allowed": [
            "covered_student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
            "other",
        ],
    },
    "service_date": {
        "description": "Date of the claimed service; other facts are assessed as of this date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_category": {
        "description": (
            "Female/male category used in the policy's reproductive criteria; "
            "'other' means neither table category, not an unknown category."
        ),
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_category": {
        "description": (
            "Partner category for the policy's reproductive criteria. "
            "'none_or_other' means no male or female partner, not unknown."
        ),
        "type": "str",
        "allowed": ["female", "male", "none_or_other"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date, needed for female age and FSH criteria.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "female_partner_age_years": {
        "description": "Female partner's completed age in years on the service date.",
        "type": "int",
        "allowed": "Nonnegative integer; needed for a male with a female partner.",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "An existing condition is demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": (
            "That condition was recognized by the patient's physician or infertility "
            "specialist and documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_voluntarily_sterilized": {
        "description": (
            "Either person has had voluntary sterilization, regardless of reversal "
            "or its results. Tubal ligation, hysterectomy, or vasectomy counts here "
            "only when obtained as voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_infertility_due_to_natural_process": {
        "description": (
            "Either person's infertility is due to a natural physiologic process, "
            "such as age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy can be attained through a less costly treatment "
            "for which this plan provides coverage."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": "Either person has a clinical diagnosis of gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "failure_to_become_pregnant": {
        "description": (
            "Failure to become pregnant despite the reported qualifying attempts. "
            "Not independently required for the glossary's dysphoria route."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "frequent_unprotected_intercourse_months": {
        "description": (
            "Completed months of frequent, unprotected heterosexual intercourse "
            "without achieving pregnancy, through the service date."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "timed_unprotected_intercourse_months": {
        "description": (
            "Completed months trying to conceive through unprotected timed sexual "
            "intercourse, through the service date."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "self_paid_donor_insemination_cycles": {
        "description": (
            "Completed donor artificial-insemination cycles while trying to conceive, "
            "self-paid/not paid by the plan, through the service date."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "abnormal_semen_analysis_dates": {
        "description": (
            "Dates of analyses with abnormal semen results, obtained no later than "
            "the service date. Two distinct dates at least 14 days apart suffice."
        ),
        "type": "list[str]",
        "format": 'Each element is "YYYY_MM_DD".',
    },
    "fsh_tests": {
        "description": (
            "Complete history, through the service date, of the patient's unmedicated "
            "day-3 FSH tests. Supply only such tests. A missing field means the "
            "history is unknown; [] means no such tests exist."
        ),
        "type": "list[dict]",
        "format": (
            'Each item has {"date": "YYYY_MM_DD", "value_miu_ml": number}; '
            "values must be finite and nonnegative. Multiple tests on one date "
            "are permitted."
        ),
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """Return whether the supplied facts establish coverage under this benefit."""
    if not isinstance(claim, dict):
        return False

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            result = datetime.strptime(value, "%Y_%m_%d").date()
            return result if result.strftime("%Y_%m_%d") == value else None
        except ValueError:
            return None

    def nonnegative_int(value):
        return type(value) is int and value >= 0

    def count_at_least(field, threshold):
        value = claim.get(field)
        return nonnegative_int(value) and value >= threshold

    def anniversary(birth, year):
        day = min(birth.day, calendar.monthrange(year, birth.month)[1])
        return date(year, birth.month, day)

    def completed_age(birth, when):
        return when.year - birth.year - (
            when < anniversary(birth, when.year)
        )

    def subtract_months(when, months):
        absolute_month = when.year * 12 + when.month - 1 - months
        year, month_zero = divmod(absolute_month, 12)
        if year < 1:
            return date.min
        month = month_zero + 1
        return date(
            year, month,
            min(when.day, calendar.monthrange(year, month)[1]),
        )

    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False

    if claim.get("charged_by_infertility_specialist") is not True:
        return False

    if claim.get("coverage_role") not in (
        "covered_student",
        "covered_dependent_legal_spouse",
        "covered_dependent_civil_union_partner",
        "covered_dependent_domestic_partner",
    ):
        return False

    for field in (
        "condition_demonstrated_to_cause_infertility",
        "condition_recognized_and_documented",
    ):
        if claim.get(field) is not True:
            return False

    for field in (
        "patient_or_partner_voluntarily_sterilized",
        "patient_or_partner_infertility_due_to_natural_process",
        "pregnancy_attainable_with_less_costly_covered_treatment",
    ):
        if claim.get(field) is not False:
            return False

    service_date = parse_date(claim.get("service_date"))
    category = claim.get("patient_category")
    partner = claim.get("partner_category")
    if (
        service_date is None
        or category not in ("female", "male", "other")
        or partner not in ("female", "male", "none_or_other")
    ):
        return False

    birth = None
    age = None
    threshold = None

    if category == "female":
        birth = parse_date(claim.get("patient_birth_date"))
        if birth is None or birth > service_date:
            return False
        age = completed_age(birth, service_date)
        threshold = 12 if age < 35 else 6
    elif category == "male" and partner == "female":
        partner_age = claim.get("female_partner_age_years")
        if not nonnegative_int(partner_age):
            return False
        threshold = 12 if partner_age < 35 else 6

    # Establish glossary infertility, independently of the table.
    glossary_met = (
        claim.get("patient_or_partner_clinically_diagnosed_gender_dysphoria")
        is True
    )

    if not glossary_met and claim.get("failure_to_become_pregnant") is True:
        if category == "female":
            if partner == "male":
                glossary_met = count_at_least(
                    "frequent_unprotected_intercourse_months", threshold
                )
            else:
                # The table requires these same self-paid cycles, so no separate
                # total-donor-cycle field is necessary to decide this benefit.
                glossary_met = count_at_least(
                    "self_paid_donor_insemination_cycles", threshold
                )
        elif category == "male" and partner == "female":
            glossary_met = count_at_least(
                "frequent_unprotected_intercourse_months", threshold
            )
        elif category == "male":
            raw_dates = claim.get("abnormal_semen_analysis_dates")
            if isinstance(raw_dates, list):
                dates = [parse_date(value) for value in raw_dates]
                if (
                    len(dates) >= 2
                    and all(d is not None and d <= service_date for d in dates)
                ):
                    glossary_met = (max(dates) - min(dates)).days >= 14

    if not glossary_met:
        return False

    # Apply the table's egg/sperm-contact thresholds to its listed categories.
    if category == "female":
        donor_met = count_at_least(
            "self_paid_donor_insemination_cycles", threshold
        )
        if partner == "male":
            timed_met = count_at_least(
                "timed_unprotected_intercourse_months", threshold
            )
            if not (timed_met or donor_met):
                return False
        elif not donor_met:
            return False
    elif category == "male" and partner == "female":
        if not count_at_least("timed_unprotected_intercourse_months", threshold):
            return False

    # Only the female rows impose FSH requirements.
    if category != "female":
        return True

    raw_tests = claim.get("fsh_tests")
    if not isinstance(raw_tests, list) or not raw_tests:
        return False

    tests = []
    for item in raw_tests:
        if not isinstance(item, dict):
            return False
        test_date = parse_date(item.get("date"))
        value = item.get("value_miu_ml")
        if (
            test_date is None
            or test_date < birth
            or test_date > service_date
            or type(value) not in (int, float)
        ):
            return False
        try:
            if not math.isfinite(value) or value < 0:
                return False
        except (OverflowError, TypeError, ValueError):
            return False
        tests.append((test_date, value))

    latest_date = max(test_date for test_date, _ in tests)
    lookback_months = 12 if age < 35 else 6
    if latest_date < subtract_months(service_date, lookback_months):
        return False

    if age < 40:
        # If several qualifying tests share the latest date, all must pass;
        # the facts do not identify which same-day result was most recent.
        return all(value < 19 for d, value in tests if d == latest_date)

    fortieth_birthday = anniversary(birth, birth.year + 40)
    return all(
        value < 19
        for test_date, value in tests
        if test_date >= fortieth_birthday
    )
