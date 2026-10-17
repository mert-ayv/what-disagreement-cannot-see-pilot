"""Three-valued comparison of unguided encodings with the expert.

For each case, an encoding is run twice: scope facts the expert does not model (provider specialty,
coverage status, enrollment) set to "met" (preds/<mode>_gold) and to "not met" (preds/<mode>_unmet).
Same outcome both times -> that outcome; different -> undetermined (the decision depends on a fact the
reference cases do not supply). Then compared with the expert's label.

Usage: python three_valued.py unguided unguided2
"""

import collections
import pickle
import sys

import expert
from config import DATA, RESULTS

PRED = RESULTS / "preds"


def cause(claim, meta):
    if meta["sex"] == "male" and meta["partner"] == "no_partner":
        return "male without a female partner (no table row)"
    if meta["fsh"] == "tie_18_18":
        return "two identical FSH tests"
    if meta["sex"] == "female" and meta["age"] >= 40 and not expert.fsh_tests_since_age_40(claim):
        return "age 40+, no FSH test since 40th birthday"
    return f"other: {meta['sex']} with {meta['partner']} partner"


def main(modes):
    data = pickle.load(open(DATA / "cases.pkl", "rb"))
    labels, cases = data["labels"]["original"], data["cases"]
    n = len(labels)
    lines = ["# Three-valued comparison with the expert (unguided encodings)", "",
             "Scope facts without an expert counterpart are treated as unknown: an encoding's answer is "
             "'undetermined' when it changes with them. Nothing is assumed about them.", "",
             "| Encoding | Agrees with expert | Undetermined, expert covers | Undetermined, expert denies | "
             "Decides differently | of which: grants what expert denies | denies what expert covers |",
             "|---|---|---|---|---|---|---|"]
    causes_all = {}
    for mode in modes:
        for path in sorted((PRED / f"{mode}_gold").glob("*.pkl")):
            met = pickle.load(open(path, "rb"))
            unmet_path = PRED / f"{mode}_unmet" / path.name
            if "crash" in met or not unmet_path.exists():
                continue
            unmet = pickle.load(open(unmet_path, "rb"))
            a, b = met["enumerated"], unmet["enumerated"]
            counts = collections.Counter()
            causes = collections.Counter()
            for k in range(n):
                y = labels[k]
                if a[k] == b[k] and a[k] is not None:
                    if a[k] == y:
                        counts["agree"] += 1
                    else:
                        counts["differs"] += 1
                        counts["grants" if a[k] else "denies"] += 1
                        causes[cause(*cases[k]) + (" (grants)" if a[k] else " (denies)")] += 1
                else:
                    counts["und_cov" if y else "und_den"] += 1
            name = f"{mode}/{path.stem}"
            causes_all[name] = causes
            pct = lambda x: f"{counts[x]} ({counts[x] / n:.1%})"
            lines.append(f"| {name} | {pct('agree')} | {pct('und_cov')} | {pct('und_den')} | {pct('differs')} | "
                         f"{counts['grants']} | {counts['denies']} |")
    lines += ["", "## Where the decided cases differ from the expert", ""]
    for name, causes in causes_all.items():
        if causes:
            lines.append(f"- **{name}:** " + "; ".join(f"{c} [{k}]" for c, k in causes.most_common(5)))
    (RESULTS / "summary_three_valued.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1:] or ["unguided", "unguided2"])
