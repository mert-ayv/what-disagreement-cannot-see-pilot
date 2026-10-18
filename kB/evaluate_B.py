"""kB: the kA role test with self-defined input interfaces (encoding + adapter per encoding).

Usage: ../.venv/bin/python evaluate_B.py <label> <dir> [<dir> ...]
Writes results/summary_<label>.md and results/preds_<label>.pkl. Pre-registration: PREREGISTRATION.md.
Each case of the kA grid goes through the encoding's adapter. Outcome "met": the adapter's ASSUMED_MET fields
(facts the reference interface does not cover) set to met, the comparison with kA. Outcome "unknown": those fields
removed; where the two differ the decision depends on facts the cases do not supply (undetermined).
"""
import copy
import pickle
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE.parent / "kA"))
import expert  # noqa: E402
import evaluate_A as A  # noqa: E402

DONOR = "D donor cycles meet the table, intercourse months do not (female with male partner)"
POINTS = A.POINTS + [DONOR]


def donor(c, m):
    if m["sex"] != "female" or m["partner"] != "male":
        return False
    need = 12 if m["age"] < 35 else 6
    return m["freq"] < need and m["timed"] < need and (c.get("num_cycles_donor_insemination") or 0) >= need


def points(c, m):
    """kA predicates, with F5 (tied FSH tests) restricted to female patients (FSH applies only to them), plus D."""
    p = set(A.points_of(c, m))
    if m["sex"] != "female":
        p.discard(A.POINTS[3])
    if donor(c, m):
        p.add(DONOR)
    return p


def load(path):
    ns = {"__name__": "encoding"}
    exec(compile(path.read_text(), str(path), "exec"), ns)
    return ns


def run_one(path):
    enc = load(path)
    adp = load(path.with_name(path.stem + "_adapter.py"))
    fn, adapt = enc["covered_under_benefit"], adp["adapt"]
    assumed = list(adp.get("ASSUMED_MET", []))

    def pred(c):
        try:
            a = adapt(copy.deepcopy(c))
        except Exception:
            return None, None
        out = []
        for claim in (a, {k: v for k, v in a.items() if k not in assumed}):
            try:
                out.append(bool(fn(copy.deepcopy(claim))))
            except Exception:
                out.append(None)
        return tuple(out)

    g = A.grid()
    res = [pred(c) for c, _ in g]
    ex = {n: pred(c)[0] for n, c in A.examples()}
    return {"name": f"{path.stem}@{path.parent.name}" if MULTI else path.stem,
            "met": [r[0] for r in res], "unknown": [r[1] for r in res], "ex": ex,
            "schema": sorted((enc.get("SCHEMA") or {}).keys()), "assumed": assumed}


MULTI = False


