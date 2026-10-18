"""
Encode the comprehensive infertility services benefit.

READING choices:
1. The eligibility table supplies additional, benefit-specific requirements;
   glossary infertility alone does not establish eligibility.
2. A claimant must fit a table row. The glossary's broader categories do not
   supply missing benefit-specific eligibility requirements.
3. Neither the patient nor their partner may have the specified sterilization
   history or infertility due to a natural physiologic process.
4. For a female with a male partner, donor insemination can satisfy the table,
   but does not replace the glossary's intercourse requirement unless the
   glossary's gender-dysphoria alternative applies.
5. Donor cycles used for table eligibility must not have been paid by this plan.
6. FSH requirements concern unmedicated day-3 tests. At age 40 or older,
   every such test at or after age 40, including the latest, must be below 19.
7. Test recency uses inclusive calendar-month lookbacks.
8. Only the two listed treatments, charged by an infertility specialist, are
   encoded as covered services. Cycle definitions do not create a cycle limit.

Missing facts do not establish eligibility. An unknown fact is immaterial when
another expressly permitted alternative independently establishes the criterion.
"""

from calendar import monthrange
from datetime import date
import math


SCHEMA = {
    "service": {
        "description": "Treatment for which coverage is requested.",
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
    "covered_role": {
        "description": "Patient's covered relationship to the student plan.",
        "type": "str",
        "allowed": [
            "student",
            "dependent_legal_spouse",
            "dependent_civil_union_partner",
            "dependent_domestic_partner",
            "other",
        ],
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition demonstrated to cause the illness of infertility exists.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": (
            "That condition is recognized by the patient's physician or infertility "
            "specialist and documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "either_has_voluntary_sterilization_history": {
        "description": (
            "Patient or partner has undergone voluntary sterilization, even if "
            "reversed. Tubal ligation, hysterectomy, and vasectomy count here "
            "only when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "either_has_natural_physiologic_infertility": {
        "description": (
            "Patient or partner has infertility due to a natural physiologic "
            "process, such as age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "successful_pregnancy_possible_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy can be attained through a less costly "
            "treatment covered by this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_table_sex": {
        "description": "Patient's female/male classification for applying the policy table.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_category": {
        "description": "Partner category for applying the glossary and table.",
        "type": "str",
        "allowed": ["male", "female", "none", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth; needed for female table rows and FSH ages.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "service_date": {
        "description": "Date of the requested service; eligibility is assessed as of this date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "female_partner_age": {
        "description": "Female partner's completed years of age on the service date.",
        "type": "int",
        "allowed": "Nonnegative integer; needed for a male with a female partner.",
    },
    "failed_frequent_unprotected_intercourse_months": {
        "description": (
            "Months of frequent, unprotected heterosexual intercourse without "
            "achieving pregnancy, for the glossary definition."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number.",
    },
    "failed_unprotected_timed_intercourse_months": {
        "description": (
            "Months of unprotected timed sexual intercourse without achieving "
            "pregnancy, for the eligibility table."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number.",
    },
    "failed_donor_insemination_cycles_not_paid_by_plan": {
        "description": (
            "Completed donor artificial insemination cycles without achieving "
            "pregnancy that were self-paid or otherwise not paid by this plan."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "either_clinically_diagnosed_gender_dysphoria": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "unmedicated_day3_fsh_tests": {
        "description": (
            "Known unmedicated day-3 FSH tests through the service date, including "
            "the most recent such test. No later such test may be omitted."
        ),
        "type": "list[dict]",
        "format": (
            "Each item has exactly the relevant facts: "
            "{'date': 'YYYY_MM_DD', 'value_miu_ml': finite nonnegative number}."
        ),
    },
    "fsh_history_complete_since_age_40": {
        "description": (
            "The supplied FSH list includes every unmedicated day-3 FSH test "
            "performed at or after age 40 through the service date."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """Return whether the supplied facts establish coverage under this benefit."""
    if not isinstance(claim, dict):
        return False

    def number(value):
        return (
            type(value) in (int, float)
            and math.isfinite(value)
            and value >= 0
        )

    def count(value):
        return type(value) is int and value >= 0

    def at_least(field, threshold):
        value = claim.get(field)
        return number(value) and value >= threshold

    def parse_date(value):
        if not isinstance(value, str):
            return None
        parts = value.split("_")
        if (
            len(parts) != 3
            or [len(part) for part in parts] != [4, 2, 2]
            or not all(part.isascii() and part.isdigit() for part in parts)
        ):
            return None
        try:
            return date(*(int(part) for part in parts))
        except ValueError:
            return None

    def age_on(birth, when):
        return when.year - birth.year - (
            (when.month, when.day) < (birth.month, birth.day)
        )

    def subtract_months(when, months):
        index = when.year * 12 + when.month - 1 - months
        year, month_index = divmod(index, 12)
        if year < 1:
            return date.min
        month = month_index + 1
        return date(year, month, min(when.day, monthrange(year, month)[1]))

    # READING: Service scope — "We will cover charges made by an infertility
    # specialist for the following infertility services" limits this rule to
    # the two enumerated treatments and specialist charges.
    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False
    if claim.get("charged_by_infertility_specialist") is not True:
        return False

    if claim.get("covered_role") not in (
        "student",
        "dependent_legal_spouse",
        "dependent_civil_union_partner",
        "dependent_domestic_partner",
    ):
        return False

    if claim.get("condition_demonstrated_to_cause_infertility") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False

    # READING: Partner exclusions — "You or your partner has not had a voluntary
    # sterilization" and "You or your partner does not have infertility ... due
    # to a natural physiologic process" are read as excluding either person's
    # disqualifying history, not as permitting it whenever the other is unaffected.
    if claim.get("either_has_voluntary_sterilization_history") is not False:
        return False
    if claim.get("either_has_natural_physiologic_infertility") is not False:
        return False
    if (
        claim.get("successful_pregnancy_possible_with_less_costly_covered_treatment")
        is not False
    ):
        return False

    service_date = parse_date(claim.get("service_date"))
    if service_date is None:
        return False

    sex = claim.get("patient_table_sex")
    partner = claim.get("partner_category")
    if partner not in ("male", "female", "none", "other"):
        return False

    # READING: Table scope — "You have met the requirement for the number of
    # months trying to conceive" followed by the table is read as requiring a
    # listed eligibility pathway. The glossary's "male without a female partner"
    # and gender-dysphoria categories do not create an unlisted table pathway.
    if sex == "female":
        birth = parse_date(claim.get("patient_birth_date"))
        if birth is None or birth > service_date:
            return False
        patient_age = age_on(birth, service_date)
        required = 12 if patient_age < 35 else 6
    elif sex == "male" and partner == "female":
        partner_age = claim.get("female_partner_age")
        if not count(partner_age):
            return False
        required = 12 if partner_age < 35 else 6
        birth = None
        patient_age = None
    else:
        return False

    cycles = claim.get("failed_donor_insemination_cycles_not_paid_by_plan")
    donor_requirement_met = count(cycles) and cycles >= required
    timed_requirement_met = at_least(
        "failed_unprotected_timed_intercourse_months", required
    )

    # READING: Donor funding — "Self paid/not paid for by plan" qualifies the
    # donor-cycle counts used to meet the table.
    if sex == "female":
        if partner == "male":
            if not (timed_requirement_met or donor_requirement_met):
                return False
        elif not donor_requirement_met:
            return False
    elif not timed_requirement_met:
        return False

    # READING: Glossary versus table — "A. ... or B. ... donor insemination"
    # provides table alternatives, but the glossary separately defines a female
    # with a male partner by unsuccessful intercourse. "For an individual or
    # their partner ... diagnosed with gender dysphoria" is an independent
    # glossary alternative, not a waiver of the benefit's table or FSH criteria.
    glossary_met = (
        claim.get("either_clinically_diagnosed_gender_dysphoria") is True
    )
    if sex == "female" and partner != "male":
        # The table's required unsuccessful donor cycles also satisfy the
        # glossary's same numerical donor-cycle threshold.
        glossary_met = glossary_met or donor_requirement_met
    else:
        glossary_met = glossary_met or at_least(
            "failed_frequent_unprotected_intercourse_months", required
        )
    if not glossary_met:
        return False

    # The male table rows expressly say FSH testing "Does not apply".
    if sex == "male":
        return True

    tests = claim.get("unmedicated_day3_fsh_tests")
    if not isinstance(tests, list) or not tests:
        return False

    parsed_tests = []
    for test in tests:
        if not isinstance(test, dict):
            return False
        test_date = parse_date(test.get("date"))
        value = test.get("value_miu_ml")
        if (
            test_date is None
            or not birth <= test_date <= service_date
            or not number(value)
        ):
            return False
        parsed_tests.append((test_date, value))

    # READING: Recency — "within the past" 12 or 6 months means calendar
    # months, inclusive of the cutoff and service date.
    latest_date = max(test_date for test_date, _ in parsed_tests)
    lookback = 12 if patient_age < 35 else 6
    if latest_date < subtract_months(service_date, lookback):
        return False

    # READING: FSH scope — "unmedicated day 3 FSH" qualifies the tests assessed.
    # "less than 19 ... in all prior tests performed after age 40" includes all
    # such tests at or after the 40th birthday through the current assessment,
    # including the latest test; a complete post-40 history is required.
    if patient_age >= 40:
        if claim.get("fsh_history_complete_since_age_40") is not True:
            return False
        return all(
            value < 19
            for test_date, value in parsed_tests
            if age_on(birth, test_date) >= 40
        )

    # If multiple tests share the latest date, all must meet the threshold.
    return all(
        value < 19
        for test_date, value in parsed_tests
        if test_date == latest_date
    )
