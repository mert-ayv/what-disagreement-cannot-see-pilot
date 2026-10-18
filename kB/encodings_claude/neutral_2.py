"""Cardinal Care 2023-2024: comprehensive infertility services benefit (pp. 62-64).

READING choices:
1. Covered services: only "Ovulation induction cycle(s) with menotropins" and
   "Intrauterine insemination" are covered services; anything else is not.
2. Infertility specialist: "We will cover charges made by an infertility specialist"
   is read as a coverage condition, so the billing provider must be an infertility specialist.
3. Unknown facts: a missing field means the fact is unknown; since True requires every
   requirement to be met, an unknown fact that a requirement depends on yields False.
4. Age: "under 35", "35 years of age or older", "age 40 and older" are measured on the
   date of service, computed from date of birth.
5. Which female's age: for a female patient, her own age; for a male patient with a
   female partner, the partner's age ("A male of any age with a female partner under 35").
6. Male with a female partner under the glossary: the glossary lists no prong for him; he is
   read as infertile when the couple meets the "female with a male partner" prong, using
   the partner's age.
7. Female with a male partner under the glossary: the glossary requires "1 year" / "6 months"
   of "frequent, unprotected heterosexual sexual intercourse"; donor insemination cycles do not
   satisfy the glossary for her, even though the table's option B lists them.
8. "1 year" in the glossary equals 12 months; "6 cycles of donor insemination" means at least 6.
9. Donor insemination cycles counted for the table must be "Self paid/not paid for by plan";
   the glossary counts all donor insemination cycles.
10. A female "without a male partner" includes a female with no partner or a female partner;
    a male "without a female partner" includes a male with no partner or a male partner.
11. Male without a female partner: the table has no row for him, so no table requirement
    (months, cycles, FSH) applies; he must meet the glossary semen-analysis prong.
12. Abnormal semen analyses "obtained at least 2 weeks apart": at least two abnormal analyses
    whose dates differ by at least 14 days.
13. Gender dysphoria: a clinical diagnosis of the patient or partner satisfies the glossary
    definition, but the table requirements for the patient's row still apply.
14. FSH window: "done within the past: 12 months / 6 months" means at least one unmedicated
    day 3 FSH test dated on or before the service date and no more than 12 / 6 calendar months
    before it. Tests dated after the service date are ignored.
15. "most recent lab test" means the most recent unmedicated day 3 FSH test on or before the
    service date.
16. Age 40 and older: "less than 19 mIU/mL in all prior tests performed after age 40" means every
    test dated on or after the 40th birthday (and on or before service) is below 19, and at
    least one such test exists.
17. Sterilization: one field records whether patient or partner had a procedure "obtained as a
    form of voluntary sterilization", regardless of reversal; a hysterectomy or tubal ligation
    for another reason does not count.
18. The "condition" bullet requires both that it is demonstrated to cause infertility and that
    it was recognized by a physician or infertility specialist and documented in the patient's
    or partner's medical records.
19. Eligible enrollees: the patient must be the student or the student's legal spouse, civil
    union partner or domestic partner; other dependents are not eligible.
"""

