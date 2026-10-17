from datetime import date
import calendar

SCHEMA = {
    "service_type": {
        "description": "Infertility service the claim is for",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "Charges are made by an infertility specialist",
        "type": "bool",
    },
    "service_date": {
        "description": "Date the service was rendered",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "coverage_type": {
        "description": "How the patient is covered under the plan",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "other_dependent", "not_covered"],
    },
    "patient_sex": {
        "description": "Sex of the patient",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_date_of_birth": {
        "description": "Patient's date of birth",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the patient's partner, or 'none' if the patient has no partner",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_date_of_birth": {
        "description": "Partner's date of birth. Needed when the patient is male with a female partner. Otherwise may be null.",
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "infertility_causing_condition_exists": {
        "description": "A condition exists that is demonstrated to cause the illness of infertility",
        "type": "bool",
    },
    "condition_recognized_and_documented": {
        "description": "The condition was recognized by a physician or infertility specialist and documented in the patient's or partner's medical records",
        "type": "bool",
    },
    "patient_or_partner_voluntary_sterilization": {
        "description": "Patient or partner had a voluntary sterilization (tubal ligation, hysterectomy or vasectomy obtained as voluntary sterilization), with or without reversal",
        "type": "bool",
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "Infertility of the patient or partner is due to a natural physiologic process, such as age-related ovarian insufficiency (perimenopause, menopause)",
        "type": "bool",
    },
    "pregnancy_attainable_with_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through a less costly treatment that is covered under this plan",
        "type": "bool",
    },
    "months_unprotected_intercourse_without_pregnancy": {
        "description": "Number of months of frequent, unprotected, timed heterosexual intercourse without becoming pregnant",
        "type": "int",
        "format": ">= 0",
    },
    "donor_insemination_cycles_without_pregnancy": {
        "description": "Number of self-paid donor artificial insemination cycles (not paid for by the plan) without becoming pregnant",
        "type": "int",
        "format": ">= 0",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of abnormal semen analyses for the patient",
        "type": "list[str]",
        "format": "list of YYYY_MM_DD",
    },
    "patient_or_partner_gender_dysphoria_diagnosis": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria",
        "type": "bool",
    },
    "fsh_tests": {
        "description": "The patient's FSH tests",
        "type": "list[dict]",
        "format": "each item: {'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated_day3': bool}",
    },
}


def _parse(d):
    if not d or not isinstance(d, str):
        return None
    try:
        y, m, dd = d.split("_")
        return date(int(y), int(m), int(dd))
    except Exception:
        return None


def _age_on(dob, on):
    return on.year - dob.year - ((on.month, on.day) < (dob.month, dob.day))


def _add_years(d, years):
    y = d.year + years
    day = min(d.day, calendar.monthrange(y, d.month)[1])
    return date(y, d.month, day)


def _sub_months(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return date(y, m, day)


def covered_under_benefit(claim: dict) -> bool:
    # Covered service
    if claim.get("service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
        return False
    if claim.get("provider_is_infertility_specialist") is not True:
        return False

    # Coverage status
    if claim.get("coverage_type") not in ("student", "spouse", "civil_union_partner", "domestic_partner"):
        return False

    service_date = _parse(claim.get("service_date"))
    dob = _parse(claim.get("patient_date_of_birth"))
    if service_date is None or dob is None:
        return False

    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex", "none")
    if sex not in ("female", "male"):
        return False

    # General eligibility conditions
    if claim.get("infertility_causing_condition_exists") is not True:
        return False
    if claim.get("condition_recognized_and_documented") is not True:
        return False
    if claim.get("patient_or_partner_voluntary_sterilization") is not False:
        return False
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False
    if claim.get("pregnancy_attainable_with_less_costly_covered_treatment") is not False:
        return False

    months = claim.get("months_unprotected_intercourse_without_pregnancy") or 0
    di_cycles = claim.get("donor_insemination_cycles_without_pregnancy") or 0
    dysphoria = claim.get("patient_or_partner_gender_dysphoria_diagnosis") is True
    age = _age_on(dob, service_date)

    # Determine the category, the infertility definition, and the table requirements
    if sex == "female":
        threshold = 12 if age < 35 else 6
        window_months = 12 if age < 35 else 6
        if partner_sex == "male":
            infertile_by_def = months >= threshold
            table_trying_met = months >= threshold or di_cycles >= threshold
        else:
            infertile_by_def = di_cycles >= threshold
            table_trying_met = di_cycles >= threshold

        if not (infertile_by_def or dysphoria):
            return False
        if not table_trying_met:
            return False

        # FSH requirement
        tests = []
        for t in claim.get("fsh_tests") or []:
            if not isinstance(t, dict) or t.get("unmedicated_day3") is not True:
                continue
            td = _parse(t.get("date"))
            val = t.get("value_miu_ml")
            if td is None or val is None or td > service_date:
                continue
            tests.append((td, float(val)))
        if not tests:
            return False
        tests.sort(key=lambda x: x[0])
        recent_date, recent_val = tests[-1]
        if recent_date < _sub_months(service_date, window_months):
            return False

        if age < 40:
            if not recent_val < 19:
                return False
        else:
            fortieth = _add_years(dob, 40)
            post40 = [v for (d, v) in tests if d >= fortieth]
            if post40:
                if not all(v < 19 for v in post40):
                    return False
            else:
                if not recent_val < 19:
                    return False
        return True

    # Male patient
    if partner_sex == "female":
        pdob = _parse(claim.get("partner_date_of_birth"))
        if pdob is None:
            return False
        partner_age = _age_on(pdob, service_date)
        threshold = 12 if partner_age < 35 else 6
        if not (months >= threshold or dysphoria):
            return False
        if months < threshold:
            return False
        return True
    else:
        # Male without a female partner: at least 2 abnormal semen analyses at least 2 weeks apart
        dates = sorted(d for d in (_parse(x) for x in (claim.get("abnormal_semen_analysis_dates") or []))
                       if d is not None and d <= service_date)
        semen_ok = len(dates) >= 2 and (dates[-1] - dates[0]).days >= 14
        if not (semen_ok or dysphoria):
            return False
        return True
