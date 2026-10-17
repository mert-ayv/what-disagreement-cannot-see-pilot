"""Run every saved encoding on all cases and write the pilot's numbers.

Usage: python evaluate.py [guided|unguided|guided_thresholds|guided_logic|mock] ...
(default: guided unguided guided_thresholds guided_logic)
Writes results/summary_<mode>.md and results/per_encoding_<mode>.csv.
"""

import collections
import csv
import pickle
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import expert
from cases import load_examples
from config import DATA, RESULTS, ROOT

ENC_DIR = RESULTS / "encodings"
PRED_DIR = RESULTS / "preds"
PYTHON = ROOT / ".venv/bin/python"
SRC = ROOT / "src"


def run(mode, enc_path):
    out = PRED_DIR / mode / (enc_path.stem + ".pkl")
    out.parent.mkdir(parents=True, exist_ok=True)
    sources = [enc_path, enc_path.with_name(enc_path.stem + "_adapter.py"), DATA / "cases.pkl"]
    newest = max(p.stat().st_mtime for p in sources if p.exists())
    if out.exists() and out.stat().st_mtime < newest:
        out.unlink()  # stale: the encoding, adapter or case set changed since the last run
    if not out.exists():
        if mode.endswith("_gold"):
            worker_mode = "unguided_gold"
        elif mode.endswith("_unmet"):
            worker_mode = "unguided_unmet"
        else:
            worker_mode = "unguided" if mode.startswith("unguided") else "guided"
        args = [str(PYTHON), str(SRC / "run_encoding.py"), worker_mode,
                str(enc_path), str(out)]
        if mode.startswith("unguided"):
            args.append(str(enc_path.with_name(enc_path.stem + "_adapter.py")))
        try:
            subprocess.run(args, cwd=SRC, timeout=900, check=False)
        except subprocess.TimeoutExpired:
            pickle.dump({"crash": "timeout"}, open(out, "wb"))
        if not out.exists():
            pickle.dump({"crash": "no output"}, open(out, "wb"))
    return pickle.load(open(out, "rb"))


def schema_keys(path):
    """Field names of the SCHEMA dict an unguided encoding defines (read without running it)."""
    import ast
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SCHEMA" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                return [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    return []


def family_of(name):
    return name.rsplit("_", 1)[0]


def error_profile(preds, labels, meta, top=3):
    groups = collections.Counter()
    for p, y, m in zip(preds, labels, meta):
        if p != y:
            key = f"{m['sex']}+{m['partner']}, age {m['age']} ({m['birthday']}), fsh {m['fsh']}"
            groups[key] += 1
    return groups.most_common(top)


def revealed_hidden(names, preds, labels):
    """Errors revealed by disagreement vs hidden (all encodings in the set agree, all wrong)."""
    enc_errors = enc_revealed = 0
    case_err = case_hidden = 0
    n = len(labels)
    for k in range(n):
        values = [preds[name][k] for name in names]
        y = labels[k]
        wrong = [v != y for v in values]
        if not any(wrong):
            continue
        case_err += 1
        unanimous = len(set(values)) == 1
        if unanimous:
            case_hidden += 1
        for v, w in zip(values, wrong):
            if w:
                enc_errors += 1
                if not unanimous:
                    enc_revealed += 1
    return {
        "encodings": len(names),
        "encoding_errors": enc_errors,
        "revealed_share": enc_revealed / enc_errors if enc_errors else None,
        "error_cases": case_err,
        "hidden_cases": case_hidden,
        "hidden_case_share": case_hidden / case_err if case_err else None,
    }


def pct(x):
    return "n/a" if x is None else f"{x:.1%}"


