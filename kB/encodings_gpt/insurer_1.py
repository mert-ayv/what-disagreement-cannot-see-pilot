"""
Comprehensive infertility-services coverage rule.

READING choices:
1. The two listed services and the table's patient categories are exhaustive.
2. The glossary is an additional requirement, not replaced by table eligibility.
   Its patient categories are read literally: it supplies no separate
   male-with-female-partner route other than the gender-dysphoria provision.
3. Gender dysphoria satisfies the glossary but does not waive the table.
4. Neither the patient nor their partner may have either disqualifying history.
5. Donor cycles used for table eligibility must not have been paid by this plan.
6. The glossary's frequent-intercourse requirement and the table's timed-
   intercourse requirement are separate requirements.
7. Female patients must satisfy the FSH requirements; male rows waive them.
   At age 40 or older, every relevant test at or after the fortieth birthday
   must be below 19, including the latest such test.
8. FSH recency uses inclusive calendar-month intervals.
9. A cycle's completion definition supplies no additional coverage limit.

Missing facts establish nothing. An unknown fact does not prevent coverage
when another expressly permitted alternative establishes the requirement.
Precertification and the other checks assigned elsewhere are not evaluated.
"""

import calendar
from datetime import datetime, date


SCHEMA = {
    "service": {
        "description": "The service for which coverage is sought.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "service_date": {
        "description": "Date of the claimed service; eligibility is assessed then.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "charges_made_by_infertility_specialist": {
        "description": "Whether the claimed charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_under_plan": {
        "description": "Whether the patient is covered under this plan on the service date.",
        "type": "bool",
        "allowed": [True, False],
    },
    "coverage_role": {
        "description": "The patient's relationship qualifying them for plan coverage.",
        "type": "str",
        "allowed": [
            "student",
            "student_legal_spouse",
            "student_civil_union_partner",
            "student_domestic_partner",
            "other",
        ],
    },
    "patient_sex": {
        "description": "The patient's female/male classification for the policy table.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's birth date; required for female table rows.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Partner classification for the table; 'none' means no partner.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's birth date; required for a male with a female partner.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition exists that is demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_required_clinician": {
        "description": (
            "That same condition was recognized by the patient's physician "
            "or an infertility specialist."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_patient_or_partner_record": {
        "description": (
            "That same condition is documented in the patient's or partner's "
            "medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "either_has_voluntary_sterilization_history": {
        "description": (
            "Whether either patient or partner has undergone voluntary "
            "sterilization, even if reversed. Count tubal ligation, hysterectomy "
            "or vasectomy only when obtained as voluntary sterilization. "
            "With no partner, this concerns only the patient."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "either_has_infertility_due_to_natural_physiologic_process": {
        "description": (
            "Whether patient or partner has infertility caused by a natural "
            "physiologic process, including age-related ovarian insufficiency. "
            "With no partner, this concerns only the patient."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "successful_pregnancy_unattainable_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy cannot be attained through less costly "
            "treatment covered under this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_clinically_diagnosed_gender_dysphoria": {
        "description": (
            "Whether the patient or their partner has been clinically "
            "diagnosed with gender dysphoria."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "failure_to_become_pregnant": {
        "description": (
            "The attempts supplied for the applicable glossary route represent "
            "failure to become pregnant, rather than merely elapsed attempts."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "frequent_unprotected_heterosexual_intercourse_months": {
        "description": (
            "Completed months of frequent, unprotected heterosexual intercourse "
            "in the conception attempt being assessed under the glossary."
        ),
        "type": "int",
        "allowed": "Nonnegative integer; bool is not accepted.",
    },
    "unprotected_timed_intercourse_months": {
        "description": (
            "Completed months of unprotected timed sexual intercourse in the "
            "conception attempt being assessed under the table."
        ),
        "type": "int",
        "allowed": "Nonnegative integer; bool is not accepted.",
    },
    "donor_insemination_cycles_not_paid_by_plan": {
        "description": (
            "Number of donor artificial-insemination cycles in the conception "
            "attempt being assessed that were self-paid or otherwise not paid "
            "by this plan."
        ),
        "type": "int",
        "allowed": "Nonnegative integer; bool is not accepted.",
    },
    "latest_unmedicated_day3_fsh_date": {
        "description": (
            "Date of the actual most recent unmedicated day-3 FSH test "
            "performed on or before the service date."
        ),
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "latest_unmedicated_day3_fsh_miu_ml": {
        "description": (
            "Result of that most recent test, in mIU/mL; used for patients "
            "under age 40."
        ),
        "type": "int or float",
        "allowed": "Finite nonnegative number; bool is not accepted.",
    },
    "all_unmedicated_day3_fsh_tests_at_or_after_40_below_19": {
        "description": (
            "Whether every unmedicated day-3 FSH test performed from the "
            "fortieth birthday through the service date, including the latest "
            "such test, was below 19 mIU/mL. True if there were no such tests."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """Return whether the supplied facts establish this benefit's coverage."""
    if not isinstance(claim, dict):
        return False

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.strptime(value, "%Y_%m_%d").date()
            return parsed if parsed.strftime("%Y_%m_%d") == value else None
        except ValueError:
            return None

    def age_on(birth, on):
        return on.year - birth.year - (
            (on.month, on.day) < (birth.month, birth.day)
        )

    def months_before(on, months):
        month_index = on.year * 12 + on.month - 1 - months
        year, zero_based_month = divmod(month_index, 12)
        if year < 1:
            return date.min
        month = zero_based_month + 1
        return date(year, month, min(on.day, calendar.monthrange(year, month)[1]))

    def at_least(field, minimum):
        value = claim.get(field)
        return type(value) is int and value >= minimum

    # READING: "We will cover charges made by an infertility specialist for
    # the following infertility services" makes the two-item list exhaustive.
    if claim.get("service") not in (
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    ):
        return False
    if claim.get("charges_made_by_infertility_specialist") is not True:
        return False

    if claim.get("covered_under_plan") is not True:
        return False
    if claim.get("coverage_role") not in (
        "student",
        "student_legal_spouse",
        "student_civil_union_partner",
        "student_domestic_partner",
    ):
        return False

    on = parse_date(claim.get("service_date"))
    if on is None:
        return False

    # READING: "recognized by your physician or infertility specialist" and
    # "in your or your partner's medical records" allow either listed clinician
    # and either record, but all conditions must concern the same condition.
    for field in (
        "condition_demonstrated_to_cause_infertility",
        "condition_recognized_by_required_clinician",
        "condition_documented_in_patient_or_partner_record",
        "successful_pregnancy_unattainable_with_less_costly_covered_treatment",
    ):
        if claim.get(field) is not True:
            return False

    # READING: "You or your partner has not had a voluntary sterilization" and
    # "You or your partner does not have infertility ... due to a natural
    # physiologic process" exclude the claim if either person has either
    # disqualifying history; one unaffected person does not cure the exclusion.
    for field in (
        "either_has_voluntary_sterilization_history",
        "either_has_infertility_due_to_natural_physiologic_process",
    ):
        if claim.get(field) is not False:
            return False

    sex = claim.get("patient_sex")
    partner = claim.get("partner_sex")
    if partner not in ("female", "male", "other", "none"):
        return False

    # READING: The table's "You are" rows exhaust its eligible categories.
    # "For a male without a female partner" in the glossary establishes a
    # definition, not an additional table row or an exemption from the table.
    if sex == "female":
        birth = parse_date(claim.get("patient_birth_date"))
        if birth is None or birth > on:
            return False
        age = age_on(birth, on)
        required = 12 if age < 35 else 6
    elif sex == "male" and partner == "female":
        birth = parse_date(claim.get("partner_birth_date"))
        if birth is None or birth > on:
            return False
        required = 12 if age_on(birth, on) < 35 else 6
        age = None
    else:
        return False

    timed_ok = at_least("unprotected_timed_intercourse_months", required)
    donor_ok = at_least("donor_insemination_cycles_not_paid_by_plan", required)

    # READING: "Self paid/not paid for by plan" limits the donor cycles counted.
    # The table's "or" supplies alternatives to months of intercourse, not
    # an additional months requirement on top of qualifying donor cycles.
    if sex == "female":
        if partner == "male":
            if not (timed_ok or donor_ok):
                return False
        elif not donor_ok:
            return False
    elif not timed_ok:
        return False

    # READING: The glossary's "For a female with a male partner" requires
    # frequent unprotected heterosexual intercourse even when donor cycles
    # satisfy the table. "Unprotected timed sexual intercourse" in the table
    # is a separate factual requirement, not a substitute for "frequent".
    #
    # READING: The glossary enumerates patient categories. It says "For a
    # female with a male partner" and "For a male without a female partner";
    # it does not give a male-with-female-partner intercourse route. Do not
    # impute the female partner's glossary classification to a male patient.
    #
    # READING: "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" independently satisfies the glossary,
    # but does not waive any eligibility requirement, including the table.
    glossary_ok = (
        claim.get("patient_or_partner_clinically_diagnosed_gender_dysphoria")
        is True
    )
    if not glossary_ok and sex == "female":
        if claim.get("failure_to_become_pregnant") is True:
            if partner == "male":
                glossary_ok = at_least(
                    "frequent_unprotected_heterosexual_intercourse_months",
                    required,
                )
            else:
                # Qualifying unpaid cycles also establish the glossary's
                # minimum total number of donor-insemination cycles.
                glossary_ok = donor_ok
    if not glossary_ok:
        return False

    # READING: Male rows say FSH "Does not apply"; female rows require an
    # actual recent unmedicated day-3 test.
    if sex == "female":
        tested = parse_date(claim.get("latest_unmedicated_day3_fsh_date"))
        if tested is None or tested < birth or tested > on:
            return False

        # READING: "within the past" 12 or 6 months means an inclusive
        # calendar-month interval, with month-end dates clamped as necessary.
        recency_months = 12 if age < 35 else 6
        if tested < months_before(on, recency_months):
            return False

        if age < 40:
            value = claim.get("latest_unmedicated_day3_fsh_miu_ml")
            if type(value) not in (int, float) or not (0 <= value < 19):
                return False
        else:
            # READING: "less than 19 ... in all prior tests performed after
            # age 40" covers all unmedicated day-3 tests at age 40 or older,
            # including the most recent, not merely one favorable result.
            # It does not expressly require a test after the birthday:
            # a recent pre-birthday test may satisfy recency, while the
            # post-40 universal condition is vacuously true if none exist.
            if claim.get(
                "all_unmedicated_day3_fsh_tests_at_or_after_40_below_19"
            ) is not True:
                return False

    # READING: "A 'cycle' is an attempt" and its stated completion rules
    # define cycle counting; they impose neither a cycle cap nor a requirement
    # that a covered service await confirmation of the cycle's outcome.
    return True
