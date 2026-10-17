from datetime import datetime, date
import calendar

SCHEMA = {
    "service_type": {
        "description": "Infertility service billed on the claim",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "intrauterine_insemination", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "Whether the charges are made by an infertility specialist",
        "type": "bool",
    },
    "service_date": {
        "description": "Date the service was rendered",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "member_coverage_category": {
        "description": "How the patient is covered under the plan",
        "type": "str",
        "allowed": ["student", "student_spouse_civil_union_or_domestic_partner", "other_dependent"],
    },
    "patient_sex": {
        "description": "Patient's reproductive sex, used for the eligibility table and infertility definition",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Reproductive sex of the patient's partner, or 'none' if the patient has no partner",
        "type": "str",
        "allowed": ["male", "female", "none"],
    },
    "partner_birth_date": {
        "description": "Partner's date of birth. Required when the patient is male with a female partner.",
        "type": "str or None",
        "format": "YYYY_MM_DD",
    },
    "infertility_condition_documented": {
        "description": "A condition demonstrated to cause infertility exists, has been recognized by the "
                       "physician or infertility specialist, and is documented in the patient's or partner's "
                       "medical records",
        "type": "bool",
    },
    "voluntary_sterilization_patient_or_partner": {
        "description": "The patient or partner has had a voluntary sterilization (tubal ligation, hysterectomy, "
                       "or vasectomy obtained as voluntary sterilization), with or without reversal",
        "type": "bool",
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "The infertility is due to a natural physiologic process such as age-related ovarian "
                       "insufficiency (perimenopause or menopause)",
        "type": "bool",
    },
    "pregnancy_attainable_by_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through a less costly treatment that is "
                       "covered under this plan",
        "type": "bool",
    },
    "months_unprotected_timed_intercourse": {
        "description": "Number of months of frequent, unprotected, timed heterosexual intercourse trying to conceive",
        "type": "int",
        "format": ">= 0",
    },
    "donor_insemination_cycles_not_plan_paid": {
        "description": "Number of donor artificial insemination cycles that were self-paid or not paid for by the plan",
        "type": "int",
        "format": ">= 0",
    },
    "fsh_tests": {
        "description": "Unmedicated day 3 FSH lab tests for the patient",
        "type": "list[dict]",
        "format": "[{'date': 'YYYY_MM_DD', 'value_miu_ml': float}, ...]",
    },
    "abnormal_semen_analysis_dates": {
        "description": "Dates of the patient's abnormal semen analyses",
        "type": "list[str]",
        "format": "['YYYY_MM_DD', ...]",
    },
    "gender_dysphoria_diagnosis_patient_or_partner": {
        "description": "The patient or partner has been clinically diagnosed with gender dysphoria",
        "type": "bool",
    },
}

COVERED_SERVICES = {"ovulation_induction_menotropins", "intrauterine_insemination"}
ELIGIBLE_COVERAGE = {"student", "student_spouse_civil_union_or_domestic_partner"}


def _parse(s):
    return datetime.strptime(s, "%Y_%m_%d").date()


def _age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _sub_months(d, months):
    total = d.year * 12 + (d.month - 1) - months
    y, m = divmod(total, 12)
    m += 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return date(y, m, day)


def _birthday(birth, years):
    y = birth.year + years
    try:
        return date(y, birth.month, birth.day)
    except ValueError:
        # Feb 29 birthday in a non-leap year: the birthday is reached on Mar 1
        return date(y, 3, 1)


def _fsh_ok(claim, service, age, window_months):
    tests = []
    for t in claim.get("fsh_tests") or []:
        try:
            td = _parse(t["date"])
            val = float(t["value_miu_ml"])
        except (KeyError, TypeError, ValueError):
            return False
        if td <= service:
            tests.append((td, val))
    if not tests:
        return False

    # A test must have been done within the required window
    window_start = _sub_months(service, window_months)
    latest_date = max(td for td, _ in tests)
    if latest_date < window_start:
        return False

    latest_values = [v for td, v in tests if td == latest_date]
    if age < 40:
        return all(v < 19 for v in latest_values)

    # Age 40 or older: all tests performed after age 40 must be below 19
    turned_40 = _birthday(_parse(claim["patient_birth_date"]), 40)
    after_40 = [v for td, v in tests if td >= turned_40]
    if not all(v < 19 for v in after_40):
        return False
    return all(v < 19 for v in latest_values)


def covered_under_benefit(claim: dict) -> bool:
    try:
        # The service must be a covered infertility service
        if claim.get("service_type") not in COVERED_SERVICES:
            return False
        if not claim.get("provider_is_infertility_specialist"):
            return False

        # General eligibility requirements
        if claim.get("member_coverage_category") not in ELIGIBLE_COVERAGE:
            return False
        if not claim.get("infertility_condition_documented"):
            return False
        if claim.get("voluntary_sterilization_patient_or_partner"):
            return False
        if claim.get("infertility_due_to_natural_physiologic_process"):
            return False
        if claim.get("pregnancy_attainable_by_less_costly_covered_treatment"):
            return False

        service = _parse(claim["service_date"])
        sex = claim.get("patient_sex")
        partner = claim.get("partner_sex", "none")
        months = int(claim.get("months_unprotected_timed_intercourse") or 0)
        donor = int(claim.get("donor_insemination_cycles_not_plan_paid") or 0)
        dysphoria = bool(claim.get("gender_dysphoria_diagnosis_patient_or_partner"))

        if sex == "female":
            age = _age(_parse(claim["patient_birth_date"]), service)
            threshold = 12 if age < 35 else 6

            if partner == "male":
                infertile = months >= threshold or dysphoria
                table_ok = months >= threshold or donor >= threshold
            elif partner in ("female", "none"):
                infertile = donor >= threshold or dysphoria
                table_ok = donor >= threshold
            else:
                return False

            if not (infertile and table_ok):
                return False
            return _fsh_ok(claim, service, age, threshold)

        if sex == "male":
            if partner == "female":
                pbd = claim.get("partner_birth_date")
                if not pbd:
                    return False
                partner_age = _age(_parse(pbd), service)
                threshold = 12 if partner_age < 35 else 6
                infertile = months >= threshold or dysphoria
                table_ok = months >= threshold
                return infertile and table_ok

            if partner in ("male", "none"):
                # The table has no row for a male without a female partner, so no
                # months-trying or FSH requirement applies to this patient.
                dates = sorted(_parse(d) for d in (claim.get("abnormal_semen_analysis_dates") or []))
                semen_ok = len(dates) >= 2 and (dates[-1] - dates[0]).days >= 14
                return semen_ok or dysphoria

            return False

        return False
    except (KeyError, TypeError, ValueError):
        return False
