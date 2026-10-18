"""
Member-favourable readings:
1. The negative eligibility clauses using "you or your partner" are disjunctive:
   a qualifying fact about either actual person satisfies the relevant clause.
2. A condition may be recognized and documented for either person; no particular
   diagnosis, cause, or additional medical-necessity test is imposed here.
3. The glossary's female-partner pregnancy-failure criteria also establish
   infertility for a male claiming services with that female partner.
4. Clinical gender dysphoria is an independent glossary route, but does not
   waive an expressly applicable eligibility-table requirement.
5. Table requirements apply only to the populations described in its rows.
6. The table's donor-insemination alternative does not independently replace
   the glossary's intercourse requirement for a female with a male partner.
7. Calendar-month FSH windows include their boundary dates. For age 40 and
   older, the numerical restriction applies only to tests at age 40 or older.
8. If several tests share the latest recorded date, a qualifying result on
   that date can satisfy the "most recent" requirement.

Inputs are factual attestations, not requests for this function to determine
medical necessity. Missing or None values are unknown, not false. The function
requires affirmative evidence for each applicable requirement, while allowing
an established alternative to succeed despite unknown facts about another.
"""

import calendar
import math
from datetime import date


SCHEMA = {
    "assessment_date": {
        "description": "Date of the claimed infertility service.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "enrollment": {
        "description": "Patient's covered relationship to the student.",
        "type": "str",
        "allowed": [
            "covered_student",
            "covered_legal_spouse",
            "covered_civil_union_partner",
            "covered_domestic_partner",
            "other",
        ],
    },
    "service": {
        "description": "Service for which coverage is claimed.",
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
    "patient_sex": {
        "description": "Patient's sex category for the glossary and table.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_sex": {
        "description": "Sex category of the relevant actual partner, or no partner.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "patient_age": {
        "description": "Patient's attained age on the assessment date.",
        "type": "int",
        "allowed": "Nonnegative whole years",
    },
    "partner_age": {
        "description": "Partner's attained age on the assessment date.",
        "type": "int",
        "allowed": "Nonnegative whole years",
    },
    "qualifying_condition": {
        "description": (
            "A condition demonstrated to cause infertility has been recognized "
            "by a physician or infertility specialist and documented in the "
            "patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": (
            "Patient has had voluntary sterilization, whether reversed or not. "
            "Count hysterectomy, tubal ligation, or vasectomy only if obtained "
            "as voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Same voluntary-sterilization fact for the actual partner.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_natural_process_infertility": {
        "description": (
            "Patient has infertility due to a natural physiologic process, "
            "including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_natural_process_infertility": {
        "description": "Same natural-process infertility fact for the actual partner.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_less_costly_treatment_can_achieve_pregnancy": {
        "description": (
            "A successful pregnancy can be attained through a less costly "
            "treatment covered by the plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "unsuccessful_intercourse_months": {
        "description": (
            "Months of unsuccessful conception attempts through frequent, "
            "unprotected, timed heterosexual intercourse with egg-sperm contact, "
            "for the patient and relevant partner."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number",
    },
    "nonplan_donor_insemination_cycles": {
        "description": (
            "Number of unsuccessful donor artificial-insemination cycles with "
            "egg-sperm contact, self-paid or otherwise not paid by this plan."
        ),
        "type": "int",
        "allowed": "Nonnegative integer",
    },
    "patient_gender_dysphoria_diagnosed": {
        "description": "Patient has a clinical diagnosis of gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_gender_dysphoria_diagnosed": {
        "description": "Actual partner has a clinical diagnosis of gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "abnormal_semen_analysis_dates": {
        "description": (
            "Dates of the patient's abnormal semen analyses. The list need not "
            "be exhaustive; two qualifying documented analyses are sufficient."
        ),
        "type": "list[str]",
        "allowed": "Each date is YYYY_MM_DD and on or before assessment_date",
    },
    "fsh_tests": {
        "description": (
            "Complete history, through assessment_date, of the patient's "
            "unmedicated day-3 FSH tests. An absent list is unknown history. "
            "Other FSH tests are not included."
        ),
        "type": "list[dict]",
        "allowed": {
            "date": "YYYY_MM_DD; required to identify timing and latest test",
            "result_miu_ml": "Finite nonnegative number; unknown if missing",
            "age_at_test": (
                "Nonnegative integer attained age; needed to identify tests "
                "at age 40 or older when the patient is currently 40 or older"
            ),
        },
    },
}


def covered_under_benefit(claim: dict) -> bool:
    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            parsed = date.fromisoformat(value.replace("_", "-"))
            return parsed if parsed.strftime("%Y_%m_%d") == value else None
        except ValueError:
            return None

    def number(value):
        return (
            type(value) in (int, float)
            and math.isfinite(value)
            and value >= 0
        )

    def whole(value):
        return type(value) is int and value >= 0

    def at_least(field, threshold, integer=False):
        value = claim.get(field)
        valid = whole(value) if integer else number(value)
        return valid and value >= threshold

    def months_before(day, months):
        index = day.year * 12 + day.month - 1 - months
        year, month_index = divmod(index, 12)
        if year < 1:
            return date.min
        month = month_index + 1
        return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))

    if claim.get("enrollment") not in (
        "covered_student",
        "covered_legal_spouse",
        "covered_civil_union_partner",
        "covered_domestic_partner",
    ):
        return False
    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False
    if claim.get("charged_by_infertility_specialist") is not True:
        return False

    sex = claim.get("patient_sex")
    partner = claim.get("partner_sex")
    if sex not in ("female", "male", "other"):
        return False
    if partner not in ("female", "male", "other", "none"):
        return False
    has_partner = partner != "none"

    # READING: "recognized ... and documented in your or your partner's medical
    # records" permits either person's records; it does not require both.
    if claim.get("qualifying_condition") is not True:
        return False

    # READING: "You or your partner has not had a voluntary sterilization"
    # is read disjunctively: either actual person's non-sterilization suffices.
    # A nonexistent partner supplies no qualifying fact.
    if not (
        claim.get("patient_voluntary_sterilization") is False
        or (
            has_partner
            and claim.get("partner_voluntary_sterilization") is False
        )
    ):
        return False

    # READING: "You or your partner does not have infertility ... due to a
    # natural physiologic process" likewise permits either person's qualifying
    # absence of that condition.
    if not (
        claim.get("patient_natural_process_infertility") is False
        or (
            has_partner
            and claim.get("partner_natural_process_infertility") is False
        )
    ):
        return False

    if claim.get("covered_less_costly_treatment_can_achieve_pregnancy") is not False:
        return False

    age = claim.get("patient_age")
    partner_age = claim.get("partner_age")
    assessment = parse_date(claim.get("assessment_date"))

    # READING: "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" is an independent glossary route.
    glossary_met = (
        claim.get("patient_gender_dysphoria_diagnosed") is True
        or (
            has_partner
            and claim.get("partner_gender_dysphoria_diagnosed") is True
        )
    )

    if sex == "female" and whole(age):
        threshold = 12 if age < 35 else 6
        if partner == "male":
            # READING: The glossary says "heterosexual sexual intercourse";
            # the table's "or ... donor insemination" satisfies the table,
            # but does not rewrite that separate glossary requirement.
            glossary_met |= at_least("unsuccessful_intercourse_months", threshold)
        else:
            glossary_met |= at_least(
                "nonplan_donor_insemination_cycles", threshold, integer=True
            )

    if sex == "male" and partner == "female" and whole(partner_age):
        # READING: "failure to become pregnant" and the table's "A male ...
        # with a female partner" make the female partner's age-based failure
        # to conceive applicable to the male member as well.
        threshold = 12 if partner_age < 35 else 6
        glossary_met |= at_least("unsuccessful_intercourse_months", threshold)

    if sex == "male" and partner != "female" and assessment is not None:
        tests = claim.get("abnormal_semen_analysis_dates")
        if isinstance(tests, list):
            dates = [
                parsed
                for value in tests
                if (parsed := parse_date(value)) is not None
                and parsed <= assessment
            ]
            if len(dates) >= 2:
                glossary_met |= (max(dates) - min(dates)).days >= 14

    if not glossary_met:
        return False

    # READING: "You have met the requirement for the number of months" and
    # the table impose only the requirements actually assigned to a listed
    # population. No waiting period or FSH rule is invented for unlisted
    # populations, including a male without a female partner.
    # The independent gender-dysphoria definition does not waive listed rows.
    if sex == "male" and partner == "female":
        if not whole(partner_age):
            return False
        return at_least(
            "unsuccessful_intercourse_months", 12 if partner_age < 35 else 6
        )

    if sex != "female":
        return True

    if not whole(age):
        return False
    threshold = 12 if age < 35 else 6
    donor_met = at_least(
        "nonplan_donor_insemination_cycles", threshold, integer=True
    )
    if partner == "male":
        if not (
            at_least("unsuccessful_intercourse_months", threshold) or donor_met
        ):
            return False
    elif not donor_met:
        return False

    tests = claim.get("fsh_tests")
    if assessment is None or not isinstance(tests, list) or not tests:
        return False

    dated_tests = []
    for test in tests:
        if not isinstance(test, dict):
            return False
        tested = parse_date(test.get("date"))
        if tested is None or tested > assessment:
            return False
        dated_tests.append((tested, test))

    # READING: "within the past ... months" includes the calendar-month
    # boundary date, rather than imposing a shorter fixed-day approximation.
    latest_date = max(tested for tested, _ in dated_tests)
    if latest_date < months_before(assessment, threshold):
        return False

    def qualifying_result(test):
        result = test.get("result_miu_ml")
        return number(result) and result < 19

    if age < 40:
        # READING: "most recent lab test" permits a qualifying test on the
        # latest date when the supplied dates do not order same-day tests.
        return any(
            qualifying_result(test)
            for tested, test in dated_tests
            if tested == latest_date
        )

    # READING: "age 40 and older ... all prior tests performed after age 40"
    # includes tests while aged 40, but does not disqualify a patient because
    # of a pre-40 result. The separate recent-test requirement still applies.
    for _, test in dated_tests:
        test_age = test.get("age_at_test")
        if not whole(test_age) or test_age > age:
            return False
        if test_age >= 40 and not qualifying_result(test):
            return False
    return True
