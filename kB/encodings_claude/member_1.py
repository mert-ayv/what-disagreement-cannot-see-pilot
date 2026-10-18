"""Cardinal Care 2023-2024, comprehensive infertility services benefit (member-favourable encoding).

READING choices:
 1. Unknown facts: positive requirements (covered service, specialist billing, enrolment status,
    documented condition, months/cycles, FSH tests) must be shown by the claim. Disqualifying
    facts phrased as things that must not exist (voluntary sterilization, natural physiologic
    process, a less costly covered treatment that could succeed) count against the member only
    when the claim affirmatively shows them. Unknown sex, partner sex or ages: covered only if
    the claim is covered under every possible value.
 2. "your partner" is a defined term ("a covered dependent who is the student's legal spouse,
    civil union partner or domestic partner, referred to as 'your partner'"): the partner's
    sterilization or natural-process infertility disqualifies only if that partner is covered
    under this plan. The table's "male partner" / "female partner" keep their ordinary meaning.
 3. "You or your partner has not had a voluntary sterilization" and "You or your partner does not
    have infertility that is due to a natural physiologic process" are read as "neither", because
    the "at least one of you" reading would leave both bullets with almost no effect.
 4. Sterilization counts only "if obtained as a form of voluntary sterilization"; a medically
    indicated hysterectomy does not disqualify.
 5. Covered services are only "Ovulation induction cycle(s) with menotropins" and "Intrauterine
    insemination", and only "charges made by an infertility specialist".
 6. The required condition may be "recognized by your physician or infertility specialist" and
    "documented in your or your partner's medical records": either clinician, either record.
 7. "less costly treatment for which coverage is available under this plan": only a cheaper
    treatment the plan covers can defeat eligibility.
 8. Glossary for a female with a male partner names only intercourse, but the table also accepts
    "B. At least 12 cycles of donor insemination" (6 if 35+). The glossary is read in harmony with
    the table so that option B also establishes infertility.
 9. The glossary has no prong for a male with a female partner; the couple's failure to conceive
    after the intercourse period set by the female partner's age (12 months under 35, 6 months
    at 35+) establishes his infertility, matching the table's male rows.
10. The table has no row for a male without a female partner; no months or FSH requirement
    applies to him (his glossary prong of 2 abnormal semen analyses still applies).
11. "Self paid/not paid for by plan" in the donor insemination column is descriptive; all donor
    insemination cycles count toward the cycle requirement.
12. "frequent" (glossary) and "timed" (table) unprotected intercourse are one count of months.
13. Eligibility ("You are eligible ... if") may be assessed as of the date approval is requested
    or the date of service, whichever lets the claim qualify; ages and the FSH look-back are
    computed as of that one date.
14. FSH "done within the past" 12/6 months is inclusive of the boundary day; "your most recent
    lab test" is the latest unmedicated day 3 FSH test on or before the assessment date, and
    later tests are ignored.
15. "after age 40" means on or after the 40th birthday; for 40+ the rule is that every test
    from the 40th birthday onward is below 19 mIU/mL, plus a test inside the 6-month window.
16. The gender dysphoria prong satisfies the glossary definition by itself; the table still
    applies wherever a row matches the patient.
"""

