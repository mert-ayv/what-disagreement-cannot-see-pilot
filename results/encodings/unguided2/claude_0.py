from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The infertility service being claimed.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "True if the charges are made by an infertility specialist.",
        "type": "bool",
    },
    "coverage_category": {
        "description": "How the patient is covered under the plan.",
        "type": "str",
        "allowed": ["student", "spouse", "civil_union_partner", "domestic_partner", "other_dependent"],
    },
    "infertility_condition_demonstrated": {
        "description": "True if there is a condition demonstrated to cause the illness of infertility.",
        "type": "bool",
    },
    "infertility_condition_documented": {
        "description": "True if that condition was recognized by the physician or infertility specialist "
                       "and documented in the patient's or partner's medical records.",
        "type": "bool",
    },
    "voluntary_sterilization_patient_or_partner": {
        "description": "True if the patient or partner ever had a voluntary sterilization "
                       "(tubal ligation, hysterectomy or vasectomy obtained as voluntary sterilization), "
                       "with or without reversal.",
        "type": "bool",
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "True if the patient's or partner's infertility is due to a natural physiologic process "
                       "such as age-related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
    },
    "less_costly_covered_treatment_could_succeed": {
        "description": "True if a successful pregnancy can be attained through less costly treatment "
                       "for which coverage is available under this plan.",
        "type": "bool",
    },
    "patient_sex": {
        "description": "Sex of the patient.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "service_date": {
        "description": "Date of the infertility service.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "has_partner": {
        "description": "True if the patient has a partner with whom they are trying to conceive.",
        "type": "bool",
    },
    "partner_sex": {
        "description": "Sex of the partner. Ignored if has_partner is False.",
        "type": "str",
        "allowed": ["female", "male", "none"],
    },
    "partner_birth_date": {
        "description": "Partner date of birth. Needed when the patient is male with a female partner.",
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of frequent, unprotected, timed heterosexual intercourse "
                       "without becoming pregnant.",
        "type": "int",
        "format": ">= 0",
    },
    "donor_insemination_cycles_not_paid_by_plan": {
        "description": "Number of donor artificial insemination cycles, self-paid or not paid for by the plan, "
                       "completed without becoming pregnant.",
        "type": "int",
        "format": ">= 0",
    },
    "fsh_tests": {
        "description": "All of the patient's unmedicated day 3 FSH test results.",
        "type": "list[dict]",
        "format": "each item: {'date': 'YYYY_MM_DD', 'value_miu_ml': float}",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of the patient's abnormal semen analyses.",
        "type": "list[str]",
        "format": "each 'YYYY_MM_DD'",
    },
    "gender_dysphoria_diagnosis_patient_or_partner": {
        "description": "True if the patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
    },
}


def _parse(d):
    y, m, dd = (int(x) for x in str(d).split("_"))
    return date(y, m, dd)


def _age_on(birth, on):
    years = on.year - birth.year
    if (on.month, on.day) < (birth.month, birth.day):
        years -= 1
    return years


def _months_before(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, min(d.day, day))
        except ValueError:
            continue
    return date(y, m, 28)


def _add_years(d, years):
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def _fsh_ok(claim, svc, birth, window_months):
    tests = []
    for t in claim.get("fsh_tests") or []:
        try:
            td = _parse(t["date"])
            val = float(t["value_miu_ml"])
        except Exception:
            continue
        if td <= svc:
            tests.append((td, val))
    if not tests:
        return False
    tests.sort(key=lambda x: x[0])
    start = _months_before(svc, window_months)
    if not any(td >= start for td, _ in tests):
        return False
    age = _age_on(birth, svc)
    if age < 40:
        return tests[-1][1] < 19
    fortieth = _add_years(birth, 40)
    return all(val < 19 for td, val in tests if td >= fortieth)


def covered_under_benefit(claim: dict) -> bool:
    try:
        # Covered service, by infertility specialist
        if claim.get("service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
            return False
        if claim.get("provider_is_infertility_specialist") is not True:
            return False

        # Enrollment category
        if claim.get("coverage_category") not in ("student", "spouse", "civil_union_partner", "domestic_partner"):
            return False

        # Condition demonstrated and documented
        if claim.get("infertility_condition_demonstrated") is not True:
            return False
        if claim.get("infertility_condition_documented") is not True:
            return False

        # Exclusionary eligibility criteria
        if claim.get("voluntary_sterilization_patient_or_partner") is not False:
            return False
        if claim.get("infertility_due_to_natural_physiologic_process") is not False:
            return False
        if claim.get("less_costly_covered_treatment_could_succeed") is not False:
            return False

        svc = _parse(claim["service_date"])
        birth = _parse(claim["patient_birth_date"])
        age = _age_on(birth, svc)
        sex = claim.get("patient_sex")
        has_partner = claim.get("has_partner") is True
        partner_sex = claim.get("partner_sex") if has_partner else "none"
        months = int(claim.get("months_unprotected_timed_intercourse") or 0)
        donor_cycles = int(claim.get("donor_insemination_cycles_not_paid_by_plan") or 0)
        dysphoria = claim.get("gender_dysphoria_diagnosis_patient_or_partner") is True

        if sex == "female":
            older = age >= 35
            threshold = 6 if older else 12
            window = 6 if older else 12
            if partner_sex == "male":
                infertile = months >= threshold or dysphoria
                trying_ok = months >= threshold or donor_cycles >= threshold
            else:
                infertile = donor_cycles >= threshold or dysphoria
                trying_ok = donor_cycles >= threshold
            if not infertile or not trying_ok:
                return False
            return _fsh_ok(claim, svc, birth, window)

        if sex == "male":
            if partner_sex == "female":
                pbd = claim.get("partner_birth_date")
                if not pbd:
                    return False
                partner_age = _age_on(_parse(pbd), svc)
                threshold = 6 if partner_age >= 35 else 12
                infertile = months >= threshold or dysphoria
                trying_ok = months >= threshold
                return infertile and trying_ok
            # Male without a female partner: no table row applies
            dates = []
            for d in claim.get("abnormal_semen_analysis_dates") or []:
                try:
                    pd = _parse(d)
                except Exception:
                    continue
                if pd <= svc:
                    dates.append(pd)
            semen_ok = len(dates) >= 2 and (max(dates) - min(dates)).days >= 14
            return semen_ok or dysphoria

        return False
    except Exception:
        return False
