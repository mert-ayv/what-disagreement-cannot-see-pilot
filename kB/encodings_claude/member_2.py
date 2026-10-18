"""Cardinal Care 2023-2024, comprehensive infertility services benefit (member-favourable encoding).

READING choices (each marked "# READING:" in the code):
 1. Covered services: only "Ovulation induction cycle(s) with menotropins" and "Intrauterine insemination"
    are covered, but any charge for a service furnished within such a cycle (monitoring, labs, drugs) is a
    charge "for" that cycle, because a cycle "begins with the initiation of therapy and ends when ...".
 2. "charges made by an infertility specialist": a positive condition of the cover that must be shown.
 3. "a condition that ... Is demonstrated to cause the illness of infertility": a condition medically
    recognised as a cause of infertility; causation need not be separately proven for this patient. A
    clinically diagnosed gender dysphoria counts, since the glossary defines it as infertility.
 4. "your partner": the patient's spouse, civil union partner or domestic partner, whether or not that
    partner is covered (the defined-term reading cuts both ways, so the plain reading is kept).
 5. Negative conditions (voluntary sterilization, infertility due to a natural physiologic process, a less
    costly covered treatment that would succeed) disqualify only when established; unknown is not
    disqualifying.
 6. "tubal ligation, hysterectomy and vasectomy only if obtained as a form of voluntary sterilization":
    a medically indicated hysterectomy or similar procedure does not disqualify.
 7. Female with a male partner: either option A (months of intercourse) or option B (donor insemination
    cycles) from the table establishes infertility, although the glossary bullet names only intercourse.
 8. Male with a female partner: the glossary has no bullet; he is infertile when the couple meets the
    months requirement set by the female partner's age ("failure to become pregnant").
 9. Male without a female partner: the table has no row, so no months-trying or FSH requirement applies.
10. Intercourse that is "frequent" (glossary) or "timed" (table) counts toward the months.
11. "Self paid/not paid for by plan": descriptive of the donor cycles, not a condition; all donor
    insemination cycles count.
12. Age is taken at the service date; if a birth date is unknown, the claim must pass every age band.
13. FSH test "done within the past" 12/6 months: measured back from either the approval request date or
    the service date, whichever lets the test qualify.
14. Only unmedicated day 3 FSH tests count, for the window, for "most recent" and for "all prior tests".
    Several tests on the most recent date: the lowest result is used.
15. "all prior tests performed after age 40": tests dated strictly after the 40th birthday.
16. "less than 19 mIU/mL": strictly below 19.
17. Gender dysphoria satisfies the glossary, but the table's months and FSH requirements still apply,
    because the eligibility list is conjunctive and the table rows are stated by sex and partner only.
"""

import calendar
import datetime

