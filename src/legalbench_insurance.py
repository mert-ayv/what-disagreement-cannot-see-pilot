"""LegalBench insurance_policy_interpretation with current models: do they recognise ambiguity?

133 policy-claim pairs, labels A (covered) / B (not covered) / C (ambiguous) from crowdworkers, joined
with the raw crowd responses and the item author's design (data/legalbench_insurance/merged.json).

Conditions:
  standard  LegalBench's base prompt verbatim (5-shot, answer a letter), RUNS runs per model
  reason    same prompt, plus a one-sentence reason; 1 run (for reading what the models resolve)

Questions for the report: accuracy against the crowd label; recall on "ambiguous"; on crowd-ambiguous
cases, do models resolve them, and do all models resolve them the same way (the shared blind spot);
does the models' "ambiguous" rate follow how split the crowd actually was.

Usage:
  python legalbench_insurance.py check                  # free: data, prompt, parser, scorer
  python legalbench_insurance.py run [family ...]       # default all families in config.MODELS; resumable
  python legalbench_insurance.py report
Writes results/legalbench/<condition>/<family>.json, results/summary_legalbench.md,
results/legalbench_review.md.
"""

import collections
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from config import DATA, EXTRA_MODELS, MODELS, RESULTS
from llm_clients import generate

DATA_DIR = DATA / "legalbench_insurance"
OUT = RESULTS / "legalbench"
RUNS = 3
CONDITIONS = {"standard": RUNS, "reason": 1}
WORKERS = {"astra": 4, "astra_max": 4, "claude": 6, "openai": 6, "openai_max": 6, "gemini": 2}
RUNS_BY_FAMILY = {"openai_max": {"standard": 1, "reason": 1}, "astra": {"standard": 0, "reason": 1},
                  "astra_max": {"standard": 0, "reason": 1}}
SUBSET = {f: (lambda it: it["label"] == "C") for f in ("astra", "astra_max")}  # the expensive model only on the crowd-ambiguous cases
ALL_MODELS = {**MODELS, **EXTRA_MODELS}  # Gemini free tier has a low request rate
LETTERS = {"A": "covered", "B": "not covered", "C": "ambiguous"}

BASE = (DATA_DIR / "base_prompt.txt").read_text() if (DATA_DIR / "base_prompt.txt").exists() else None
REASON_SUFFIX = ("\n\nReply in exactly this format:\nLabel: <A, B or C>\nReason: <one sentence>")


def items():
    return json.loads((DATA_DIR / "merged.json").read_text())


def prompt(item, condition):
    p = BASE.replace("{{policy}}", item["policy"]).replace("{{claim}}", item["claim"])
    return p + REASON_SUFFIX if condition == "reason" else p


def parse(text):
    t = (text or "").strip().strip("*").strip()
    m = re.search(r"Label:\s*\**\s*([ABC])(?![A-Za-z])", t)
    if m:
        return m.group(1)
    # a bare letter, alone or followed by punctuation / a line break (not the article "A claim ...")
    m = re.match(r"\(?([ABC])\)?\s*(?:$|[:.)\n])", t)
    if m:
        return m.group(1)
    m = re.search(r"(?:answer|label) is:?\s*\**\(?([ABC])\b", t, re.I)
    return m.group(1) if m else "unparsed"


def reason_of(text):
    m = re.search(r"Reason:\s*(.+)", text or "")
    return m.group(1).strip()[:300] if m else ""


def run_family(family, condition):
    path = OUT / condition / f"{family}.json"
    done = json.loads(path.read_text()) if path.exists() else {}
    lock = threading.Lock()
    runs = RUNS_BY_FAMILY.get(family, CONDITIONS)[condition]
    keep = SUBSET.get(family, lambda it: True)
    jobs = [(it, r) for r in range(runs) for it in items() if keep(it) and f"{it['index']}_r{r}" not in done]

    def save():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(done, indent=1))
        tmp.replace(path)

    def one(job):
        it, r = job
        text = generate(family, prompt(it, condition), tag=f"lb_{condition}_{it['index']}_r{r}",
                        effort="medium" if family == "claude" else "high")
        with lock:
            done[f"{it['index']}_r{r}"] = {"answer": parse(text), "reason": reason_of(text), "raw": text.strip()[:400]}
            if len(done) % 25 == 0:
                save()

    failed = 0
    with ThreadPoolExecutor(max_workers=WORKERS.get(family, 4)) as pool:
        for fut in [pool.submit(one, j) for j in jobs]:
            try:
                fut.result()
            except Exception as exc:
                failed += 1
                if failed <= 3:
                    print("FAIL", family, condition, type(exc).__name__, str(exc)[:150])
    save()
    print(f"{family} {condition}: {len(done)} answers, {failed} failed this run")


