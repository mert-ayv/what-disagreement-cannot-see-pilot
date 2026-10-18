"""
Comprehensive infertility-services coverage rule.

READING choices:
1. The enumerated services and table rows are exhaustive for this benefit.
2. Glossary categories apply to the patient, not automatically to their partner.
   Thus a male with a female partner needs the gender-dysphoria glossary route.
3. Gender dysphoria satisfies the glossary definition but does not waive the
   separate eligibility requirements or create an additional table row.
4. Neither the patient nor an existing partner may have a disqualifying voluntary
   sterilization or infertility due to a natural physiologic process.
5. For a female with a male partner, the table's donor-insemination alternative
   does not replace the glossary's intercourse requirement.
6. Qualifying donor cycles must be completed, self-paid, and not paid by the plan.
7. FSH recency uses inclusive calendar-month boundaries. At age 40 or older,
   both the latest qualifying result and every qualifying result on or after
   the 40th birthday must be strictly below 19 mIU/mL.

Unknown facts fail any requirement that needs them. Irrelevant fields may be
omitted. Clinical and historical fields describe established facts, not merely
the claimant's assertion that they are eligible.
"""

import calendar
import math
import re
from datetime import date


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
    "billed_by_infertility_specialist": {
        "description": "The charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_role": {
        "description": "Patient's covered status under this plan.",
        "type": "str",
        "allowed": [
            "student",
            "student_legal_spouse",
            "student_civil_union_partner",
            "student_domestic_partner",
            "other",
        ],
    },
    "patient_category": {
        "description": "Patient's applicable female/male category in the policy.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_category": {
        "description": (
            "Category of the patient's partner; 'none' means no partner. "
            "'Other' means an existing partner in neither listed category."
        ),
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "patient_age": {
        "description": "Patient's age in completed years on the service date.",
        "type": "int",
        "allowed": "Nonnegative integer; required for female table rows.",
    },
    "partner_age": {
        "description": "Partner's age in completed years on the service date.",
        "type": "int",
        "allowed": "Nonnegative integer; required for male-with-female table rows.",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition has been demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_physician_or_specialist": {
        "description": (
            "That same condition is recognized by the patient's physician "
            "or infertility specialist."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_patient_or_partner_records": {
        "description": (
            "That same condition is documented in the patient's or "
            "existing partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": (
            "Patient has ever undergone voluntary sterilization, regardless "
            "of reversal or reversal results. Tubal ligation, hysterectomy, "
            "and vasectomy count only when obtained for voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": (
            "Existing partner has ever undergone voluntary sterilization, "
            "using the same definition as for the patient."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_infertility_due_to_natural_process": {
        "description": (
            "Patient has infertility due to a natural physiologic process, "
            "including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_infertility_due_to_natural_process": {
        "description": (
            "Existing partner has infertility due to a natural physiologic "
            "process, including age-related ovarian insufficiency."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "successful_pregnancy_unattainable_through_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy cannot be attained through less costly "
            "treatment covered under the plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": (
            "Patient or an existing partner has a clinical diagnosis "
            "of gender dysphoria."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "failed_to_become_pregnant_during_qualifying_attempts": {
        "description": (
            "The qualifying intercourse or insemination history represents "
            "failure to become pregnant for the glossary definition."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "months_frequent_unprotected_heterosexual_intercourse": {
        "description": (
            "Months of qualifying frequent, unprotected heterosexual "
            "intercourse for the glossary definition."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number, excluding bool.",
    },
    "months_unprotected_timed_sexual_intercourse": {
        "description": (
            "Months trying to conceive through unprotected timed sexual "
            "intercourse, with egg and sperm contact, for the table."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number, excluding bool.",
    },
    "completed_self_paid_donor_insemination_cycles": {
        "description": (
            "Number of donor artificial-insemination cycles involving egg "
            "and sperm contact that were self-paid and not paid by the plan. "
            "Count only completed cycles: initiation through confirmed "
            "non-pregnancy, or through six weeks after a positive pregnancy "
            "test. Each treatment type counts separately."
        ),
        "type": "int",
        "allowed": "Nonnegative integer, excluding bool.",
    },
    "service_date": {
        "description": "Date of the requested service; reference date for FSH recency.",
        "type": "str",
        "allowed": "Valid date in YYYY_MM_DD format.",
    },
    "latest_unmedicated_day3_fsh_date": {
        "description": (
            "Date of the most recent unmedicated day-3 FSH test "
            "performed on or before the service date."
        ),
        "type": "str",
        "allowed": "Valid date in YYYY_MM_DD format.",
    },
    "latest_unmedicated_day3_fsh_value": {
        "description": "Result of that most recent qualifying FSH test, in mIU/mL.",
        "type": "int or float",
        "allowed": "Finite nonnegative number, excluding bool.",
    },
    "all_unmedicated_day3_fsh_tests_at_or_after_40_below_19": {
        "description": (
            "Every unmedicated day-3 FSH test performed from the patient's "
            "40th birthday through the service date, including the latest "
            "such test, had a result strictly below 19 mIU/mL. "
            "True requires knowledge of the entire applicable test history."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """Return whether the claim satisfies this benefit's service and eligibility rules."""

    def nonnegative_integer(value):
        return type(value) is int and value >= 0

    def nonnegative_number(value):
        if type(value) is int:
            return value >= 0
        return type(value) is float and math.isfinite(value) and value >= 0

    def at_least(field, minimum):
        value = claim.get(field)
        return nonnegative_number(value) and value >= minimum

    def parse_date(value):
        if not isinstance(value, str):
            return None
        if re.fullmatch(r"[0-9]{4}_[0-9]{2}_[0-9]{2}", value) is None:
            return None
        try:
            return date(*(int(part) for part in value.split("_")))
        except ValueError:
            return None

    def months_before(value, months):
        month_index = value.year * 12 + value.month - 1 - months
        year, month_zero = divmod(month_index, 12)
        if year < 1:
            return date.min
        month = month_zero + 1
        day = min(value.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    # READING: Service scope — "the following infertility services" is an
    # exhaustive list here, not coverage for every infertility-related service.
    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False
    if claim.get("billed_by_infertility_specialist") is not True:
        return False

    if claim.get("covered_role") not in (
        "student",
        "student_legal_spouse",
        "student_civil_union_partner",
        "student_domestic_partner",
    ):
        return False

    required_true = (
        "condition_demonstrated_to_cause_infertility",
        "condition_recognized_by_physician_or_specialist",
        "condition_documented_in_patient_or_partner_records",
        "successful_pregnancy_unattainable_through_less_costly_covered_treatment",
    )
    if any(claim.get(field) is not True for field in required_true):
        return False

    patient = claim.get("patient_category")
    partner = claim.get("partner_category")
    if patient not in ("female", "male"):
        return False
    if partner not in ("female", "male", "other", "none"):
        return False

    # READING: Partner exclusions — "You or your partner has not had" and
    # "You or your partner does not have" exclude a disqualifying history or
    # cause in either person; one unaffected person does not cure the other.
    if claim.get("patient_voluntary_sterilization") is not False:
        return False
    if claim.get("patient_infertility_due_to_natural_process") is not False:
        return False
    if partner != "none":
        if claim.get("partner_voluntary_sterilization") is not False:
            return False
        if claim.get("partner_infertility_due_to_natural_process") is not False:
            return False

    # READING: Table scope — "You have met the requirement for the number of
    # months" and the listed "You are" categories require an applicable row.
    # The glossary's male-without-female route does not create a table row.
    if patient == "male" and partner != "female":
        return False

    if patient == "female":
        age = claim.get("patient_age")
        if not nonnegative_integer(age):
            return False
        threshold = 12 if age < 35 else 6
    else:
        partner_age = claim.get("partner_age")
        if not nonnegative_integer(partner_age):
            return False
        threshold = 12 if partner_age < 35 else 6

    cycles = claim.get("completed_self_paid_donor_insemination_cycles")

    # READING: Donor-cycle accounting — "Self paid/not paid for by plan" and
    # "a cycle is considered completed" require completed self-paid cycles
    # without plan payment, rather than merely initiated or plan-funded cycles.
    donor_requirement_met = (
        nonnegative_integer(cycles) and cycles >= threshold
    )
    timed_requirement_met = at_least(
        "months_unprotected_timed_sexual_intercourse", threshold
    )

    if patient == "male":
        if not timed_requirement_met:
            return False
    elif partner == "male":
        if not (timed_requirement_met or donor_requirement_met):
            return False
    elif not donor_requirement_met:
        return False

    gender_dysphoria = (
        claim.get("patient_or_partner_clinically_diagnosed_gender_dysphoria")
        is True
    )

    # READING: Glossary subjects — "For a female with a male partner" applies
    # to a female patient, not automatically to her male partner. The glossary
    # supplies no ordinary male-with-female timing route; such a patient must
    # qualify under "an individual or their partner ... gender dysphoria".
    #
    # READING: Independent conditions — "You are eligible ... if" preserves
    # every table requirement even when gender dysphoria establishes infertility.
    if not gender_dysphoria:
        if patient != "female":
            return False
        if claim.get("failed_to_become_pregnant_during_qualifying_attempts") is not True:
            return False
        if partner == "male":
            # READING: Separate glossary and table tests — glossary "after ...
            # frequent, unprotected heterosexual sexual intercourse" remains
            # necessary despite the table's alternative "or ... donor insemination".
            if not at_least(
                "months_frequent_unprotected_heterosexual_intercourse",
                threshold,
            ):
                return False
        elif not donor_requirement_met:
            return False

    # Male rows explicitly say FSH testing and results "Does not apply".
    if patient == "male":
        return True

    service_date = parse_date(claim.get("service_date"))
    test_date = parse_date(claim.get("latest_unmedicated_day3_fsh_date"))
    result = claim.get("latest_unmedicated_day3_fsh_value")
    if service_date is None or test_date is None:
        return False
    if not nonnegative_number(result):
        return False

    # READING: FSH recency — "within the past" 12 or 6 "months" means calendar
    # months, including the exact cutoff date, and excludes future tests.
    recency_months = 12 if age < 35 else 6
    if not months_before(service_date, recency_months) <= test_date <= service_date:
        return False

    # READING: Age-40 FSH history — "less than 19 ... in all prior tests
    # performed after age 40" includes tests from the 40th birthday onward
    # and does not permit a failing latest result. Exactly 19 fails.
    if result >= 19:
        return False
    if age >= 40:
        if (
            claim.get("all_unmedicated_day3_fsh_tests_at_or_after_40_below_19")
            is not True
        ):
            return False

    return True
