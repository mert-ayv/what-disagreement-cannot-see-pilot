"""Self-repair loop for unguided encodings: does feedback fix real errors, and does it know when not to?

Starting point: unguided encodings (own SCHEMA) plus their LLM adapters, run on reference claims with
no hand mapping. As generated they deny almost every claim (they ask for facts the reference interface
lacks). A repairer model gets the failing training cases and rewrites the adapter and, if needed, the
encoding. Up to ROUNDS rounds, three arms:

  labels          expected outcomes from the expert encoding; make the cases pass (the plain loop)
  labels_contest  same, but the repairer may contest an expected outcome that rests on a point the
                  policy text does not settle, instead of fitting it
  disagreement    no expert labels: feedback is where the encoding differs from an independent
                  reading of the policy text (GPT's answers from abstain_test.py, explicit prompt,
                  majority of 3 runs, "undetermined" allowed); repairer may fix, keep or escalate

Training cases: the 58 stratified cases of direct_answer.py (gap cases plus controls), so the
independent reading is already paid for. Evaluation, after the last round:
  - held-out cases from the same strata (not used in training)
  - all 907,200 enumerated cases, split into the policy gaps (three_valued.cause) and the rest
  - the 75 CodeX example cases
  - for the escalating arms: verdicts per stratum (gap strata should be escalated, the rest fixed)

Usage:
  python self_repair.py check            # free: runs the originals on the training cases, no API calls
  python self_repair.py smoke            # one repair call (labels arm, first encoding), to see tokens
  python self_repair.py run [arm ...]    # all encodings, given arms (default all); resumable
  python self_repair.py report           # full evaluation and results/summary_self_repair.md
"""

import collections
import json
import pickle
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from config import DATA, MODELS, RESULTS, ROOT
from direct_answer import select_cases
from llm_clients import RAW_DIR, generate
from prompts import GLOSSARY, INTERFACE_DOC, POLICY
from three_valued import cause

PYTHON = ROOT / ".venv/bin/python"
SRC = ROOT / "src"
ENC_DIR = RESULTS / "encodings"
OUT = RESULTS / "self_repair"

REPAIRER = "openai"  # Claude credit is used up; GPT-6.1 Sol repairs every encoding, so arms are comparable
ROUNDS = 3
MAX_SHOWN = 30  # failing cases shown per round
ALL_ENCODINGS = [  # diverse starting points, see summary_three_valued.md
    "unguided2/openai_0",  # typical: timed/frequent conflation, asks for scope facts
    "unguided2/claude_4",  # closest to the expert after hand mapping
    "unguided2/openai_1",  # also differs on identical FSH tests
    "unguided2/openai_2",  # denies every claim the expert covers, even with hand mapping
]
ACTIVE = 2  # encodings in use; about 12k input and 5k output tokens per repair call, so 2 keeps it to ~18 calls
ENCODINGS = ALL_ENCODINGS[:ACTIVE]
ARMS = ["labels", "labels_contest", "disagreement"]
GAP_STRATA = {"male without female partner", "age 40, no test since 40th birthday", "two identical FSH tests"}
GAP_CAUSES = ("male without a female partner", "two identical FSH tests", "age 40+, no FSH test")

INTERFACE = INTERFACE_DOC + """\
abnormal_semen_analyses: list of dates "YYYY_MM_DD"   (present when there are any)
patient_or_partner_diagnosed_with_gender_dysphoria: "yes" | "no"
exclusions: list   (always empty here)
"""

HEADER = """\
You maintain a Python encoding of one coverage rule of a health insurance policy. The encoding defines
its own claim fields (SCHEMA) and a function covered_under_benefit(claim). An adapter, adapt(ref_claim),
converts claims from a reference interface into the encoding's fields. Both are run on test claims.

Policy text:
<policy>
{policy}

{glossary}
</policy>

Test convention: for every test claim, the patient is a covered student, the provider is an in-network
infertility specialist, precertification was obtained, the service is medically necessary, no plan
limit is reached and no general exclusion applies. The only question is whether the claim is covered
under the comprehensive infertility services benefit.

Reference interface:
<interface>
{interface}
</interface>

Current encoding:
```python
{encoding}
```

Current adapter:
```python
{adapter}
```

{task}

<cases>
{cases}
</cases>

Reply in this order:
1. A ```json block with one entry per case: [{{"case": <number>, "verdict": "{verdicts}", "cause": "<one sentence>", "readings": "<only for {escalate}: the competing readings>"}}, ...]
2. A ```python block whose first line is `# FILE: adapter.py`, with the complete new adapter.
3. Only if you change the encoding: a ```python block whose first line is `# FILE: encoding.py`, with the complete new encoding.
Use only the Python standard library.
"""

