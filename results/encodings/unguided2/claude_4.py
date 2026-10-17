from datetime import date

# Covered services under this benefit, when billed by an infertility specialist.
COVERED_SERVICES = {
    "ovulation_induction_with_menotropins",
    "intrauterine_insemination",
}

SCHEMA = {
    "service_type": {
        "description": "Type of service on the claim.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "provider_is_infertility_specialist": {
        "description": "True if the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "service_date": {
        "description": "Date of service. Ages and FSH test windows are measured from this date.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "coverage_role": {
        "description": (
            "How the patient is covered: as the student, as the student's legal spouse, "
            "civil union partner or domestic partner, or as some other kind of dependent."
        ),
        "type": "str",
        "allowed": ["student", "student_spouse_or_partner", "other_dependent"],
    },
    "patient_sex": {
        "description": "Sex of the patient, as used in the infertility table.",
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
        "allowed": ["male", "female", "none"],
    },
    "partner_birth_date": {
        "description": (
            "Partner's date of birth. Required when a male patient has a female partner; "
            "otherwise it may be null."
        ),
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "infertility_condition_documented": {
        "description": (
            "True if there is a condition that is demonstrated to cause infertility, has been "
            "recognized by a physician or infertility specialist, and is documented in the "
            "patient's or partner's medical records."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_or_partner_voluntary_sterilization": {
        "description": (
            "True if the patient or partner ever had a voluntary sterilization (tubal ligation, "
            "hysterectomy or vasectomy done as voluntary sterilization). This counts whether or "
            "not it was surgically reversed."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": (
            "True if the patient's or partner's infertility is due to a natural physiologic "
            "process, such as age-related ovarian insufficiency (perimenopause or menopause)."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_can_achieve_pregnancy": {
        "description": (
            "True if a successful pregnancy can be attained through a less costly treatment "
            "that is covered under this plan."
        ),
        "type": "bool",
        "allowed": [True, False],
    },
    "months_unprotected_timed_intercourse": {
        "description": (
            "Number of months of frequent, unprotected, timed heterosexual intercourse "
            "without becoming pregnant."
        ),
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_self_paid": {
        "description": (
            "Number of donor artificial insemination cycles that were self-paid or not paid "
            "for by the plan, without becoming pregnant."
        ),
        "type": "int",
        "allowed": ">= 0",
    },
    "unmedicated_day3_fsh_tests": {
        "description": "List of all of the patient's unmedicated day 3 FSH lab tests.",
        "type": "list of dict",
        "format": '[{"date": "YYYY_MM_DD", "value_miu_ml": float}, ...]',
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of the patient's abnormal semen analyses.",
        "type": "list of str",
        "format": "YYYY_MM_DD",
    },
    "patient_or_partner_gender_dysphoria_diagnosis": {
        "description": "True if the patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
}


def _parse(d):
    y, m, dd = str(d).split("_")
    return date(int(y), int(m), int(dd))


def _age_on(birth, on):
    years = on.year - birth.year
    if (on.month, on.day) < (birth.month, birth.day):
        years -= 1
    return years


def _add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # Feb 29 birthday in a non-leap target year: use Feb 28.
        return d.replace(year=d.year + years, day=28)


def _months_before(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    day = d.day
    while True:
        try:
            return date(y, m, day)
        except ValueError:
            day -= 1


def _fsh_ok(claim, svc, birth, age, window_months):
    tests = []
    for t in claim.get("unmedicated_day3_fsh_tests") or []:
        try:
            tests.append((_parse(t["date"]), float(t["value_miu_ml"])))
        except (KeyError, TypeError, ValueError):
            continue

    # A test must have been done within the past window, and not after the service date.
    start = _months_before(svc, window_months)
    in_window = [t for t in tests if start <= t[0] <= svc]
    if not in_window:
        return False

    prior = [t for t in tests if t[0] <= svc]
    if age < 40:
        # The most recent test must be under 19 mIU/mL.
        most_recent = max(prior, key=lambda t: t[0])
        return most_recent[1] < 19
    else:
        # Every prior test performed at or after age 40 must be under 19 mIU/mL.
        fortieth = _add_years(birth, 40)
        return all(v < 19 for (dt, v) in prior if dt >= fortieth)


def covered_under_benefit(claim: dict) -> bool:
    # Service must be a covered infertility service from an infertility specialist.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # Patient must be the student or the student's spouse, civil union or domestic partner.
    if claim.get("coverage_role") not in ("student", "student_spouse_or_partner"):
        return False

    # General eligibility conditions.
    if claim.get("infertility_condition_documented") is not True:
        return False
    if claim.get("patient_or_partner_voluntary_sterilization") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("less_costly_covered_treatment_can_achieve_pregnancy") is not False:
        return False

    try:
        svc = _parse(claim["service_date"])
        birth = _parse(claim["patient_birth_date"])
    except (KeyError, TypeError, ValueError):
        return False
    age = _age_on(birth, svc)

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    months = int(claim.get("months_unprotected_timed_intercourse") or 0)
    di_cycles = int(claim.get("donor_insemination_cycles_self_paid") or 0)
    dysphoria = claim.get("patient_or_partner_gender_dysphoria_diagnosis") is True

    if sex == "female":
        threshold = 12 if age < 35 else 6
        window = 12 if age < 35 else 6

        if partner_sex == "male":
            # Glossary definition of infertility.
            infertile = months >= threshold or dysphoria
            # Table: months of intercourse OR donor insemination cycles.
            trying_ok = months >= threshold or di_cycles >= threshold
        else:
            # Female without a male partner.
            infertile = di_cycles >= threshold or dysphoria
            trying_ok = di_cycles >= threshold

        if not infertile or not trying_ok:
            return False
        return _fsh_ok(claim, svc, birth, age, window)

    if sex == "male":
        if partner_sex == "female":
            try:
                p_birth = _parse(claim["partner_birth_date"])
            except (KeyError, TypeError, ValueError):
                return False
            p_age = _age_on(p_birth, svc)
            threshold = 12 if p_age < 35 else 6
            infertile = months >= threshold or dysphoria
            trying_ok = months >= threshold
            # The FSH requirement does not apply to a male patient.
            return infertile and trying_ok

        # Male without a female partner: the table has no row for this case,
        # so the months-trying requirement cannot be met.
        return False

    return False