import calendar
from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The infertility service billed on the claim.",
        "type": "str",
        "allowed": [
            "ovulation_induction_menotropins",
            "intrauterine_insemination",
            "ovulation_induction_other",
            "other",
        ],
    },
    "billed_by_infertility_specialist": {
        "description": "The charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "covered_as": {
        "description": "How the patient is covered under this plan.",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "other_dependent"],
    },
    "partner_covered_under_plan": {
        "description": "The patient's spouse/civil union/domestic partner is also covered under this plan "
        "(only read when the patient is the student; a dependent patient's partner is the student).",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_sex": {
        "description": "Sex of the patient as used by the policy table.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if the patient has no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "patient_date_of_birth": {"description": "Patient's date of birth.", "type": "str", "allowed": "YYYY_MM_DD"},
    "partner_date_of_birth": {"description": "Partner's date of birth.", "type": "str", "allowed": "YYYY_MM_DD"},
    "service_date": {"description": "Date the service was rendered.", "type": "str", "allowed": "YYYY_MM_DD"},
    "approval_request_date": {
        "description": "Date the provider requested advance approval for the infertility services.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "months_unprotected_intercourse": {
        "description": "Months of frequent/timed unprotected heterosexual intercourse without pregnancy.",
        "type": "number",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles": {
        "description": "Number of donor (artificial) insemination cycles without pregnancy, regardless of payer.",
        "type": "int",
        "allowed": ">= 0",
    },
    "semen_analyses": {
        "description": "Patient's semen analyses.",
        "type": "list[dict]",
        "allowed": "each {'date': 'YYYY_MM_DD', 'abnormal': bool}",
    },
    "fsh_tests": {
        "description": "Patient's unmedicated day 3 FSH tests (only such tests are listed).",
        "type": "list[dict]",
        "allowed": "each {'date': 'YYYY_MM_DD', 'value_miu_ml': number}",
    },
    "patient_gender_dysphoria_diagnosis": {
        "description": "Patient has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_gender_dysphoria_diagnosis": {
        "description": "Patient's partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_condition_documented": {
        "description": "A condition demonstrated to cause infertility has been recognized by a physician or "
        "infertility specialist and documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": "Patient ever had a voluntary sterilization (tubal ligation, hysterectomy, vasectomy obtained "
        "as voluntary sterilization), reversed or not.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Partner ever had a voluntary sterilization, reversed or not.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_infertility_due_to_natural_physiologic_process": {
        "description": "Patient's infertility is due to a natural physiologic process (e.g. perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_infertility_due_to_natural_physiologic_process": {
        "description": "Partner's infertility is due to a natural physiologic process.",
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_could_achieve_pregnancy": {
        "description": "A less costly treatment covered under this plan could achieve a successful pregnancy.",
        "type": "bool",
        "allowed": [True, False],
    },
}

# READING: covered services. "We will cover charges made by an infertility specialist for the following
# infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine insemination" -> only these two,
# and ovulation induction only when menotropins are used.
COVERED_SERVICES = {"ovulation_induction_menotropins", "intrauterine_insemination"}
ELIGIBLE_COVERAGE = {"student", "spouse", "civil_union_partner", "domestic_partner"}
FSH_LIMIT = 19.0


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = value.split("_")
        return date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _num(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return float(value)


def _age(dob, on):
    return on.year - dob.year - ((on.month, on.day) < (dob.month, dob.day))


def _minus_months(d, n):
    y, m = d.year, d.month - n
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _fortieth_birthday(dob):
    try:
        return date(dob.year + 40, dob.month, dob.day)
    except ValueError:  # 29 February birthday in a non-leap year
        return date(dob.year + 40, 3, 1)


def _patient_bracket(age):
    if age < 35:
        return "lt35"
    if age < 40:
        return "35to39"
    return "ge40"


def _two_abnormal_semen_analyses(claim, ref):
    dates = []
    for item in claim.get("semen_analyses") or []:
        if not isinstance(item, dict) or item.get("abnormal") is not True:
            continue
        d = _date(item.get("date"))
        if d is not None and (ref is None or d <= ref):
            dates.append(d)
    # "At least 2 abnormal semen analyses obtained at least 2 weeks apart"
    return len(dates) >= 2 and (max(dates) - min(dates)).days >= 14


def _months_and_cycles(claim):
    # READING: "frequent, unprotected heterosexual sexual intercourse" (glossary) and "unprotected timed sexual
    # intercourse" (table) are treated as one count of months trying to conceive.
    months = _num(claim.get("months_unprotected_intercourse"))
    # READING: donor cycle column "Self paid/not paid for by plan" is read as descriptive, not as excluding
    # cycles paid by anyone else; every donor insemination cycle counts.
    cycles = _num(claim.get("donor_insemination_cycles"))
    return months, cycles


def _infertile(claim, sex, psex, bracket, pbracket, ref):
    # READING: gender dysphoria prong. "For an individual or their partner who has been clinically diagnosed with
    # gender dysphoria" -> satisfies the glossary definition on its own.
    if claim.get("patient_gender_dysphoria_diagnosis") is True or claim.get("partner_gender_dysphoria_diagnosis") is True:
        return True
    months, cycles = _months_and_cycles(claim)
    if sex == "female":
        n = 12 if bracket == "lt35" else 6
        if psex == "male":
            # READING: glossary "For a female with a male partner, after: 1 year of frequent, unprotected heterosexual
            # sexual intercourse" is harmonized with the table's "B. At least 12 cycles of donor insemination" for the
            # same row, so donor cycles also establish infertility.
            return months >= n or cycles >= n
        # "For a female without a male partner, after: At least 12 cycles ... 6 cycles of donor insemination"
        return cycles >= n
    if psex == "female":
        # READING: the glossary has no prong for a male with a female partner; the couple's failure to conceive after
        # the period for "a female with a male partner" (set by her age) establishes his infertility, as the table's
        # rows "A male of any age with a female partner" presuppose.
        n = 12 if pbracket == "lt35" else 6
        return months >= n
    return _two_abnormal_semen_analyses(claim, ref)


def _fsh_ok(claim, bracket, ref, dob):
    if ref is None:
        return False
    tests = []
    for item in claim.get("fsh_tests") or []:
        if not isinstance(item, dict):
            continue
        d = _date(item.get("date"))
        if d is None or d > ref:
            continue
        v = item.get("value_miu_ml")
        tests.append((d, None if isinstance(v, bool) or not isinstance(v, (int, float)) else float(v)))
    if not tests:
        return False
    latest_date, latest_value = max(tests, key=lambda t: t[0])
    window = 12 if bracket == "lt35" else 6
    # READING: "You need to have an unmedicated day 3 FSH test done within the past: 12 months / 6 months" is measured
    # back from the assessment date and includes the boundary day; "your most recent lab test" is the latest test on
    # or before that date.
    if latest_date < _minus_months(ref, window):
        return False
    if bracket != "ge40":
        # "Must be less than 19 mIU/mL in your most recent lab test"
        return latest_value is not None and latest_value < FSH_LIMIT
    # READING: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40"
    # -> every test on or after the 40th birthday (up to the assessment date) is below 19; no separate
    # most-recent-test condition is added.
    if dob is not None:
        start = _fortieth_birthday(dob)
        relevant = [v for d, v in tests if d >= start]
    else:
        relevant = [v for _, v in tests]
    return all(v is not None and v < FSH_LIMIT for v in relevant)


def _table_ok(claim, sex, psex, bracket, pbracket, ref, dob):
    months, cycles = _months_and_cycles(claim)
    if sex == "female":
        n = 12 if bracket == "lt35" else 6
        if psex == "male":
            # "A. 12 months or more or B. At least 12 cycles of donor insemination" (6 for 35+)
            tried = months >= n or cycles >= n
        else:
            # Without a male partner: intercourse "Does not apply"; "At least 12 cycles" / "At least 6 cycles"
            tried = cycles >= n
        return tried and _fsh_ok(claim, bracket, ref, dob)
    if psex == "female":
        # "A male of any age with a female partner under 35": "12 months or more"; 35+: "6 months or more";
        # donor cycles, FSH window and FSH results "Does not apply".
        n = 12 if pbracket == "lt35" else 6
        return months >= n
    # READING: the table has no row for a male without a female partner, so "You have met the requirement for the
    # number of months" and the FSH criteria impose nothing on him.
    return True


def _eligible_as_of(claim, sex, psex, ref):
    dob = _date(claim.get("patient_date_of_birth"))
    pdob = _date(claim.get("partner_date_of_birth"))
    # READING: unknown ages. A claim with an unknown age is covered only if it is covered in every age bracket.
    if dob is not None and ref is not None:
        brackets = [_patient_bracket(_age(dob, ref))]
    else:
        brackets = ["lt35", "35to39", "ge40"]
    if pdob is not None and ref is not None:
        pbrackets = ["lt35" if _age(pdob, ref) < 35 else "ge35"]
    else:
        pbrackets = ["lt35", "ge35"]
    for b in brackets:
        for pb in pbrackets:
            if not _infertile(claim, sex, psex, b, pb, ref):
                return False
            if not _table_ok(claim, sex, psex, b, pb, ref, dob):
                return False
    return True


def covered_under_benefit(claim: dict) -> bool:
    g = claim.get

    if g("service_type") not in COVERED_SERVICES:
        return False
    # "We will cover charges made by an infertility specialist"
    if g("billed_by_infertility_specialist") is not True:
        return False

    # "covered under this plan as a student or as a covered dependent who is the student's legal spouse, civil union
    # partner or domestic partner"
    covered_as = g("covered_as")
    if covered_as not in ELIGIBLE_COVERAGE:
        return False

    # READING: "Has been recognized by your physician or infertility specialist and documented in your or your
    # partner's medical records" -> either clinician, either person's records.
    if g("infertility_condition_documented") is not True:
        return False

    # READING: "your partner" is the defined term ("a covered dependent who is the student's legal spouse, civil
    # union partner or domestic partner, referred to as 'your partner'"); the partner's facts below count only when
    # that partner is covered under this plan. A dependent patient's partner is the student, who is covered.
    if covered_as == "student":
        partner_is_your_partner = g("partner_covered_under_plan") is True
    else:
        partner_is_your_partner = True
    if g("partner_sex") == "none":
        partner_is_your_partner = False

    # READING: "You or your partner has not had a voluntary sterilization with or without surgical reversal" is read
    # as neither person has had one; a sterilization counts only "if obtained as a form of voluntary sterilization".
    # Unknown history is not treated as a disqualifying sterilization.
    if g("patient_voluntary_sterilization") is True:
        return False
    if partner_is_your_partner and g("partner_voluntary_sterilization") is True:
        return False

    # READING: "You or your partner does not have infertility that is due to a natural physiologic process" is read
    # as neither; unknown is not treated as such a process.
    if g("patient_infertility_due_to_natural_physiologic_process") is True:
        return False
    if partner_is_your_partner and g("partner_infertility_due_to_natural_physiologic_process") is True:
        return False

    # READING: "A successful pregnancy cannot be attained through less costly treatment for which coverage is
    # available under this plan" -> fails only where a cheaper treatment that this plan covers could succeed.
    if g("less_costly_covered_treatment_could_achieve_pregnancy") is True:
        return False

    # READING: "You are eligible for infertility services if" -> eligibility may be assessed as of the approval
    # request date ("Your provider will request approval from us in advance") or the service date; all age and FSH
    # tests are then evaluated as of that single date.
    refs = [d for d in (_date(g("approval_request_date")), _date(g("service_date"))) if d is not None]
    if not refs:
        refs = [None]

    # READING: unknown sex or partner sex -> covered only if covered for every possible value.
    sexes = [g("patient_sex")] if g("patient_sex") in ("female", "male") else ["female", "male"]
    psexes = [g("partner_sex")] if g("partner_sex") in ("female", "male", "none") else ["female", "male", "none"]

    for sex in sexes:
        for psex in psexes:
            if not any(_eligible_as_of(claim, sex, psex, ref) for ref in refs):
                return False
    return True
