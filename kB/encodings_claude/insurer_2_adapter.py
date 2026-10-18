from datetime import date

ASSUMED_MET = [
    "billed_by_infertility_specialist",
    "patient_coverage_status",
    "condition_recognized_by_physician_or_specialist",
    "pregnancy_during_attempts",
]

_NATURAL = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _parse(s):
    y, m, d = s.split("_")
    return date(int(y), int(m), int(d))


def _fmt(d):
    return "%04d_%02d_%02d" % (d.year, d.month, d.day)


def _yes_no(v):
    if v == "yes":
        return True
    if v == "no":
        return False
    return None


def adapt(ref_claim: dict) -> dict:
    c = {}

    # Fields the reference interface does not cover: set to "requirement met".
    c["billed_by_infertility_specialist"] = True
    c["patient_coverage_status"] = "student"
    c["condition_recognized_by_physician_or_specialist"] = True
    c["pregnancy_during_attempts"] = False

    # Service type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            c["service_type"] = "intrauterine_insemination"
        elif st == "ovulation_induction_cycle_with_menotropins":
            c["service_type"] = "ovulation_induction_menotropins"
        else:
            c["service_type"] = "other"

    # Dates
    if "date_service_received" in ref_claim:
        c["service_date"] = ref_claim["date_service_received"]
    if "patient_dob" in ref_claim:
        c["patient_date_of_birth"] = ref_claim["patient_dob"]

    # Sexes
    patient_sex = ref_claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex in ("female", "male"):
        c["patient_sex"] = patient_sex
    partner_ref = ref_claim.get("sex_of_patients_partner")
    partner_sex = None
    if partner_ref in ("male", "female"):
        partner_sex = partner_ref
    elif partner_ref == "no_partner":
        partner_sex = "none"
    if partner_sex is not None:
        c["partner_sex"] = partner_sex

    # Partner date of birth, derived from the female partner's age so that the
    # partner's age on the date of service equals the reported age.
    age = ref_claim.get("age_of_patients_female_partner")
    if isinstance(age, int) and not isinstance(age, bool) and "date_service_received" in ref_claim:
        try:
            sd = _parse(ref_claim["date_service_received"])
            y = sd.year - age
            try:
                dob = date(y, sd.month, sd.day)
            except ValueError:
                dob = date(y, sd.month, sd.day - 1)
            c["partner_date_of_birth"] = _fmt(dob)
        except (ValueError, AttributeError, TypeError):
            pass

    # Gender dysphoria
    gd = _yes_no(ref_claim.get("patient_or_partner_diagnosed_with_gender_dysphoria"))
    if gd is not None:
        c["gender_dysphoria_diagnosis"] = gd

    # Causal condition and natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        c["causal_condition_demonstrated"] = True
        c["condition_documented_in_records"] = True
        natural = cond in _NATURAL
        patient_natural = False
        partner_natural = False
        if natural:
            if cond == "natural_male_reproductive_aging":
                owner_is_partner = patient_sex == "female" and partner_sex == "male"
            elif cond in ("natural_menopause", "natural_perimenopause"):
                owner_is_partner = patient_sex == "male" and partner_sex == "female"
            else:
                owner_is_partner = False
            if owner_is_partner:
                partner_natural = True
            else:
                patient_natural = True
        c["patient_infertility_due_to_natural_process"] = patient_natural
        c["partner_infertility_due_to_natural_process"] = partner_natural

    # Voluntary sterilization
    ps = _yes_no(ref_claim.get("patient_has_had_voluntary_sterilization"))
    if ps is not None:
        c["patient_voluntary_sterilization"] = ps
    pts = _yes_no(ref_claim.get("partner_has_had_voluntary_sterilization"))
    if pts is not None:
        c["partner_voluntary_sterilization"] = pts
    elif partner_sex == "none":
        c["partner_voluntary_sterilization"] = False

    # Less costly treatment
    lc = _yes_no(ref_claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"))
    if lc is not None:
        c["less_costly_covered_treatment_could_succeed"] = lc

    # Intercourse months: must be frequent, unprotected, timed and heterosexual,
    # so the count is bounded by both reference counts.
    timed = ref_claim.get("num_months_timed_unprotected_intercourse")
    frequent = ref_claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    if (
        isinstance(timed, int) and not isinstance(timed, bool)
        and isinstance(frequent, int) and not isinstance(frequent, bool)
    ):
        c["months_frequent_unprotected_timed_intercourse"] = min(timed, frequent)

    # Donor insemination cycles (reference counts only self-paid / not plan-paid)
    if "num_cycles_donor_insemination" in ref_claim:
        c["self_paid_donor_insemination_cycles"] = ref_claim["num_cycles_donor_insemination"]

    # FSH tests: ordered by date and time so the most recent test comes last.
    if "day_3_fsh_tests" in ref_claim:
        tests = list(ref_claim["day_3_fsh_tests"] or [])
        tests = sorted(tests, key=lambda t: (t[1], t[2]))
        c["fsh_tests"] = [
            {"date": t[1], "value_miu_ml": float(t[0]), "unmedicated_day3": True}
            for t in tests
        ]

    return c
