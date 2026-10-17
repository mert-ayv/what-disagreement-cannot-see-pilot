"""Encoding of the Wellfleet 2025-26 Infertility Treatment Benefit over the pilot's claim fields.

Text: ../inputs/W_wellfleet_2025-26.txt (benefit 6, Medically Necessary definition, Family Planning exclusions)
and ../inputs/ASRM_2023.txt (the guideline the benefit names for eligibility).

Certificate level, as for the old version (expert.covered_under_benefit): no provider tier, precertification,
cost sharing or cycle limits.

Facts the old case space lacks, added as explicit dimensions:
  tier1_failed  "If the above infertility services do not result in increased fertility" (basic services tried)
  med_nec       "may be covered if the tests are determined to be Medically Necessary"

Every interpretive choice is a named reading (READINGS). Defaults are not chosen here; the diff runs all of them.
  exclusion  How the Family Planning exclusions ("Infertility Treatment (male or female)", "Ovulation induction and
             monitoring", "Injectable infertility medication, including ... menotropins") interact with benefit 6,
             which lists "Ovulation induction and monitoring" and "Artificial insemination" as covered.
             "benefit": the specific benefit prevails over the exclusion list (exclusions apply outside benefit 6).
             "listed": listed exclusions remove the overlapping items (ovulation induction, menotropins); IUI stays.
             "void": the exclusion heading removes all infertility treatment (makes benefit 6 meaningless;
             reported separately as implausible).
  cause      "when such infertility is the result of malformation, disease or dysfunction or a correctable medical
             condition otherwise covered".
             "strict": needs a documented condition that is not a natural physiologic process.
             "asrm": infertility as ASRM defines it is itself a "disease"; natural ageing does not bar coverage.
  asrm       How the ASRM definition decides who is "an appropriate candidate".
             "months": the 12 / 6 months rule (female partner under / at least 35) is the threshold for couples
             trying with intercourse; people needing donor gametes qualify by need.
             "history": the first bullet (inability "based on ... history, age, physical findings, diagnostic
             testing") is enough once a condition is documented; no month threshold.
"""

READINGS = {
    "exclusion": ["benefit", "listed", "void"],
    "cause": ["strict", "asrm"],
    "asrm": ["months", "history"],
}

NATURAL_CONDITIONS = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}

IUI = "intrauterine_insemination"
OI = "ovulation_induction_cycle_with_menotropins"


def _n(claim, field):
    v = claim.get(field)
    return v if v is not None else 0


def _age(claim):
    # Same age rule as the old version's port (intended birthday reading); imported lazily to keep this file
    # readable on its own.
    import expert
    return expert.patient_age(claim)


def asrm_candidate(claim, reading):
    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    months = max(_n(claim, "num_months_timed_unprotected_intercourse"),
                 _n(claim, "num_months_frequent_unprotected_heterosexual_intercourse"))
    if sex == "female" and partner == "male":
        if reading == "history":
            return claim.get("demonstrated_and_documented_condition_causing_infertility") is not None
        age = _age(claim)
        if age is None:
            return False
        return months >= (12 if age < 35 else 6)
    if sex == "female":
        # No male partner: "The need for medical intervention, including ... donor gametes ... as an individual or
        # with a partner", and "Nothing in this definition shall be used to deny or delay treatment ... regardless of
        # relationship status or sexual orientation".
        return True
    if sex == "male" and partner == "female":
        if reading == "history":
            return claim.get("demonstrated_and_documented_condition_causing_infertility") is not None
        page = claim.get("age_of_patients_female_partner")
        if page is None:
            return False
        return months >= (12 if page < 35 else 6)
    # Male without a female partner: IUI and ovulation induction are performed on a female; no insured female.
    return False


def cause_ok(claim, reading):
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if reading == "asrm":
        return True
    return condition is not None and condition not in NATURAL_CONDITIONS


def covered(claim, tier1_failed, med_nec, r):
    """r: dict with keys exclusion, cause, asrm."""
    service = claim.get("service_type")
    if service not in (IUI, OI):
        return False  # IVF and others: excluded ("In vitro fertilization ...") or not listed
    if r["exclusion"] == "void":
        return False
    if service == OI and r["exclusion"] == "listed":
        return False
    # Both services sit in the second list: only "If the above infertility services do not result in increased
    # fertility" and if "determined to be Medically Necessary".
    if not (tier1_failed and med_nec):
        return False
    # No sterilization bar (only reversal is excluded), no FSH criterion, no less-costly-treatment clause.
    return asrm_candidate(claim, r["asrm"]) and cause_ok(claim, r["cause"])
