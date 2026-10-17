"""InsLogicBench (ACL 2026) with current models: accuracy, and which labels rest on a resolved ambiguity?

110 Chinese insurance policies, 2,621 synthetic claim inquiries with an approved / denied label
(data/inslogicbench). The labels were built bottom-up from proposition truth values, with the rule
"if vague or insufficient -> false" (paper appendix), so a vague case is labelled as if the condition
failed. That is one reading built into the reference.

Sample: POLICIES policies (fixed seed), all their inquiries, BATCH inquiries per call (same policy, so
the long policy text is sent once per batch). Two conditions, one run each:
  binary  approved / denied, as in the benchmark
  three   approved / denied / undetermined (explicit), plus the kind of undetermined: missing_fact (the
          inquiry does not state a fact the decision depends on) or open_text (the policy wording allows
          more than one reasonable reading)

Report: accuracy per model and per scenario x exception cell; cases where every model disagrees with
the label (shared deviation); how often models flag undetermined, of which kind, and whether the
disagreements concentrate there. A review file lists those cases with an English summary, the label's
own explanation and the models' reasons, for hand classification (model error / label choice / open).

Usage:
  python inslogic.py check                # free: sample, prompt, token estimate, scorer check
  python inslogic.py run [family ...]     # resumable
  python inslogic.py report
"""

import collections
import json
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from config import DATA, MODELS, RESULTS
from llm_clients import generate

DATA_DIR = DATA / "inslogicbench"
OUT = RESULTS / "inslogic"
POLICIES = 10  # 20 doubles the sample (about 538 inquiries) and the cost
BATCH = 8
SEED = 11
CONDITIONS = ["binary", "three"]
WORKERS = {"claude": 4, "openai": 4, "gemini": 1}
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.S)
LABEL = {"赔付": "approved", "不赔付": "denied"}

PROMPT = """\
You decide insurance claims under the policy below. The policy and the inquiries are in Chinese. Use only
the policy text and the facts stated in each inquiry.

<policy>
{policy}
</policy>

For each inquiry, decide whether the insurer has to pay under this policy: "approved" or "denied".{extra}
Judge each inquiry on its own.

<inquiries>
{inquiries}
</inquiries>

Reply with a single ```json block and nothing else, in English:
[{{"inquiry": 1, "answer": "{answers}",{kind} "summary_en": "<the case in one sentence>", "reason": "<one sentence>"}}, ...]
"""

EXTRA = {
    "binary": "",
    "three": ("\nIf the policy text and the stated facts do not clearly settle the case, answer \"undetermined\" "
              "instead of choosing yourself, and say why: \"missing_fact\" if the inquiry does not state a fact the "
              "decision depends on, \"open_text\" if the policy wording allows more than one reasonable reading of "
              "the stated facts. Answer \"approved\" or \"denied\" only when the text and facts clearly decide."),
}


def load():
    policies = {p["id"]: p["policy"] for p in map(json.loads, open(DATA_DIR / "Policy.jsonl"))}
    qa = json.loads((DATA_DIR / "Q&A.json").read_text())
    return policies, qa


def sample():
    """[(policy_id, [inquiries])] for POLICIES policies chosen with a fixed seed."""
    policies, qa = load()
    by_pol = collections.defaultdict(list)
    for q in qa:
        by_pol[q["policy_id"]].append(q)
    ids = sorted(by_pol, key=lambda x: int(x) if x.isdigit() else x)
    chosen = random.Random(SEED).sample(ids, POLICIES)
    return policies, [(pid, by_pol[pid]) for pid in chosen]


