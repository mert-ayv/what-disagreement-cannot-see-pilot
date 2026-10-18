"""Cardinal Care 2023-2024, comprehensive infertility services benefit (insurer reading).

READING choices (each marked "# READING:" in the code):
1. Unknown facts: a missing field means the claimant has not shown the fact, so the claim is not covered.
2. Covered services: only the two listed services ("ovulation induction cycle(s) with menotropins",
   "intrauterine insemination"); ovulation induction without menotropins is not covered.
3. Provider: the charge must be made "by an infertility specialist".
4. "Your partner": the sterilization and physiologic-process exclusions apply to any partner with whom
   conception is attempted, not only to a covered dependent partner.
5. Condition: "demonstrated to cause the illness of infertility" requires an identified causal condition;
   unexplained infertility (a diagnosis by exclusion) does not satisfy it.
6. Natural physiologic process: "infertility that is due to" excludes infertility caused in whole or in part
   by a natural physiologic process.
7. Less costly treatment: the claimant must show that pregnancy cannot be attained through a less costly
   covered treatment.
8. Age: "You are a female under 35" is read in the present tense, at the date of service.
9. Glossary and table both apply: a female with a male partner (absent a gender dysphoria diagnosis) must
   show the glossary's months of intercourse; the table's donor insemination option B does not replace it.
10. Male with a female partner: the glossary has no prong for him, so he is infertile only through the
    couple's failure under the "female with a male partner" prong (by the female partner's age) or the
    gender dysphoria prong.
11. Male without a female partner: the table has no row for him, so the "number of months trying" bullet
    cannot be met and he is not eligible.
12. Intercourse months: only months of intercourse that was both "frequent" (glossary) and "timed" (table)
    and unprotected count.
13. Donor insemination cycles: only cycles "Self paid/not paid for by plan" count.
14. FSH test window: "done within the past" 12/6 months is measured back from the date of service.
15. FSH "most recent lab test": the most recent FSH lab test of any kind must be below 19 mIU/mL.
16. FSH "all prior tests performed after age 40": every FSH test from the 40th birthday on counts.
17. FSH for male patients: the table says "Does not apply", so no FSH requirement for a male patient.
"""

