from datetime import date

SCHEMA = {
    "service_type": {
        "description": "Infertility service billed on the claim.",
        "type": "str",
        "allowed": ["ovulation_induction_with_menotropins", "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "True if the charges are made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "service_date": {
        "description": "Date the service was rendered.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "coverage_role": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "student_partner", "other_dependent"],
        "notes": "student_partner means the student's legal spouse, civil union partner or domestic partner.",
    },
    "infertility_condition_demonstrated": {
        "description": "True if a condition exists that is demonstrated to cause the illness of infertility.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_and_documented": {
        "description": "True if the condition was recognized by a physician or infertility specialist and documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "voluntary_sterilization_patient_or_partner": {
        "description": "True if the patient or partner has had a voluntary sterilization (e.g. tubal ligation, hysterectomy or vasectomy obtained as voluntary sterilization), with or without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "True if the patient's or partner's infertility is due to a natural physiologic process such as age-related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_could_succeed": {
        "description": "True if a successful pregnancy can be attained through less costly treatment that is covered under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_sex": {
        "description": "Sex of the patient receiving the service.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_date_of_birth": {
        "description": "Patient's date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if the patient has no partner.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_date_of_birth": {
        "description": "Partner's date of birth. Needed when the patient is male, to determine the female partner's age. Empty string or None if not applicable.",
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of unprotected timed sexual intercourse trying to conceive.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_not_plan_paid": {
        "description": "Number of donor artificial insemination cycles that were self-paid or not paid for by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_tests": {
        "description": "The patient's own FSH lab tests.",
        "type": "list of dict",
        "format": "[{'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated_day3': bool}, ...]",
    },
}

COVERED_SERVICES = {"ovulation_induction_with_menotropins", "intrauterine_insemination"}
FSH_LIMIT = 19.0


def _parse_date(s):
    if not s or not isinstance(s, str):
        return None
    parts = s.strip().split("_")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, TypeError):
        return None


def _age_on(dob, on):
    years = on.year - dob.year
    if (on.month, on.day) < (dob.month, dob.day):
        years -= 1
    return years


def _subtract_months(d, months):
    total = d.year * 12 + (d.month - 1) - months
    year, month0 = divmod(total, 12)
    month = month0 + 1
    if month == 12:
        next_first = date(year + 1, 1, 1)
    else:
        next_first = date(year, month + 1, 1)
    last_day = (next_first - date(year, month, 1)).days
    return date(year, month, min(d.day, last_day))


def _to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _valid_fsh_tests(claim, service_dt):
    tests = []
    raw = claim.get("fsh_tests") or []
    if not isinstance(raw, list):
        return tests
    for t in raw:
        if not isinstance(t, dict):
            continue
        if t.get("unmedicated_day3") is not True:
            continue
        d = _parse_date(t.get("date"))
        if d is None or d > service_dt:
            continue
        try:
            val = float(t.get("value_miu_ml"))
        except (TypeError, ValueError):
            continue
        tests.append((d, val))
    tests.sort(key=lambda x: x[0])
    return tests


def covered_under_benefit(claim: dict) -> bool:
    # Covered service rendered by an infertility specialist
    if claim.get("service_type") not in COVERED_SERVICES:
        return False
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    service_dt = _parse_date(claim.get("service_date"))
    if service_dt is None:
        return False

    # Coverage role: student, or the student's spouse / civil union / domestic partner
    if claim.get("coverage_role") not in ("student", "student_partner"):
        return False

    # Infertility condition exists, recognized and documented
    if claim.get("infertility_condition_demonstrated") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False

    # No voluntary sterilization
    if claim.get("voluntary_sterilization_patient_or_partner") is not False:
        return False

    # Not due to a natural physiologic process
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False

    # Less costly covered treatment cannot achieve pregnancy
    if claim.get("less_costly_covered_treatment_could_succeed") is not False:
        return False

    patient_sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    months_ic = _to_int(claim.get("months_unprotected_timed_intercourse"))
    donor_cycles = _to_int(claim.get("donor_insemination_cycles_not_plan_paid"))

    patient_dob = _parse_date(claim.get("patient_date_of_birth"))
    if patient_dob is None:
        return False

    if patient_sex == "female":
        age = _age_on(patient_dob, service_dt)
        if age < 0:
            return False
        has_male_partner = partner_sex == "male"
        required = 12 if age < 35 else 6

        # Months trying to conceive / donor insemination cycles
        if has_male_partner:
            if not (months_ic >= required or donor_cycles >= required):
                return False
        else:
            if donor_cycles < required:
                return False

        # Unmedicated day 3 FSH test within the past `required` months
        tests = _valid_fsh_tests(claim, service_dt)
        if not tests:
            return False
        window_start = _subtract_months(service_dt, required)
        most_recent_date, most_recent_val = tests[-1]
        if most_recent_date < window_start:
            return False

        if age < 40:
            if not (most_recent_val < FSH_LIMIT):
                return False
        else:
            for d, val in tests:
                if _age_on(patient_dob, d) >= 40 and not (val < FSH_LIMIT):
                    return False
        return True

    if patient_sex == "male":
        # Table applies only to a male with a female partner
        if partner_sex != "female":
            return False
        partner_dob = _parse_date(claim.get("partner_date_of_birth"))
        if partner_dob is None:
            return False
        partner_age = _age_on(partner_dob, service_dt)
        if partner_age < 0:
            return False
        required = 12 if partner_age < 35 else 6
        if months_ic < required:
            return False
        return True

    return False