def main(label, dirs):
    global MULTI
    MULTI = len(dirs) > 1
    paths = sorted(p for d in dirs for p in (HERE / d).glob("*.py") if not p.stem.endswith("_adapter"))
    g = A.grid()
    ex = A.examples()
    expert.set_params({})
    ref = [bool(expert.covered_under_benefit(c)) for c, _ in g]
    ref_ex = {n: expert.covered_under_benefit(c) for n, c in ex}
    ex_points = {n: A.points_of_example(c) for n, c in ex}
    pts = [points(c, m) for c, m in g]
    with ProcessPoolExecutor(max_workers=6, initializer=_set_multi, initargs=(MULTI,)) as pool:
        res = list(pool.map(run_one, paths))
    R = {r["name"]: r for r in res}
    pickle.dump(R, open(HERE / "results" / f"preds_{label}.pkl", "wb"))
    N = len(g)
    L = [f"# kB results: {label}", "", f"Grid: {N:,} cases. Encodings: {', '.join(R)}.", "",
         "## Admissibility (encoding + adapter, ASSUMED_MET set to met; same rule as kA)", "",
         "| Encoding | Clear examples failed | Failed on recorded points | Grid crashes | Agreement with expert | "
         "Undetermined (met vs unknown differ) | SCHEMA fields | ASSUMED_MET |", "|---|---|---|---|---|---|---|---|"]
    adm = {}
    for n, r in R.items():
        clear = [e for e in ref_ex if r["ex"][e] != ref_ex[e] and not ex_points[e]]
        onpt = [e for e in ref_ex if r["ex"][e] != ref_ex[e] and ex_points[e]]
        crash = sum(v is None for v in r["met"])
        agree = sum(a == b for a, b in zip(r["met"], ref)) / N
        und = sum(a != b for a, b in zip(r["met"], r["unknown"])) / N
        adm[n] = not clear and crash == 0
        L.append(f"| {n} | {len(clear)} {clear[:3]} | {len(onpt)} | {crash:,} | {agree:.4f} | {und:.2%} | "
                 f"{len(r['schema'])} | {', '.join(r['assumed']) or '-'} |")
    role_names = [n for n in R if not n.startswith("neutral")]
    inad = [n for n in role_names if not adm[n]]
    L += ["", f"Inadmissible role encodings: {len(inad)} of {len(role_names)} {inad}", ""]
    by = {r: [n for n in R if n.startswith(r) and adm[n]] for r in A.ROLES}
    cov = lambda n, k: R[n]["met"][k] is True
    anyp, strict, neu = [], [], []
    for k in range(N):
        m = [cov(n, k) for n in by["member"]]
        i = [cov(n, k) for n in by["insurer"]]
        u = [cov(n, k) for n in by["neutral"]]
        if m and i and any(m) and not all(i):
            anyp.append(k)
        if m and i and sum(m) * 2 > len(m) and sum(i) * 2 < len(i):
            strict.append(k)
        if len(set(u)) > 1:
            neu.append(k)
    cnt = lambda idx: Counter(p for k in idx for p in (pts[k] or {"(no recorded point)"}))
    ca, cs, cn = cnt(anyp), cnt(strict), cnt(neu)
    L += ["## Slack and neutral disagreement", "",
          f"Any-pair slack: {len(anyp):,}. Strict slack: {len(strict):,}. Neutral disagreement: {len(neu):,}.", "",
          "| Point | Any-pair | Strict | Neutral disagreement |", "|---|---|---|---|"]
    for p in POINTS + ["(no recorded point)"]:
        L.append(f"| {p} | {ca[p]:,} | {cs[p]:,} | {cn[p]:,} |")
    rec = [p for p in A.POINTS if cs[p] > 0]
    only = Counter(next(iter(pts[k])) for k in strict if len(pts[k]) == 1)
    rec1 = [p for p in A.POINTS if only[p] > 0]
    L += ["", f"Recovered representable points (strict, any case on the point): {len(rec)} of 6 {rec}",
          f"Recovered with cases where the point is the only one involved: {len(rec1)} of 6 {rec1}", "",
          "## Direction: share covered per point (expert / neutral / member / insurer; admissible encodings)", "",
          "| Point | Expert | Neutral | Member | Insurer |", "|---|---|---|---|---|"]
    for p in POINTS:
        idx = [k for k in range(N) if p in pts[k]]
        if not idx:
            continue
        sh = lambda ns: (sum(sum(cov(n, k) for k in idx) for n in ns) / (len(idx) * len(ns))) if ns else float("nan")
        L.append(f"| {p} | {sum(ref[k] for k in idx) / len(idx):.3f} | {sh(by['neutral']):.3f} | "
                 f"{sh(by['member']):.3f} | {sh(by['insurer']):.3f} |")
    L += ["", "## Interface: SCHEMA fields per encoding", ""]
    for n, r in R.items():
        L.append(f"- {n}: {', '.join(r['schema'])}")
    (HERE / "results" / f"summary_{label}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40]))


def _set_multi(v):
    global MULTI
    MULTI = v


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