SCHEMA = {
    "service_type": {
        "description": "Treatment the billed service is, or is furnished as part of a cycle of.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "ovulation_induction_other",
                    "intrauterine_insemination", "ivf", "other"],
    },
    "rendered_by_infertility_specialist": {
        "description": "The charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "member_status": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "other_dependent"],
    },
    "service_date": {
        "description": "Date of service.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "approval_request_date": {
        "description": "Date the provider requested advance approval (optional).",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Patient's sex as used by the table rows (female/male).",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or none if no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's date of birth.",
        "type": "str",
        "allowed": "YYYY_MM_DD",
    },
    "infertility_condition_documented": {
        "description": "A condition recognised as causing infertility has been recognised by the physician or "
                       "infertility specialist and documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "gender_dysphoria_diagnosed": {
        "description": "The patient or the partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": "The patient had a voluntary sterilization (with or without reversal).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "The partner had a voluntary sterilization (with or without reversal).",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "The patient's or partner's infertility is due to a natural physiologic process "
                       "(e.g. perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_would_succeed": {
        "description": "A successful pregnancy can be attained through a less costly treatment covered by the plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_intercourse": {
        "description": "Months of frequent or timed unprotected heterosexual intercourse without pregnancy.",
        "type": "float",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles": {
        "description": "Number of donor artificial insemination cycles without pregnancy.",
        "type": "int",
        "allowed": ">= 0",
    },
    "semen_analyses": {
        "description": "Patient's semen analyses.",
        "type": "list[dict]",
        "allowed": "each {'date': 'YYYY_MM_DD', 'abnormal': bool}",
    },
    "fsh_tests": {
        "description": "Patient's day 3 FSH tests.",
        "type": "list[dict]",
        "allowed": "each {'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated_day3': bool}",
    },
}

COVERED_SERVICES = {"ovulation_induction_menotropins", "intrauterine_insemination"}
ELIGIBLE_STATUSES = {"student", "spouse", "civil_union_partner", "domestic_partner"}

# Per age band: months of intercourse, donor cycles, FSH window in months, FSH rule.
BANDS = {
    "under_35": {"months": 12, "donor": 12, "window": 12, "fsh": "most_recent"},
    "35_to_39": {"months": 6, "donor": 6, "window": 6, "fsh": "most_recent"},
    "40_plus": {"months": 6, "donor": 6, "window": 6, "fsh": "all_after_40"},
}


def _date(value):
    if not isinstance(value, str):
        return None
    try:
        y, m, d = (int(p) for p in value.split("_"))
        return datetime.date(y, m, d)
    except (ValueError, TypeError):
        return None


def _age(birth, on):
    if birth is None or on is None:
        return None
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _bands(age):
    # READING: age banding. "under 35 years of age" / "35 years of age or older" / "age 40 and older";
    # age at the service date. Unknown age: the claim must pass every band.
    if age is None:
        return list(BANDS.values())
    if age < 35:
        return [BANDS["under_35"]]
    if age < 40:
        return [BANDS["35_to_39"]]
    return [BANDS["40_plus"]]


def _minus_months(d, n):
    y, m = d.year, d.month - n
    while m <= 0:
        m += 12
        y -= 1
    return datetime.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _fortieth_birthday(birth):
    try:
        return birth.replace(year=birth.year + 40)
    except ValueError:  # 29 February
        return datetime.date(birth.year + 40, 3, 1)


def _num(claim, key):
    value = claim.get(key)
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def _semen_ok(claim):
    analyses = claim.get("semen_analyses")
    if not isinstance(analyses, list):
        return False
    dates = sorted(
        d for d in (_date(a.get("date")) for a in analyses if isinstance(a, dict) and a.get("abnormal") is True)
        if d is not None
    )
    # "At least 2 abnormal semen analyses obtained at least 2 weeks apart": 14 days or more.
    return len(dates) >= 2 and (dates[-1] - dates[0]).days >= 14


def _fsh_ok(band, claim, birth):
    tests = []
    for t in claim.get("fsh_tests") or []:
        if not isinstance(t, dict):
            continue
        # READING: "unmedicated day 3 Follicle Stimulating Hormone (FSH) level"; only tests flagged as
        # unmedicated day 3 tests count for the window, "most recent" and "all prior tests".
        if t.get("unmedicated_day3") is not True:
            continue
        d, v = _date(t.get("date")), t.get("value_miu_ml")
        if d is None or not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        tests.append((d, float(v)))

    # READING: "You need to have an unmedicated day 3 FSH test done within the past"; the window runs back
    # from either the approval request date ("request approval from us in advance") or the service date.
    anchors = [a for a in (_date(claim.get("approval_request_date")), _date(claim.get("service_date"))) if a]
    for anchor in anchors:
        prior = [t for t in tests if t[0] <= anchor]
        start = _minus_months(anchor, band["window"])
        if not any(start <= d for d, _ in prior):
            continue
        if band["fsh"] == "most_recent":
            latest = max(d for d, _ in prior)
            # READING: "less than 19 mIU/mL in your most recent lab test"; strictly below 19, and with
            # several tests on the latest date the lowest result is used.
            if min(v for d, v in prior if d == latest) < 19:
                return True
        else:
            if birth is None:
                considered = prior
            else:
                # READING: "all prior tests performed after age 40"; tests dated strictly after the 40th birthday.
                cutoff = _fortieth_birthday(birth)
                considered = [t for t in prior if t[0] > cutoff]
            if all(v < 19 for _, v in considered):
                return True
    return False


def covered_under_benefit(claim: dict) -> bool:
    # READING: covered services. "We will cover charges made by an infertility specialist for the following
    # infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine insemination" and
    # "The cycle begins with the initiation of therapy"; any service furnished within such a cycle counts,
    # nothing else does.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False
    # READING: "charges made by an infertility specialist"; a positive condition, must be shown.
    if claim.get("rendered_by_infertility_specialist") is not True:
        return False

    # "You are covered under this plan as a student or as a covered dependent who is the student's legal
    # spouse, civil union partner or domestic partner".
    if claim.get("member_status") not in ELIGIBLE_STATUSES:
        return False

    gender_dysphoria = claim.get("gender_dysphoria_diagnosed") is True

    # READING: "a condition that: Is demonstrated to cause the illness of infertility. Has been recognized by
    # your physician or infertility specialist and documented"; a condition medically recognised as causing
    # infertility suffices, and a clinical gender dysphoria diagnosis counts because the glossary defines it
    # as infertility.
    if not (claim.get("infertility_condition_documented") is True or gender_dysphoria):
        return False

    # READING: negative conditions disqualify only when established ("has not had", "does not have",
    # "cannot be attained"); an unknown fact is not disqualifying.
    # READING: "your partner" means the patient's spouse, civil union or domestic partner, covered or not.
    # READING: "tubal ligation, hysterectomy and vasectomy only if obtained as a form of voluntary
    # sterilization"; the fields record only voluntary sterilizations.
    if claim.get("patient_voluntary_sterilization") is True:
        return False
    if claim.get("partner_voluntary_sterilization") is True:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is True:
        return False
    if claim.get("less_costly_covered_treatment_would_succeed") is True:
        return False

    service_date = _date(claim.get("service_date"))
    patient_birth = _date(claim.get("patient_birth_date"))
    partner_birth = _date(claim.get("partner_birth_date"))
    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    months = _num(claim, "months_unprotected_intercourse")
    donor = _num(claim, "donor_insemination_cycles")

    if sex == "female":
        bands = _bands(_age(patient_birth, service_date))
        if partner_sex == "male":
            # READING: female with a male partner. Table: "A. 12 months or more or B. At least 12 cycles of
            # donor insemination" (6 if 35 or older); either option establishes the glossary's "failure to
            # become pregnant" as well as the table requirement.
            # READING: "frequent" (glossary) or "timed" (table) unprotected intercourse both count.
            # READING: "Self paid/not paid for by plan" is descriptive; all donor cycles count.
            trying_ok = all(months >= b["months"] or donor >= b["donor"] for b in bands)
        else:
            # Female without a male partner: "At least 12 cycles of donor insemination" / "6 cycles".
            trying_ok = all(donor >= b["donor"] for b in bands)
        infertile = gender_dysphoria or trying_ok
        # READING: gender dysphoria satisfies the glossary, but "You have met the requirement for the number
        # of months trying to conceive" and the FSH table still apply to the row the patient falls in.
        table_ok = trying_ok and all(_fsh_ok(b, claim, patient_birth) for b in bands)
    elif sex == "male":
        if partner_sex == "female":
            # READING: male with a female partner; the glossary has no bullet, so he is infertile when the
            # couple meets "12 months or more" / "6 months or more" set by the female partner's age.
            bands = _bands(_age(partner_birth, service_date))
            trying_ok = all(months >= b["months"] for b in bands)
            infertile = gender_dysphoria or trying_ok
            table_ok = trying_ok  # FSH: "Does not apply"
        else:
            # Glossary: "For a male without a female partner, after: At least 2 abnormal semen analyses".
            infertile = gender_dysphoria or _semen_ok(claim)
            # READING: the table has no row for a male without a female partner; no months or FSH requirement.
            table_ok = True
    else:
        return False

    return infertile and table_ok
