"""Load CodeX's example claims (.hdf) into Python dicts.

Values: integers stay ints, dates and atoms stay strings ('2024_08_10', 'female'),
day_3_fsh_tests -> list of (level, date, time), abnormal_semen_analyses -> list of dates.
"""

import re

from config import EXAMPLES_DIR

LINE = re.compile(r"^claim\.([a-z0-9_]+)\(claim1,\s*(.*)\)\s*$")
FSH = re.compile(r"fsh_test\(\s*(\d+)\s*,\s*([\d_]+)\s*,\s*([\d_]+)\s*\)")
SEMEN = re.compile(r"abnormal_semen_analysis\(\s*([\d_]+)\s*\)")


def _value(field, raw):
    raw = raw.strip()
    if field == "day_3_fsh_tests":
        return [(int(l), d, t) for l, d, t in FSH.findall(raw)]
    if field == "abnormal_semen_analyses":
        return SEMEN.findall(raw)
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def parse_hdf(text):
    claim = {"exclusions": []}  # every example imports no_exclusion_claim.hdf
    for line in text.splitlines():
        m = LINE.match(line.strip())
        if m:
            field, raw = m.groups()
            claim[field] = _value(field, raw)
    return claim


def load_examples():
    """[(name, claim, expected_covered)] for all CodeX example datasets."""
    out = []
    for path in sorted(EXAMPLES_DIR.glob("*.hdf")):
        expected = "_not_covered" not in path.stem
        out.append((path.stem, parse_hdf(path.read_text()), expected))
    return out