TASKS = {
    "labels": dict(
        verdicts="fix", escalate="none",
        text="""\
Below are test claims where the encoding's answer differs from the expected outcome. The expected
outcomes come from a reference implementation and are correct. Find out why each case fails, and change
the adapter and, if needed, the encoding so these cases produce the expected outcome. Keep the encoding
faithful to the policy text for all other claims."""),
    "labels_contest": dict(
        verdicts="fix | contest", escalate="contest",
        text="""\
Below are test claims where the encoding's answer differs from the expected outcome. The expected
outcomes come from a reference implementation written by legal experts. For each case decide:
- "fix": the encoding or adapter misreads the policy or the claim. Repair it.
- "contest": the expected outcome rests on one reading of a point the policy text does not settle (no
  provision addresses the situation, or the wording allows more than one reasonable reading). Do not
  change the code to match it; name the competing readings."""),
    "disagreement": dict(
        verdicts="fix | keep | undetermined", escalate="undetermined",
        text="""\
No reference outcomes are available. Below are test claims where the encoding's answer differs from an
independent reading of the policy text by another system, or where that reading found that the policy
does not settle the case. The independent reading can be wrong. For each case decide:
- "fix": the encoding or adapter misreads the policy or the claim. Repair it.
- "keep": the encoding is right and the independent reading is wrong. Do not change the code for it.
- "undetermined": the policy text does not settle the case (no provision addresses the situation, or
  the wording allows more than one reasonable reading). Do not change the code for it; name the
  competing readings."""),
}

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.S)
PY_BLOCK = re.compile(r"```python\s*\n(.*?)```", re.S)
ANSWER = {True: "covered", False: "not covered", None: "error"}

_data = None


def data():
    global _data
    if _data is None:
        _data = pickle.load(open(DATA / "cases.pkl", "rb"))
    return _data


def training():
    """[(case id, stratum, enumeration index, claim, expert label)]; case id = position + 1."""
    return [(i + 1, name, k, claim, y) for i, (name, k, claim, y) in enumerate(select_cases(data=data()))]


def held_out(train_idx):
    sel = select_cases(seed=8, data=data(), exclude=frozenset(train_idx))
    return [(name, k) for name, k, _, _ in sel]


def independent_reading():
    """case id -> (answer, reason): majority of GPT's explicit-prompt abstention answers."""
    votes = collections.defaultdict(list)
    for path in sorted((RESULTS / "abstain").glob("explicit_openai_run*_batch*.json")):
        b = int(path.stem.rsplit("batch", 1)[1])
        for a in json.loads(path.read_text()):
            answer = str(a.get("answer", "")).strip().lower().replace(" ", "_")
            votes[b * 10 + a["case"]].append((answer, a.get("reason", "")))
    out = {}
    for cid, vs in votes.items():
        counts = collections.Counter(v for v, _ in vs)
        top = max(counts.values())
        answer = "undetermined" if counts["undetermined"] == top else counts.most_common(1)[0][0]
        out[cid] = (answer, next(r for v, r in vs if v == answer))
    return out


def run_subset(round_dir, claims):
    claims_path = round_dir / "_claims.pkl"
    out_path = round_dir / "_subset.json"
    pickle.dump(claims, open(claims_path, "wb"))
    try:
        subprocess.run([str(PYTHON), str(SRC / "run_subset.py"), str(round_dir / "encoding.py"),
                        str(round_dir / "adapter.py"), str(claims_path), str(out_path)],
                       cwd=SRC, timeout=120, check=False, capture_output=True)
        res = json.loads(out_path.read_text())
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as exc:
        res = {"crash": type(exc).__name__}
    claims_path.unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
    if isinstance(res, dict):  # file did not load: every case is an error
        return [{"pred": None, "adapted": None, "error": "crash: " + res["crash"][-300:]} for _ in claims]
    return res


def failing(arm, train, results, reading, settled):
    """Case ids that go into the next repair prompt."""
    out = []
    for (cid, _, _, _, y), r in zip(train, results):
        if cid in settled:
            continue
        if arm == "disagreement":
            answer, _ = reading[cid]
            if answer == "undetermined" or r["pred"] is None or r["pred"] != (answer == "covered"):
                out.append(cid)
        elif r["pred"] != y:
            out.append(cid)
    return out


