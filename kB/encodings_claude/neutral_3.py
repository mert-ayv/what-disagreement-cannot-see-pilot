"""Cardinal Care 2023-2024: comprehensive infertility services benefit (pp. 62-64).

READING choices:
1. Covered services: only "Ovulation induction cycle(s) with menotropins" and
   "Intrauterine insemination", and only when "charges made by an infertility specialist".
2. Eligible member: the patient must be the student or the student's spouse / civil union
   partner / domestic partner covered as a dependent; other dependents are not eligible.
3. Age: every age threshold ("under 35", "35 years of age or older", "age 40 and older")
   is measured on the service date.
4. Male patient with a female partner: the glossary has no male-with-female-partner line,
   so the couple's infertility is tested with the "female with a male partner" line using
   the female partner's age, matching the table rows for males.
5. Glossary and table are cumulative: a female with a male partner must meet the glossary's
   months of intercourse (unless the gender dysphoria line applies) even though the table
   also allows donor insemination cycles (option B).
6. Gender dysphoria line of the glossary satisfies infertility by itself, but the table's
   requirements for the patient's row still apply.
7. Male without a female partner: the table has no row for him, so no months, donor-cycle
   or FSH requirement from the table applies.
8. Donor insemination cycles count only cycles "Self paid/not paid for by plan".
9. FSH "within the past" 12 / 6 months: at least one unmedicated day 3 FSH test dated on or
   before the service date and no earlier than 12 / 6 calendar months before it.
10. "Most recent lab test" means the latest unmedicated day 3 FSH test on or before the
    service date.
11. Age 40 and older: every unmedicated day 3 FSH test performed on or after the 40th
    birthday must be below 19 mIU/mL, and the most recent test must also be below 19.
12. "You or your partner" in the sterilization and natural-process bullets: a disqualifying
    fact in either person excludes coverage.
13. Unknown facts: a missing field that is needed to establish coverage yields False.
14. Glossary "at least 2 abnormal semen analyses obtained at least 2 weeks apart": any two
    analyses dated 14 or more days apart satisfy it.
"""

from datetime import date, datetime

SCHEMA = {
    "service_type": {
        "description": "Infertility service billed on the claim.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "Charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "coverage_role": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "student_spouse_or_partner_dependent", "other_dependent"],
    },
    "service_date": {
        "description": "Date of the service.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Sex of the patient as used to pick the table row.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if the patient has no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's date of birth (needed for a male patient with a female partner).",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "gender_dysphoria_diagnosis": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition exists that is demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": "The condition was recognized by the physician or infertility specialist and "
                       "documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "voluntary_sterilization": {
        "description": "Patient or partner had a voluntary sterilization (tubal ligation, hysterectomy "
                       "or vasectomy obtained as voluntary sterilization), with or without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Patient's or partner's infertility is due to a natural physiologic process such "
                       "as age related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through less costly treatment covered "
                       "under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_intercourse": {
        "description": "Months of frequent/timed unprotected heterosexual intercourse without pregnancy.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_not_plan_paid": {
        "description": "Donor artificial insemination cycles without pregnancy that were self paid or "
                       "not paid for by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of abnormal semen analyses of a male patient.",
        "type": "list[str]",
        "format": "list of YYYY_MM_DD",
    },
    "fsh_tests": {
        "description": "Unmedicated day 3 FSH tests of a female patient.",
        "type": "list[dict]",
        "format": "list of {'date': 'YYYY_MM_DD', 'value_miu_ml': float}",
    },
}

COVERED_SERVICES = {"ovulation_induction_menotropins", "intrauterine_insemination"}
FSH_LIMIT = 19.0


def _parse(s):
    return datetime.strptime(s, "%Y_%m_%d").date()


def _age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _minus_months(d, months):
    y, m = d.year, d.month - months
    while m <= 0:
        m += 12
        y -= 1
    # clamp the day to the last valid day of the target month
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, day)
        except ValueError:
            continue
    return date(y, m, 28)


def _birthday(birth, years):
    try:
        return date(birth.year + years, birth.month, birth.day)
    except ValueError:  # 29 February
        return date(birth.year + years, 3, 1)


def _fsh_ok(claim, service_date, birth, age, window_months):
    tests = claim.get("fsh_tests")
    if tests is None:
        return False
    parsed = []
    for t in tests:
        if not isinstance(t, dict) or t.get("date") is None or t.get("value_miu_ml") is None:
            continue
        td = _parse(t["date"])
        if td <= service_date:
            parsed.append((td, float(t["value_miu_ml"])))
    if not parsed:
        return False
    parsed.sort()
    # READING: FSH test window. "You need to have an unmedicated day 3 FSH test done within
    # the past: 12 months / 6 months" -> at least one test between service date minus the
    # window and the service date.
    start = _minus_months(service_date, window_months)
    if not any(start <= td <= service_date for td, _ in parsed):
        return False
    # READING: "your most recent lab test" -> latest unmedicated day 3 FSH test on or before
    # the service date.
    most_recent_value = parsed[-1][1]
    if not most_recent_value < FSH_LIMIT:
        return False
    if age >= 40:
        # READING: "must be less than 19 mIU/mL in all prior tests performed after age 40"
        # -> every test on or after the 40th birthday must be below 19 (most recent also
        # checked above).
        fortieth = _birthday(birth, 40)
        if any(v >= FSH_LIMIT for td, v in parsed if td >= fortieth):
            return False
    return True