def evaluate(mode):
    data = pickle.load(open(DATA / "cases.pkl", "rb"))
    variant = mode.split("_", 1)[1] if mode.startswith("guided_") else "original"
    labels = data["labels"][variant]
    original = data["labels"]["original"]
    meta = [m for _, m in data["cases"]]
    ex = load_examples()
    expert.set_params(__import__("variants").params(variant))
    ex_labels = [expert.covered_under_benefit(c) for _, c, _ in ex]
    expert.set_params({})
    n_cov = sum(labels)

    enc_dir = ENC_DIR / (mode.rsplit("_", 1)[0] if mode.endswith(("_gold", "_unmet")) else mode)
    files = sorted(p for p in enc_dir.glob("*.py") if not p.stem.endswith("_adapter"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda p: run(mode, p), files))
    rows, preds = [], {}
    for path, res in zip(files, results):
        name = path.stem
        if "crash" in res:
            rows.append({"encoding": name, "crash": res["crash"].strip().splitlines()[-1][:120]})
            continue
        p, pe = res["enumerated"], res["examples"]
        preds[name] = p
        errors = sum(a != b for a, b in zip(p, labels))
        denied = sum(1 for a, b in zip(p, labels) if b and a is not True)
        granted = sum(1 for a, b in zip(p, labels) if not b and a is True)
        rows.append({
            "encoding": name,
            "crash": "",
            "raised_on_cases": sum(v is None for v in p),
            "test_cases_correct": f"{sum(a == b for a, b in zip(pe, ex_labels))}/{len(ex_labels)}",
            "enumerated_accuracy": pct(1 - errors / len(labels)),
            "errors": errors,
            "wrongly_denied": denied,
            "wrongly_granted": granted,
            "recall_on_covered": pct(1 - denied / n_cov),
            "top_error_groups": "; ".join(f"{k} [{v}]" for k, v in error_profile(p, labels, meta)),
        })

    with open(RESULTS / f"per_encoding_{mode}.csv", "w", newline="") as f:
        fields = ["encoding", "crash", "raised_on_cases", "test_cases_correct", "enumerated_accuracy", "errors",
                  "wrongly_denied", "wrongly_granted", "recall_on_covered", "top_error_groups"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    sets = {}
    if len(preds) > 1:
        sets["all encodings, mixed families"] = sorted(preds)
        fams = collections.defaultdict(list)
        for name in preds:
            fams[family_of(name)].append(name)
        for fam, names in sorted(fams.items()):
            if len(names) > 1:
                sets[f"{fam} only (resampled)"] = sorted(names)
        firsts = [sorted(v)[0] for v in fams.values()]
        if len(firsts) > 1:
            sets["one per family"] = sorted(firsts)
    blind = {label: revealed_hidden(names, preds, labels) for label, names in sets.items()}

    lines = [f"# Pilot results: {mode}", "",
             f"{len(labels)} enumerated cases ({n_cov} covered, {n_cov / len(labels):.1%}); "
             f"{len(ex_labels)} CodeX test cases. Labels: expert port, benefit level.", "",
             "## Per encoding", "",
             "| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("crash"):
            lines.append(f"| {r['encoding']} | {r['crash']} | | | | | | |")
        else:
            lines.append(f"| {r['encoding']} | | {r['test_cases_correct']} | {r['enumerated_accuracy']} | {r['errors']} | "
                         f"{r['wrongly_denied']} | {r['wrongly_granted']} | {r['recall_on_covered']} |")
    lines += ["", "## Disagreement: revealed vs hidden errors", "",
              "| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |",
              "|---|---|---|---|---|---|"]
    for label, b in blind.items():
        lines.append(f"| {label} | {b['encodings']} | {b['encoding_errors']} | {pct(b['revealed_share'])} | "
                     f"{b['error_cases']} | {b['hidden_cases']} ({pct(b['hidden_case_share'])}) |")
    lines += ["", "## Where each encoding goes wrong (top error groups)", ""]
    for r in rows:
        if not r.get("crash") and r["errors"]:
            lines.append(f"- **{r['encoding']}:** {r['top_error_groups']}")
    if variant != "original" and preds:
        sensitive = [k for k in range(len(labels)) if labels[k] != original[k]]
        lines += ["", f"## Memorisation test: {variant} variant", "",
                  f"{len(sensitive)} cases where the variant and the original policy give different answers. "
                  "An encoding that follows the original there is recalling the public policy, not translating the text.", "",
                  "| Encoding | Follows the variant | Follows the original | Other or error |", "|---|---|---|---|"]
        for name in sorted(preds):
            p = preds[name]
            var = sum(p[k] == labels[k] for k in sensitive)
            orig = sum(p[k] == original[k] for k in sensitive)
            other = len(sensitive) - var - orig
            lines.append(f"| {name} | {pct(var / len(sensitive))} | {pct(orig / len(sensitive))} | {pct(other / len(sensitive))} |")
    if mode.startswith("unguided"):
        lines += ["", "## Input fields each encoding chose (for the hand mapping to the expert interface)", ""]
        for path in files:
            lines.append(f"- **{path.stem}:** {', '.join(schema_keys(path)) or 'no SCHEMA found'}")
    (RESULTS / f"summary_{mode}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    for m in sys.argv[1:] or ["guided", "unguided", "guided_thresholds", "guided_logic"]:
        evaluate(m)
