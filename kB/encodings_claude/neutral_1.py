"""Cardinal Care 2023-2024: comprehensive infertility services benefit (pp. 62-64).

READING choices made in this encoding:
R1  Covered services: only "Ovulation induction cycle(s) with menotropins" and
    "Intrauterine insemination" are covered services under this benefit.
R2  Billing provider: "charges made by an infertility specialist" is read as a
    coverage condition of this benefit, so the service must be rendered by an
    infertility specialist.
R3  Eligible member: the patient must be the student or the student's spouse,
    civil union partner or domestic partner; other dependents are not eligible.
R4  "Your partner" / "male partner" / "female partner": read as the patient's
    current partner as reported in the claim; a female whose partner is female
    (or who has no partner) is "without a male partner".
R5  Age reference date: all ages ("under 35", "35 or older", "less than age 40")
    are measured on the date of service.
R6  Negative eligibility facts (sterilization, natural physiologic process,
    less costly treatment) must be affirmatively known to be absent; an unknown
    value means the requirement is not shown to be met.
R7  Male with a female partner: the glossary has no male-with-female-partner
    prong, so such a male is read as infertile when the couple meets the
    female-with-male-partner prong, using the female partner's age.
R8  Female with a male partner, glossary versus table option B: the glossary
    defines infertility for this group only by months of intercourse, and the
    task requires glossary infertility, so donor insemination cycles alone do
    not make her infertile (unless the gender dysphoria prong applies).
R9  Gender dysphoria: this prong satisfies only the glossary definition; the
    table row matching the patient's sex and partner status still applies.
R10 Male without a female partner: the table has no row for this group, so no
    table requirement (months, cycles or FSH) applies to him.
R11 "Self paid/not paid for by plan": only donor insemination cycles not paid
    for by this plan count toward the table's cycle requirement; the glossary
    cycle count includes all donor insemination cycles.
R12 "Frequent, unprotected heterosexual sexual intercourse" (glossary) and
    "unprotected timed sexual intercourse" (table) are counted with one
    month field, measured without a resulting pregnancy.
R13 FSH test window: "done within the past" 12 or 6 months is measured back from
    the date of service, inclusive, and applies to the most recent test.
R14 FSH, age 40 and older: the most recent test must be under 19 mIU/mL and,
    in addition, every test performed on or after the 40th birthday must be
    under 19 mIU/mL.
R15 FSH applies only to a female patient; for male rows the table says
    "Does not apply".
R16 Abnormal semen analyses "at least 2 weeks apart": at least two analyses
    whose dates differ by 14 days or more.
"""

import calendar
import datetime