def answers(condition, family):
    path = OUT / condition / f"{family}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def majority(votes):
    votes = [v for v in votes if v in LETTERS]
    if not votes:
        return None
    c = collections.Counter(votes)
    top = max(c.values())
    winners = [v for v in "CAB" if c[v] == top]  # ties go to C: the model was not settled
    return winners[0]


def score(its, got):
    """got: index -> list of letters. Returns dict of metrics (majority answer per item)."""
    conf = collections.Counter()
    consistent = n = 0
    for it in its:
        votes = got.get(it["index"], [])
        maj = majority(votes)
        if maj is None:
            continue
        n += 1
        conf[(it["label"], maj)] += 1
        consistent += len(set(votes)) == 1 and len(votes) > 1
    acc = sum(conf[(l, l)] for l in LETTERS) / n if n else 0
    recall = {l: conf[(l, l)] / max(1, sum(conf[(l, p)] for p in LETTERS)) for l in LETTERS}
    return {"n": n, "acc": acc, "recall": recall, "conf": conf, "consistent": consistent,
            "pred_c": sum(conf[(l, "C")] for l in LETTERS) / n if n else 0}


def check():
    its = items()
    print(f"{len(its)} items; labels", dict(collections.Counter(i["label"] for i in its)),
          "; design", dict(collections.Counter(i["design"] for i in its)))
    assert BASE, "data/legalbench_insurance/base_prompt.txt missing"
    p = prompt(its[0], "reason")
    print(f"prompt chars {len(p)}; ends with:\n{p[-400:]}\n")
    for t, want in [("B", "B"), ("**C**", "C"), ("Label: A\nReason: x", "A"), ("A claim like this is covered. Label: B", "B"),
                    ("The answer is C: ambiguous", "C"), ("I cannot tell", "unparsed")]:
        assert parse(t) == want, (t, parse(t), want)
    gold = {i["index"]: [i["label"]] * 3 for i in its}
    s = score(its, gold)
    assert abs(s["acc"] - 1) < 1e-9 and s["consistent"] == len(its)
    always_c = score(its, {i["index"]: ["C"] for i in its})
    print(f"parser ok; oracle scores {s['acc']:.0%}; always-'C' baseline {always_c['acc']:.0%}; "
          f"majority-class baseline = {max(collections.Counter(i['label'] for i in its).values()) / len(its):.0%}")
    calls = sum(CONDITIONS.values()) * len(its)
    print(f"calls per model: {calls} (about {len(p) // 4:,} input tokens each); models: {list(MODELS)}")


