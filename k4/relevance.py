"""K4: which unknown facts can change the outcome of the Comprehensive Infertility coverage?

Abstract user-level facts are mapped to a claim for the expert port (pilot/src/expert.py, certificate level:
covered_under_benefit). For a case with known facts and a list of hidden facts, every combination of hidden values
is evaluated. The outcome is determined if all completions agree; a hidden fact is relevant if some pair of
completions that differ only in that fact give different outcomes.
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import expert  # noqa: E402

SERVICE_DATE = "2024_08_10"
FSH = {  # most recent unmedicated day-3 FSH situation
    "recent_ok": [(16, "2024_07_10", "12_00")],      # 1 month old, below 19
    "recent_high": [(21, "2024_07_10", "12_00")],    # 1 month old, 19 or above
    "old_ok": [(16, "2023_07_01", "12_00")],         # 13 months old, below 19
    "none": [],
}
DOMAINS = {  # values used when a fact is hidden
    "age": [30, 37, 41],
    "partner_age": [30, 37],
    "freq_months": [3, 8, 14],
    "timed_months": [3, 8, 14],
    "donor_cycles": [0, 8, 14],
    "sterilized": ["no", "yes"],
    "condition": ["other", "natural_menopause", None],
    "less_costly": ["no", "yes"],
    "fsh": list(FSH),
    "semen": [0, 2],
}


def claim(f):
    c = {
        "service_type": f["service"],
        "patient_dob": f"{2024 - f['age']}_02_01",
        "date_service_received": SERVICE_DATE,
        "sex_of_patient_trying_to_conceive": f["sex"],
        "sex_of_patients_partner": f["partner"],
        "num_months_timed_unprotected_intercourse": f["timed_months"],
        "num_months_frequent_unprotected_heterosexual_intercourse": f["freq_months"],
        "num_cycles_donor_insemination": f["donor_cycles"],
        "patient_has_had_voluntary_sterilization": f["sterilized"],
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan": f["less_costly"],
        "day_3_fsh_tests": list(FSH[f["fsh"]]),
        "patient_or_partner_diagnosed_with_gender_dysphoria": "no",
        "exclusions": [],
    }
    if f["condition"] is not None:
        c["demonstrated_and_documented_condition_causing_infertility"] = f["condition"]
    if f.get("partner_age") is not None:
        c["age_of_patients_female_partner"] = f["partner_age"]
    if f["semen"]:
        c["abnormal_semen_analyses"] = ["2024_07_01", "2024_07_15"]
    return c


def outcome(f):
    return expert.covered_under_benefit(claim(f))


def analyse(known, hidden):
    """Returns (determined outcome or None, set of relevant hidden facts)."""
    expert.set_params({})
    combos = list(itertools.product(*(DOMAINS[h] for h in hidden))) if hidden else [()]
    results = {}
    for vals in combos:
        f = dict(known, **dict(zip(hidden, vals)))
        results[vals] = outcome(f)
    outs = set(results.values())
    determined = outs.pop() if len(outs) == 1 else None
    relevant = set()
    for i, h in enumerate(hidden):
        for vals, out in results.items():
            for alt in DOMAINS[h]:
                other = vals[:i] + (alt,) + vals[i + 1:]
                if results[other] != out:
                    relevant.add(h)
    return determined, relevant
