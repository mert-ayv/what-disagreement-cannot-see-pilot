"""
Comprehensive infertility-services coverage rule.

READING choices (explained at the corresponding code comments):
1. The listed services and table categories are exhaustive.
2. The glossary and benefit-specific eligibility requirements are cumulative.
3. Either person's voluntary sterilization or naturally caused infertility bars coverage.
4. Male applicants with female partners use the glossary's corresponding couple criteria.
5. Gender dysphoria supplies a glossary alternative, not an exemption from the table.
6. Donor cycles used for the table must not have been paid for by the plan.
7. Calendar-month lookback periods include their boundary dates.
8. At age 40 or older, the FSH threshold applies to every qualifying test at age
   40 or older, including the latest test; the recent-test requirement still applies.

Fields describe established facts. Missing or unknown facts cannot establish a
required condition. An alternative route may establish eligibility even when
facts relevant only to another route are unknown.

The FSH history field, when supplied, represents the complete specified history;
omit it if that history is unknown. No precertification, network, medical-
necessity, plan-limit, or general-exclusion checks are performed.
"""

import calendar
import math
import re
from datetime import date


SCHEMA = {
    "service": {
        "description": "The service for which charges are claimed.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "charged_by_infertility_specialist": {
        "description": "Whether the claimed charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "plan_relationship": {
        "description": "The patient's status under this plan.",
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
        "description": "Date of the claimed service; eligibility is evaluated on this date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_table_category": {
        "description": "Whether the patient falls within a female or male table category.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_category": {
        "description": "The patient's partner category for the glossary and table.",
        "type": "str",
        "allowed": ["male", "female", "no_partner", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date; needed for the female table rows.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "female_partner_birth_date": {
        "description": "Female partner's birth date; needed for the male table rows.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition has been demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "same_condition_recognized_by_physician_or_specialist": {
        "description": (
            "That same condition has been recognized by the patient's physician "
            "or infertility specialist."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "same_condition_documented_in_patient_or_partner_records": {
        "description": (
            "That same condition is documented in the patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "either_person_had_voluntary_sterilization": {
        "description": (
            "Whether the patient or partner ever had voluntary sterilization, "
            "regardless of reversal or its outcome. Tubal ligation, hysterectomy, "
            "and vasectomy count here only when obtained for voluntary sterilization. "
            "False establishes that neither person had it; an absent partner adds no history."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "either_person_infertility_due_to_natural_physiology": {
        "description": (
            "Whether either person's infertility is due to a natural physiologic "
            "process, such as age-related ovarian insufficiency. False establishes "
            "that neither person's infertility has such a cause."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "successful_pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": (
            "Whether a successful pregnancy can be attained through less costly "
            "treatment covered by this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "failure_to_become_pregnant": {
        "description": "Whether the failure to become pregnant underlying the claim is established.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": "Whether either person has a clinical diagnosis of gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "frequent_unprotected_heterosexual_intercourse_months": {
        "description": (
            "Established duration of unsuccessful attempts through frequent, "
            "unprotected heterosexual intercourse for this couple."
        ),
        "type": "int | float",
        "allowed": "Finite nonnegative number of months.",
    },
    "unprotected_timed_intercourse_months": {
        "description": (
            "Established duration of unsuccessful attempts through unprotected "
            "timed sexual intercourse involving egg and sperm contact."
        ),
        "type": "int | float",
        "allowed": "Finite nonnegative number of months.",
    },
    "donor_insemination_cycles_not_paid_by_plan": {
        "description": (
            "Number of unsuccessful donor artificial-insemination cycles involving "
            "egg and sperm contact that were self-paid or otherwise not paid by this plan."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "latest_unmedicated_day3_fsh_test": {
        "description": (
            "The actual most recent unmedicated day-3 FSH test, not merely the "
            "most recent test whose result is known."
        ),
        "type": "dict",
        "format": (
            "{'date': 'YYYY_MM_DD', 'value': finite nonnegative int or float}; "
            "value is in mIU/mL."
        ),
    },
    "all_unmedicated_day3_fsh_tests_at_age_40_or_older": {
        "description": (
            "Complete history through the service date of unmedicated day-3 FSH "
            "tests performed when the patient was at least 40, including the "
            "latest test if applicable. An empty list asserts that there were none."
        ),
        "type": "list[dict]",
        "format": (
            "Each item is {'date': 'YYYY_MM_DD', "
            "'value': finite nonnegative int or float in mIU/mL}."
        ),
    },
}


def covered_under_benefit(claim: dict) -> bool:
    def parse_date(value):
        if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}_\d{2}_\d{2}", value
        ):
            return None
        try:
            return date(*map(int, value.split("_")))
        except ValueError:
            return None

    def nonnegative_number(value):
        if type(value) not in (int, float):
            return False
        if isinstance(value, float) and not math.isfinite(value):
            return False
        return value >= 0

    def reaches(value, threshold):
        return nonnegative_number(value) and value >= threshold

    def age_on(birth, on_date):
        return (
            on_date.year
            - birth.year
            - ((on_date.month, on_date.day) < (birth.month, birth.day))
        )

    def months_before(on_date, months):
        month_index = on_date.year * 12 + on_date.month - 1 - months
        year, month_zero = divmod(month_index, 12)
        if year < 1:
            return date.min
        month = month_zero + 1
        day = min(on_date.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def parse_test(value):
        if not isinstance(value, dict):
            return None
        test_date = parse_date(value.get("date"))
        result = value.get("value")
        if test_date is None or not nonnegative_number(result):
            return None
        return test_date, result

    if not isinstance(claim, dict):
        return False

    # READING: Exhaustive services — "We will cover charges made by an infertility
    # specialist for the following infertility services" limits this rule to the
    # two listed services, including the menotropins qualification.
    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False
    if claim.get("charged_by_infertility_specialist") is not True:
        return False

    if claim.get("plan_relationship") not in (
        "covered_student",
        "covered_dependent_legal_spouse",
        "covered_dependent_civil_union_partner",
        "covered_dependent_domestic_partner",
    ):
        return False

    for field in (
        "condition_demonstrated_to_cause_infertility",
        "same_condition_recognized_by_physician_or_specialist",
        "same_condition_documented_in_patient_or_partner_records",
    ):
        if claim.get(field) is not True:
            return False

    # READING: Either-person bars — "You or your partner has not had a voluntary
    # sterilization" and "You or your partner does not have infertility that is
    # due to a natural physiologic process" require both people to be free of
    # the respective disqualifying fact, rather than merely one of them.
    for field in (
        "either_person_had_voluntary_sterilization",
        "either_person_infertility_due_to_natural_physiology",
        "successful_pregnancy_attainable_with_less_costly_covered_treatment",
    ):
        if claim.get(field) is not False:
            return False

    service_date = parse_date(claim.get("service_date"))
    if service_date is None:
        return False

    category = claim.get("patient_table_category")
    partner = claim.get("partner_category")

    # READING: Exhaustive table categories — "You are" introduces the table's
    # categories. A glossary diagnosis does not supply an omitted table row,
    # so a male without a female partner, or a patient outside these categories,
    # cannot satisfy this benefit's table.
    if category == "female":
        if partner not in ("male", "female", "no_partner", "other"):
            return False
        birth = parse_date(claim.get("patient_birth_date"))
    elif category == "male" and partner == "female":
        birth = parse_date(claim.get("female_partner_birth_date"))
    else:
        return False

    if birth is None or birth > service_date:
        return False

    female_age = age_on(birth, service_date)
    required_months_or_cycles = 12 if female_age < 35 else 6

    timed_ok = reaches(
        claim.get("unprotected_timed_intercourse_months"),
        required_months_or_cycles,
    )
    cycles = claim.get("donor_insemination_cycles_not_paid_by_plan")
    donor_ok = (
        type(cycles) is int
        and cycles >= required_months_or_cycles
    )

    # READING: Unfunded donor cycles — "Self paid/not paid for by plan" qualifies
    # the donor artificial-insemination counts; plan-paid cycles do not count.
    if category == "female":
        table_attempts_ok = (timed_ok or donor_ok) if partner == "male" else donor_ok
    else:
        # Male rows say "Does not apply" for donor insemination.
        table_attempts_ok = timed_ok

    if not table_attempts_ok:
        return False

    # READING: Cumulative definitions — "You are eligible ... if" and "You have
    # met the requirement" impose the table in addition to the glossary's
    # "A disease defined by the failure to become pregnant." In particular,
    # donor cycles alone do not replace the glossary's intercourse criterion
    # for a female with a male partner.
    if claim.get("failure_to_become_pregnant") is not True:
        return False

    frequent_intercourse_ok = reaches(
        claim.get("frequent_unprotected_heterosexual_intercourse_months"),
        required_months_or_cycles,
    )

    # READING: Male/female couples — the glossary's "For a female with a male
    # partner" describes the couple's failed conception attempts and applies
    # when its male member claims under "A male ... with a female partner."
    if category == "male" or partner == "male":
        ordinary_glossary_ok = frequent_intercourse_ok
    else:
        ordinary_glossary_ok = donor_ok

    # READING: Gender dysphoria — "For an individual or their partner who has
    # been clinically diagnosed with gender dysphoria" is an alternative
    # glossary route, but does not waive "You have met the requirement for the
    # number of months trying to conceive" or the table's other requirements.
    dysphoria_glossary_ok = (
        claim.get("patient_or_partner_clinically_diagnosed_gender_dysphoria")
        is True
    )
    if not (ordinary_glossary_ok or dysphoria_glossary_ok):
        return False

    # Male table rows expressly make the FSH requirements inapplicable.
    if category == "male":
        return True

    latest = parse_test(claim.get("latest_unmedicated_day3_fsh_test"))
    if latest is None:
        return False
    latest_date, latest_value = latest
    if not birth <= latest_date <= service_date:
        return False

    lookback_months = 12 if female_age < 35 else 6

    # READING: Calendar lookback — "within the past" 12 or 6 months means
    # calendar months, including the boundary date, rather than a fixed number
    # of days.
    if latest_date < months_before(service_date, lookback_months):
        return False

    if female_age < 40:
        return latest_value < 19

    # READING: Age-40 history — "less than 19 mIU/mL in all prior tests
    # performed after age 40" includes every qualifying test performed at age
    # 40 or older through this claim, including the latest test. A later low
    # result cannot cure an earlier high result. The separate recent-test
    # requirement remains applicable. No post-40 test is invented if the
    # qualifying recent test actually occurred before the 40th birthday.
    history = claim.get("all_unmedicated_day3_fsh_tests_at_age_40_or_older")
    if not isinstance(history, list):
        return False

    latest_is_in_history = False
    for item in history:
        test = parse_test(item)
        if test is None:
            return False
        test_date, value = test
        if not birth <= test_date <= latest_date:
            return False
        if age_on(birth, test_date) < 40 or value >= 19:
            return False
        if test_date == latest_date and value == latest_value:
            latest_is_in_history = True

    if age_on(birth, latest_date) >= 40:
        return latest_value < 19 and latest_is_in_history

    return not history
