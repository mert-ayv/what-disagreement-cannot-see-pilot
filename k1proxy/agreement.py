"""K1 proxy: do human readers agree that an insurance item is undetermined?

Data: LegalBench insurance_policy_interpretation raw crowd responses (Waldon, Brodsky, Ma, Degen 2023),
../data/legalbench_insurance/crowd_main-merged.csv and merged.json (133 test items joined).
Each worker answers yes (covered) / no / cantdecide. LegalBench's label C ("ambiguous") is assigned when neither
yes nor no has a 95% CI lower bound >= 0.5, i.e. it is computed from disagreement, not from people saying
"can't decide".
"""
import csv, json
from collections import Counter, defaultdict
from statistics import mean
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data" / "legalbench_insurance"
rows = list(csv.DictReader(open(D / "crowd_main-merged.csv")))
items = defaultdict(list)
for r in rows:
    items[(r["title"], r["version"])].append(r["individual_judgment"])
CATS = ["yes", "no", "cantdecide"]


def fleiss(groups, cats):
    N = len(groups)
    P, totals, nsum = [], Counter(), 0
    for g in groups:
        n = len(g); c = Counter(g); nsum += n
        for k in cats: totals[k] += c[k]
        P.append((sum(c[k] ** 2 for k in cats) - n) / (n * (n - 1)))
    pj = {k: totals[k] / nsum for k in cats}
    Pbar, Pe = mean(P), sum(v ** 2 for v in pj.values())
    return (Pbar - Pe) / (1 - Pe), pj


groups = list(items.values())
k3, pj = fleiss(groups, CATS)
print(f"items {len(groups)}, responses {len(rows)}, mean raters/item {mean(map(len, groups)):.1f}")
print(f"category shares {', '.join(f'{k} {v:.3f}' for k, v in pj.items())}")
print(f"Fleiss kappa, 3 categories, all items: {k3:.3f}")
for design in ["unambiguous_covered", "unambiguous_uncovered", "controversial"]:
    g = [v for (t, ver), v in items.items() if ver == design]
    k, _ = fleiss(g, CATS)
    cd = mean(Counter(x)["cantdecide"] / len(x) for x in g)
    split = mean(min(Counter(x)["yes"], Counter(x)["no"]) / len(x) for x in g)
    print(f"  {design:22} items {len(g):3}  kappa {k:.3f}  mean p(cantdecide) {cd:.3f}  mean minority yes/no share {split:.3f}")

m = json.load(open(D / "merged.json"))
lab = Counter((x["design"], x["label"]) for x in m)
print("design x LegalBench label:", dict(lab))
C = [x for x in m if x["label"] == "C"]
print(f"label C items {len(C)}: mean p_cantdecide {mean(x['p_cantdecide'] for x in C):.3f}, "
      f"max {max(x['p_cantdecide'] for x in C):.3f}; items where cantdecide is the plurality: "
      f"{sum(x['p_cantdecide'] > max(x['p_yes'], x['p_no']) for x in C)}")
print(f"label C items with p_cantdecide >= 0.2: {sum(x['p_cantdecide'] >= 0.2 for x in C)}")
lt = Counter(r["subject_information.legaltraining"] for r in rows)
print("legal training field:", lt.most_common(6))
