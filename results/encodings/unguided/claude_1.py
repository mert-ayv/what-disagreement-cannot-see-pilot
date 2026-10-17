from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The infertility service billed on the claim.",
        "type": "str",
        "allowed": [
            "ovulation_induction_with_menotropins",
            "intrauterine_insemination",
            "other",
        ],
    },
    "rendering_provider_is_infertility_specialist": {
        "description": "Whether the charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_coverage_type": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": [
            "student",
            "dependent_legal_spouse",
            "dependent_civil_union_partner",
            "dependent_domestic_partner",
            "other_dependent",
        ],
    },
    "infertility_condition_demonstrated": {
        "description": "A condition exists that is demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_physician_or_infertility_specialist": {
        "description": "The infertility-causing condition has been recognized by the patient's physician or an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_patient_or_partner_records": {
        "description": "The condition is documented in the patient's or the partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_had_voluntary_sterilization": {
        "description": "The patient has had a voluntary sterilization (for example tubal ligation, hysterectomy or vasectomy obtained as voluntary sterilization), with or without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_had_voluntary_sterilization": {
        "description": "The partner has had a voluntary sterilization, with or without reversal. Use False if there is no partner.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "The patient's or partner's infertility is due to a natural physiologic process, such as age-related ovarian insufficiency (perimenopause or menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_through_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through a less costly treatment that is covered under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_sex": {
        "description": "Sex of the patient receiving the service.",
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
        "description": "Partner's date of birth. Needed when a male patient has a female partner; otherwise may be null.",
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "service_date": {
        "description": "Date the infertility service was rendered.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of unprotected timed sexual intercourse (egg and sperm contact) attempting conception.",
        "type": "int",
        "allowed": ">= 0",
    },
    "self_paid_donor_insemination_cycles": {
        "description": "Number of donor artificial insemination cycles that were self-paid or not paid for by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_tests": {
        "description": "All of the patient's day 3 FSH lab tests. Each item has 'date' (YYYY_MM_DD), 'value_miu_per_ml' (float) and 'unmedicated' (bool).",
        "type": "list[dict]",
        "format": "[{'date': 'YYYY_MM_DD', 'value_miu_per_ml': float, 'unmedicated': bool}, ...]",
    },
}

_COVERED_SERVICES = {"ovulation_induction_with_menotropins", "intrauterine_insemination"}
_ELIGIBLE_COVERAGE = {
    "student",
    "dependent_legal_spouse",
    "dependent_civil_union_partner",
    "dependent_domestic_partner",
}
_FSH_LIMIT = 19.0


def _parse_date(s):
    if not isinstance(s, str):
        return None
    parts = s.split("_")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, TypeError):
        return None


def _age_on(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # Feb 29 -> Mar 1
        return date(d.year + years, 3, 1)


def _months_before(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, day)
        except ValueError:
            continue
    return date(y, m, 28)


def _bool(claim, key):
    v = claim.get(key)
    return v if isinstance(v, bool) else None


def _int(claim, key):
    v = claim.get(key)
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v


def _fsh_ok(claim, svc_date, birth, age, window_months):
    tests = claim.get("fsh_tests")
    if not isinstance(tests, list):
        return False
    parsed = []
    for t in tests:
        if not isinstance(t, dict):
            continue
        if t.get("unmedicated") is not True:
            continue
        d = _parse_date(t.get("date"))
        v = t.get("value_miu_per_ml")
        if d is None or isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if d > svc_date:
            continue
        parsed.append((d, float(v)))
    if not parsed:
        return False

    window_start = _months_before(svc_date, window_months)
    if not any(window_start <= d <= svc_date for d, _ in parsed):
        return False

    if age < 40:
        most_recent_date = max(d for d, _ in parsed)
        recent_values = [v for d, v in parsed if d == most_recent_date]
        return all(v < _FSH_LIMIT for v in recent_values)

    fortieth = _add_years(birth, 40)
    after_40 = [v for d, v in parsed if d >= fortieth]
    return all(v < _FSH_LIMIT for v in after_40)


def covered_under_benefit(claim: dict) -> bool:
    if not isinstance(claim, dict):
        return False

    # Covered service rendered by an infertility specialist
    if claim.get("service_type") not in _COVERED_SERVICES:
        return False
    if _bool(claim, "rendering_provider_is_infertility_specialist") is not True:
        return False

    # Coverage status
    if claim.get("patient_coverage_type") not in _ELIGIBLE_COVERAGE:
        return False

    # Infertility condition demonstrated, recognized and documented
    if _bool(claim, "infertility_condition_demonstrated") is not True:
        return False
    if _bool(claim, "condition_recognized_by_physician_or_infertility_specialist") is not True:
        return False
    if _bool(claim, "condition_documented_in_patient_or_partner_records") is not True:
        return False

    # Exclusionary eligibility conditions
    if _bool(claim, "patient_had_voluntary_sterilization") is not False:
        return False
    if _bool(claim, "partner_had_voluntary_sterilization") is not False:
        return False
    if _bool(claim, "infertility_due_to_natural_physiologic_process") is not False:
        return False
    if _bool(claim, "pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    svc_date = _parse_date(claim.get("service_date"))
    birth = _parse_date(claim.get("patient_birth_date"))
    if svc_date is None or birth is None or birth > svc_date:
        return False
    age = _age_on(birth, svc_date)

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if partner_sex not in ("female", "male", "none"):
        return False

    months = _int(claim, "months_unprotected_timed_intercourse")
    donor_cycles = _int(claim, "self_paid_donor_insemination_cycles")

    if sex == "female":
        required = 12 if age < 35 else 6
        has_male_partner = partner_sex == "male"
        if has_male_partner:
            trying_ok = (months is not None and months >= required) or (
                donor_cycles is not None and donor_cycles >= required
            )
        else:
            trying_ok = donor_cycles is not None and donor_cycles >= required
        if not trying_ok:
            return False
        return _fsh_ok(claim, svc_date, birth, age, required)

    if sex == "male":
        if partner_sex != "female":
            return False
        partner_birth = _parse_date(claim.get("partner_birth_date"))
        if partner_birth is None or partner_birth > svc_date:
            return False
        partner_age = _age_on(partner_birth, svc_date)
        required = 12 if partner_age < 35 else 6
        return months is not None and months >= required

    return False
