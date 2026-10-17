"""Direction A test: admissibility, slack region, attribution to recorded points, direction.

Usage: ../.venv/bin/python evaluate_A.py            (writes results/summary.md and results/preds.pkl)
Pre-registration: PREREGISTRATION.md.
"""
import copy
import pickle
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE))
import expert  # noqa: E402
from cases import load_examples  # noqa: E402
from config import DATA  # noqa: E402
from helpers_A import Helpers  # noqa: E402

ROLES = ["neutral", "member", "insurer"]
POINTS = ["F1/P3 male with female partner", "F4 male without female partner", "F2 age 40+, no test since 40",
          "F5 tied latest FSH tests", "F6 partner sterilized, patient not", "F7 timed vs frequent across threshold"]


def grid():
    data = pickle.load(open(DATA / "cases.pkl", "rb"))
    out = []
    for claim, meta in data["cases"]:
        for ps in ("no", "yes"):
            c = dict(claim)
            c["partner_has_had_voluntary_sterilization"] = ps
            out.append((c, dict(meta, partner_sterilized=ps)))
    return out


def examples():
    out = []
    for name, c, _ in load_examples():
        if "comprehensive" not in name:
            continue
        c = dict(c)
        c["partner_has_had_voluntary_sterilization"] = "no"
        out.append((name, c))
    return out


def points_of(claim, meta):
    p = set()
    sex, partner = meta["sex"], meta["partner"]
    if sex == "male" and partner == "female":
        p.add(POINTS[0])
    if sex == "male" and partner == "no_partner":
        p.add(POINTS[1])
    if sex == "female" and meta["age"] >= 40 and not expert.fsh_tests_since_age_40(claim):
        p.add(POINTS[2])
    if meta["fsh"] == "tie_18_18":
        p.add(POINTS[3])
    if meta["partner_sterilized"] == "yes" and claim["patient_has_had_voluntary_sterilization"] == "no":
        p.add(POINTS[4])
    if partner == "male" or (sex == "male" and partner == "female"):
        ref_age = meta["age"] if sex == "female" else meta["partner_age"]
        need = 12 if ref_age < 35 else 6
        if (meta["timed"] >= need) != (meta["freq"] >= need):
            p.add(POINTS[5])
    return p


def load_fn(path):
    ns = {"__name__": "encoding"}
    exec(compile(open(path).read(), str(path), "exec"), ns)
    return ns["covered_under_benefit"]


def run_one(path):
    fn = load_fn(path)

    def pred(c):
        try:
            return bool(fn(copy.deepcopy(c), Helpers))
        except Exception:
            return None
    g = grid()
    return path.stem, [pred(c) for c, _ in g], {n: pred(c) for n, c in examples()}


