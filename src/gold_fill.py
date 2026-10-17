"""Hand mapping for unguided encodings (the "gold" step of P3).

The LLM adapters leave out fields that have no counterpart in the reference interface, e.g.
"provider is an infertility specialist" or "patient is covered as a student". The expert encoding
does not check these at the benefit level, so for a fair comparison they are filled with the value
meaning "requirement met". Fields that can be derived from the reference claim are derived.
Only absent or None fields are filled; whatever the LLM adapter produced is kept.

Caveat: gemini_1 asks for a pre-computed fact ("all FSH tests after 40 under 19"). It is filled with
the expert's reading (at least one test since 40, all below 19), which imports the expert's
interpretation into that encoding.
"""

import expert

NATURAL = expert.NATURAL_CONDITIONS


def _student_value(spec):
    if isinstance(spec, dict):
        allowed = spec.get("allowed") or spec.get("allowed_values") or spec.get("values") or []
        if isinstance(allowed, (list, tuple)):
            for v in allowed:
                if isinstance(v, str) and "student" in v and "partner" not in v and "dependent" not in v:
                    return v
            for v in allowed:
                if isinstance(v, str) and "student" in v:
                    return v
    return True


SCOPE_NOTE = "facts the expert does not model: provider specialty, coverage status, plan enrollment"


def fill(adapted, ref, schema, unmet=False):
    """unmet=True sets the scope facts (no expert counterpart) to 'not met' instead of 'met'."""
    out = dict(adapted or {})
    sy = int(ref["date_service_received"][:4])
    sterilized = ref.get("patient_has_had_voluntary_sterilization") == "yes"
    natural = ref.get("demonstrated_and_documented_condition_causing_infertility") in NATURAL
    for key, spec in schema.items():
        if out.get(key) is not None:
            continue
        k = key.lower()
        if "specialist" in k:
            out[key] = not unmet
        elif "semen" in k:
            dates = ref.get("abnormal_semen_analyses") or []
            fmt = str(spec.get("format", "")) if isinstance(spec, dict) else ""
            out[key] = [{"date": d, "abnormal": True} for d in dates] if "abnormal" in fmt else list(dates)
        elif "dysphoria" in k:
            out[key] = ref.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
        elif k == "covered_under_plan":
            out[key] = not unmet
        elif "treatment" not in k and any(w in k for w in ("role", "category", "coverage_type", "relationship")):
            out[key] = "not_given" if unmet else _student_value(spec)
        elif "student" in k and "dependent" in k:
            out[key] = not unmet
        elif any(w in k for w in ("coverage", "covered_role", "relationship")):
            out[key] = "not_given" if unmet else _student_value(spec)
        elif "partner" in k and ("birth" in k or "dob" in k):
            age = ref.get("age_of_patients_female_partner")
            out[key] = f"{sy - age}_01_01" if age is not None else None
        elif k == "partner_age":
            out[key] = ref.get("age_of_patients_female_partner")
        elif "steriliz" in k:
            out[key] = sterilized
        elif "natural" in k:
            out[key] = natural
        elif "after_40" in k and "fsh" in k:
            tests = expert.fsh_tests_since_age_40(ref) or []
            out[key] = bool(tests) and all(t[0] < 19 for t in tests)
    return out
