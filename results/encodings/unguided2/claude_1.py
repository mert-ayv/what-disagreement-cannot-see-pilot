from datetime import date

SCHEMA = {
    "service_type": {
        "description": "Infertility service being claimed",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "Charges are made by an infertility specialist",
        "type": "bool",
    },
    "service_date": {
        "description": "Date the service is (or will be) rendered",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "member_role": {
        "description": "Patient's coverage status under the plan",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "child", "other"],
    },
    "patient_sex": {
        "description": "Sex of the patient",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if no partner",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's date of birth (needed when patient is male with a female partner); null if no partner",
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "months_unprotected_intercourse_without_pregnancy": {
        "description": "Months of frequent, unprotected, timed heterosexual intercourse without becoming pregnant",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_self_paid": {
        "description": "Number of donor artificial insemination cycles without pregnancy, self-paid / not paid for by the plan",
        "type": "int",
        "allowed": ">= 0",
    },
    "fsh_tests": {
        "description": "All unmedicated day 3 FSH tests of the patient",
        "type": "list[dict]",
        "format": "[{'date': 'YYYY_MM_DD', 'value_miu_ml': float}, ...]",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of the patient's abnormal semen analyses",
        "type": "list[str]",
        "format": "YYYY_MM_DD each",
    },
    "gender_dysphoria_diagnosis": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria",
        "type": "bool",
    },
    "infertility_condition_demonstrated": {
        "description": "A condition exists that is demonstrated to cause the illness of infertility",
        "type": "bool",
    },
    "condition_recognized_and_documented": {
        "description": "That condition is recognized by a physician/infertility specialist and documented in the patient's or partner's medical records",
        "type": "bool",
    },
    "voluntary_sterilization": {
        "description": "Patient or partner has had a voluntary sterilization (with or without reversal)",
        "type": "bool",
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Infertility of patient or partner is due to a natural physiologic process (e.g. perimenopause, menopause)",
        "type": "bool",
    },
    "less_costly_covered_treatment_can_achieve_pregnancy": {
        "description": "A successful pregnancy can be attained through less costly treatment covered under the plan",
        "type": "bool",
    },
}


def _parse(s):
    try:
        y, m, d = (int(p) for p in str(s).split("_"))
        return date(y, m, d)
    except Exception:
        return None


def _age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _add_years(d, n):
    try:
        return d.replace(year=d.year + n)
    except ValueError:
        return d.replace(year=d.year + n, day=28)


def _months_before(d, n):
    y, m = d.year, d.month - n
    while m <= 0:
        m += 12
        y -= 1
    day = d.day
    while True:
        try:
            return date(y, m, day)
        except ValueError:
            day -= 1


def covered_under_benefit(claim: dict) -> bool:
    # Covered service and provider
    if claim.get("service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
        return False
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # Covered as student or student's spouse / civil union / domestic partner
    if claim.get("member_role") not in ("student", "spouse", "civil_union_partner", "domestic_partner"):
        return False

    # Condition demonstrated and documented
    if claim.get("infertility_condition_demonstrated") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False

    # Exclusionary eligibility conditions
    if claim.get("voluntary_sterilization") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("less_costly_covered_treatment_can_achieve_pregnancy") is not False:
        return False

    service_date = _parse(claim.get("service_date"))
    birth = _parse(claim.get("patient_birth_date"))
    if service_date is None or birth is None:
        return False
    age = _age(birth, service_date)
    if age < 0:
        return False

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if sex not in ("female", "male") or partner_sex not in ("female", "male", "none"):
        return False

    months = claim.get("months_unprotected_intercourse_without_pregnancy") or 0
    di_cycles = claim.get("donor_insemination_cycles_self_paid") or 0
    try:
        months = int(months)
        di_cycles = int(di_cycles)
    except Exception:
        return False
    gender_dysphoria = claim.get("gender_dysphoria_diagnosis") is True

    if sex == "female":
        has_male_partner = partner_sex == "male"
        threshold = 12 if age < 35 else 6

        # Infertility definition (glossary)
        if has_male_partner:
            infertile = months >= threshold
        else:
            infertile = di_cycles >= threshold
        infertile = infertile or gender_dysphoria
        if not infertile:
            return False

        # Table: months trying / donor insemination cycles
        if has_male_partner:
            trying_ok = months >= threshold or di_cycles >= threshold
        else:
            trying_ok = di_cycles >= threshold
        if not trying_ok:
            return False

        # Table: unmedicated day 3 FSH
        tests = []
        for t in claim.get("fsh_tests") or []:
            if not isinstance(t, dict):
                return False
            td = _parse(t.get("date"))
            val = t.get("value_miu_ml")
            if td is None or not isinstance(val, (int, float)) or isinstance(val, bool):
                return False
            if td <= service_date:
                tests.append((td, float(val)))
        if not tests:
            return False
        window_start = _months_before(service_date, threshold)
        recent_in_window = [t for t in tests if t[0] >= window_start]
        if not recent_in_window:
            return False
        most_recent = max(tests, key=lambda t: t[0])
        if age < 40:
            if not most_recent[1] < 19:
                return False
        else:
            fortieth = _add_years(birth, 40)
            if any(v >= 19 for d, v in tests if d >= fortieth):
                return False
        return True

    # Male patient
    if partner_sex == "female":
        pbirth = _parse(claim.get("partner_birth_date"))
        if pbirth is None:
            return False
        page = _age(pbirth, service_date)
        if page < 0:
            return False
        threshold = 12 if page < 35 else 6
        trying_ok = months >= threshold
        infertile = trying_ok or gender_dysphoria
        if not infertile or not trying_ok:
            return False
        return True
    else:
        # Male without a female partner: no table row applies
        dates = [_parse(d) for d in (claim.get("abnormal_semen_analysis_dates") or [])]
        if any(d is None for d in dates):
            return False
        dates = [d for d in dates if d <= service_date]
        semen_ok = len(dates) >= 2 and (max(dates) - min(dates)).days >= 14
        return semen_ok or gender_dysphoria
