"""Cardinal Care 2023-2024: comprehensive infertility services benefit (insurer-favourable encoding).

READING choices (each is marked "# READING:" in the code):
 1. Covered services: only "ovulation induction cycle(s) with menotropins" and "intrauterine
    insemination"; ovulation induction with other drugs is not a covered service.
 2. Billing provider: the charge must be "made by an infertility specialist".
 3. Coverage role: only the student, or a covered dependent who is the student's legal spouse,
    civil union partner or domestic partner; any other dependent is ineligible.
 4. Causal condition: "a condition that is demonstrated to cause the illness of infertility" requires a
    specific identified causal condition; unexplained infertility does not qualify.
 5. "You or your partner has not had a voluntary sterilization": read as neither the patient nor the
    partner may have had one.
 6. "You or your partner does not have infertility that is due to a natural physiologic process":
    read as neither may have it, and "due to" includes partly due to.
 7. "Partner" in the exclusions and the table means the person the patient is trying to conceive with,
    whether or not that person is covered under the plan.
 8. Age: "You are a female under 35 ..." is evaluated at the date of the service claimed.
 9. Glossary for a female with a male partner requires months of "frequent, unprotected heterosexual
    sexual intercourse"; table option B (donor insemination) does not satisfy the glossary for her
    unless the gender dysphoria bullet applies.
10. Table months require "unprotected timed sexual intercourse"; glossary months require "frequent"
    intercourse; both qualities must hold for the counted months.
11. Donor insemination cycles count only if "Self paid/not paid for by plan".
12. A male patient with a female partner is infertile under the glossary when the couple meets the
    "female with a male partner" bullet, judged by the female partner's age.
13. A male without a female partner has no row in the table, so the table requirement cannot be met
    and the claim is not covered.
14. "Failure to become pregnant" is not shown if a pregnancy occurred during the counted period; the
    gender dysphoria bullet still requires failure to become pregnant but no minimum period.
15. Gender dysphoria satisfies only the glossary; every eligibility bullet and the table still apply.
16. FSH "within the past" N months is measured back from the service date, boundary excluded.
17. FSH "most recent lab test": both the most recent unmedicated day 3 FSH test and the most recent
    FSH test of any kind must be below 19 mIU/mL.
18. Age 40 and older: "after age 40" includes tests on or after the 40th birthday, covers FSH tests of
    any kind, and at least one such test must exist.
19. "Less costly treatment": coverage requires an affirmative finding that pregnancy cannot be attained
    through less costly covered treatment.
"""

import datetime

