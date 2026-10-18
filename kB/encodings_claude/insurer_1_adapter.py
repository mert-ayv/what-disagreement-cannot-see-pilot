import datetime

ASSUMED_MET = [
    "provider_is_infertility_specialist",
    "coverage_role",
    "condition_recognized_by_physician_or_specialist",
    "pregnancy_during_counted_period",
]

_NATURAL = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _parse_date(s):
    if not isinstance(s, str):
        return None
    try:
        y, m, d = s.split("_")
        return datetime.date(int(y), int(m), int(d))
    except (ValueError, TypeError):
        return None


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _age(birth, on):
    return on.year - birth.year - ((on.month, on.day) < (birth.month, birth.day))


def _years_before(d, years):
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        # 29 February in a non-leap target year
        return d.replace(year=d.year - years, day=28)


def _yes_no(v):
    if v == "yes":
        return True
    if v == "no":
        return False
    return None


def adapt(ref_claim: dict) -> dict:
    out = {}

    # Service type
    st = ref_claim.get("service_type")
    if isinstance(st, str):
        if st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        elif st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_menotropins"
        elif "ovulation_induction" in st:
            out["service_type"] = "ovulation_induction_other_drug"
        else:
            out["service_type"] = "other"

    # Facts not covered by the reference interface: set to "requirement met"
    out["provider_is_infertility_specialist"] = True
    out["coverage_role"] = "student"
    out["condition_recognized_by_physician_or_specialist"] = True
    out["pregnancy_during_counted_period"] = False

    # Dates
    service_str = ref_claim.get("date_service_received")
    service_date = _parse_date(service_str)
    if service_str is not None:
        out["service_date"] = service_str
    dob_str = ref_claim.get("patient_dob")
    birth = _parse_date(dob_str)
    if dob_str is not None:
        out["patient_birth_date"] = dob_str

    # Sexes
    patient_sex = ref_claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex in ("female", "male"):
        out["patient_sex"] = patient_sex
    ps = ref_claim.get("sex_of_patients_partner")
    partner_sex = None
    if ps in ("female", "male"):
        partner_sex = ps
    elif ps == "no_partner":
        partner_sex = "none"
    if partner_sex is not None:
        out["partner_sex"] = partner_sex

    # Partner birth date derived from the female partner's age at the service date
    partner_age = ref_claim.get("age_of_patients_female_partner")
    if (partner_sex == "female" and isinstance(partner_age, int) and not isinstance(partner_age, bool)
            and service_date is not None):
        out["partner_birth_date"] = _fmt(_years_before(service_date, partner_age))

    # Gender dysphoria
    gd = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if gd is not None:
        out["gender_dysphoria_diagnosis"] = gd

    # Months of intercourse. The reference count of timed months is the counted period;
    # "frequent" holds when the frequent-intercourse months also reach the required duration.
    timed_months = ref_claim.get("num_months_timed_unprotected_intercourse")
    freq_months = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    if isinstance(timed_months, int) and not isinstance(timed_months, bool):
        out["months_unprotected_intercourse"] = timed_months
        out["intercourse_timed"] = True
    if isinstance(freq_months, int) and not isinstance(freq_months, bool):
        required = None
        if patient_sex == "female" and birth is not None and service_date is not None:
            required = 12 if _age(birth, service_date) < 35 else 6
        elif (patient_sex == "male" and partner_sex == "female"
              and isinstance(partner_age, int) and not isinstance(partner_age, bool)):
            required = 12 if partner_age < 35 else 6
        if required is not None:
            out["intercourse_frequent"] = freq_months >= required
        elif isinstance(timed_months, int) and not isinstance(timed_months, bool):
            out["intercourse_frequent"] = freq_months >= timed_months

    # Donor insemination cycles (self paid / not paid by plan)
    di = ref_claim.get("num_cycles_donor_insemination")
    if isinstance(di, int) and not isinstance(di, bool):
        out["donor_insemination_cycles_self_paid"] = di

    # Causal condition and natural physiologic process
    cond = ref_claim.get("demonstrated_and_documented_condition_causing_infertility")
    if isinstance(cond, str):
        out["causal_condition_demonstrated"] = True
        out["condition_documented_in_medical_records"] = True
        patient_nat = False
        partner_nat = False
        if cond in _NATURAL:
            holder = "patient"
            if cond in ("natural_menopause", "natural_perimenopause"):
                if patient_sex != "female" and partner_sex == "female":
                    holder = "partner"
            elif cond == "natural_male_reproductive_aging":
                if patient_sex != "male" and partner_sex == "male":
                    holder = "partner"
            if holder == "patient":
                patient_nat = True
            else:
                partner_nat = True
        out["patient_infertility_due_to_natural_physiologic_process"] = patient_nat
        out["partner_infertility_due_to_natural_physiologic_process"] = partner_nat

    # Voluntary sterilization
    pst = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    if pst is not None:
        out["patient_voluntary_sterilization"] = pst
    prst = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if prst is not None:
        out["partner_voluntary_sterilization"] = prst

    # Less costly treatment
    lc = _yes_no(ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"))
    if lc is not None:
        out["pregnancy_not_attainable_by_less_costly_covered_treatment"] = not lc

    # FSH tests: the reference lists unmedicated day 3 tests
    tests = ref_claim.get("day_3_fsh_tests")
    if isinstance(tests, (list, tuple)):
        fsh = []
        for t in tests:
            try:
                level, date, _time = t
            except (TypeError, ValueError):
                continue
            fsh.append({
                "date": date,
                "value_miu_ml": float(level),
                "unmedicated": True,
                "cycle_day": 3,
            })
        out["fsh_tests"] = fsh

    return out
