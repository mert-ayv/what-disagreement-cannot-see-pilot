from datetime import date


def adapt(ref_claim: dict) -> dict:
    out = {}

    def _parse(d):
        y, m, dd = (int(x) for x in str(d).split("_"))
        return date(y, m, dd)

    def _fmt(d):
        return "%04d_%02d_%02d" % (d.year, d.month, d.day)

    def _sub_years(d, years):
        try:
            return d.replace(year=d.year - years)
        except ValueError:
            return d.replace(year=d.year - years, day=28)

    # service_type
    if "service_type" in ref_claim:
        st = ref_claim["service_type"]
        if st == "intrauterine_insemination":
            out["service_type"] = "intrauterine_insemination"
        elif st == "ovulation_induction_cycle_with_menotropins":
            out["service_type"] = "ovulation_induction_menotropins"
        else:
            out["service_type"] = "other"

    # condition demonstrated/documented, natural physiologic process
    if "demonstrated_and_documented_condition_causing_infertility" in ref_claim:
        cond = ref_claim["demonstrated_and_documented_condition_causing_infertility"]
        out["infertility_condition_demonstrated"] = True
        out["infertility_condition_documented"] = True
        out["infertility_due_to_natural_physiologic_process"] = cond in (
            "natural_menopause",
            "natural_perimenopause",
            "natural_male_reproductive_aging",
            "other_natural_physiologic_process",
        )

    # voluntary sterilization
    if "patient_has_had_voluntary_sterilization" in ref_claim:
        v = str(ref_claim["patient_has_had_voluntary_sterilization"]).lower()
        if v in ("yes", "no"):
            out["voluntary_sterilization_patient_or_partner"] = (v == "yes")

    # less costly treatment
    key = "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    if key in ref_claim:
        v = str(ref_claim[key]).lower()
        if v in ("yes", "no"):
            out["less_costly_covered_treatment_could_succeed"] = (v == "yes")

    # patient sex
    if "sex_of_patient_trying_to_conceive" in ref_claim:
        out["patient_sex"] = ref_claim["sex_of_patient_trying_to_conceive"]

    # dates
    if "patient_dob" in ref_claim:
        out["patient_birth_date"] = ref_claim["patient_dob"]
    if "date_service_received" in ref_claim:
        out["service_date"] = ref_claim["date_service_received"]

    # partner
    if "sex_of_patients_partner" in ref_claim:
        ps = ref_claim["sex_of_patients_partner"]
        if ps == "no_partner":
            out["has_partner"] = False
            out["partner_sex"] = "none"
        else:
            out["has_partner"] = True
            out["partner_sex"] = ps

    # partner birth date derived from partner age at service date
    if "age_of_patients_female_partner" in ref_claim and "date_service_received" in ref_claim:
        try:
            age = int(ref_claim["age_of_patients_female_partner"])
            svc = _parse(ref_claim["date_service_received"])
            out["partner_birth_date"] = _fmt(_sub_years(svc, age))
        except Exception:
            pass

    # months of intercourse: must satisfy both "timed" and "frequent heterosexual"
    vals = []
    for k in ("num_months_timed_unprotected_intercourse",
              "num_months_frequent_unprotected_heterosexual_intercourse"):
        if k in ref_claim and ref_claim[k] is not None:
            try:
                vals.append(int(ref_claim[k]))
            except Exception:
                pass
    if vals:
        out["months_unprotected_timed_intercourse"] = min(vals)

    # donor insemination cycles
    if "num_cycles_donor_insemination" in ref_claim and ref_claim["num_cycles_donor_insemination"] is not None:
        try:
            out["donor_insemination_cycles_not_paid_by_plan"] = int(ref_claim["num_cycles_donor_insemination"])
        except Exception:
            pass

    # FSH tests
    if "day_3_fsh_tests" in ref_claim:
        tests = []
        for t in ref_claim["day_3_fsh_tests"] or []:
            try:
                if isinstance(t, dict):
                    level = t.get("level")
                    d = t.get("date")
                else:
                    level = t[0]
                    d = t[1]
                tests.append({"date": d, "value_miu_ml": float(level)})
            except Exception:
                continue
        out["fsh_tests"] = tests

    return out
