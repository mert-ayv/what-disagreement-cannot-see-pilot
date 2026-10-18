"""Cardinal Care 2023-2024: comprehensive infertility services benefit (member-favourable encoding).

READING choices (each is marked "# READING:" at the point where it is applied):

R1  Covered services: only "Ovulation induction cycle(s) with menotropins" and "Intrauterine insemination",
    billed by an infertility specialist. IUI is covered with or without ovulation induction.
R2  Member status: "covered under this plan as a student or as a covered dependent who is the student's legal
    spouse, civil union partner or domestic partner" covers those four statuses and no others.
R3  Negative eligibility bullets ("has not had a voluntary sterilization", "does not have infertility that is due
    to a natural physiologic process", "cannot be attained through less costly treatment") fail only when the
    disqualifying fact is shown; an unknown fact does not defeat coverage.
R4  Sterilization bars only when "obtained as a form of voluntary sterilization"; a medically required
    hysterectomy or similar procedure does not bar.
R5  Ages are measured on the date of service (the latest relevant date, at which lower thresholds apply).
R6  Female with a male partner: infertility under the glossary may rest either on the months of intercourse or on
    the donor insemination cycles that the table accepts as alternative B for the same person.
R7  Male with a female partner: the glossary has no male-with-female-partner bullet, so the male is infertile when
    the couple meets the failure-to-conceive test that the glossary sets "for a female with a male partner",
    keyed to the female partner's age, as the table's male rows do.
R8  Donor insemination cycles count regardless of who paid; "Self paid/not paid for by plan" describes the
    cycles and does not exclude any.
R9  Where no table row fits the patient (e.g. a male without a female partner), the table imposes no months,
    cycles or FSH requirement; the glossary alone decides infertility.
R10 "Frequent" (glossary) and "timed" (table) intercourse are not separate tests; the count of months of
    unprotected heterosexual intercourse without pregnancy is the fact used.
R11 "within the past: 12 months / 6 months" is measured back from the date of service or, if given, from the date
    the provider requested advance approval, whichever lets the test qualify; the window is inclusive.
R12 Only tests known to be unmedicated day 3 FSH tests count for the FSH criteria.
R13 Age 40 and older: the text requires "less than 19 mIU/mL in all prior tests performed after age 40" and says
    nothing about the most recent test; if no such test exists the condition is met.  "after age 40" means tests
    dated after the 40th birthday.
R14 The 6-month cycle and FSH rows apply at "35 years of age or older"; the 12-month rows apply under 35.
R15 Semen analyses "at least 2 weeks apart" means 14 or more days between the two test dates.
R16 Gender dysphoria makes the patient infertile under the glossary, but the table requirements still apply when
    a table row fits the patient.
"""

from datetime import date

