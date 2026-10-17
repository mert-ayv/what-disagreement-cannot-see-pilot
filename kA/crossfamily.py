"""Cross-family comparison (written after the second- and third-family runs; descriptive, not pre-registered).

Reads results/preds.pkl (Claude), preds_gemini.pkl, preds_gpt_r2.pkl (GPT-6.1 Sol, amended prompt) and
preds_astra.pkl (GPT-6 Astra, amended prompt). Writes results/crossfamily.md.
"""
import pickle
from collections import Counter
import evaluate_A as E
import expert

RUNS = [("Claude", ""), ("Gemini 3.8 Flash", "_gemini"), ("GPT-6.1 Sol", "_gpt_r2"), ("GPT-6 Astra", "_astra")]
DONOR = "D donor cycles meet the table, intercourse months do not (female with male partner)"


def donor(c, m):
    if m["sex"] != "female" or m["partner"] != "male":
        return False
    need = 12 if m["age"] < 35 else 6
    return m["freq"] < need and m["timed"] < need and (c.get("num_cycles_donor_insemination") or 0) >= need


def main():
    g = E.grid()
    pts = [E.points_of(c, m) | ({DONOR} if donor(c, m) else set()) for c, m in g]
    expert.set_params({})
    ref = [expert.covered_under_benefit(c) for c, _ in g]
    P = {lab: pickle.load(open(E.HERE / "results" / f"preds{suf}.pkl", "rb"))["preds"] for lab, suf in RUNS}
    role = lambda lab, r: [n for n in P[lab] if n.startswith(r)]
    L = ["# Cross-family comparison (descriptive, not pre-registered)", ""]
    # identical outcomes within a role, and between the two GPT models
    L += ["## Do encodings of one role give identical outcomes?", ""]
    for lab, _ in RUNS:
        same = {r: all(P[lab][n] == P[lab][role(lab, r)[0]] for n in role(lab, r)) for r in E.ROLES}
        L.append(f"- {lab}: " + ", ".join(f"{r} {'identical' if s else 'differ'}" for r, s in same.items()))
    L.append(f"- GPT-6.1 Sol vs GPT-6 Astra, all nine encodings: "
             f"{'identical outcomes' if all(P['GPT-6.1 Sol'][n] == P['GPT-6 Astra'][n] for n in P['GPT-6 Astra']) else 'differ'}")
    fams = ["Claude", "Gemini 3.8 Flash", "GPT-6 Astra"]
    neu_dis_within = {f: sum(len({P[f][n][k] is True for n in role(f, 'neutral')}) > 1 for k in range(len(g))) for f in fams}
    cross = [k for k in range(len(g)) if len({P[f][n][k] is True for f in fams for n in role(f, "neutral")}) > 1]
    cc = Counter(p for k in cross for p in (pts[k] or {"(no recorded point)"}))
    L += ["", "## Neutral disagreement within and across families", "",
          "Within family: " + "; ".join(f"{f} {v:,}" for f, v in neu_dis_within.items()) + " cases.",
          f"Across the three families' neutral encodings: {len(cross):,} cases.", "",
          "| Point | Cross-family neutral disagreement |", "|---|---|"]
    for p in E.POINTS + [DONOR, "(no recorded point)"]:
        L.append(f"| {p} | {cc[p]:,} |")
    L += ["", "## Share of cases covered, per point (neutral / member / insurer; member blank where inadmissible)", "",
          "| Point | Expert port | " + " | ".join(fams) + " |", "|---|---|" + "---|" * len(fams)]
    for p in E.POINTS + [DONOR]:
        idx = [k for k in range(len(g)) if p in pts[k]]
        def sh(f, r):
            ns = role(f, r)
            return sum(sum(P[f][n][k] is True for k in idx) for n in ns) / (len(idx) * len(ns))
        cells = [f"{sh(f,'neutral'):.3f} / {sh(f,'member'):.3f} / {sh(f,'insurer'):.3f}" for f in fams]
        L.append(f"| {p} | {sum(ref[k] for k in idx) / len(idx):.3f} | " + " | ".join(cells) + " |")
    L += ["", "GPT member encodings are inadmissible under the pre-registered floor (two CodeX sterilization examples); their",
          "shares are shown for description only."]
    (E.HERE / "results" / "crossfamily.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