from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The infertility service billed.",
        "type": "str",
        "allowed": ["ovulation_induction_menotropins", "ovulation_induction_other_drug",
                    "intrauterine_insemination", "ivf", "other"],
    },
    "provider_is_infertility_specialist": {
        "description": "The charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "member_status": {
        "description": "Patient's coverage status under the plan.",
        "type": "str",
        "allowed": ["student", "dependent_spouse", "dependent_civil_union_partner",
                    "dependent_domestic_partner", "dependent_child", "other"],
    },
    "service_date": {
        "description": "Date the service is rendered.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_sex": {
        "description": "Patient's sex for the table rows.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_birth_date": {
        "description": "Patient's date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "has_partner": {
        "description": "Patient has a partner of the opposite sex with whom conception is attempted "
                       "(a male partner for a female patient, a female partner for a male patient).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_birth_date": {
        "description": "Date of birth of that partner (needed for a male patient's female partner).",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "failed_to_become_pregnant": {
        "description": "The attempts to conceive did not result in pregnancy.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_frequent_unprotected_timed_intercourse": {
        "description": "Months of frequent, unprotected, timed heterosexual intercourse with the partner.",
        "type": "int",
        "allowed": ">= 0",
    },
    "donor_insemination_cycles_self_paid": {
        "description": "Donor artificial insemination cycles self paid / not paid for by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "semen_analyses": {
        "description": "Semen analyses of the patient: list of {'date': 'YYYY_MM_DD', 'abnormal': bool}.",
        "type": "list[dict]",
        "format": "[{'date': str, 'abnormal': bool}]",
    },
    "gender_dysphoria_diagnosis": {
        "description": "Patient or partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_demonstrated_to_cause_infertility": {
        "description": "An identified condition exists that is demonstrated to cause infertility "
                       "(not unexplained infertility).",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_physician_or_specialist": {
        "description": "That condition has been recognized by the physician or infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_medical_records": {
        "description": "That condition is documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": "Patient has had a voluntary sterilization (tubal ligation, hysterectomy, vasectomy "
                       "obtained as voluntary sterilization), with or without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Partner has had a voluntary sterilization, with or without reversal.",
        "type": "bool",
        "allowed": [True, False],
    },
    "infertility_due_to_natural_physiologic_process": {
        "description": "The infertility of patient or partner is caused in whole or in part by a natural "
                       "physiologic process (e.g. perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "pregnancy_attainable_by_less_costly_covered_treatment": {
        "description": "A successful pregnancy can be attained through less costly treatment covered "
                       "by the plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "fsh_tests": {
        "description": "All FSH lab tests of the patient: list of "
                       "{'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated_day3': bool}.",
        "type": "list[dict]",
        "format": "[{'date': str, 'value_miu_ml': float, 'unmedicated_day3': bool}]",
    },
}


class _Unknown(Exception):
    pass


def _get(claim, key):
    # READING: unknown facts. "A missing field means the fact is unknown"; the claimant must show each
    # eligibility fact ("You are eligible for infertility services if: ..."), so an unknown fact fails.
    if key not in claim or claim[key] is None:
        raise _Unknown(key)
    return claim[key]


def _date(s):
    y, m, d = (int(p) for p in s.split("_"))
    return date(y, m, d)


def _age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _months_before(d, months):
    y, m = d.year, d.month - months
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
    try:
        return _covered(claim)
    except _Unknown:
        return False


def _covered(claim):
    # READING: covered services. "We will cover charges made by an infertility specialist for the
    # following infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine
    # insemination". Only these two; ovulation induction with other drugs is not covered.
    if _get(claim, "service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
        return False
    # READING: provider. "charges made by an infertility specialist" is a condition of payment.
    if _get(claim, "provider_is_infertility_specialist") is not True:
        return False

    # Member eligibility.
    if _get(claim, "member_status") not in ("student", "dependent_spouse",
                                            "dependent_civil_union_partner", "dependent_domestic_partner"):
        return False

    # READING: condition. "There exists a condition that: Is demonstrated to cause the illness of
    # infertility" requires an identified causal condition; unexplained infertility does not qualify.
    if _get(claim, "condition_demonstrated_to_cause_infertility") is not True:
        return False
    if _get(claim, "condition_recognized_by_physician_or_specialist") is not True:
        return False
    if _get(claim, "condition_documented_in_medical_records") is not True:
        return False

    has_partner = _get(claim, "has_partner")

    # READING: partner. "You or your partner has not had a voluntary sterilization" is applied to any
    # partner with whom conception is attempted (the table's "male partner"/"female partner").
    if _get(claim, "patient_voluntary_sterilization") is not False:
        return False
    if has_partner and _get(claim, "partner_voluntary_sterilization") is not False:
        return False

    # READING: physiologic process. "does not have infertility that is due to a natural physiologic
    # process" excludes infertility caused in whole or in part by such a process.
    if _get(claim, "infertility_due_to_natural_physiologic_process") is not False:
        return False

    # READING: less costly treatment. "A successful pregnancy cannot be attained through less costly
    # treatment" must be shown by the claimant; only an established False passes.
    if _get(claim, "pregnancy_attainable_by_less_costly_covered_treatment") is not False:
        return False

    service = _date(_get(claim, "service_date"))
    sex = _get(claim, "patient_sex")
    # READING: age. "You are a female under 35 years of age" is present tense, measured at service date.
    patient_age = _age(_date(_get(claim, "patient_birth_date")), service)
    gd = _get(claim, "gender_dysphoria_diagnosis") is True
    failed = _get(claim, "failed_to_become_pregnant") is True

    # READING: intercourse months. Glossary "frequent, unprotected heterosexual sexual intercourse" and
    # table "unprotected timed sexual intercourse" together: only months that were frequent and timed count.
    def months():
        return _get(claim, "months_frequent_unprotected_timed_intercourse")

    # READING: donor cycles. Table column "Number of donor artificial insemination cycles: Self paid/not
    # paid for by plan" counts only self-paid cycles, for both the table and the glossary count.
    def donor_cycles():
        return _get(claim, "donor_insemination_cycles_self_paid")

    if sex == "female":
        threshold = 12 if patient_age < 35 else 6
        # Glossary: infertile.
        if gd:
            infertile = True
        elif not failed:
            infertile = False
        elif has_partner:
            # READING: glossary and table both apply. Glossary "For a female with a male partner, after:
            # 1 year of frequent, unprotected heterosexual sexual intercourse" must be met; the table's
            # option "B. At least 12 cycles of donor insemination" does not substitute for it.
            infertile = months() >= threshold
        else:
            infertile = donor_cycles() >= threshold
        if not infertile:
            return False
        # Table: months trying to conceive.
        if has_partner:
            # Table "A. 12 months or more or B. At least 12 cycles of donor insemination".
            if not (months() >= threshold or donor_cycles() >= threshold):
                return False
        else:
            if donor_cycles() < threshold:
                return False
        # Table: FSH.
        if not _fsh_ok(claim, service, patient_age, threshold):
            return False
        return True

    if sex == "male":
        if not has_partner:
            # READING: male without a female partner. The table has rows only for "A male of any age with
            # a female partner"; "You have met the requirement for the number of months trying to
            # conceive" cannot be met without a row, so he is not eligible.
            return False
        partner_age = _age(_date(_get(claim, "partner_birth_date")), service)
        threshold = 12 if partner_age < 35 else 6
        # READING: male with a female partner. The glossary lists no prong for him; he is infertile through
        # the couple's "failure to become pregnant ... For a female with a male partner, after 1 year /
        # 6 months" by the female partner's age, or through the gender dysphoria prong.
        if not gd and not (failed and months() >= threshold):
            return False
        # Table "12 months or more" / "6 months or more".
        if months() < threshold:
            return False
        # READING: FSH for male patients. The table states "Does not apply"; no FSH requirement.
        return True

    return False


def _fsh_ok(claim, service, patient_age, window_months):
    tests = _get(claim, "fsh_tests")
    parsed = []
    for t in tests:
        parsed.append((_date(t["date"]), float(t["value_miu_ml"]), bool(t.get("unmedicated_day3"))))
    parsed = [p for p in parsed if p[0] <= service]
    if not parsed:
        return False
    # READING: FSH window. "You need to have an unmedicated day 3 FSH test done within the past: 12 months"
    # is measured back from the date of service.
    start = _months_before(service, window_months)
    if not any(p[2] and start <= p[0] <= service for p in parsed):
        return False
    if patient_age < 40:
        # READING: most recent test. "Must be less than 19 mIU/mL in your most recent lab test" refers to
        # the most recent FSH lab test of any kind, medicated or not.
        most_recent = max(parsed, key=lambda p: p[0])
        return most_recent[1] < 19
    # READING: after age 40. "must be less than 19 mIU/mL in all prior tests performed after age 40"
    # covers every FSH test from the 40th birthday on.
    birth = _date(_get(claim, "patient_birth_date"))
    try:
        fortieth = birth.replace(year=birth.year + 40)
    except ValueError:
        fortieth = date(birth.year + 40, 3, 1)
    after_40 = [p for p in parsed if p[0] >= fortieth]
    if not after_40:
        return False
    return all(p[1] < 19 for p in after_40)
