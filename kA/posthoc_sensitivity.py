"""POST HOC (written after seeing the GPT-6.1 Sol results): slack when the admissibility floor ignores the two CodeX
examples on the inverse sterilization case (patient sterilized, partner not). Not a pre-registered measure."""
import pickle, sys
from collections import Counter
import evaluate_A as E

label = sys.argv[1]
P = pickle.load(open(E.HERE / "results" / f"preds_{label}.pkl", "rb"))["preds"]
g = E.grid()
pts = [E.points_of(c, m) for c, m in g]
mem = [n for n in P if n.startswith("member") and None not in P[n][:1]]
ins = [n for n in P if n.startswith("insurer")]
strict = [k for k in range(len(g)) if sum(P[n][k] is True for n in mem) * 2 > len(mem) and sum(P[n][k] is True for n in ins) * 2 < len(ins)]
c = Counter(p for k in strict for p in (pts[k] or {"(no recorded point)"}))
print(label, "strict slack", len(strict)); [print(" ", p, c[p]) for p in E.POINTS + ["(no recorded point)"]]
for p in E.POINTS:
    idx = [k for k in range(len(g)) if p in pts[k]]
    s = lambda ns: sum(sum(P[n][k] is True for k in idx) for n in ns) / (len(idx) * len(ns))
    print(f"  dir {p}: member {s(mem):.3f} insurer {s(ins):.3f}")
