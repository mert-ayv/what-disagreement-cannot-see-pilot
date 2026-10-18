"""
Cardinal Care 2023-2024 Certificate of Coverage, comprehensive infertility services
benefit (pp. 62-64) with the Glossary definition of "Infertile or infertility",
encoded from the insurer's claims-counsel perspective.

READING choices (each is marked "# READING:" in the code):
 R1  Unknown facts: a missing field is not established, so the claim is not covered.
 R2  Covered services: only ovulation induction with menotropins and intrauterine
     insemination; ovulation induction with any other drug is not covered.
 R3  Provider: "charges made by an infertility specialist" is a coverage condition.
 R4  Cause: "a condition that ... is demonstrated to cause the illness of infertility"
     requires a specific identified causal condition; unexplained infertility fails.
 R5  "You or your partner" in the sterilization and natural-process bullets bars
     coverage if either person is affected; "partner" includes the partner with whom
     conception is attempted, whether or not that partner is covered.
 R6  Ages (patient and partner) are measured on the date of service.
 R7  "1 year" in the glossary means 12 months.
 R8  Intercourse months count only if the intercourse was frequent (glossary),
     unprotected and timed (table), and heterosexual.
 R9  A female with a male partner must meet the glossary intercourse period; the
     table's donor-insemination route B satisfies the table but establishes
     infertility only where the gender dysphoria prong applies.
 R10 A male with a female partner has no glossary prong of his own; he is infertile
     only if the couple meets the female-with-male-partner prong by the female
     partner's age (or the gender dysphoria prong).
 R11 A male without a female partner has no table row, so the "number of months
     trying to conceive" requirement cannot be met and he is not eligible.
 R12 Donor insemination cycles count only if "Self paid/not paid for by plan".
 R13 "Failure to become pregnant": any pregnancy during the qualifying period,
     however it ended, defeats the definition.
 R14 FSH window: the most recent unmedicated day 3 FSH test on or before the date of
     service must fall strictly within the 12 or 6 months before the date of service.
 R15 Age 40 and older: at least one unmedicated day 3 FSH test must have been
     performed on or after the 40th birthday, and every such test must be < 19 mIU/mL.
 R16 The FSH criteria apply only to female patients ("Does not apply" in male rows).
"""

from datetime import date

