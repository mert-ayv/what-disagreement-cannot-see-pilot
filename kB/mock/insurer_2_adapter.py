ASSUMED_MET = ["enrolled_as_student"]
def adapt(ref_claim):
    d = dict(ref_claim); d["enrolled_as_student"] = True; d.pop("day_3_fsh_tests", None); return d
