"""Policy variants for the memorisation test: paired edits to the policy text and the expert port.

If a model scores well on the original policy but follows the original rules on a variant, it is
recalling the public encoding rather than translating the text.
Edits are made line by line on data/policy_comprehensive_infertility.txt and checked, so a change
in the extracted text fails loudly instead of silently producing a wrong variant.
"""

from config import DATA

BASE_TEXT = (DATA / "policy_comprehensive_infertility.txt").read_text()

# line number (1-based) -> (expected original line, replacement)
_AGE = {44: ("under 35 ", "under 37 "), 62: ("under 35 ", "under 37 "), 75: ("35 years ", "37 years "),
        100: ("35 years ", "37 years "), 127: ("under 35 ", "under 37 "), 137: ("partner 35 ", "partner 37 ")}
_FSH = {57: ("19 mIU/mL in your ", "17 mIU/mL in your "), 71: ("19 mIU/mL in your ", "17 mIU/mL in your "),
        88: ("less than 19 ", "less than 17 "), 95: ("less than 19 ", "less than 17 "),
        111: ("less than 19 ", "less than 17 "), 118: ("less than 19 ", "less than 17 ")}
_AND = {51: ("or ", "and "), 82: ("or ", "and ")}
_WINDOW = {56: ("12 months Must be less than ", "9 months Must be less than "),
           70: ("12 months Must be less than ", "9 months Must be less than ")}

VARIANTS = {
    "original": {"edits": {}, "params": {}},
    "thresholds": {"edits": {**_AGE, **_FSH}, "params": {"AGE_SPLIT": 37, "FSH_MAX": 17}},
    "logic": {"edits": {**_AND, **_WINDOW}, "params": {"CONTACT_AND": True, "FSH_WINDOW_UNDER": 9}},
}


def policy_text(variant):
    lines = BASE_TEXT.split("\n")
    for n, (expected, new) in VARIANTS[variant]["edits"].items():
        if lines[n - 1] != expected:
            raise ValueError(f"line {n}: expected {expected!r}, found {lines[n - 1]!r}")
        lines[n - 1] = new
    return "\n".join(lines)


def params(variant):
    return VARIANTS[variant]["params"]