from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The infertility service billed on the claim.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "billing_provider_is_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "service_date": {
        "description": "Date the service was provided.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "member_type": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "other_dependent"],
    },
    "patient_sex": {
        "description": "Sex of the patient for the infertility definition and table rows.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_date_of_birth": {
        "description": "Patient's date of birth.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_date_of_birth": {
        "description": "Partner's date of birth (needed for a male patient with a female partner).",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "A condition exists that is demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": "That condition was recognized by the physician or infertility specialist and "
                       "documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "voluntary_sterilization_patient_or_partner": {
        "description": "Patient or partner had a procedure obtained as voluntary sterilization "
                       "(tubal ligation, hysterectomy, vasectomy), with or without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Patient's or partner's infertility is due to a natural physiologic process "
                       "such as age related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_can_achieve_pregnancy": {
        "description": "A successful pregnancy can be attained through less costly treatment "
                       "for which coverage is available under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_intercourse": {
        "description": "Months of frequent, unprotected (timed) heterosexual intercourse without pregnancy.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_total": {
        "description": "Total cycles of donor insemination without pregnancy.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_not_plan_paid": {
        "description": "Cycles of donor insemination without pregnancy that were self paid / not paid by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_tests": {
        "description": "Unmedicated day 3 FSH tests of the female patient.",
        "type": "list[dict]",
        "allowed": "each item {'date': 'YYYY_MM_DD', 'value_miu_ml': float}",
    },
    "semen_analyses": {
        "description": "Semen analyses of a male patient.",
        "type": "list[dict]",
        "allowed": "each item {'date': 'YYYY_MM_DD', 'abnormal': bool}",
    },
    "gender_dysphoria_diagnosis_patient_or_partner": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
}

COVERED_SERVICES = {"ovulation_induction_menotropins", "intrauterine_insemination"}
ELIGIBLE_MEMBER_TYPES = {"student", "spouse", "civil_union_partner", "domestic_partner"}


def _parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = value.split("_")
        return date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # Feb 29 in a non-leap year
        return d.replace(year=d.year + years, month=3, day=1)


def _sub_months(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, day)
        except ValueError:
            continue
    return None


def _age_on(dob, on):
    age = on.year - dob.year
    if (on.month, on.day) < (dob.month, dob.day):
        age -= 1
    return age


def _is_bool(v):
    return isinstance(v, bool)


def _is_count(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _fsh_ok(claim, service_date, patient_dob, age, window_months):
    tests = claim.get("fsh_tests")
    if not isinstance(tests, list):
        return False
    parsed = []
    for t in tests:
        if not isinstance(t, dict):
            return False
        td = _parse_date(t.get("date"))
        val = t.get("value_miu_ml")
        if td is None or not isinstance(val, (int, float)) or isinstance(val, bool):
            return False
        if td <= service_date:  # READING: tests after the service date are ignored
            parsed.append((td, float(val)))
    if not parsed:
        return False
    # READING: FSH window. "You need to have an unmedicated day 3 FSH test done within the past:
    # 12 months / 6 months" -> a test no more than that many months before the service date.
    window_start = _sub_months(service_date, window_months)
    if window_start is None or not any(td >= window_start for td, _ in parsed):
        return False
    if age < 40:
        # READING: "Must be less than 19 mIU/mL in your most recent lab test" -> the most recent
        # unmedicated day 3 FSH test on or before the service date.
        most_recent = max(parsed, key=lambda x: x[0])
        return most_recent[1] < 19
    # READING: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests
    # performed after age 40" -> every test on or after the 40th birthday is below 19, and at
    # least one such test exists.
    fortieth = _add_years(patient_dob, 40)
    after_40 = [v for td, v in parsed if td >= fortieth]
    return bool(after_40) and all(v < 19 for v in after_40)


def _semen_prong_met(claim):
    analyses = claim.get("semen_analyses")
    if not isinstance(analyses, list):
        return False
    abnormal_dates = []
    for a in analyses:
        if not isinstance(a, dict):
            return False
        ad = _parse_date(a.get("date"))
        ab = a.get("abnormal")
        if ad is None or not _is_bool(ab):
            return False
        if ab:
            abnormal_dates.append(ad)
    # READING: "At least 2 abnormal semen analyses obtained at least 2 weeks apart" -> two
    # abnormal analyses whose dates differ by at least 14 days.
    if len(abnormal_dates) < 2:
        return False
    return (max(abnormal_dates) - min(abnormal_dates)).days >= 14


def covered_under_benefit(claim: dict) -> bool:
    # Service: "We will cover charges made by an infertility specialist for the following
    # infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine insemination"
    if claim.get("service_type") not in COVERED_SERVICES:
        return False
    # READING: "charges made by an infertility specialist" is a coverage condition.
    if claim.get("billing_provider_is_infertility_specialist") is not True:
        return False

    service_date = _parse_date(claim.get("service_date"))
    if service_date is None:
        return False

    # READING: "covered under this plan as a student or as a covered dependent who is the student's
    # legal spouse, civil union partner or domestic partner" -> other dependents are ineligible.
    if claim.get("member_type") not in ELIGIBLE_MEMBER_TYPES:
        return False

    # READING: "Is demonstrated to cause the illness of infertility" and "Has been recognized ...
    # and documented" -> both must hold.
    if claim.get("condition_demonstrated_to_cause_infertility") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False

    # READING: "This includes tubal ligation, hysterectomy and vasectomy only if obtained as a form
    # of voluntary sterilization" -> the field records only procedures obtained as sterilization.
    if claim.get("voluntary_sterilization_patient_or_partner") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("less_costly_covered_treatment_can_achieve_pregnancy") is not False:
        return False

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if sex not in ("female", "male") or partner_sex not in ("female", "male", "none"):
        return False
    patient_dob = _parse_date(claim.get("patient_date_of_birth"))
    if patient_dob is None:
        return False

    gd = claim.get("gender_dysphoria_diagnosis_patient_or_partner")
    gender_dysphoria = gd is True  # unknown or False -> this prong not shown

    months = claim.get("months_unprotected_intercourse")
    di_total = claim.get("donor_insemination_cycles_total")
    di_self = claim.get("donor_insemination_cycles_not_plan_paid")

    if sex == "female":
        # READING: "under 35" / "35 years of age or older" measured on the service date.
        age = _age_on(patient_dob, service_date)
        under_35 = age < 35
        threshold = 12 if under_35 else 6
        if partner_sex == "male":
            # READING: glossary "1 year of frequent, unprotected heterosexual sexual intercourse"
            # applies to a female with a male partner; donor cycles do not satisfy the glossary.
            glossary_met = gender_dysphoria or (_is_count(months) and months >= threshold)
            if not glossary_met:
                return False
            # Table: "A. 12 months or more or B. At least 12 cycles of donor insemination"
            # READING: option B counts only cycles "Self paid/not paid for by plan".
            table_a = _is_count(months) and months >= threshold
            table_b = _is_count(di_self) and di_self >= threshold
            if not (table_a or table_b):
                return False
        else:
            # READING: "A female without a male partner" includes no partner or a female partner.
            # READING: glossary "6 cycles of donor insemination" read as at least 6.
            glossary_met = gender_dysphoria or (_is_count(di_total) and di_total >= threshold)
            if not glossary_met:
                return False
            # Table: "At least 12 cycles of donor insemination" with "Self paid/not paid for by plan".
            if not (_is_count(di_self) and di_self >= threshold):
                return False
        # Table FSH column: "within the past: 12 months" (<35) or "6 months" (35+).
        return _fsh_ok(claim, service_date, patient_dob, age, threshold)

    # Male patient
    if partner_sex == "female":
        partner_dob = _parse_date(claim.get("partner_date_of_birth"))
        if partner_dob is None:
            return False
        # READING: "A male of any age with a female partner under 35 years of age" -> partner's age
        # on the service date decides the row.
        partner_age = _age_on(partner_dob, service_date)
        threshold = 12 if partner_age < 35 else 6
        # READING: glossary has no male-with-female-partner prong; the couple's "female with a male
        # partner" prong (intercourse months by the female's age) is applied.
        glossary_met = gender_dysphoria or (_is_count(months) and months >= threshold)
        if not glossary_met:
            return False
        # Table: "12 months or more" / "6 months or more"; FSH and donor cycles "Does not apply".
        return _is_count(months) and months >= threshold

    # READING: "For a male without a female partner, after: At least 2 abnormal semen analyses" and
    # the table has no row for him -> only the glossary prong applies.
    return gender_dysphoria or _semen_prong_met(claim)