def show_case(arm, case, r, reading):
    cid, _, _, claim, y = case
    lines = [f"Case {cid}",
             "reference claim: " + json.dumps(claim, default=str),
             "adapter produced: " + (json.dumps(r["adapted"], default=str) if r["adapted"] is not None
                                     else f"error: {r['error']}"),
             "encoding answered: " + (ANSWER[r["pred"]] if r["pred"] is not None or r["adapted"] is None
                                      else f"error: {r['error']}")]
    if arm == "disagreement":
        answer, reason = reading[cid]
        lines.append(f"independent reading: {answer.replace('_', ' ')} ({reason})")
    else:
        lines.append(f"expected: {ANSWER[y]}")
    return "\n".join(lines)


def parse_reply(text):
    m = JSON_BLOCK.search(text)
    try:
        verdicts = json.loads(m.group(1)) if m else []
    except json.JSONDecodeError:
        verdicts = []
    files = {}
    for block in PY_BLOCK.findall(text):
        first = block.lstrip().splitlines()[0] if block.strip() else ""
        for name in ("adapter.py", "encoding.py"):
            if name in first:
                files[name] = block
    return verdicts, files


def repair_one(arm, enc_name, max_rounds=ROUNDS):
    """Run (or resume) the loop for one encoding and arm. Returns the log of rounds."""
    train = training()
    reading = independent_reading()
    base = OUT / arm / enc_name.replace("/", "_")
    r0 = base / "round0"
    if not (r0 / "encoding.py").exists():
        r0.mkdir(parents=True, exist_ok=True)
        shutil.copy(ENC_DIR / f"{enc_name}.py", r0 / "encoding.py")
        shutil.copy(ENC_DIR / f"{enc_name}_adapter.py", r0 / "adapter.py")
    settled = set()  # contested / undetermined / kept cases: not shown again
    log = []
    for r in range(max_rounds + 1):
        rd = base / f"round{r}"
        results = run_subset(rd, [c[3] for c in train])
        fail = failing(arm, train, results, reading, settled)
        wrong = sum(res["pred"] != c[4] for c, res in zip(train, results))
        log.append({"round": r, "shown": len(fail[:MAX_SHOWN]), "failing": len(fail), "wrong_vs_expert": wrong,
                    "preds": [res["pred"] for res in results]})
        (rd / "train_eval.json").write_text(json.dumps(log[-1], indent=1))
        if not fail or r == max_rounds:
            break
        nxt = base / f"round{r + 1}"
        if (nxt / "verdicts.json").exists():  # resume: this repair was already done
            verdicts = json.loads((nxt / "verdicts.json").read_text())
        else:
            by_id = {c[0]: (c, res) for c, res in zip(train, results)}
            shown = fail[:MAX_SHOWN]
            task = TASKS[arm]
            prompt = HEADER.format(policy=POLICY, glossary=GLOSSARY, interface=INTERFACE,
                                   encoding=(rd / "encoding.py").read_text(), adapter=(rd / "adapter.py").read_text(),
                                   task=task["text"], verdicts=task["verdicts"], escalate=task["escalate"],
                                   cases="\n\n".join(show_case(arm, *by_id[cid], reading) for cid in shown))
            reply = generate(REPAIRER, prompt, tag=f"repair_{arm}_{enc_name.replace('/', '_')}_r{r + 1}")
            verdicts, files = parse_reply(reply)
            nxt.mkdir(parents=True, exist_ok=True)
            for name in ("encoding.py", "adapter.py"):
                (nxt / name).write_text(files.get(name) or (rd / name).read_text())
            (nxt / "verdicts.json").write_text(json.dumps({"shown": shown, "verdicts": verdicts,
                                                           "changed": sorted(files)}, indent=1))
            verdicts = json.loads((nxt / "verdicts.json").read_text())
        settled |= {v.get("case") for v in verdicts["verdicts"] if v.get("verdict") in ("contest", "undetermined", "keep")}
    return log