def batches():
    policies, sel = sample()
    out = []
    for pid, qs in sel:
        for b in range(0, len(qs), BATCH):
            out.append((pid, b // BATCH, qs[b:b + BATCH]))
    return policies, out


def prompt(policy_text, qs, condition):
    inquiries = "\n\n".join(f"Inquiry {n + 1}: {q['question']}" for n, q in enumerate(qs))
    three = condition == "three"
    return PROMPT.format(policy=policy_text, inquiries=inquiries, extra=EXTRA[condition],
                         answers="approved | denied | undetermined" if three else "approved | denied",
                         kind=' "kind": "missing_fact | open_text | null",' if three else "")


def ask(family, condition, pid, b, qs, policy_text):
    path = OUT / condition / family / f"p{pid}_b{b}.json"
    if path.exists():
        return json.loads(path.read_text())
    reply = generate(family, prompt(policy_text, qs, condition), tag=f"inslogic_{condition}_p{pid}_b{b}",
                     effort="medium" if family == "claude" else "high")
    m = JSON_BLOCK.search(reply)
    parsed = json.loads(m.group(1) if m else reply)
    by_n = {a.get("inquiry"): a for a in parsed}
    rows = []
    for n, q in enumerate(qs):
        a = by_n.get(n + 1, {})
        rows.append({"question_id": q["question_id"], "answer": str(a.get("answer", "")).strip().lower(),
                     "kind": a.get("kind"), "summary_en": a.get("summary_en", ""), "reason": a.get("reason", "")})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    return rows


def run(family, condition):
    policies, bs = batches()
    failed = 0
    with ThreadPoolExecutor(max_workers=WORKERS.get(family, 2)) as pool:
        futures = [pool.submit(ask, family, condition, pid, b, qs, policies[pid]) for pid, b, qs in bs]
        for fut in futures:
            try:
                fut.result()
            except Exception as exc:
                failed += 1
                if failed <= 3:
                    print("FAIL", family, condition, type(exc).__name__, str(exc)[:150])
    print(f"{family} {condition}: {len(bs) - failed} of {len(bs)} batches present")


def results(condition, family):
    out = {}
    for p in (OUT / condition / family).glob("*.json"):
        for r in json.loads(p.read_text()):
            out[r["question_id"]] = r
    return out


def cell(q):
    return f"scenario {q['scenario']}{' + exception' if q['exception'] else ''}"


def check():
    policies, sel = sample()
    qs = [q for _, group in sel for q in group]
    policies_all, qa = load()
    print(f"sample: {POLICIES} of {len(policies_all)} policies, {len(qs)} of {len(qa)} inquiries")
    print("labels", dict(collections.Counter(LABEL[q["conclusion"]] for q in qs)),
          "| cells", dict(sorted(collections.Counter(cell(q) for q in qs).items())))
    full = dict(collections.Counter(LABEL[q["conclusion"]] for q in qa))
    print("full benchmark labels", full)
    _, bs = batches()
    chars = sum(len(prompt(policies[pid], b_qs, "three")) for pid, _, b_qs in bs)
    print(f"batches per condition and model: {len(bs)}; prompt characters {chars:,} "
          f"(Chinese text is roughly 0.7 to 1 token per character: about {int(chars * 0.7):,} to {chars:,} "
          f"input tokens per condition and model)")
    # scorer check: an oracle that returns the label must score 100%
    oracle = {q["question_id"]: {"answer": LABEL[q["conclusion"]]} for q in qs}
    acc = sum(oracle[q["question_id"]]["answer"] == LABEL[q["conclusion"]] for q in qs) / len(qs)
    print(f"oracle accuracy {acc:.0%}; always-'denied' baseline "
          f"{sum(LABEL[q['conclusion']] == 'denied' for q in qs) / len(qs):.0%}")
    print("\nprompt preview (first batch, condition three), last 900 characters:\n")
    pid, _, b_qs = bs[0]
    print(prompt(policies[pid], b_qs, "three")[-900:])


def report():
    policies, sel = sample()
    qs = [q for _, group in sel for q in group]
    fams = [f for f in MODELS if results("binary", f)]
    lines = ["# InsLogicBench: current models on Chinese insurance claims, and labels that rest on a reading", "",
             f"Sample: {POLICIES} policies (seed {SEED}), {len(qs)} inquiries, {BATCH} per call. Labels: approved "
             f"{sum(LABEL[q['conclusion']] == 'approved' for q in qs)}, denied "
             f"{sum(LABEL[q['conclusion']] == 'denied' for q in qs)}. Scenario 1 = covered and no exclusion "
             "(approved); 2 = not covered; 3 = covered but excluded; 4 = neither. '+ exception' = an exception "
             "to an exclusion applies.", "",
             "## Binary condition (approved / denied)", "",
             "| Model | Answered | Accuracy | Wrongly denied | Wrongly approved |", "|---|---|---|---|---|"]
    binr = {f: results("binary", f) for f in fams}
    for f in fams:
        r = binr[f]
        ans = [q for q in qs if r.get(q["question_id"], {}).get("answer") in ("approved", "denied")]
        right = sum(r[q["question_id"]]["answer"] == LABEL[q["conclusion"]] for q in ans)
        wd = sum(r[q["question_id"]]["answer"] == "denied" and LABEL[q["conclusion"]] == "approved" for q in ans)
        wa = sum(r[q["question_id"]]["answer"] == "approved" and LABEL[q["conclusion"]] == "denied" for q in ans)
        lines.append(f"| {f} ({MODELS[f]['model']}) | {len(ans)} | {right / max(1, len(ans)):.0%} | {wd} | {wa} |")
    cells = sorted({cell(q) for q in qs})
    lines += ["", "Accuracy per cell:", "", "| Cell | n | " + " | ".join(fams) + " |", "|---|---|" + "---|" * len(fams)]
    for c in cells:
        cq = [q for q in qs if cell(q) == c]
        accs = []
        for f in fams:
            a = [q for q in cq if binr[f].get(q["question_id"], {}).get("answer") in ("approved", "denied")]
            accs.append(f"{sum(binr[f][q['question_id']]['answer'] == LABEL[q['conclusion']] for q in a) / max(1, len(a)):.0%}")
        lines.append(f"| {c} | {len(cq)} | " + " | ".join(accs) + " |")

    shared = [q for q in qs if fams and all(binr[f].get(q["question_id"], {}).get("answer") in ("approved", "denied")
                                            and binr[f][q["question_id"]]["answer"] != LABEL[q["conclusion"]] for f in fams)]
    lines += ["", f"Every model disagrees with the label on {len(shared)} of {len(qs)} inquiries "
              f"(label denied {sum(LABEL[q['conclusion']] == 'denied' for q in shared)}, "
              f"approved {sum(LABEL[q['conclusion']] == 'approved' for q in shared)}).", ""]

    thr = {f: results("three", f) for f in fams if results("three", f)}
    if thr:
        lines += ["## Three-valued condition (undetermined allowed)", "",
                  "| Model | Answered | Undetermined | of which missing fact / open text | Accuracy on decided | "
                  "Undetermined among binary disagreements | Undetermined among binary agreements |",
                  "|---|---|---|---|---|---|---|"]
        for f, r in thr.items():
            ans = [q for q in qs if r.get(q["question_id"], {}).get("answer") in ("approved", "denied", "undetermined")]
            und = [q for q in ans if r[q["question_id"]]["answer"] == "undetermined"]
            kinds = collections.Counter(r[q["question_id"]].get("kind") for q in und)
            dec = [q for q in ans if q not in und]
            acc = sum(r[q["question_id"]]["answer"] == LABEL[q["conclusion"]] for q in dec) / max(1, len(dec))
            b = binr.get(f, {})
            dis = [q for q in ans if b.get(q["question_id"], {}).get("answer") not in (None, "", LABEL[q["conclusion"]])]
            agr = [q for q in ans if b.get(q["question_id"], {}).get("answer") == LABEL[q["conclusion"]]]
            u = lambda group: f"{sum(r[q['question_id']]['answer'] == 'undetermined' for q in group)}/{len(group)}"
            lines.append(f"| {f} | {len(ans)} | {len(und)} ({len(und) / max(1, len(ans)):.0%}) | "
                         f"{kinds.get('missing_fact', 0)} / {kinds.get('open_text', 0)} | {acc:.0%} | {u(dis)} | {u(agr)} |")
        lines.append("")
    (RESULTS / "summary_inslogic.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    # review file: shared deviations, and cases flagged undetermined by at least two models
    flagged = [q for q in qs if sum(thr[f].get(q["question_id"], {}).get("answer") == "undetermined" for f in thr) >= 2]
    rev = ["# InsLogicBench cases for hand review", "",
           "For each case decide: model error / label choice (the label picks one reading of an open point) / "
           "genuinely open. Label explanations are the benchmark's own (Chinese).", ""]
    for title, group in [("Every model disagrees with the label", shared),
                         ("Undetermined for at least two models", [q for q in flagged if q not in shared])]:
        rev += [f"## {title} ({len(group)})", ""]
        for q in group:
            first = next((binr[f][q["question_id"]] for f in fams if q["question_id"] in binr[f]), {})
            rev += [f"### {q['question_id'][:8]} (policy {q['policy_id']}, {cell(q)}, label {LABEL[q['conclusion']]})", "",
                    f"Summary (model): {first.get('summary_en', '')}", "", f"Inquiry: {q['question']}", "",
                    f"Label explanation: {q['explain']['global']}", ""]
            rev += [f"- proposition: {p}" for p in q["explain"]["proposition"]]
            for f in fams:
                b = binr[f].get(q["question_id"], {})
                t = thr.get(f, {}).get(q["question_id"], {})
                rev.append(f"- {f}: binary {b.get('answer', '-')} ({b.get('reason', '')}); three {t.get('answer', '-')}"
                           f"{' / ' + str(t.get('kind')) if t.get('answer') == 'undetermined' else ''} ({t.get('reason', '')})")
            rev.append("")
    (RESULTS / "inslogic_review.md").write_text("\n".join(rev) + "\n")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        check()
    elif cmd == "run":
        fams = sys.argv[2:] or list(MODELS)
        for cond in CONDITIONS:
            with ThreadPoolExecutor(max_workers=len(fams)) as pool:
                list(pool.map(lambda f: run(f, cond), fams))
    elif cmd == "report":
        report()


if __name__ == "__main__":
    main()
