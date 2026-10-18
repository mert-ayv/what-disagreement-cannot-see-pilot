"""
Member-favourable readings used:
1. The two "you or your partner" negative eligibility conditions are
   disjunctive: a qualifying fact about either actual person suffices.
2. A condition documented in either person's records suffices; it need not
   be documented in both.
3. Clinical gender dysphoria is an independent glossary route, but does not
   waive an applicable table requirement.
4. For a male with a female partner, the glossary's pregnancy-failure
   definition is applied through that female partner.
5. The table supplies no additional waiting period or FSH requirement for
   categories it does not address.
6. Donor cycles not paid for by this plan count toward the table, even if
   someone other than the member paid for them.
7. The donor alternative in the table does not rewrite the glossary's
   intercourse requirement for a female with a male partner.
8. FSH requirements concern unmedicated day-3 tests. At age 40 or older,
   the result restriction concerns tests performed at age 40 or older,
   not tests before age 40.
9. "Within the past" includes the calendar-month boundary.
10. No cycle-count coverage limit is inferred from the definition of cycle.

Unknown facts do not establish eligibility. An unknown fact does not defeat
coverage when a known alternative independently establishes the requirement.
Counts and durations describe completed attempts before the claimed service.
Inputs are assumed truthful; malformed values do not establish a requirement.
"""

from calendar import monthrange
from datetime import datetime