def main():
    encs = sorted((HERE / "encodings").glob("*.py"))
    g = grid()
    ex = examples()
    expert.set_params({})
    ref_grid = [expert.covered_under_benefit(c) for c, _ in g]
    ref_ex = {n: expert.covered_under_benefit(c) for n, c in ex}
    ex_points = {n: points_of_example(c) for n, c in ex}
    with ProcessPoolExecutor(max_workers=3) as pool:
        res = list(pool.map(run_one, encs))
    preds = {name: grid_p for name, grid_p, _ in res}
    expreds = {name: ex_p for name, _, ex_p in res}
    pickle.dump({"preds": preds, "ex": expreds}, open(HERE / "results" / "preds.pkl", "wb"))

    L = ["# Direction A test: results", "", f"Grid: {len(g):,} cases. Encodings: {', '.join(p.stem for p in encs)}.", ""]
    # admissibility
    L += ["## Admissibility (CodeX comprehensive examples where the expert port's certificate-level outcome is the reference)", "",
          "| Encoding | Examples failed (clear) | Failed on recorded points | Grid crashes | Agreement with expert on grid |", "|---|---|---|---|---|"]
    admissible = {}
    for name in preds:
        clear_fail = [n for n in ref_ex if expreds[name][n] != ref_ex[n] and not ex_points[n]]
        point_fail = [n for n in ref_ex if expreds[name][n] != ref_ex[n] and ex_points[n]]
        crashes = sum(v is None for v in preds[name])
        agree = sum(a == b for a, b in zip(preds[name], ref_grid)) / len(ref_grid)
        admissible[name] = not clear_fail and crashes == 0
        L.append(f"| {name} | {len(clear_fail)} {clear_fail[:3]} | {len(point_fail)} | {crashes} | {agree:.4f} |")
    role_encs = [n for n in preds if not n.startswith("neutral")]
    inad = [n for n in role_encs if not admissible[n]]
    L += ["", f"Inadmissible role encodings: {len(inad)} of {len(role_encs)} {inad}", ""]

    byrole = {r: [n for n in preds if n.startswith(r) and admissible[n]] for r in ROLES}
    pts = [points_of(c, m) for c, m in g]
    # slack regions
    def covered(name, k):
        return preds[name][k] is True
    anypair, strict, neutral_dis = [], [], []
    for k in range(len(g)):
        mem = [covered(n, k) for n in byrole["member"]]
        ins = [covered(n, k) for n in byrole["insurer"]]
        neu = [covered(n, k) for n in byrole["neutral"]]
        if mem and ins and any(mem) and not all(ins):
            anypair.append(k)
        if mem and ins and sum(mem) * 2 > len(mem) and sum(ins) * 2 < len(ins):
            strict.append(k)
        if len(set(neu)) > 1:
            neutral_dis.append(k)

    def point_counts(idx):
        c = Counter()
        for k in idx:
            for p in pts[k]:
                c[p] += 1
            if not pts[k]:
                c["(no recorded point)"] += 1
        return c
    L += ["## Slack region and neutral disagreement", "",
          f"Any-pair slack (some member encoding covers, some insurer encoding denies): {len(anypair):,} cases",
          f"Strict slack (member majority covers, insurer majority denies): {len(strict):,} cases",
          f"Neutral disagreement (the neutral encodings are not unanimous): {len(neutral_dis):,} cases", "",
          "| Point | Any-pair slack | Strict slack | Neutral disagreement |", "|---|---|---|---|"]
    ca, cs, cn = point_counts(anypair), point_counts(strict), point_counts(neutral_dis)
    for p in POINTS + ["(no recorded point)"]:
        L.append(f"| {p} | {ca[p]:,} | {cs[p]:,} | {cn[p]:,} |")
    recovered_any = [p for p in POINTS if ca[p] > 0]
    recovered_strict = [p for p in POINTS if cs[p] > 0]
    L += ["", f"Recovered points, any-pair: {len(recovered_any)} of 6; strict: {len(recovered_strict)} of 6.", ""]
    # new points: unattributed slack cases grouped by features
    groups = Counter()
    for k in strict:
        if not pts[k]:
            m = g[k][1]
            band = "<35" if m["age"] < 35 else ("35-39" if m["age"] < 40 else "40+")
            groups[(m["service"][:4], m["sex"], m["partner"], band, m["gate"], m["fsh"])] += 1
    L += [f"Unattributed strict-slack cases: {sum(groups.values()):,} in {len(groups)} feature groups (top 15 below)", ""]
    for key, n in groups.most_common(15):
        L.append(f"- {key}: {n:,}")
    # direction
    L += ["", "## Direction: share of cases covered, per point", "",
          "| Point | Expert port | Neutral (mean) | Member (mean) | Insurer (mean) |", "|---|---|---|---|---|"]
    for p in POINTS:
        idx = [k for k in range(len(g)) if p in pts[k]]
        if not idx:
            continue
        def share(names):
            if not names:
                return float("nan")
            return sum(sum(preds[n][k] is True for k in idx) for n in names) / (len(idx) * len(names))
        e = sum(ref_grid[k] for k in idx) / len(idx)
        L.append(f"| {p} | {e:.3f} | {share(byrole['neutral']):.3f} | {share(byrole['member']):.3f} | {share(byrole['insurer']):.3f} |")
    (HERE / "results" / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


def points_of_example(c):
    """Recorded points an example claim touches (same predicates, from the claim fields)."""
    sex = c.get("sex_of_patient_trying_to_conceive")
    partner = c.get("sex_of_patients_partner")
    p = set()
    if sex == "male" and partner == "female":
        p.add(POINTS[0])
    if sex == "male" and partner != "female":
        p.add(POINTS[1])
    age = expert.patient_age(c)
    if sex == "female" and age is not None and age >= 40 and not expert.fsh_tests_since_age_40(c):
        p.add(POINTS[2])
    tests = c.get("day_3_fsh_tests") or []
    if tests:
        latest = max((d, t) for _, d, t in tests)
        if sum((d, t) == latest for _, d, t in tests) > 1:
            p.add(POINTS[3])
    t, f = c.get("num_months_timed_unprotected_intercourse"), c.get("num_months_frequent_unprotected_heterosexual_intercourse")
    if t is not None and f is not None and age is not None and partner == "male":
        need = 12 if age < 35 else 6
        if (t >= need) != (f >= need):
            p.add(POINTS[5])
    return p


if __name__ == "__main__":
    (HERE / "results").mkdir(exist_ok=True)
    main()
