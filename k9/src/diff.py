"""Behavioural diff between the old version (expert port, certificate level) and the Wellfleet encoding.

Usage: python3 diff.py            -> results/diff_summary.md and results/patterns.tsv
Case space: the pilot's data/cases.pkl (907,200 boundary-value claims). New facts (tier1_failed, med_nec) are
crossed with every case.
"""

import itertools
import pickle
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent.parent
sys.path.insert(0, str(PILOT / "src"))
sys.path.insert(0, str(HERE))

import expert  # noqa: E402
import wellfleet  # noqa: E402

RESULTS = HERE.parent / "results"

PLAUSIBLE = [dict(zip(wellfleet.READINGS, combo)) for combo in itertools.product(
    ["benefit", "listed"], wellfleet.READINGS["cause"], wellfleet.READINGS["asrm"])]


def rname(r):
    return f"excl={r['exclusion']},cause={r['cause']},asrm={r['asrm']}"


def old_reasons(claim):
    """Why the old version denies (first failing condition), for pattern labels."""
    if claim["service_type"] not in expert.COMPREHENSIVE_SERVICES:
        return "service not in benefit"
    if not expert.patient_is_infertile(claim):
        return "not infertile (glossary)"
    if claim["patient_has_had_voluntary_sterilization"] != "no":
        return "sterilization"
    if claim["demonstrated_and_documented_condition_causing_infertility"] in expert.NATURAL_CONDITIONS:
        return "natural process"
    if claim["successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"] != "no":
        return "less costly treatment"
    if not expert.meets_policy_wording_table_reqs(claim):
        return "table (contact months / donor cycles / FSH)"
    return "covered"


def main():
    data = pickle.load(open(PILOT / "data" / "cases.pkl", "rb"))
    cases = data["cases"]
    old_labels = data["labels"]["original"]
    expert.set_params({})

    patterns = defaultdict(Counter)  # key -> Counter of outcome signatures
    totals = Counter()
    for (claim, meta), old in zip(cases, old_labels):
        reason = old_reasons(claim)
        for t1, mn in itertools.product([True, False], repeat=2):
            new = tuple(wellfleet.covered(claim, t1, mn, r) for r in PLAUSIBLE)
            void = wellfleet.covered(claim, t1, mn, {"exclusion": "void", "cause": "asrm", "asrm": "history"})
            if all(n == old for n in new):
                kind = "same"
            elif all(n != old for n in new):
                kind = "robust change"
            else:
                kind = "reading-dependent"
            totals[(kind, old)] += 1
            if kind == "same":
                continue
            person = f"{meta['sex']}/{meta['partner']}" + (f"/p{meta['partner_age']}" if meta["partner_age"] else "")
            band = "<35" if meta["age"] < 35 else ("35-39" if meta["age"] < 40 else "40+")
            key = (kind, meta["service"], person, band, reason, f"tier1={t1},mednec={mn}",
                   "old=covered" if old else "old=denied")
            patterns[key][new] += 1
            _ = void

    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "patterns.tsv", "w") as f:
        f.write("kind\tservice\tperson\tage_band\told_reason\tnew_facts\told\tn_cases\tnew_outcomes_by_reading\n")
        for key, sigs in sorted(patterns.items(), key=lambda kv: -sum(kv[1].values())):
            for sig, n in sigs.most_common():
                outs = ";".join(f"{rname(r)}:{'C' if v else 'N'}" for r, v in zip(PLAUSIBLE, sig))
                f.write("\t".join(map(str, key)) + f"\t{n}\t{outs}\n")

    n = len(cases) * 4
    with open(RESULTS / "diff_summary.md", "w") as f:
        f.write("# K9 diff summary\n\n")
        f.write(f"Cases: {len(cases):,} claims x 4 combinations of new facts = {n:,}. Readings: {len(PLAUSIBLE)} "
                "plausible (exclusion benefit/listed x cause x asrm); 'void' reported separately.\n\n")
        f.write("| kind | old outcome | cases |\n|---|---|---|\n")
        for (kind, old), c in sorted(totals.items()):
            f.write(f"| {kind} | {'covered' if old else 'denied'} | {c:,} |\n")
        f.write(f"\nDistinct pattern keys: {len(patterns)} (see patterns.tsv)\n")
    print(open(RESULTS / "diff_summary.md").read())


if __name__ == "__main__":
    main()