SCHEMA = {
    "service_type": {
        "description": "The infertility service billed on the claim.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "rendering_provider_is_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_coverage_status": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner",
                    "other_dependent", "not_covered"],
    },
    "patient_sex": {
        "description": "Patient's sex as used in the policy table (female or male).",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if the patient has no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "partner_birth_date": {
        "description": "Partner's date of birth (needed when a male patient has a female partner).",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "service_date": {
        "description": "Date the infertility service is rendered.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "infertility_condition_demonstrated": {
        "description": "A condition exists that is demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": "The condition has been recognized by the physician or infertility "
                       "specialist and documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "voluntary_sterilization_patient_or_partner": {
        "description": "Patient or partner has had a voluntary sterilization (tubal ligation, "
                       "hysterectomy or vasectomy obtained as voluntary sterilization), with or "
                       "without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Patient's or partner's infertility is due to a natural physiologic process "
                       "such as age related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through less costly treatment for "
                       "which coverage is available under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "gender_dysphoria_diagnosis_patient_or_partner": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_intercourse_without_pregnancy": {
        "description": "Months of frequent/timed unprotected heterosexual intercourse with the "
                       "partner without achieving pregnancy.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_without_pregnancy": {
        "description": "Total donor (artificial) insemination cycles without achieving pregnancy, "
                       "regardless of who paid.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_not_plan_paid_without_pregnancy": {
        "description": "Donor (artificial) insemination cycles without pregnancy that were self "
                       "paid or otherwise not paid for by this plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of the patient's abnormal semen analyses.",
        "type": "list[str]",
        "allowed": "list of YYYY_MM_DD",
    },
    "fsh_tests": {
        "description": "The patient's unmedicated day 3 FSH tests.",
        "type": "list[dict]",
        "allowed": "list of {'date': 'YYYY_MM_DD', 'value_miu_per_ml': float}",
    },
}

COVERED_SERVICES = {"ovulation_induction_menotropins", "intrauterine_insemination"}
ELIGIBLE_COVERAGE = {"student", "spouse", "civil_union_partner", "domestic_partner"}
FSH_LIMIT = 19.0


def _parse_date(value):
    if not isinstance(value, str):
        return None
    parts = value.split("_")
    if len(parts) != 3:
        return None
    try:
        return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _age_on(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _minus_months(d, months):
    total = d.year * 12 + (d.month - 1) - months
    year, month0 = divmod(total, 12)
    month = month0 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _at_least(value, threshold):
    n = _number(value)
    return n is not None and n >= threshold


def _female_age_bracket_threshold(female_age):
    # 12 months / 12 cycles under 35; 6 months / 6 cycles at 35 or older.
    return 12 if female_age < 35 else 6


def _is_infertile(claim, sex, has_partner_of_other_sex, patient_age, partner_age):
    if claim.get("gender_dysphoria_diagnosis_patient_or_partner") is True:
        # READING: gender dysphoria prong; "For an individual or their partner who has been
        # clinically diagnosed with gender dysphoria" satisfies the glossary by itself; the
        # table still applies (see R9).
        return True

    months = claim.get("months_unprotected_intercourse_without_pregnancy")

    if sex == "female" and has_partner_of_other_sex:
        # READING: glossary versus table option B; the glossary says "For a female with a
        # male partner, after: 1 year ... / 6 months of frequent, unprotected heterosexual
        # sexual intercourse"; donor insemination cycles do not satisfy this prong.
        return _at_least(months, _female_age_bracket_threshold(patient_age))

    if sex == "female":
        # READING: "At least 12 cycles of donor insemination if under the age of 35 / 6 cycles
        # of donor insemination if age 35 or older"; all cycles count here, whoever paid.
        return _at_least(claim.get("donor_insemination_cycles_without_pregnancy"),
                         _female_age_bracket_threshold(patient_age))

    if has_partner_of_other_sex:
        # READING: male with a female partner; the glossary lists only "For a female with a
        # male partner"; the male is read as infertile when the couple meets that prong,
        # using the female partner's age.
        if partner_age is None:
            return False
        return _at_least(months, _female_age_bracket_threshold(partner_age))

    # Male without a female partner.
    # READING: "At least 2 abnormal semen analyses obtained at least 2 weeks apart" means
    # two analyses whose dates differ by 14 days or more.
    raw = claim.get("abnormal_semen_analysis_dates")
    if not isinstance(raw, list):
        return False
    dates = [_parse_date(x) for x in raw]
    if any(d is None for d in dates):
        return False
    dates.sort()
    return len(dates) >= 2 and (dates[-1] - dates[0]).days >= 14


def _fsh_met(claim, patient_birth, patient_age, service_date):
    raw = claim.get("fsh_tests")
    if not isinstance(raw, list):
        return False
    tests = []
    for entry in raw:
        if not isinstance(entry, dict):
            return False
        d = _parse_date(entry.get("date"))
        v = _number(entry.get("value_miu_per_ml"))
        if d is None or v is None:
            return False
        if d <= service_date:
            tests.append((d, v))
    if not tests:
        return False

    # READING: test window; "You need to have an unmedicated day 3 FSH test done within the
    # past: 12 months / 6 months" is measured back from the date of service, inclusive.
    window = 12 if patient_age < 35 else 6
    most_recent_date, most_recent_value = max(tests, key=lambda t: t[0])
    if most_recent_date < _minus_months(service_date, window):
        return False

    # "Must be less than 19 mIU/mL in your most recent lab test".
    if not most_recent_value < FSH_LIMIT:
        return False

    if patient_age >= 40:
        # READING: age 40 and older; "must be less than 19 mIU/mL in all prior tests performed
        # after age 40" is applied to every test on or after the 40th birthday, in addition
        # to the most recent test.
        for d, v in tests:
            if _age_on(patient_birth, d) >= 40 and not v < FSH_LIMIT:
                return False
    return True


def _table_met(claim, sex, has_partner_of_other_sex, patient_age, partner_age,
               patient_birth, service_date):
    months = claim.get("months_unprotected_intercourse_without_pregnancy")
    # READING: donor cycle column; "Number of donor artificial insemination cycles: Self
    # paid/not paid for by plan" counts only cycles not paid for by this plan.
    plan_unpaid_cycles = claim.get("donor_insemination_cycles_not_plan_paid_without_pregnancy")

    if sex == "female":
        threshold = _female_age_bracket_threshold(patient_age)
        if has_partner_of_other_sex:
            # "A. 12 months or more or B. At least 12 cycles of donor insemination"
            # (6 / 6 at age 35 or older).
            trying_met = (_at_least(months, threshold)
                          or _at_least(plan_unpaid_cycles, threshold))
        else:
            # Months column "Does not apply"; "At least 12 cycles" / "At least 6 cycles".
            trying_met = _at_least(plan_unpaid_cycles, threshold)
        if not trying_met:
            return False
        return _fsh_met(claim, patient_birth, patient_age, service_date)

    if has_partner_of_other_sex:
        # READING: FSH for males; the male rows read "Does not apply" for cycles, FSH window
        # and FSH result, so only the months requirement is checked.
        if partner_age is None:
            return False
        return _at_least(months, _female_age_bracket_threshold(partner_age))

    # READING: male without a female partner; the table has rows only for "A male of any age
    # with a female partner", so no table requirement applies to him.
    return True


def covered_under_benefit(claim: dict) -> bool:
    # READING: covered services; "We will cover charges made by an infertility specialist for
    # the following infertility services: Ovulation induction cycle(s) with menotropins,
    # Intrauterine insemination"; only these two services are covered.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    # READING: provider; "charges made by an infertility specialist" is a coverage condition
    # of this benefit, not a network rule.
    if claim.get("rendering_provider_is_infertility_specialist") is not True:
        return False

    # "covered under this plan as a student or as a covered dependent who is the student's
    # legal spouse, civil union partner or domestic partner".
    if claim.get("patient_coverage_status") not in ELIGIBLE_COVERAGE:
        return False

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if sex not in ("female", "male") or partner_sex not in ("female", "male", "none"):
        return False
    # READING: partner status; "with a male partner" / "without a male partner" refers to the
    # patient's current partner; a same-sex partner or no partner counts as "without".
    has_partner_of_other_sex = (
        (sex == "female" and partner_sex == "male")
        or (sex == "male" and partner_sex == "female")
    )

    service_date = _parse_date(claim.get("service_date"))
    patient_birth = _parse_date(claim.get("patient_birth_date"))
    if service_date is None or patient_birth is None:
        return False
    # READING: age date; "A female under 35 years of age", "If you are less than age 40":
    # ages are measured on the date of service.
    patient_age = _age_on(patient_birth, service_date)
    partner_birth = _parse_date(claim.get("partner_birth_date"))
    partner_age = _age_on(partner_birth, service_date) if partner_birth else None

    # "There exists a condition that: Is demonstrated to cause the illness of infertility.
    # Has been recognized by your physician or infertility specialist and documented".
    if claim.get("infertility_condition_demonstrated") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False

    # READING: unknown negatives; "has not had a voluntary sterilization", "does not have
    # infertility that is due to a natural physiologic process", "cannot be attained through
    # less costly treatment" must be known to hold; a missing value fails the requirement.
    if claim.get("voluntary_sterilization_patient_or_partner") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    # READING: intercourse months; glossary "frequent, unprotected heterosexual sexual
    # intercourse" and table "unprotected timed sexual intercourse" use one month count.
    if not _is_infertile(claim, sex, has_partner_of_other_sex, patient_age, partner_age):
        return False

    # "You have met the requirement for the number of months trying to conceive" and
    # "Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following
    # criteria" (table).
    if not _table_met(claim, sex, has_partner_of_other_sex, patient_age, partner_age,
                      patient_birth, service_date):
        return False

    return True
