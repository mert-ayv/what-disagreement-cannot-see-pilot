"""Compare kA (fixed interface) with kB (self-defined fields) per family. Descriptive, not pre-registered.
Robustness: also reported without the contradictory grid cases (no partner, but partner sterilization 'yes')."""
import pickle, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src")); sys.path.insert(0, str(HERE.parent / "kA"))
import evaluate_A as A
import expert
from evaluate_B import points, DONOR

FAM = [("Claude", "", "claude", {"member_1"}, {"insurer_1", "insurer_2", "member_2", "member_3"}),
       ("GPT", "_gpt_r2", "gpt", {"member_1", "member_2", "member_3"}, {"member_1", "member_2", "member_3"}),
       ("Gemini", "_gemini", "gemini", set(), None)]


def main():
    g = A.grid(); N = len(g)
    pts = [points(c, m) for c, m in g]
    consistent = [not (m["partner"] == "no_partner" and m["partner_sterilized"] == "yes") for _, m in g]
    expert.set_params({}); ref = [bool(expert.covered_under_benefit(c)) for c, _ in g]
    L = ["# kA vs kB per family (descriptive)", "",
         "Columns: kA fixed interface | kB self-defined fields. 'cons.' = without contradictory cases "
         "(no partner but partner sterilization 'yes').", ""]
    for lab, sa, sb, dropA, dropB in FAM:
        pa = HERE.parent / "kA" / "results" / f"preds{sa}.pkl"; pb = HERE / "results" / f"preds_{sb}.pkl"
        if not (pa.exists() and pb.exists()):
            L.append(f"## {lab}: missing results"); continue
        PA = {n: v for n, v in pickle.load(open(pa, "rb"))["preds"].items()}
        PB = {n: r["met"] for n, r in pickle.load(open(pb, "rb")).items()}
        L += [f"## {lab}", "", "| Measure | kA | kB | kA cons. | kB cons. |", "|---|---|---|---|---|"]
        def neu_dis(P, mask):
            ns = [n for n in P if n.startswith("neutral")]
            return sum(1 for k in range(N) if mask[k] and len({P[n][k] is True for n in ns}) > 1)
        allm = [True] * N
        L.append(f"| Neutral disagreement within family | {neu_dis(PA, allm):,} | {neu_dis(PB, allm):,} | "
                 f"{neu_dis(PA, consistent):,} | {neu_dis(PB, consistent):,} |")
        def slack(P, drop, mask):
            mem = [n for n in P if n.startswith("member") and n not in drop]
            ins = [n for n in P if n.startswith("insurer") and n not in drop]
            if not mem or not ins:
                return None
            idx = [k for k in range(N) if mask[k] and sum(P[n][k] is True for n in mem) * 2 > len(mem)
                   and sum(P[n][k] is True for n in ins) * 2 < len(ins)]
            anyp = sum(Counter(p for k in idx for p in pts[k])[p] > 0 for p in A.POINTS)
            only = Counter(next(iter(pts[k])) for k in idx if len(pts[k]) == 1)
            return len(idx), anyp, sum(only[p] > 0 for p in A.POINTS)
        for name, mask in (("all", allm), ("cons.", consistent)):
            a = slack(PA, dropA, mask); b = slack(PB, dropB or set(), mask)
            fmt = lambda x: "not measurable" if x is None else f"{x[0]:,} cases; {x[1]} of 6 any, {x[2]} of 6 single"
            L.append(f"| Member vs insurer strict slack ({name}) | {fmt(a)} | {fmt(b)} | | |")
        L += ["", "Share covered per point, consistent cases (expert / neutral / member / insurer; admissible only):", ""]
        L += ["| Point | kA | kB |", "|---|---|---|"]
        for p in A.POINTS + [DONOR]:
            idx = [k for k in range(N) if consistent[k] and p in pts[k]]
            def sh(P, role, drop):
                ns = [n for n in P if n.startswith(role) and n not in drop]
                return "-" if not ns else f"{sum(sum(P[n][k] is True for k in idx) for n in ns) / (len(idx) * len(ns)):.3f}"
            e = f"{sum(ref[k] for k in idx) / len(idx):.3f}"
            cell = lambda P, drop: f"{e} / {sh(P,'neutral',drop)} / {sh(P,'member',drop)} / {sh(P,'insurer',drop)}"
            L.append(f"| {p[:45]} | {cell(PA, dropA)} | {cell(PB, dropB or set())} |")
        L.append("")
    (HERE / "results" / "compare_AB.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