SCHEMA = {
    "service_type": {
        "description": "The service claimed.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "ovulation_induction_other_drug",
                    "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "service_date": {
        "description": "Date of the service claimed.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "coverage_role": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "dependent_legal_spouse", "dependent_civil_union_partner",
                    "dependent_domestic_partner", "dependent_other"],
    },
    "patient_sex": {
        "description": "Sex of the patient as used in the table.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the partner the patient is trying to conceive with; 'none' if no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's date of birth (needed for a male patient with a female partner).",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "gender_dysphoria_diagnosis": {
        "description": "Whether the patient or the partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_intercourse": {
        "description": "Number of months of unprotected sexual intercourse with the male/female partner while trying to conceive.",
        "type": "int",
        "allowed": ">= 0",
    },
    "intercourse_timed": {
        "description": "Whether the counted intercourse was timed.",
        "type": "bool",
        "allowed": [True, False],
    },
    "intercourse_frequent": {
        "description": "Whether the counted intercourse was frequent.",
        "type": "bool",
        "allowed": [True, False],
    },
    "donor_insemination_cycles_self_paid": {
        "description": "Number of donor artificial insemination cycles self paid / not paid for by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "pregnancy_during_counted_period": {
        "description": "Whether a pregnancy occurred during the counted months or cycles.",
        "type": "bool",
        "allowed": [True, False],
    },
    "causal_condition_demonstrated": {
        "description": "Whether a specific condition exists that is demonstrated to cause infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_physician_or_specialist": {
        "description": "Whether that condition has been recognized by the patient's physician or infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_medical_records": {
        "description": "Whether that condition is documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": "Whether the patient has had a voluntary sterilization (with or without reversal), including tubal ligation, hysterectomy or vasectomy obtained as voluntary sterilization.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Whether the partner has had a voluntary sterilization (with or without reversal).",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_infertility_due_to_natural_physiologic_process": {
        "description": "Whether the patient's infertility is wholly or partly due to a natural physiologic process (e.g. age related ovarian insufficiency, perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_infertility_due_to_natural_physiologic_process": {
        "description": "Whether the partner's infertility is wholly or partly due to a natural physiologic process.",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_not_attainable_by_less_costly_covered_treatment": {
        "description": "Whether it is established that a successful pregnancy cannot be attained through less costly treatment covered under the plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "fsh_tests": {
        "description": "All FSH lab tests of the female patient.",
        "type": "list[dict]",
        "allowed": "each item {'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated': bool, 'cycle_day': int}",
    },
}

FSH_LIMIT = 19.0


def _date(s):
    if not isinstance(s, str):
        return None
    try:
        y, m, d = s.split("_")
        return datetime.date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _minus_months(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    for day in (d.day, 30, 29, 28):
        try:
            return datetime.date(y, m, day)
        except ValueError:
            continue
    return None


def _is_true(claim, key):
    return claim.get(key) is True


def _is_false(claim, key):
    return claim.get(key) is False


def _int(claim, key):
    v = claim.get(key)
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v


def _intercourse_months_table(claim, required):
    # READING: "months of unprotected timed sexual intercourse" - the table counts only timed intercourse.
    months = _int(claim, "months_unprotected_intercourse")
    return months is not None and months >= required and _is_true(claim, "intercourse_timed")


def _intercourse_months_glossary(claim, required):
    # READING: glossary "frequent, unprotected heterosexual sexual intercourse" - counted months must
    # also be frequent; both "timed" (table) and "frequent" (glossary) must hold.
    months = _int(claim, "months_unprotected_intercourse")
    return (months is not None and months >= required
            and _is_true(claim, "intercourse_frequent")
            and _is_true(claim, "intercourse_timed"))


def _di_cycles(claim, required):
    # READING: column "Number of donor artificial insemination cycles: Self paid/not paid for by plan" -
    # only cycles not paid for by the plan are counted, for both the table and the glossary.
    cycles = _int(claim, "donor_insemination_cycles_self_paid")
    return cycles is not None and cycles >= required


def _fsh_ok(claim, service_date, age):
    tests = claim.get("fsh_tests")
    if not isinstance(tests, list) or not tests:
        return False
    parsed = []
    for t in tests:
        if not isinstance(t, dict):
            return False
        d = _date(t.get("date"))
        v = t.get("value_miu_ml")
        if d is None or isinstance(v, bool) or not isinstance(v, (int, float)):
            return False
        if d > service_date:
            continue
        parsed.append((d, float(v), t.get("unmedicated") is True and t.get("cycle_day") == 3))
    if not parsed:
        return False

    window = 12 if age < 35 else 6
    # READING: "You need to have an unmedicated day 3 FSH test done within the past: 12 months / 6 months" -
    # measured back from the service date; a test exactly on the boundary date is outside the window.
    cutoff = _minus_months(service_date, window)
    if cutoff is None:
        return False
    qualifying = [p for p in parsed if p[2] and p[0] > cutoff]
    if not qualifying:
        return False

    if age < 40:
        # READING: "Must be less than 19 mIU/mL in your most recent lab test" - both the most recent
        # unmedicated day 3 FSH test and the most recent FSH test of any kind must be below 19.
        latest_day3 = max(p[0] for p in parsed if p[2])
        if any(p[1] >= FSH_LIMIT for p in parsed if p[2] and p[0] == latest_day3):
            return False
        latest_any = max(p[0] for p in parsed)
        if any(p[1] >= FSH_LIMIT for p in parsed if p[0] == latest_any):
            return False
        return True

    # READING: "must be less than 19 mIU/mL in all prior tests performed after age 40" - "after age 40"
    # includes tests on or after the 40th birthday, covers FSH tests of any kind, and at least one such
    # test must exist (the requirement is not met vacuously).
    birth = _date(claim.get("patient_birth_date"))
    try:
        fortieth = birth.replace(year=birth.year + 40)
    except ValueError:
        fortieth = datetime.date(birth.year + 40, 3, 1)
    after_40 = [p for p in parsed if p[0] >= fortieth]
    if not after_40:
        return False
    return all(p[1] < FSH_LIMIT for p in after_40)


def covered_under_benefit(claim: dict) -> bool:
    # --- Covered service ---
    # READING: "Ovulation induction cycle(s) with menotropins" and "Intrauterine insemination" are the only
    # covered services; ovulation induction with any other drug is not a covered service.
    if claim.get("service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
        return False
    # READING: "We will cover charges made by an infertility specialist" - the charge must be made by an
    # infertility specialist.
    if not _is_true(claim, "provider_is_infertility_specialist"):
        return False

    service_date = _date(claim.get("service_date"))
    birth = _date(claim.get("patient_birth_date"))
    if service_date is None or birth is None:
        return False
    # READING: "You are a female under 35 years of age ..." - age is evaluated on the date of the service.
    age = _age(birth, service_date)

    # --- Eligibility bullets ---
    # READING: "covered under this plan as a student or as a covered dependent who is the student's legal
    # spouse, civil union partner or domestic partner" - any other dependent is ineligible.
    if claim.get("coverage_role") not in ("student", "dependent_legal_spouse",
                                          "dependent_civil_union_partner", "dependent_domestic_partner"):
        return False

    # READING: "There exists a condition that: Is demonstrated to cause the illness of infertility" - a
    # specific identified causal condition is required; unexplained infertility does not qualify.
    if not (_is_true(claim, "causal_condition_demonstrated")
            and _is_true(claim, "condition_recognized_by_physician_or_specialist")
            and _is_true(claim, "condition_documented_in_medical_records")):
        return False

    # READING: "You or your partner has not had a voluntary sterilization" - neither the patient nor the
    # partner may have had one. "Partner" means the person the patient is trying to conceive with, covered
    # under the plan or not.
    partner_sex = claim.get("partner_sex")
    if partner_sex not in ("female", "male", "none"):
        return False
    if not _is_false(claim, "patient_voluntary_sterilization"):
        return False
    if partner_sex != "none" and not _is_false(claim, "partner_voluntary_sterilization"):
        return False

    # READING: "You or your partner does not have infertility that is due to a natural physiologic process" -
    # neither may have it, and "due to" includes infertility partly due to such a process.
    if not _is_false(claim, "patient_infertility_due_to_natural_physiologic_process"):
        return False
    if partner_sex != "none" and not _is_false(claim, "partner_infertility_due_to_natural_physiologic_process"):
        return False

    # READING: "A successful pregnancy cannot be attained through less costly treatment for which coverage is
    # available" - this must be affirmatively established.
    if not _is_true(claim, "pregnancy_not_attainable_by_less_costly_covered_treatment"):
        return False

    # READING: "A disease defined by the failure to become pregnant" - a pregnancy during the counted period
    # means failure is not shown; this applies to every glossary bullet, including gender dysphoria.
    if not _is_false(claim, "pregnancy_during_counted_period"):
        return False
    # READING: "For an individual or their partner who has been clinically diagnosed with gender dysphoria" -
    # satisfies only the glossary; the eligibility bullets and the table still apply.
    gd = _is_true(claim, "gender_dysphoria_diagnosis")

    sex = claim.get("patient_sex")
    if sex == "female":
        required = 12 if age < 35 else 6
        if partner_sex == "male":
            # Table: "A. 12/6 months or more or B. At least 12/6 cycles of donor insemination".
            table_ok = _intercourse_months_table(claim, required) or _di_cycles(claim, required)
            # READING: glossary "For a female with a male partner, after: 1 year / 6 months of frequent,
            # unprotected heterosexual sexual intercourse" - donor insemination (table option B) does not
            # make her infertile under the glossary unless the gender dysphoria bullet applies.
            glossary_ok = gd or _intercourse_months_glossary(claim, required)
        else:
            # Table: "Does not apply" for intercourse; "At least 12/6 cycles of donor insemination".
            table_ok = _di_cycles(claim, required)
            # Glossary: "At least 12 cycles ... if under the age of 35 / 6 cycles ... if age 35 or older".
            glossary_ok = gd or _di_cycles(claim, required)
        if not (table_ok and glossary_ok):
            return False
        # "Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following criteria".
        return _fsh_ok(claim, service_date, age)

    if sex == "male":
        if partner_sex != "female":
            # READING: the table has rows only for "A male of any age with a female partner"; a male without
            # a female partner cannot meet "the requirement for the number of months trying to conceive".
            return False
        partner_birth = _date(claim.get("partner_birth_date"))
        if partner_birth is None:
            return False
        partner_age = _age(partner_birth, service_date)
        required = 12 if partner_age < 35 else 6
        table_ok = _intercourse_months_table(claim, required)
        # READING: the glossary has no bullet for a male with a female partner; he is infertile when the
        # couple meets "For a female with a male partner", judged by the female partner's age.
        glossary_ok = gd or _intercourse_months_glossary(claim, required)
        # FSH criteria: "Does not apply" for male rows.
        return table_ok and glossary_ok

    return False