SCHEMA = {
    "service_type": {
        "description": "The service for which coverage is requested.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "billed_by_infertility_specialist": {
        "description": "Whether the charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_person_category": {
        "description": "The patient's covered status under this plan.",
        "type": "str",
        "allowed": [
            "student",
            "covered_dependent_legal_spouse",
            "covered_dependent_civil_union_partner",
            "covered_dependent_domestic_partner",
            "other",
        ],
    },
    "patient_category": {
        "description": "The patient's female/male category for applying the policy's rows.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "partner_category": {
        "description": "The actual partner's category; 'none' means no partner.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "patient_age": {
        "description": "Patient's age in completed years when the service is provided.",
        "type": "int",
        "allowed": "Nonnegative integer; bool is not an integer here.",
    },
    "female_partner_age": {
        "description": "Female partner's age in completed years at the service date.",
        "type": "int",
        "allowed": "Nonnegative integer; relevant to a male with a female partner.",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition is demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_physician_or_specialist": {
        "description": "That condition is recognized by the patient's physician or infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_either_record": {
        "description": "That same condition is documented in the patient's or actual partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_had_voluntary_sterilization": {
        "description": (
            "Patient ever had voluntary sterilization, regardless of reversal. "
            "Tubal ligation, hysterectomy, or vasectomy counts only if obtained "
            "as voluntary sterilization."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_had_voluntary_sterilization": {
        "description": "Same sterilization fact for the actual partner, if any.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_has_natural_process_infertility": {
        "description": "Patient has infertility due to a natural physiologic process.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_has_natural_process_infertility": {
        "description": "Actual partner has infertility due to a natural physiologic process.",
        "type": "bool",
        "allowed": [True, False],
    },
    "cannot_achieve_pregnancy_with_less_costly_covered_treatment": {
        "description": (
            "A successful pregnancy cannot be attained through less costly "
            "treatment for which this plan provides coverage."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_has_clinically_diagnosed_gender_dysphoria": {
        "description": "Patient or an actual partner has clinically diagnosed gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "unsuccessful_intercourse_months": {
        "description": (
            "Completed months of frequent, unprotected, timed heterosexual "
            "intercourse with egg-and-sperm contact and failure to become "
            "pregnant, for the patient or the male patient's female partner."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "unsuccessful_donor_insemination_cycles": {
        "description": "Completed donor insemination cycles without pregnancy, regardless of payer.",
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "unsuccessful_donor_cycles_not_paid_by_plan": {
        "description": (
            "Completed donor insemination cycles without pregnancy that were "
            "not paid for by this plan; a subset of all donor cycles."
        ),
        "type": "int",
        "allowed": "Nonnegative integer.",
    },
    "abnormal_semen_analysis_dates": {
        "description": (
            "Dates of known abnormal semen analyses. A complete history is "
            "unnecessary if two qualifying analyses are supplied."
        ),
        "type": "list[str]",
        "allowed": 'Each date is "YYYY_MM_DD".',
    },
    "service_date": {
        "description": "Date of the claimed service; used for dated test requirements.",
        "type": "str",
        "allowed": '"YYYY_MM_DD".',
    },
    "latest_unmedicated_day3_fsh_date": {
        "description": (
            "Date of the most recent unmedicated day-3 FSH test obtained "
            "on or before the service date."
        ),
        "type": "str",
        "allowed": '"YYYY_MM_DD".',
    },
    "latest_unmedicated_day3_fsh_value": {
        "description": "Result of that most recent test in mIU/mL.",
        "type": "int | float",
        "allowed": "Finite nonnegative number; bool excluded.",
    },
    "all_fsh_tests_at_age_40_or_older_below_19": {
        "description": (
            "Whether every unmedicated day-3 FSH test performed at age 40 "
            "or older, through the service date, was below 19 mIU/mL. "
            "True requires knowledge of the relevant history; it is also "
            "true if there have been no such tests."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
}


def covered_under_benefit(claim: dict) -> bool:
    """Decide only the specified comprehensive-infertility benefit rule."""

    def nonnegative_int(field):
        value = claim.get(field)
        return value if type(value) is int and value >= 0 else None

    def at_least(field, threshold):
        value = nonnegative_int(field)
        return value is not None and value >= threshold

    def parse_date(value):
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.strptime(value, "%Y_%m_%d").date()
            return parsed if parsed.strftime("%Y_%m_%d") == value else None
        except ValueError:
            return None

    def either_person_is_negative(patient_field, partner_field):
        # READING: "You or your partner has not had" and "You or your
        # partner does not have" permit either actual person's negative
        # fact to satisfy the respective condition, rather than requiring
        # negative facts about both people.
        return (
            claim.get(patient_field) is False
            or (
                partner in {"female", "male", "other"}
                and claim.get(partner_field) is False
            )
        )

    if claim.get("service_type") not in {
        "ovulation_induction_with_menotropins",
        "intrauterine_insemination",
    }:
        return False
    if claim.get("billed_by_infertility_specialist") is not True:
        return False
    if claim.get("covered_person_category") not in {
        "student",
        "covered_dependent_legal_spouse",
        "covered_dependent_civil_union_partner",
        "covered_dependent_domestic_partner",
    }:
        return False

    patient = claim.get("patient_category")
    partner = claim.get("partner_category")
    if patient not in {"female", "male", "other"}:
        return False
    if partner not in {"female", "male", "other", "none"}:
        return False

    # READING: "documented in your or your partner's medical records"
    # permits documentation in either person's records, not necessarily both.
    for field in (
        "condition_demonstrated_to_cause_infertility",
        "condition_recognized_by_physician_or_specialist",
        "condition_documented_in_either_record",
        "cannot_achieve_pregnancy_with_less_costly_covered_treatment",
    ):
        if claim.get(field) is not True:
            return False

    if not either_person_is_negative(
        "patient_had_voluntary_sterilization",
        "partner_had_voluntary_sterilization",
    ):
        return False
    if not either_person_is_negative(
        "patient_has_natural_process_infertility",
        "partner_has_natural_process_infertility",
    ):
        return False

    age = nonnegative_int("patient_age")
    partner_age = nonnegative_int("female_partner_age")

    # READING: "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" is an independent glossary route.
    # It does not erase the separate benefit's applicable table conditions.
    glossary_met = (
        claim.get(
            "patient_or_partner_has_clinically_diagnosed_gender_dysphoria"
        )
        is True
    )

    if patient == "female" and age is not None:
        threshold = 12 if age < 35 else 6
        if partner == "male":
            # READING: The glossary says "unprotected heterosexual sexual
            # intercourse" here. The table's donor alternative does not
            # itself replace this separate glossary requirement.
            glossary_met |= at_least("unsuccessful_intercourse_months", threshold)
        else:
            # A known subset of sufficient size also establishes the total.
            glossary_met |= (
                at_least("unsuccessful_donor_insemination_cycles", threshold)
                or at_least("unsuccessful_donor_cycles_not_paid_by_plan", threshold)
            )
    elif patient == "male" and partner == "female" and partner_age is not None:
        # READING: "A disease defined by the failure to become pregnant,"
        # together with the table's "A male ... with a female partner",
        # applies the female partner's pregnancy-failure duration to him.
        threshold = 12 if partner_age < 35 else 6
        glossary_met |= at_least("unsuccessful_intercourse_months", threshold)
    elif patient == "male" and partner != "female":
        service_date = parse_date(claim.get("service_date"))
        dates = claim.get("abnormal_semen_analysis_dates")
        if service_date is not None and isinstance(dates, list):
            known_dates = [
                parsed
                for value in dates
                if (parsed := parse_date(value)) is not None
                and parsed <= service_date
            ]
            if known_dates:
                glossary_met |= (
                    max(known_dates) - min(known_dates)
                ).days >= 14

    if not glossary_met:
        return False

    if patient == "female":
        if age is None:
            return False
        threshold = 12 if age < 35 else 6

        # READING: "Self paid/not paid for by plan" includes donor cycles
        # funded by others, provided this plan did not pay for them.
        donor_requirement_met = at_least(
            "unsuccessful_donor_cycles_not_paid_by_plan", threshold
        )
        if partner == "male":
            attempts_met = (
                at_least("unsuccessful_intercourse_months", threshold)
                or donor_requirement_met
            )
        else:
            attempts_met = donor_requirement_met
        if not attempts_met:
            return False

        service_date = parse_date(claim.get("service_date"))
        test_date = parse_date(claim.get("latest_unmedicated_day3_fsh_date"))
        if service_date is None or test_date is None:
            return False

        months = 12 if age < 35 else 6
        month_index = service_date.year * 12 + service_date.month - 1 - months
        year, zero_based_month = divmod(month_index, 12)
        if year < 1:
            return False
        month = zero_based_month + 1
        boundary = service_date.replace(
            year=year,
            month=month,
            day=min(service_date.day, monthrange(year, month)[1]),
        )

        # READING: "within the past" 6 or 12 months includes the boundary
        # date, using calendar months rather than a fixed number of days.
        if not boundary <= test_date <= service_date:
            return False

        # READING: "Your unmedicated day 3 ... FSH" scopes the relevant
        # tests. "Age 40 and older ... all prior tests performed after
        # age 40" includes tests at age 40, but not pre-40 tests.
        # If no tests were performed at 40+, that universal result condition
        # is satisfied; the independent recent-test requirement still applies.
        if age >= 40:
            if claim.get("all_fsh_tests_at_age_40_or_older_below_19") is not True:
                return False
        else:
            value = claim.get("latest_unmedicated_day3_fsh_value")
            if type(value) not in (int, float) or not 0 <= value < 19:
                return False

    elif patient == "male" and partner == "female":
        if partner_age is None:
            return False
        threshold = 12 if partner_age < 35 else 6
        if not at_least("unsuccessful_intercourse_months", threshold):
            return False

    # READING: "met the requirement for the number of months" refers to
    # the supplied table. No extra waiting period or FSH threshold is
    # specified for a male without a female partner or another unlisted
    # category; their glossary route and all other conditions still apply.
    #
    # READING: "Each treatment type is counted as a separate cycle" defines
    # counting, but states no coverage limit, so none is inferred.
    return True
