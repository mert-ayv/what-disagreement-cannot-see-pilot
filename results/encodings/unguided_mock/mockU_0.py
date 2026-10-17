# Pipeline test only: an unguided-style encoding with its own fields.
SCHEMA = {"treatment": "str", "is_woman": "bool", "has_male_partner": "bool", "age_years": "int",
          "months_trying": "int", "donor_cycles": "int", "latest_fsh": "int|None", "fsh_age_months": "int|None",
          "eligible_flags_ok": "bool", "infertile": "bool"}
def covered_under_benefit(c):
    if c.get("treatment") not in ("iui", "ovulation_induction"): return False
    if not c.get("infertile") or not c.get("eligible_flags_ok"): return False
    if not c.get("is_woman"): return False
    need = 12 if c["age_years"] < 35 else 6
    contact = c["donor_cycles"] >= need or (c["has_male_partner"] and c["months_trying"] >= need)
    return contact and c["latest_fsh"] is not None and c["latest_fsh"] < 19 and c["fsh_age_months"] is not None and c["fsh_age_months"] <= need