SCHEMA = {
    "service_type": {
        "description": "The infertility service billed on the claim.",
        "type": "str",
        "allowed": [
            "ovulation_induction_menotropins",
            "ovulation_induction_other_drug",
            "intrauterine_insemination",
            "other",
        ],
    },
    "billed_by_infertility_specialist": {
        "description": "Whether the charge is made by an infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "service_date": {
        "description": "Date of service.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "patient_coverage_status": {
        "description": "Basis on which the patient is covered under the plan.",
        "type": "str",
        "allowed": [
            "student",
            "student_spouse",
            "student_civil_union_partner",
            "student_domestic_partner",
            "other_dependent",
            "not_covered",
        ],
    },
    "patient_sex": {
        "description": "Sex of the patient for the table row.",
        "type": "str",
        "allowed": ["female", "male"],
    },
    "patient_date_of_birth": {
        "description": "Patient's date of birth.",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "partner_sex": {
        "description": "Sex of the partner with whom conception is attempted, or 'none'.",
        "type": "str",
        "allowed": ["male", "female", "none"],
    },
    "partner_date_of_birth": {
        "description": "Partner's date of birth (needed for a male patient with a female partner).",
        "type": "str",
        "format": "YYYY_MM_DD",
    },
    "gender_dysphoria_diagnosis": {
        "description": "Whether the patient or the partner has been clinically diagnosed with gender dysphoria.",
        "type": "bool",
        "allowed": [True, False],
    },
    "causal_condition_demonstrated": {
        "description": "Whether a specific identified condition is demonstrated to cause the infertility "
                       "(False for unexplained infertility).",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_recognized_by_physician_or_specialist": {
        "description": "Whether that condition has been recognized by the patient's physician or infertility specialist.",
        "type": "bool",
        "allowed": [True, False],
    },
    "condition_documented_in_records": {
        "description": "Whether that condition is documented in the patient's or partner's medical records.",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_voluntary_sterilization": {
        "description": "Whether the patient has ever had a voluntary sterilization (tubal ligation, hysterectomy "
                       "or vasectomy obtained as voluntary sterilization), reversed or not.",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_voluntary_sterilization": {
        "description": "Same as patient_voluntary_sterilization, for the partner (False if no partner).",
        "type": "bool",
        "allowed": [True, False],
    },
    "patient_infertility_due_to_natural_process": {
        "description": "Whether the patient's infertility is due to a natural physiologic process such as "
                       "age-related ovarian insufficiency (perimenopause, menopause).",
        "type": "bool",
        "allowed": [True, False],
    },
    "partner_infertility_due_to_natural_process": {
        "description": "Same as patient_infertility_due_to_natural_process, for the partner (False if no partner).",
        "type": "bool",
        "allowed": [True, False],
    },
    "less_costly_covered_treatment_could_succeed": {
        "description": "Whether a successful pregnancy can be attained through less costly treatment for which "
                       "coverage is available under this plan.",
        "type": "bool",
        "allowed": [True, False],
    },
    "months_frequent_unprotected_timed_intercourse": {
        "description": "Months of frequent, unprotected, timed heterosexual intercourse trying to conceive.",
        "type": "int",
        "allowed": ">= 0",
    },
    "self_paid_donor_insemination_cycles": {
        "description": "Number of donor artificial insemination cycles that were self paid / not paid for by the plan.",
        "type": "int",
        "allowed": ">= 0",
    },
    "pregnancy_during_attempts": {
        "description": "Whether any pregnancy occurred during the qualifying intercourse or insemination period.",
        "type": "bool",
        "allowed": [True, False],
    },
    "fsh_tests": {
        "description": "The patient's FSH lab tests.",
        "type": "list[dict]",
        "format": "each item {'date': 'YYYY_MM_DD', 'value_miu_ml': float, 'unmedicated_day3': bool}",
    },
}


def _parse(s):
    y, m, d = s.split("_")
    return date(int(y), int(m), int(d))


def _age_on(dob, when):
    years = when.year - dob.year
    if (when.month, when.day) < (dob.month, dob.day):
        years -= 1
    return years


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


def _bool(claim, key):
    # READING: unknown facts. "A missing field means the fact is unknown"; the claimant
    # must establish each eligibility fact, so an unknown fact is treated as not met.
    v = claim.get(key)
    return v if isinstance(v, bool) else None


def _int(claim, key):
    v = claim.get(key)
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v


def covered_under_benefit(claim: dict) -> bool:
    # --- Covered service --------------------------------------------------------
    # READING: covered services. "We will cover ... Ovulation induction cycle(s) with
    # menotropins" and "Intrauterine insemination": only these two services; ovulation
    # induction with any other drug is outside the benefit.
    if claim.get("service_type") not in ("ovulation_induction_menotropins", "intrauterine_insemination"):
        return False

    # READING: provider. "We will cover charges made by an infertility specialist":
    # charges made by any other provider are not covered under this benefit.
    if _bool(claim, "billed_by_infertility_specialist") is not True:
        return False

    try:
        service_date = _parse(claim["service_date"])
        patient_dob = _parse(claim["patient_date_of_birth"])
    except (KeyError, ValueError, AttributeError, TypeError):
        return False

    # --- Covered person ---------------------------------------------------------
    if claim.get("patient_coverage_status") not in (
        "student",
        "student_spouse",
        "student_civil_union_partner",
        "student_domestic_partner",
    ):
        return False

    # --- Causal condition -------------------------------------------------------
    # READING: cause. "There exists a condition that: Is demonstrated to cause the illness
    # of infertility": a specific identified causal condition is required; unexplained
    # infertility (no identified cause) does not satisfy this bullet.
    for key in (
        "causal_condition_demonstrated",
        "condition_recognized_by_physician_or_specialist",
        "condition_documented_in_records",
    ):
        if _bool(claim, key) is not True:
            return False

    # --- Sterilization and natural physiologic process --------------------------
    # READING: "You or your partner has not had a voluntary sterilization" and "You or
    # your partner does not have infertility that is due to a natural physiologic process":
    # coverage is barred if either the patient or the partner is affected, and "partner"
    # includes the partner with whom conception is attempted, covered or not.
    for key in (
        "patient_voluntary_sterilization",
        "partner_voluntary_sterilization",
        "patient_infertility_due_to_natural_process",
        "partner_infertility_due_to_natural_process",
    ):
        if _bool(claim, key) is not False:
            return False

    # --- Less costly treatment --------------------------------------------------
    if _bool(claim, "less_costly_covered_treatment_could_succeed") is not False:
        return False

    # --- Table row --------------------------------------------------------------
    sex = claim.get("patient_sex")
    partner_sex = claim.get("partner_sex")
    if sex not in ("female", "male") or partner_sex not in ("male", "female", "none"):
        return False

    # READING: age reference date. "A female under 35 years of age", "If you are age 40
    # and older": the text names no date, so age is measured on the date of service.
    patient_age = _age_on(patient_dob, service_date)

    months = _int(claim, "months_frequent_unprotected_timed_intercourse")
    donor_cycles = _int(claim, "self_paid_donor_insemination_cycles")
    pregnancy = _bool(claim, "pregnancy_during_attempts")
    dysphoria = _bool(claim, "gender_dysphoria_diagnosis")

    # READING: intercourse months. Glossary "frequent, unprotected heterosexual sexual
    # intercourse" and table "unprotected timed sexual intercourse": both descriptions apply
    # cumulatively, so only months of frequent, unprotected, timed heterosexual intercourse count.
    # READING: donor cycles. Table column "Number of donor artificial insemination cycles:
    # Self paid/not paid for by plan": only cycles not paid for by the plan count.
    # READING: failure to become pregnant. Glossary "A disease defined by the failure to
    # become pregnant": any pregnancy during the qualifying period, however it ended,
    # defeats the definition.
    # READING: "1 year of frequent, unprotected heterosexual sexual intercourse": 1 year = 12 months.

    if sex == "female":
        older = patient_age >= 35
        required = 6 if older else 12
        fsh_window_months = 6 if older else 12

        if partner_sex == "male":
            route_a = months is not None and months >= required
            route_b = donor_cycles is not None and donor_cycles >= required
            if not (route_a or route_b):
                return False
            # READING: glossary versus table for a female with a male partner. Glossary
            # "For a female with a male partner, after: 1 year [or] 6 months of frequent,
            # unprotected heterosexual sexual intercourse": the table's route "B. At least 12
            # [6] cycles of donor insemination" meets the table requirement but does not
            # establish infertility; only the intercourse period or the gender dysphoria
            # prong does.
            glossary_infertile = (route_a and pregnancy is False) or dysphoria is True
        else:
            # Female without a male partner: table requires donor insemination cycles.
            route_b = donor_cycles is not None and donor_cycles >= required
            if not route_b:
                return False
            glossary_infertile = pregnancy is False or dysphoria is True

        if not glossary_infertile:
            return False

        # --- FSH criteria (female rows only) ------------------------------------
        # READING: FSH applies only to females. The male rows read "Does not apply" in the
        # FSH columns, so no FSH test is required for a male patient or his partner.
        tests = claim.get("fsh_tests")
        if not isinstance(tests, list):
            return False
        valid = []
        for t in tests:
            if not isinstance(t, dict) or t.get("unmedicated_day3") is not True:
                continue
            try:
                t_date = _parse(t["date"])
                value = float(t["value_miu_ml"])
            except (KeyError, ValueError, AttributeError, TypeError):
                return False
            if t_date <= service_date:
                valid.append((t_date, value))
        if not valid:
            return False
        valid.sort(key=lambda x: x[0])
        latest_date, latest_value = valid[-1]

        # READING: FSH window. "You need to have an unmedicated day 3 FSH test done within
        # the past: 12 months [6 months]" and "in your most recent lab test": the window runs
        # back from the date of service, and the most recent unmedicated day 3 test on or
        # before that date must fall strictly inside it.
        if latest_date <= _months_before(service_date, fsh_window_months):
            return False

        if patient_age >= 40:
            # READING: age 40 and older. "must be less than 19 mIU/mL in all prior tests
            # performed after age 40": at least one unmedicated day 3 test must have been
            # performed on or after the 40th birthday, and every such test must be below 19.
            after_40 = [v for d, v in valid if _age_on(patient_dob, d) >= 40]
            if not after_40 or any(v >= 19 for v in after_40):
                return False
        else:
            if not latest_value < 19:
                return False
        return True

    # sex == "male"
    if partner_sex != "female":
        # READING: male without a female partner. The table has rows only for "A male of
        # any age with a female partner"; with no row, "the requirement for the number of
        # months trying to conceive" cannot be met, so he is not eligible.
        return False

    try:
        partner_dob = _parse(claim["partner_date_of_birth"])
    except (KeyError, ValueError, AttributeError, TypeError):
        return False
    partner_age = _age_on(partner_dob, service_date)
    required = 6 if partner_age >= 35 else 12
    if months is None or months < required:
        return False

    # READING: male with a female partner. The glossary has no prong for "a male with a
    # female partner"; he is infertile only if the couple meets "For a female with a male
    # partner, after: 1 year [or] 6 months of frequent, unprotected heterosexual sexual
    # intercourse" by the female partner's age, or the gender dysphoria prong applies.
    if not (pregnancy is False or dysphoria is True):
        return False

    return True
