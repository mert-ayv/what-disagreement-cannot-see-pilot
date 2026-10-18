"""Valid-case recount (2026-10-19; descriptive, not pre-registered).

The kA grid doubles every case into partner sterilization 'yes' and 'no', including patients without a partner, for
whom 'partner sterilized: yes' is contradictory input. This script recounts the headline numbers on the 1,555,200
valid cases (F5 restricted to female patients, as in attribution_check.py). Writes results/valid_cases.md.
"""
import pickle
from collections import Counter
import evaluate_A as E
import expert

RUNS = {"Claude Opus 5.5": ("", {"member_1"}), "Gemini 3.8 Flash": ("_gemini", set()), "GPT-6 Astra": ("_astra", None)}


def main():
    expert.set_params({})
    g = E.grid(); N = len(g); F5 = E.POINTS[3]
    pts = []
    for c, m in g:
        p = set(E.points_of(c, m))
        if m["sex"] != "female":
            p.discard(F5)
        pts.append(p)
    V = [k for k, (_, m) in enumerate(g) if not (m["partner"] == "no_partner" and m["partner_sterilized"] == "yes")]
    ref = [bool(expert.covered_under_benefit(c)) for c, _ in g]
    P = {lab: pickle.load(open(E.HERE / "results" / f"preds{suf}.pkl", "rb"))["preds"] for lab, (suf, _) in RUNS.items()}
    L = ["# Valid-case recount (descriptive, not pre-registered)", "",
         f"Valid cases: {len(V):,} of {N:,} (contradictory 'no partner, partner sterilized' cases removed).", "",
         "| Family | Member vs insurer strict slack | Points (any) | Points (single point only) | "
         "Neutral disagreement within family |", "|---|---|---|---|---|"]
    for lab, (suf, drop) in RUNS.items():
        ns = [n for n in P[lab] if n.startswith("neutral")]
        within = sum(1 for k in V if len({P[lab][n][k] is True for n in ns}) > 1)
        if drop is None:
            L.append(f"| {lab} | not measurable | | | {within:,} |"); continue
        mem = [n for n in P[lab] if n.startswith("member") and n not in drop]
        ins = [n for n in P[lab] if n.startswith("insurer")]
        st = [k for k in V if sum(P[lab][n][k] is True for n in mem) * 2 > len(mem)
              and sum(P[lab][n][k] is True for n in ins) * 2 < len(ins)]
        a = Counter(p for k in st for p in pts[k]); o = Counter(next(iter(pts[k])) for k in st if len(pts[k]) == 1)
        L.append(f"| {lab} | {len(st):,} | {sum(a[p] > 0 for p in E.POINTS)} of 6 | "
                 f"{sum(o[p] > 0 for p in E.POINTS)} of 6 | {within:,} |")
    neu = {f"{lab}:{n}": [v is True for v in P[lab][n]] for lab in P for n in P[lab] if n.startswith("neutral")}
    cross = {k for k in V if len({neu[n][k] for n in neu}) > 1}
    L += ["", f"Neutral disagreement across the three families: {len(cross):,} cases.", "",
          "| Neutral encoding | Divergent from expert | Revealed within family | Revealed across families |",
          "|---|---|---|---|"]
    hidden = set()
    for n in neu:
        D = [k for k in V if neu[n][k] != ref[k]]
        fam = n.split(":")[0]
        w = sum(1 for k in D if len({neu[m][k] for m in neu if m.split(":")[0] == fam}) > 1)
        L.append(f"| {n} | {len(D):,} | {w / len(D):.1%} | {sum(k in cross for k in D) / len(D):.1%} |")
        hidden.add(frozenset(k for k in D if k not in cross))
    if len(hidden) == 1:
        H = next(iter(hidden))
        f6 = sum(1 for k in H if g[k][1]["partner_sterilized"] == "yes" and ref[k])
        f5 = sum(1 for k in H if g[k][1]["fsh"] == "tie_18_18" and not ref[k])
        L += ["", f"Hidden set identical for all nine: {len(H):,} cases = {f6:,} partner-sterilized cases the expert "
                  f"covers + {f5:,} tied-FSH cases it denies + {len(H) - f6 - f5:,} other."]
    (E.HERE / "results" / "valid_cases.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