def check():
    """Free setup check: training data, independent reading, originals on the training cases."""
    train = training()
    reading = independent_reading()
    strata = collections.Counter(c[1] for c in train)
    print(f"training cases: {len(train)}", dict(strata))
    print(f"independent reading available for {sum(c[0] in reading for c in train)} of {len(train)}")
    ho = held_out([c[2] for c in train])
    print(f"held-out cases: {len(ho)}", dict(collections.Counter(n for n, _ in ho)),
          "overlap with training:", len({k for _, k in ho} & {c[2] for c in train}))
    # the reading per stratum should match summary_abstain.md (explicit prompt, openai)
    for s in strata:
        print(f"  {s}: reading", dict(collections.Counter(reading[c[0]][0] for c in train if c[1] == s)))
    # sanity: the expert itself, wrapped as encoding + identity adapter, must fail nothing in the label arms
    mock = OUT / "_mock" / "round0"
    mock.mkdir(parents=True, exist_ok=True)
    (mock / "encoding.py").write_text("import expert\nSCHEMA = {}\n\ndef covered_under_benefit(claim):\n"
                                      "    return expert.covered_under_benefit(claim)\n")
    (mock / "adapter.py").write_text("def adapt(ref_claim):\n    return ref_claim\n")
    res = run_subset(mock, [c[3] for c in train])
    print("expert mock: failing in labels arm:", len(failing("labels", train, res, reading, set())),
          "| disagreement arm sees:", len(failing("disagreement", train, res, reading, set())))
    for enc in ENCODINGS:
        rd = OUT / "_check" / enc.replace("/", "_")
        rd.mkdir(parents=True, exist_ok=True)
        shutil.copy(ENC_DIR / f"{enc}.py", rd / "encoding.py")
        shutil.copy(ENC_DIR / f"{enc}_adapter.py", rd / "adapter.py")
        res = run_subset(rd, [c[3] for c in train])
        print(f"{enc}: covered {sum(r['pred'] is True for r in res)}, errors {sum(r['pred'] is None for r in res)}, "
              f"failing labels {len(failing('labels', train, res, reading, set()))}, "
              f"failing disagreement {len(failing('disagreement', train, res, reading, set()))}")
    shutil.rmtree(OUT / "_check")


def full_eval(round_dir):
    out = round_dir / "_full.pkl"
    if not out.exists():
        subprocess.run([str(PYTHON), str(SRC / "run_encoding.py"), "unguided", str(round_dir / "encoding.py"),
                        str(out), str(round_dir / "adapter.py")], cwd=SRC, timeout=1800, check=False)
    return pickle.load(open(out, "rb")) if out.exists() else {"crash": "no output"}


def last_round(base):
    rounds = sorted((int(p.name[5:]), p) for p in base.glob("round*") if (p / "train_eval.json").exists())
    return rounds[-1][1] if rounds else None


