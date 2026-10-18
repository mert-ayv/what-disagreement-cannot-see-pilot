"""
Comprehensive infertility services coverage rule.

READING choices:
- Disjunctive exclusions: either member of a couple may satisfy each negative
  eligibility statement.
- Glossary and table are cumulative; donor cycles do not by themselves replace
  the glossary's intercourse requirement for a female with a male partner.
- A male with a female partner may establish infertility through the couple's
  unsuccessful attempts, using the female partner's age.
- A clinical gender-dysphoria diagnosis is an independent glossary pathway, not
  a waiver of otherwise applicable eligibility requirements.
- Table requirements apply only to the categories the table actually describes.
- Only donor cycles not paid for by the plan count toward the table thresholds.
- FSH testing windows use inclusive calendar-month boundaries.
- At age 40 or older, the FSH threshold applies to tests performed at age 40
  or older, rather than imposing a lifetime threshold.
- No numerical cycle limit or requirement to finish a treatment cycle is added.

Unknown facts do not establish a requirement, but need not defeat coverage when
another expressly permitted alternative establishes it. Input facts are assumed
truthful. Historical lists described as complete must be supplied as complete
lists, not merely selected favorable results.
"""

from calendar import monthrange
from datetime import datetime
import math


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
    "charged_by_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_capacity": {
        "description": "The patient's capacity as a person currently covered under this plan.",
        "type": "str",
        "allowed": [
            "student",
            "students_legal_spouse",
            "students_civil_union_partner",
            "students_domestic_partner",
            "other_or_not_covered",
        ],
    },
    "patient_sex": {
        "description": "Patient's applicable female/male classification for the policy's categories.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_sex": {
        "description": "Partner's applicable classification; 'none' means no partner.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "service_date": {
        "description": "Date on which coverage and age-dependent requirements are evaluated.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_birth_date": {
        "description": "Patient's date of birth; needed for female table rows.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_birth_date": {
        "description": "Partner's date of birth; needed for a male with a female partner.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "documented_infertility_causing_condition": {
        "description": (
            "A condition demonstrated to cause infertility has been recognized "
            "by the patient's physician or infertility specialist and documented "
            "in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": (
            "Patient has undergone voluntary sterilization, regardless of reversal "
            "or its results. Tubal ligation, hysterectomy and vasectomy count only "
            "when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Same sterilization fact for the partner, if there is one.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_natural_process_infertility": {
        "description": (
            "Patient has infertility due to a natural physiologic process, "
            "such as age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_natural_process_infertility": {
        "description": "Same natural-process infertility fact for the partner.",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy can be attained through a less costly "
            "treatment covered under this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "unsuccessful_frequent_intercourse_months": {
        "description": (
            "Months of frequent, unprotected heterosexual intercourse without "
            "achieving pregnancy, for the patient and applicable partner."
        ),
        "type": "int or float",
        "allowed": "Finite number >= 0",
    },
    "unsuccessful_timed_intercourse_months": {
        "description": (
            "Months trying to conceive through unprotected timed sexual "
            "intercourse involving egg and sperm contact, without success."
        ),
        "type": "int or float",
        "allowed": "Finite number >= 0",
    },
    "unsuccessful_donor_insemination_cycles": {
        "description": (
            "Total completed donor insemination cycles without achieving "
            "pregnancy, regardless of payer."
        ),
        "type": "int",
        "allowed": "Integer >= 0",
    },
    "nonplan_unsuccessful_donor_insemination_cycles": {
        "description": (
            "Completed unsuccessful donor artificial insemination cycles "
            "self-paid or otherwise not paid for by this plan; a subset of "
            "the total donor cycles."
        ),
        "type": "int",
        "allowed": "Integer >= 0",
    },
    "abnormal_semen_analysis_dates": {
        "description": (
            "Dates of abnormal semen analyses obtained by the patient. "
            "A qualifying pair suffices; the list need not include normal results."
        ),
        "type": "list[str]",
        "format": 'Each item is "YYYY_MM_DD"',
    },
    "clinical_gender_dysphoria_patient_or_partner": {
        "description": (
            "The patient or their partner has been clinically diagnosed "
            "with gender dysphoria."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Complete history through the service date of the patient's "
            "unmedicated day-3 FSH tests, in any order. Values are in mIU/mL. "
            "An empty list establishes that no such test exists."
        ),
        "type": "list[dict]",
        "format": '[{"date": "YYYY_MM_DD", "value": finite_number_ge_0}, ...]',
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """Return whether the supplied known facts establish this benefit's coverage."""

    def date_value(value):
        if not isinstance(value, str):
            return None
        try:
            result = datetime.strptime(value, "%Y_%m_%d").date()
            return result if result.strftime("%Y_%m_%d") == value else None
        except ValueError:
            return None

    def number(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        try:
            return value if math.isfinite(value) and value >= 0 else None
        except (OverflowError, TypeError):
            return None

    def count(value):
        return value if type(value) is int and value >= 0 else None

    def at_least(field, threshold):
        value = number(claim.get(field))
        return value is not None and value >= threshold

    def age_on(birth, day):
        if birth is None or day is None or birth > day:
            return None
        return day.year - birth.year - (
            (day.month, day.day) < (birth.month, birth.day)
        )

    def months_before(day, months):
        index = day.year * 12 + day.month - 1 - months
        year, month_index = divmod(index, 12)
        if year < 1:
            return None
        month = month_index + 1
        return day.replace(
            year=year,
            month=month,
            day=min(day.day, monthrange(year, month)[1]),
        )

    if claim.get("service") not in {
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    }:
        return False
    if claim.get("charged_by_infertility_specialist") is not True:
        return False
    if claim.get("covered_capacity") not in {
        "student",
        "students_legal_spouse",
        "students_civil_union_partner",
        "students_domestic_partner",
    }:
        return False

    sex = claim.get("patient_sex")
    partner = claim.get("partner_sex")
    if sex not in {"female", "male", "other"}:
        return False
    if partner not in {"female", "male", "other", "none"}:
        return False

    if claim.get("documented_infertility_causing_condition") is not True:
        return False

    # READING: Disjunctive exclusions. "You or your partner has not had a
    # voluntary sterilization" and "You or your partner does not have infertility
    # that is due to a natural physiologic process" permit either person to
    # satisfy each negative statement. Without a partner, only the patient can.
    def negative_requirement(patient_field, partner_field):
        return (
            claim.get(patient_field) is False
            or (
                partner != "none"
                and claim.get(partner_field) is False
            )
        )

    if not negative_requirement(
        "patient_voluntary_sterilization",
        "partner_voluntary_sterilization",
    ):
        return False
    if not negative_requirement(
        "patient_natural_process_infertility",
        "partner_natural_process_infertility",
    ):
        return False

    if claim.get(
        "pregnancy_attainable_with_less_costly_covered_treatment"
    ) is not False:
        return False

    day = date_value(claim.get("service_date"))
    birth = date_value(claim.get("patient_birth_date"))
    patient_age = age_on(birth, day)
    partner_age = age_on(date_value(claim.get("partner_birth_date")), day)

    nonplan_cycles = count(
        claim.get("nonplan_unsuccessful_donor_insemination_cycles")
    )
    total_cycles = count(claim.get("unsuccessful_donor_insemination_cycles"))
    # A known subset itself establishes a lower bound on the total.
    known_cycle_counts = [
        value for value in (total_cycles, nonplan_cycles) if value is not None
    ]
    donor_lower_bound = max(known_cycle_counts, default=0)

    # READING: Independent glossary pathway. "For an individual or their partner
    # who has been clinically diagnosed with gender dysphoria" establishes
    # glossary infertility without the other glossary waiting periods. It does
    # not say that otherwise applicable eligibility/table conditions are waived.
    infertile = (
        claim.get("clinical_gender_dysphoria_patient_or_partner") is True
    )

    if sex == "female" and patient_age is not None:
        threshold = 12 if patient_age < 35 else 6
        if partner == "male":
            # READING: Cumulative glossary and table. The glossary says "after ...
            # frequent, unprotected heterosexual sexual intercourse" for a
            # female with a male partner. The table's donor-cycle "or" satisfies
            # the table, but does not erase this separate glossary requirement.
            infertile = infertile or at_least(
                "unsuccessful_frequent_intercourse_months", threshold
            )
        else:
            infertile = infertile or donor_lower_bound >= threshold

    if sex == "male" and partner == "female" and partner_age is not None:
        # READING: Couple-based infertility. The definition is "failure to become
        # pregnant," and the table expressly includes "A male of any age with a
        # female partner." Apply the female partner's glossary waiting period
        # to the couple rather than excluding this expressly listed male.
        threshold = 12 if partner_age < 35 else 6
        infertile = infertile or at_least(
            "unsuccessful_frequent_intercourse_months", threshold
        )

    if sex == "male" and partner != "female" and not infertile:
        analyses = claim.get("abnormal_semen_analysis_dates")
        if isinstance(analyses, list) and day is not None:
            dates = [
                parsed
                for item in analyses
                if (parsed := date_value(item)) is not None and parsed <= day
            ]
            infertile = (
                len(dates) >= 2 and (max(dates) - min(dates)).days >= 14
            )

    if not infertile:
        return False

    # READING: Unlisted table categories. "You have met the requirement for the
    # number of months trying to conceive" is quantified by the following table.
    # No waiting period or FSH requirement is invented for a category absent
    # from that table, such as a male without a female partner.
    if sex == "female":
        if patient_age is None:
            return False
        threshold = 12 if patient_age < 35 else 6

        # READING: Donor-cycle payment. The table labels its donor cycles
        # "Self paid/not paid for by plan"; count any cycles not paid by this
        # plan, without additionally requiring personal out-of-pocket payment.
        donor_ok = nonplan_cycles is not None and nonplan_cycles >= threshold
        intercourse_ok = at_least(
            "unsuccessful_timed_intercourse_months", threshold
        )
        if partner == "male":
            if not (intercourse_ok or donor_ok):
                return False
        elif not donor_ok:
            return False

        tests = claim.get("unmedicated_day3_fsh_tests")
        if not isinstance(tests, list) or not tests or day is None:
            return False

        parsed_tests = []
        for test in tests:
            if not isinstance(test, dict):
                return False
            test_day = date_value(test.get("date"))
            value = number(test.get("value"))
            if (
                test_day is None
                or value is None
                or test_day > day
                or test_day < birth
            ):
                return False
            parsed_tests.append((test_day, value))

        # READING: Calendar windows. "within the past" 12 or 6 "months" means
        # calendar months, including the boundary date, not a shorter fixed-day
        # approximation.
        earliest = months_before(day, threshold)
        latest = max(test_day for test_day, _ in parsed_tests)
        if earliest is not None and latest < earliest:
            return False

        if patient_age < 40:
            # All results tied for the most recent date must satisfy the limit;
            # their within-day order is not established by date-only inputs.
            if any(
                value >= 19
                for test_day, value in parsed_tests
                if test_day == latest
            ):
                return False
        else:
            # READING: Age-40 history. "less than 19 mIU/mL in all prior tests
            # performed after age 40" covers all tests at age 40 or older,
            # including the latest; earlier elevated results do not disqualify.
            # A recent test is still required, but need not postdate turning 40.
            if any(
                value >= 19
                for test_day, value in parsed_tests
                if age_on(birth, test_day) >= 40
            ):
                return False

    elif sex == "male" and partner == "female":
        if partner_age is None:
            return False
        threshold = 12 if partner_age < 35 else 6
        if not at_least("unsuccessful_timed_intercourse_months", threshold):
            return False
        # The male rows expressly mark donor cycles and FSH "Does not apply".

    # READING: Cycle definition, not a limit. "Each treatment type is counted as
    # a separate cycle" supplies accounting rules, but no numerical cap.
    # "The cycle begins with the initiation of therapy" also permits coverage
    # before the later confirmation that completes the cycle.
    return True
