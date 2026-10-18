"""Attribution check (2026-10-18, after a mock check in kB; descriptive, not pre-registered).

The kA F5 predicate (tied latest FSH tests) also tagged male patients, for whom FSH requirements do not apply, and
many slack cases fall on two recorded points at once. This script recounts the strict slack per family with F5
restricted to female patients, and counts only cases where exactly one recorded point is involved.
Writes results/attribution.md.
"""
import pickle
from collections import Counter
import evaluate_A as E

RUNS = [("Claude Opus 5.5", "", {"member_1"}), ("Gemini 3.8 Flash", "_gemini", set())]  # inadmissible role encodings


def main():
    g = E.grid()
    F5 = E.POINTS[3]
    pts = []
    for c, m in g:
        p = set(E.points_of(c, m))
        if m["sex"] != "female":
            p.discard(F5)
        pts.append(p)
    L = ["# Attribution check (descriptive, not pre-registered)", "",
         "F5 restricted to female patients. 'Any' counts strict-slack cases that fall on the point (kA's rule);",
         "'only' counts strict-slack cases that fall on this point and on no other recorded point.", ""]
    for lab, suf, drop in RUNS:
        P = pickle.load(open(E.HERE / "results" / f"preds{suf}.pkl", "rb"))["preds"]
        mem = [n for n in P if n.startswith("member") and n not in drop]
        ins = [n for n in P if n.startswith("insurer")]
        strict = [k for k in range(len(g)) if sum(P[n][k] is True for n in mem) * 2 > len(mem)
                  and sum(P[n][k] is True for n in ins) * 2 < len(ins)]
        any_ = Counter(p for k in strict for p in pts[k])
        only = Counter(next(iter(pts[k])) for k in strict if len(pts[k]) == 1)
        L += [f"## {lab}: strict slack {len(strict):,} cases", "", "| Point | Any | Only |", "|---|---|---|"]
        for p in E.POINTS:
            L.append(f"| {p} | {any_[p]:,} | {only[p]:,} |")
        L += ["", f"Recovered (any): {sum(any_[p] > 0 for p in E.POINTS)} of 6. "
                  f"Recovered (only): {sum(only[p] > 0 for p in E.POINTS)} of 6.", ""]
    (E.HERE / "results" / "attribution.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