def covered_under_benefit(claim: dict) -> bool:
    # READING: unknown facts. "A missing field means the fact is unknown" -> any fact needed
    # to establish coverage that is missing yields False.

    # Covered service.
    # READING: covered services. "We will cover charges made by an infertility specialist for
    # the following infertility services: Ovulation induction cycle(s) with menotropins;
    # Intrauterine insemination" -> only these two, and only by an infertility specialist.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # READING: eligible member. "covered under this plan as a student or as a covered dependent
    # who is the student's legal spouse, civil union partner or domestic partner" -> other
    # dependents are not eligible.
    if claim.get("coverage_role") not in ("student", "student_spouse_or_partner_dependent"):
        return False

    # Documented infertility-causing condition.
    if claim.get("condition_demonstrated_to_cause_infertility") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False

    # READING: "You or your partner has not had a voluntary sterilization" and "You or your
    # partner does not have infertility that is due to a natural physiologic process" -> a
    # disqualifying fact in either person excludes coverage.
    if claim.get("voluntary_sterilization") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("pregnancy_attainable_with_less_costly_covered_treatment") is not False:
        return False

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if sex not in ("female", "male") or partner_sex not in ("female", "male", "none"):
        return False
    if claim.get("service_date") is None or claim.get("patient_birth_date") is None:
        return False
    service_date = _parse(claim["service_date"])
    birth = _parse(claim["patient_birth_date"])
    # READING: age reference date. "A female under 35 years of age", "If you are age 40 and
    # older" -> ages are measured on the service date.
    age = _age(birth, service_date)

    gd = claim.get("gender_dysphoria_diagnosis")
    months = claim.get("months_unprotected_intercourse")
    cycles = claim.get("donor_insemination_cycles_not_plan_paid")
    # READING: donor cycles. "Number of donor artificial insemination cycles: Self paid/not
    # paid for by plan" -> only cycles not paid by the plan count; the field holds that count.

    if sex == "female" and partner_sex == "male":
        threshold = 12 if age < 35 else 6
        # READING: glossary and table cumulative. Glossary: "For a female with a male partner,
        # after: 1 year ... / 6 months of frequent, unprotected heterosexual sexual intercourse";
        # table: "A. 12 months or more or B. At least 12 cycles of donor insemination" -> both
        # must hold, so the months requirement binds unless the gender dysphoria line applies.
        glossary_months = months is not None and months >= threshold
        if not (glossary_months or gd is True):
            return False
        table_months = (months is not None and months >= threshold) or (
            cycles is not None and cycles >= threshold
        )
        if not table_months:
            return False
        return _fsh_ok(claim, service_date, birth, age, 12 if age < 35 else 6)

    if sex == "female":  # without a male partner
        threshold = 12 if age < 35 else 6
        # Glossary: "At least 12 cycles of donor insemination if under the age of 35 / 6 cycles
        # of donor insemination if age 35 or older"; the table repeats the same counts.
        meets_cycles = cycles is not None and cycles >= threshold
        # READING: gender dysphoria. "For an individual or their partner who has been clinically
        # diagnosed with gender dysphoria" -> satisfies the glossary alone, but the table row
        # for the patient still applies.
        if not meets_cycles:
            return False
        return _fsh_ok(claim, service_date, birth, age, 12 if age < 35 else 6)

    if sex == "male" and partner_sex == "female":
        if claim.get("partner_birth_date") is None:
            return False
        partner_age = _age(_parse(claim["partner_birth_date"]), service_date)
        threshold = 12 if partner_age < 35 else 6
        # READING: male with a female partner. The glossary has no line for him; table rows
        # "A male of any age with a female partner under 35 years of age: 12 months or more"
        # -> the couple is tested on the "female with a male partner" line using the female
        # partner's age; donor cycles and FSH "Does not apply".
        meets_months = months is not None and months >= threshold
        if not meets_months:
            return False
        return True

    # Male without a female partner.
    # Glossary: "At least 2 abnormal semen analyses obtained at least 2 weeks apart".
    # READING: semen analyses spacing. "obtained at least 2 weeks apart" -> any two analyses
    # dated 14 or more days apart.
    dates = claim.get("abnormal_semen_analysis_dates")
    semen_ok = False
    if dates is not None:
        parsed = sorted(_parse(d) for d in dates if d is not None)
        if len(parsed) >= 2 and (parsed[-1] - parsed[0]).days >= 14:
            semen_ok = True
    if not (semen_ok or gd is True):
        return False
    # READING: male without a female partner in the table. The table lists only "A male of any
    # age with a female partner" -> no months, donor-cycle or FSH requirement applies to him.
    return True