SCHEMA = {
    "service_type": {
        "description": "Infertility service billed on the claim.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "billed_by_infertility_specialist": {
        "description": "The charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "member_status": {
        "description": "How the patient is covered under this plan.",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "other_dependent", "not_covered"],
    },
    "service_date": {
        "description": "Date the service was rendered.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "approval_request_date": {
        "description": "Date the provider requested advance approval (optional).",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Sex of the patient as used by the table and glossary.",
        "type": "str",
        "allowed": ["female", "male", "other"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if the patient has no partner.",
        "type": "str",
        "allowed": ["female", "male", "other", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's date of birth (needed for a male patient with a female partner).",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "infertility_condition_documented": {
        "description": "A condition demonstrated to cause infertility has been recognized by the patient's physician or "
                       "infertility specialist and documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": "Patient has had a procedure obtained as a form of voluntary sterilization (with or without "
                       "reversal).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Partner has had a procedure obtained as a form of voluntary sterilization (with or without "
                       "reversal).",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_infertility_natural_process": {
        "description": "Patient's infertility is due to a natural physiologic process such as age related ovarian "
                       "insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_infertility_natural_process": {
        "description": "Partner's infertility is due to a natural physiologic process.",
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_could_succeed": {
        "description": "A successful pregnancy can be attained through less costly treatment covered under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_intercourse": {
        "description": "Months of unprotected (frequent/timed) heterosexual intercourse without achieving pregnancy.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles": {
        "description": "Number of donor artificial insemination cycles without achieving pregnancy, however paid.",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_tests": {
        "description": "Day 3 FSH tests of the patient.",
        "type": "list[dict]",
        "format": "each item {'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated_day3': bool}",
    },
    "semen_analyses": {
        "description": "Semen analyses of the patient.",
        "type": "list[dict]",
        "format": "each item {'date': 'YYYY_MM_DD', 'abnormal': bool}",
    },
    "patient_gender_dysphoria_diagnosis": {
        "description": "Patient has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_gender_dysphoria_diagnosis": {
        "description": "Partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
}


def _parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = value.split("_")
        return date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _age_on(birth, on):
    if birth is None or on is None:
        return None
    years = on.year - birth.year
    if (on.month, on.day) < (birth.month, birth.day):
        years -= 1
    return years


def _add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 February
        return d.replace(year=d.year + years, day=28)


def _months_before(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    # Clamp to the month's last day, which gives the wider (earlier-starting) window.
    for day in (d.day, 31, 30, 29, 28):
        if day <= d.day:
            try:
                return date(y, m, day)
            except ValueError:
                continue
    return date(y, m, 28)


def _int_or_none(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _num_or_none(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _qualifying_fsh_tests(claim):
    tests = claim.get("fsh_tests")
    if not isinstance(tests, list):
        return []
    out = []
    for t in tests:
        if not isinstance(t, dict):
            continue
        # READING: R12, "Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level"; only tests known to be
        # unmedicated day 3 tests count, and an undated test cannot be placed in time.
        if t.get("unmedicated_day3") is not True:
            continue
        d = _parse_date(t.get("date"))
        if d is None:
            continue
        out.append((d, _num_or_none(t.get("value_miu_ml"))))
    out.sort(key=lambda x: x[0])
    return out


def _fsh_ok(claim, window_months, birth, age, ref_dates):
    tests = _qualifying_fsh_tests(claim)
    for ref in ref_dates:
        prior = [(d, v) for d, v in tests if d <= ref]
        # READING: R11, "You need to have an unmedicated day 3 FSH test done within the past: 12 months / 6 months";
        # measured back from the service date or the advance-approval request date, inclusive.
        start = _months_before(ref, window_months)
        if not any(start <= d <= ref for d, _ in prior):
            continue
        if age < 40:
            most_recent_value = prior[-1][1]
            if most_recent_value is not None and most_recent_value < 19:
                return True
        else:
            # READING: R13, "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed
            # after age 40"; only tests dated after the 40th birthday are checked, and none existing satisfies it.
            fortieth = _add_years(birth, 40)
            after_40 = [v for d, v in prior if d > fortieth]
            if all(v is not None and v < 19 for v in after_40):
                return True
    return False


def _semen_test_met(claim):
    analyses = claim.get("semen_analyses")
    if not isinstance(analyses, list):
        return False
    dates = sorted(
        d for d in (
            _parse_date(a.get("date")) for a in analyses
            if isinstance(a, dict) and a.get("abnormal") is True
        ) if d is not None
    )
    # READING: R15, "At least 2 abnormal semen analyses obtained at least 2 weeks apart"; 14 or more days between
    # the earliest and latest abnormal analyses.
    return len(dates) >= 2 and (dates[-1] - dates[0]).days >= 14


def covered_under_benefit(claim: dict) -> bool:
    # --- Covered service -------------------------------------------------------------------------------------
    # READING: R1, "We will cover charges made by an infertility specialist for the following infertility services:
    # Ovulation induction cycle(s) with menotropins; Intrauterine insemination"; only these two, billed by an
    # infertility specialist; IUI is covered with or without ovulation induction.
    if claim.get("service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
        return False
    if claim.get("billed_by_infertility_specialist") is not True:
        return False

    # --- Member status ---------------------------------------------------------------------------------------
    # READING: R2, "covered under this plan as a student or as a covered dependent who is the student's legal spouse,
    # civil union partner or domestic partner".
    if claim.get("member_status") not in ("student", "spouse", "civil_union_partner", "domestic_partner"):
        return False

    # --- Documented condition --------------------------------------------------------------------------------
    if claim.get("infertility_condition_documented") is not True:
        return False

    # --- Negative bullets ------------------------------------------------------------------------------------
    # READING: R3, "has not had a voluntary sterilization", "does not have infertility that is due to a natural
    # physiologic process", "cannot be attained through less costly treatment"; each bars only when the
    # disqualifying fact is shown to be true.
    # READING: R4, "tubal ligation, hysterectomy and vasectomy only if obtained as a form of voluntary
    # sterilization"; the sterilization fields record only procedures obtained as voluntary sterilization.
    for field in (
        "patient_voluntary_sterilization",
        "partner_voluntary_sterilization",
        "patient_infertility_natural_process",
        "partner_infertility_natural_process",
        "less_costly_covered_treatment_could_succeed",
    ):
        if claim.get(field) is True:
            return False

    # --- Ages ------------------------------------------------------------------------------------------------
    service = _parse_date(claim.get("service_date"))
    if service is None:
        return False
    birth = _parse_date(claim.get("patient_birth_date"))
    # READING: R5, "A female under 35 years of age" / "35 years of age or older"; age on the date of service.
    age = _age_on(birth, service)
    partner_birth = _parse_date(claim.get("partner_birth_date"))
    partner_age = _age_on(partner_birth, service)

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if sex not in ("female", "male", "other") or partner_sex not in ("female", "male", "other", "none"):
        return False

    months = _int_or_none(claim.get("months_unprotected_intercourse"))
    # READING: R8, "Number of donor artificial insemination cycles: Self paid/not paid for by plan"; all donor
    # insemination cycles count, however paid.
    di_cycles = _int_or_none(claim.get("donor_insemination_cycles"))
    # READING: R10, "frequent, unprotected heterosexual sexual intercourse" / "unprotected timed sexual
    # intercourse"; one count of months of unprotected intercourse without pregnancy, no separate frequency test.

    ref_dates = [service]
    approval = _parse_date(claim.get("approval_request_date"))
    if approval is not None and approval <= service:
        ref_dates.insert(0, approval)

    gender_dysphoria = (
        claim.get("patient_gender_dysphoria_diagnosis") is True
        or claim.get("partner_gender_dysphoria_diagnosis") is True
    )

    # --- Table rows and glossary -----------------------------------------------------------------------------
    # READING: R16, "For an individual or their partner who has been clinically diagnosed with gender dysphoria";
    # this satisfies the glossary, but a fitting table row still applies.
    if sex == "female":
        if age is None or birth is None:
            return False
        # READING: R14, "under 35 years of age" vs "35 years of age or older".
        threshold = 12 if age < 35 else 6
        if partner_sex == "male":
            # READING: R6, "A. 12 months or more or B. At least 12 cycles of donor insemination"; the table's
            # alternative B also establishes glossary infertility for this person.
            trying_met = (months is not None and months >= threshold) or (
                di_cycles is not None and di_cycles >= threshold
            )
        else:
            trying_met = di_cycles is not None and di_cycles >= threshold
        # Glossary infertility for a female is the same failure-to-conceive test (or gender dysphoria), so the
        # table requirement implies it.
        if not trying_met:
            return False
        return _fsh_ok(claim, threshold, birth, age, ref_dates)

    if sex == "male" and partner_sex == "female":
        if partner_age is None:
            return False
        threshold = 12 if partner_age < 35 else 6
        # READING: R7, "For a female with a male partner, after: 1 year ... if under the age of 35 / 6 months ... if
        # age 35 or older" read with the table rows "A male of any age with a female partner under 35 / 35 years of
        # age or older"; the male is infertile when the couple meets this test, keyed to the partner's age.
        return months is not None and months >= threshold

    # READING: R9, the table has rows only for females and for "A male of any age with a female partner"; where no
    # row fits, no months, cycles or FSH requirement applies and the glossary alone decides.
    if sex == "male" and partner_sex != "female":
        return _semen_test_met(claim) or gender_dysphoria
    return gender_dysphoria