def report():
    from cases import load_examples
    d = data()
    labels, cases = d["labels"]["original"], d["cases"]
    train = training()
    ho = held_out([c[2] for c in train])
    examples = load_examples()
    is_gap = [cause(*cases[k]).startswith(GAP_CAUSES) for k in range(len(cases))]
    n_gap = sum(is_gap)

    jobs = [(None, enc, OUT / ARMS[0] / enc.replace("/", "_") / "round0") for enc in ENCODINGS]
    for arm in ARMS:
        for enc in ENCODINGS:
            rd = last_round(OUT / arm / enc.replace("/", "_"))
            if rd is not None:
                jobs.append((arm, enc, rd))
    jobs = [j for j in jobs if (j[2] / "encoding.py").exists()]
    with ThreadPoolExecutor(max_workers=4) as pool:
        fulls = list(pool.map(lambda j: full_eval(j[2]), jobs))

    lines = ["# Self-repair loop: does feedback fix real errors, and does it know when not to?", "",
             f"Repairer: {MODELS[REPAIRER]['model']}, up to {ROUNDS} rounds, {len(train)} training cases "
             f"(direct_answer.py strata). Baseline = encoding and LLM adapter as generated, no hand mapping. "
             f"Policy gaps = {n_gap:,} enumerated cases whose outcome depends on a point the policy does not settle "
             "(male without a female partner, identical FSH tests, age 40+ without a test since 40); the expert "
             "denies all of them. 'Rest' = the other cases, where the expert's answer follows from the text.", "",
             "## Full enumeration (907,200 cases) and CodeX examples", "",
             "| Arm | Encoding | Rounds | Rest: wrongly denied | Rest: wrongly granted | Errors (crash) | "
             "Gaps: covered (reading against the expert) | CodeX examples passed |",
             "|---|---|---|---|---|---|---|---|"]
    held = {}
    for (arm, enc, rd), full in zip(jobs, fulls):
        name = arm or "baseline"
        rounds = int(rd.name[5:])
        if "crash" in full:
            lines.append(f"| {name} | {enc} | {rounds} | crash | | | | |")
            continue
        p = full["enumerated"]
        c = collections.Counter()
        for k, (pk, y) in enumerate(zip(p, labels)):
            if pk is None:
                c["err"] += 1
            elif is_gap[k]:
                c["gap_cov"] += pk
            elif pk != y:
                c["denied" if y else "granted"] += 1
        ex = sum(pe == ye for pe, (_, _, ye) in zip(full["examples"], examples))
        lines.append(f"| {name} | {enc} | {rounds} | {c['denied']:,} | {c['granted']:,} | {c['err']:,} | "
                     f"{c['gap_cov']:,} of {n_gap:,} | {ex}/{len(examples)} |")
        held[(name, enc)] = {s: [p[k] for n, k in ho if n == s] for s in dict.fromkeys(n for n, _ in ho)}

    lines += ["", "## Held-out cases from the training strata", "",
              "Answers as covered / not covered / error. Expert: gap strata and 'just below' are not covered, "
              "'covered' and 'timed vs frequent' are covered.", ""]
    strata = list(dict.fromkeys(n for n, _ in ho))
    lines += ["| Arm | Encoding | " + " | ".join(f"{s} (n={sum(n == s for n, _ in ho)})" for s in strata) + " |",
              "|---|---|" + "---|" * len(strata)]
    for (name, enc), per in held.items():
        cells = []
        for s in strata:
            v = per[s]
            cells.append(f"{sum(x is True for x in v)}/{sum(x is False for x in v)}/{sum(x is None for x in v)}")
        lines.append(f"| {name} | {enc} | " + " | ".join(cells) + " |")

    lines += ["", "## Verdicts on the training cases", "",
              "Gap strata should be contested / undetermined; the other strata fixed (or kept when the "
              "encoding is right).", ""]
    strat_of = {c[0]: c[1] for c in train}
    for arm in ARMS:
        tally = collections.defaultdict(collections.Counter)
        for enc in ENCODINGS:
            for vf in (OUT / arm / enc.replace("/", "_")).glob("round*/verdicts.json"):
                for v in json.loads(vf.read_text())["verdicts"]:
                    s = strat_of.get(v.get("case"))
                    if s:
                        tally[s][v.get("verdict", "?")] += 1
        if tally:
            lines.append(f"**{arm}:** " + "; ".join(
                f"{s}{' (gap)' if s in GAP_STRATA else ''}: " + ", ".join(f"{k} {n}" for k, n in t.most_common())
                for s, t in tally.items()))
            lines.append("")

    lines += ["## Training cases wrong vs the expert, per round", ""]
    for arm in ARMS:
        for enc in ENCODINGS:
            evs = sorted((OUT / arm / enc.replace("/", "_")).glob("round*/train_eval.json"))
            if evs:
                seq = [json.loads(p.read_text()) for p in evs]
                seq.sort(key=lambda e: e["round"])
                lines.append(f"- {arm} / {enc}: " + " -> ".join(
                    f"{e['wrong_vs_expert']} (shown {e['shown']})" for e in seq))
    usage = [json.loads(p.read_text()).get("usage") or {} for p in RAW_DIR.glob("repair_*.json")]
    tin = sum(u.get("input_tokens", 0) for u in usage)
    tout = sum(u.get("output_tokens", 0) for u in usage)
    lines += ["", f"Repair calls: {len(usage)}, input tokens {tin:,}, output tokens {tout:,} (incl. reasoning)."]
    (RESULTS / "summary_self_repair.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        check()
    elif cmd == "smoke":
        print(repair_one("labels", ENCODINGS[0], max_rounds=1))
        u = json.loads((RAW_DIR / f"repair_labels_{ENCODINGS[0].replace('/', '_')}_r1_{REPAIRER}.json").read_text())
        print("usage:", u.get("usage"))
    elif cmd == "run":
        arms = sys.argv[2:] or ARMS
        jobs = [(a, e) for a in arms for e in ENCODINGS]
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(repair_one, a, e): (a, e) for a, e in jobs}
            for fut, (a, e) in futures.items():
                try:
                    log = fut.result()
                    print("ok  ", a, e, [x["wrong_vs_expert"] for x in log])
                except Exception as exc:
                    print("FAIL", a, e, type(exc).__name__, str(exc)[:200])
    elif cmd == "report":
        report()


if __name__ == "__main__":
    main()
