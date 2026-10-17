"""Generate every combination of boundary values for the comprehensive infertility benefit,
label each case with the expert port, and save them.

Service date is fixed at 2024_08_10 (as in all CodeX examples); ages, test dates and the 40th
birthday are placed relative to it, so each boundary (age 35 and 40, FSH test exactly 6 or 12
months old or one day older, level 19, ties) is hit exactly and just past.
"""

import itertools
import pickle

import expert
from config import DATA
from variants import VARIANTS, params

SERVICE_DATE = "2024_08_10"
OUT = DATA / "cases.pkl"

SERVICES = ["intrauterine_insemination", "ovulation_induction_cycle_with_menotropins", "in_vitro_fertilization"]

# (sex, partner, partner_age or None)
PEOPLE = [
    ("female", "male", None),
    ("female", "female", 34),
    ("female", "female", 35),
    ("female", "no_partner", None),
    ("male", "female", 34),
    ("male", "female", 35),
    ("male", "no_partner", None),
]

# Patient ages around 35 and 40; birthday either well past or exactly on the service date.
AGES = [34, 35, 36, 37, 39, 40]  # 36/37 cover the "thresholds" variant (split at 37)
BIRTHDAY_TIMING = {"past": "02_01", "today": "08_10"}

TIMED_MONTHS = [5, 6, 11, 12]
DONOR_CYCLES = [5, 6, 11, 12]
FREQ_MONTHS = [0, 6, 12]

# (sterilization, condition, less_costly_treatment_possible)
GATES = [
    ("no", "other", "no"),
    ("yes", "other", "no"),
    ("no", "natural_menopause", "no"),
    ("no", "natural_male_reproductive_aging", "no"),
    ("no", "other", "yes"),
]

FSH_SCENARIOS = {
    "none": [],
    "1mo_18": [(18, "2024_07_10", "12_00")],
    "1mo_19": [(19, "2024_07_10", "12_00")],
    "1mo_16": [(16, "2024_07_10", "12_00")],  # 16/17 cover the "thresholds" variant (FSH limit 17)
    "1mo_17": [(17, "2024_07_10", "12_00")],
    "9mo_exact_18": [(18, "2023_11_10", "12_00")],  # 9 months covers the "logic" variant window
    "9mo_plus1d_18": [(18, "2023_11_09", "12_00")],
    "6mo_exact_18": [(18, "2024_02_10", "12_00")],
    "6mo_plus1d_18": [(18, "2024_02_09", "12_00")],
    "12mo_exact_18": [(18, "2023_08_10", "12_00")],
    "12mo_plus1d_18": [(18, "2023_08_09", "12_00")],
    "older19_recent18": [(19, "2024_05_10", "12_00"), (18, "2024_07_10", "12_00")],
    "older18_recent19": [(18, "2024_05_10", "12_00"), (19, "2024_07_10", "12_00")],
    "tie_18_18": [(18, "2024_07_10", "12_00"), (18, "2024_07_10", "12_00")],
    "old19_dec_recent18": [(19, "2023_12_15", "12_00"), (18, "2024_07_10", "12_00")],
}

SEMEN = ["2024_07_01", "2024_07_15"]


def build_cases():
    cases = []
    for (service, (sex, partner, page), age, timing, timed, donor, freq, gate, fsh_name) in itertools.product(
        SERVICES, PEOPLE, AGES, BIRTHDAY_TIMING, TIMED_MONTHS, DONOR_CYCLES, FREQ_MONTHS, GATES, FSH_SCENARIOS
    ):
        sterilization, condition, less_costly = gate
        claim = {
            "service_type": service,
            "patient_dob": f"{2024 - age}_{BIRTHDAY_TIMING[timing]}",
            "date_service_received": SERVICE_DATE,
            "sex_of_patient_trying_to_conceive": sex,
            "sex_of_patients_partner": partner,
            "num_months_timed_unprotected_intercourse": timed,
            "num_months_frequent_unprotected_heterosexual_intercourse": freq,
            "num_cycles_donor_insemination": donor,
            "patient_has_had_voluntary_sterilization": sterilization,
            "demonstrated_and_documented_condition_causing_infertility": condition,
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan": less_costly,
            "day_3_fsh_tests": list(FSH_SCENARIOS[fsh_name]),
            "patient_or_partner_diagnosed_with_gender_dysphoria": "no",
            "exclusions": [],
        }
        if page is not None:
            claim["age_of_patients_female_partner"] = page
        if sex == "male":
            claim["abnormal_semen_analyses"] = list(SEMEN)
        meta = {
            "service": service, "sex": sex, "partner": partner, "partner_age": page, "age": age,
            "birthday": timing, "timed": timed, "donor": donor, "freq": freq,
            "gate": "/".join(gate), "fsh": fsh_name,
        }
        cases.append((claim, meta))
    return cases


def label(cases):
    """Labels per policy variant (intended birthday reading), plus the literal birthday reading."""
    labels = {}
    for variant in VARIANTS:
        expert.set_params(params(variant))
        labels[variant] = [expert.covered_under_benefit(c) for c, _ in cases]
    expert.set_params({})
    expert.LITERAL_BIRTHDAY_CLAUSE = True
    literal = [expert.covered_under_benefit(c) for c, _ in cases]
    expert.LITERAL_BIRTHDAY_CLAUSE = False
    return labels, literal


if __name__ == "__main__":
    cases = build_cases()
    labels, literal = label(cases)
    with open(OUT, "wb") as f:
        pickle.dump({"cases": cases, "labels": labels, "labels_literal_birthday": literal}, f)
    n = len(cases)
    for variant, lab in labels.items():
        changed = sum(a != b for a, b in zip(lab, labels["original"]))
        print(f"{variant:>10}: {sum(lab)} of {n} covered ({sum(lab) / n:.1%}); differs from original in {changed}")
    diff = sum(a != b for a, b in zip(labels["original"], literal))
    print(f"literal birthday clause changes the original outcome in {diff} cases")