def report():
    its = items()
    by_idx = {i["index"]: i for i in its}
    fams = [f for f in ALL_MODELS if answers("standard", f)]
    lines = ["# LegalBench insurance_policy_interpretation: do current models recognise ambiguity?", "",
             f"{len(its)} cases; crowd labels A covered {sum(i['label'] == 'A' for i in its)}, B not covered "
             f"{sum(i['label'] == 'B' for i in its)}, C ambiguous {sum(i['label'] == 'C' for i in its)}. "
             f"LegalBench base prompt verbatim (5-shot), {RUNS} runs; majority answer per case (ties count as C). "
             f"Majority-class baseline (always C): {sum(i['label'] == 'C' for i in its) / len(its):.0%}.", "",
             "| Model | n | Accuracy | Recall covered | Recall not covered | Recall ambiguous | Answers 'ambiguous' | "
             "Same answer in all runs |", "|---|---|---|---|---|---|---|---|"]
    maj = {}
    for f in fams:
        a = answers("standard", f)
        got = collections.defaultdict(list)
        for k, v in a.items():
            got[int(k.split("_r")[0])].append(v["answer"])
        maj[f] = {i: majority(v) for i, v in got.items()}
        s = score(its, got)
        lines.append(f"| {f} ({ALL_MODELS[f]['model']}) | {s['n']} | {s['acc']:.0%} | {s['recall']['A']:.0%} | "
                     f"{s['recall']['B']:.0%} | {s['recall']['C']:.0%} | {s['pred_c']:.0%} | {s['consistent']}/{s['n']} |")
    for f in fams:
        a = answers("standard", f)
        got = collections.defaultdict(list)
        for k, v in a.items():
            got[int(k.split("_r")[0])].append(v["answer"])
        s = score(its, got)
        lines += ["", f"Confusion, {f} (rows crowd, columns model): ", "",
                  "| crowd \\ model | A | B | C |", "|---|---|---|---|"]
        for l in LETTERS:
            lines.append(f"| {l} | " + " | ".join(str(s["conf"][(l, p)]) for p in LETTERS) + " |")

    # shared resolution of crowd-ambiguous cases
    amb = [i for i in its if i["label"] == "C"]
    lines += ["", "## Crowd-ambiguous cases (C)", ""]
    if fams:
        shared = [i for i in amb if all(maj[f].get(i["index"]) in ("A", "B") for f in fams)
                  and len({maj[f].get(i["index"]) for f in fams}) == 1]
        any_c = [i for i in amb if any(maj[f].get(i["index"]) == "C" for f in fams)]
        lines += [f"- {len(any_c)} of {len(amb)} flagged ambiguous by at least one model.",
                  f"- {len(shared)} of {len(amb)} resolved the same way by every model (no model would reveal "
                  f"the ambiguity by disagreeing): covered {sum(maj[fams[0]][i['index']] == 'A' for i in shared)}, "
                  f"not covered {sum(maj[fams[0]][i['index']] == 'B' for i in shared)}.", ""]
        # graded: does the model 'C' rate follow how split the crowd was?
        lines += ["Model 'ambiguous' rate by how split the crowd was (share of the larger of yes / no):", "",
                  "| Crowd split | n | " + " | ".join(fams) + " |", "|---|---|" + "---|" * len(fams)]
        buckets = [("clear (>= 80%)", 0.8, 1.01), ("leaning (60 to 80%)", 0.6, 0.8), ("split (< 60%)", 0, 0.6)]
        for name, lo, hi in buckets:
            b = [i for i in its if lo <= max(i["p_yes"], i["p_no"]) < hi]
            cells = [f"{sum(maj[f].get(i['index']) == 'C' for i in b) / max(1, len(b)):.0%}" for f in fams]
            lines.append(f"| {name} | {len(b)} | " + " | ".join(cells) + " |")
        lines += ["", "By the item author's design (controversial vs written to be clear):", "",
                  "| Design | Crowd label | n | " + " | ".join(f"{f}: A/B/C" for f in fams) + " |",
                  "|---|---|---|" + "---|" * len(fams)]
        for (d, l), n in sorted(collections.Counter((i["design"], i["label"]) for i in its).items()):
            sel = [i for i in its if i["design"] == d and i["label"] == l]
            cells = ["/".join(str(sum(maj[f].get(i["index"]) == x for i in sel)) for x in "ABC") for f in fams]
            lines.append(f"| {d} | {l} | {n} | " + " | ".join(cells) + " |")
    (RESULTS / "summary_legalbench.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    # review file: crowd-ambiguous cases every model resolved, with the reasons from the 'reason' run
    rev = ["# Crowd-ambiguous cases the models resolved (reasons from the 'reason' run)", ""]
    reasons = {f: answers("reason", f) for f in fams}
    for i in amb:
        if fams and all(maj[f].get(i["index"]) in ("A", "B") for f in fams):
            rev += [f"## {i['index']}: {i['title']} (crowd yes {i['p_yes']:.0%} / no {i['p_no']:.0%} / "
                    f"can't decide {i['p_cantdecide']:.0%}; design {i['design']})", "",
                    f"Policy: {i['policy']}", "", f"Claim: {i['claim']}", ""]
            for f in fams:
                r = reasons[f].get(f"{i['index']}_r0", {})
                rev.append(f"- {f}: majority {maj[f].get(i['index'])}; reason run: {r.get('answer', '-')}, {r.get('reason', '')}")
            rev.append("")
    (RESULTS / "legalbench_review.md").write_text("\n".join(rev) + "\n")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        check()
    elif cmd == "run":
        fams = sys.argv[2:] or list(MODELS)
        for cond in CONDITIONS:
            with ThreadPoolExecutor(max_workers=len(fams)) as pool:
                list(pool.map(lambda f: run_family(f, cond), fams))
    elif cmd == "report":
        report()


if __name__ == "__main__":
    main()
