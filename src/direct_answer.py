"""Direct-answer baseline: can an LLM answer coverage questions straight from the policy text?

60 cases from the enumeration, stratified: the divergence points found in the unguided runs, plus
controls. Each case is written out in plain language, as a policyholder would describe it. Every model
answers every case 3 times (10 cases per call, each to be judged independently). Compared with the
expert's benefit-level label; consistency = same answer in all 3 runs.

Usage: python direct_answer.py
Writes results/direct/<family>_run<r>_batch<b>.json and results/summary_direct.md.
"""

import json
import pickle
import random
import re
from datetime import date

from config import DATA, MODELS, RESULTS
from llm_clients import generate
from prompts import GLOSSARY, POLICY

OUT = RESULTS / "direct"
RUNS = 3
BATCH = 10
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.S)

PROMPT = """\
You answer coverage questions for a student health insurance plan, using only the policy text below.

<policy>
{policy}

{glossary}
</policy>

For every case, assume the following are satisfied, since they are checked elsewhere: the patient is a
covered student, the provider is an in-network infertility specialist, precertification was obtained, the
service is medically necessary, no plan limit is reached and no general exclusion applies. Decide only
whether the claim is covered under the comprehensive infertility services benefit described above.

Judge each case on its own.

<cases>
{cases}
</cases>

Reply with a single ```json block and nothing else:
[{{"case": 1, "covered": true, "reason": "<one short sentence>"}}, ...]
"""


def _d(s):
    y, m, d = (int(x) for x in s.split("_"))
    return date(y, m, d).strftime("%-d %B %Y")


def describe(claim):
    sex = claim["sex_of_patient_trying_to_conceive"]
    partner = claim["sex_of_patients_partner"]
    lines = [f"Service: {claim['service_type'].replace('_', ' ')}, received on {_d(claim['date_service_received'])}."]
    lines.append(f"Patient: {sex}, born {_d(claim['patient_dob'])}.")
    if partner == "no_partner":
        lines.append("The patient has no partner.")
    else:
        p = f"The patient's partner is {partner}"
        if "age_of_patients_female_partner" in claim:
            p += f", aged {claim['age_of_patients_female_partner']}"
        lines.append(p + ".")
    lines.append(f"Months of timed unprotected intercourse: {claim['num_months_timed_unprotected_intercourse']}. "
                 f"Months of frequent unprotected heterosexual intercourse: "
                 f"{claim['num_months_frequent_unprotected_heterosexual_intercourse']}. "
                 f"Self-paid donor insemination cycles: {claim['num_cycles_donor_insemination']}.")
    cond = claim["demonstrated_and_documented_condition_causing_infertility"]
    lines.append("A condition causing infertility is demonstrated and documented in the medical records."
                 if cond == "other" else
                 f"The infertility is due to {cond.replace('natural_', 'natural ').replace('_', ' ')}.")
    lines.append(f"Voluntary sterilization of the patient: {claim['patient_has_had_voluntary_sterilization']}. "
                 "The partner has not had a voluntary sterilization.")
    lines.append("A successful pregnancy could be attained through less costly covered treatment: "
                 f"{claim['successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan']}.")
    tests = claim.get("day_3_fsh_tests") or []
    if tests:
        lines.append("Unmedicated day 3 FSH tests: " + "; ".join(
            f"{lvl} mIU/mL on {_d(dt)} at {tm.replace('_', ':')}" for lvl, dt, tm in tests) + ".")
    else:
        lines.append("No day 3 FSH test has been done.")
    if claim.get("abnormal_semen_analyses"):
        lines.append("Abnormal semen analyses on " + " and ".join(_d(x) for x in claim["abnormal_semen_analyses"]) + ".")
    lines.append("Nobody has been diagnosed with gender dysphoria.")
    return " ".join(lines)


def select_cases(seed=7, data=None, exclude=frozenset()):
    """exclude: case indices to leave out of every pool (self_repair.py draws held-out cases this way)."""
    data = data or pickle.load(open(DATA / "cases.pkl", "rb"))
    cases, labels = data["cases"], data["labels"]["original"]
    rng = random.Random(seed)
    idx = range(len(cases))
    base = lambda m: m["gate"] == "no/other/no" and m["service"] == "intrauterine_insemination"

    def pick(name, cond, n):
        pool = [k for k in idx if k not in exclude and cond(cases[k][1], labels[k])]
        return [(name, k) for k in rng.sample(pool, min(n, len(pool)))]

    sel = []
    sel += pick("male without female partner", lambda m, y: base(m) and m["sex"] == "male" and m["partner"] == "no_partner" and m["freq"] == 12, 8)
    sel += pick("age 40, no test since 40th birthday", lambda m, y: base(m) and m["sex"] == "female" and m["age"] == 40 and m["birthday"] == "today"
                and m["fsh"] == "1mo_18" and m["donor"] == 12 and m["freq"] == 12, 8)
    sel += pick("two identical FSH tests", lambda m, y: base(m) and m["sex"] == "female" and m["fsh"] == "tie_18_18" and m["donor"] == 12 and m["freq"] == 12, 6)
    sel += pick("timed vs frequent (donor path)", lambda m, y: base(m) and m["sex"] == "female" and m["partner"] == "male" and m["age"] == 34
                and m["timed"] < 12 and m["donor"] == 12 and m["freq"] == 12 and m["fsh"] == "1mo_18", 8)
    sel += pick("control: covered", lambda m, y: y, 10)
    sel += pick("control: just below a threshold", lambda m, y: base(m) and not y and m["freq"] == 12 and m["sex"] == "female"
                and m["fsh"] in ("1mo_19", "12mo_plus1d_18", "6mo_plus1d_18") and m["donor"] >= 11, 10)
    sel += pick("control: random", lambda m, y: True, 10)
    return [(name, k, cases[k][0], labels[k]) for name, k in sel]


def ask(family, run, batch_no, batch):
    path = OUT / f"{family}_run{run}_batch{batch_no}.json"
    if path.exists():
        return json.loads(path.read_text())
    text = "\n\n".join(f"Case {i + 1}: {describe(c)}" for i, (_, _, c, _) in enumerate(batch))
    reply = generate(family, PROMPT.format(policy=POLICY, glossary=GLOSSARY, cases=text),
                     tag=f"direct_{family}_r{run}_b{batch_no}")
    m = JSON_BLOCK.search(reply)
    answers = json.loads(m.group(1) if m else reply)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(answers, indent=2))
    return answers


def main():
    sel = select_cases()
    batches = [sel[i:i + BATCH] for i in range(0, len(sel), BATCH)]
    results = {}  # (family, case index in sel) -> list of answers over runs
    for family in MODELS:
        for run in range(RUNS):
            for b, batch in enumerate(batches):
                try:
                    answers = ask(family, run, b, batch)
                except Exception as exc:
                    print("FAIL", family, run, b, type(exc).__name__, str(exc)[:120])
                    continue
                by_case = {a.get("case"): a.get("covered") for a in answers}
                for i in range(len(batch)):
                    results.setdefault((family, b * BATCH + i), []).append(by_case.get(i + 1))

    lines = ["# Direct answers from the policy text vs the expert", "",
             f"{len(sel)} cases, {RUNS} runs per model, {BATCH} cases per call. 'Correct' = majority answer equals the "
             "expert; 'consistent' = same answer in every run.", ""]
    strata = list(dict.fromkeys(name for name, *_ in sel))
    for family in MODELS:
        got = {i: results.get((family, i), []) for i in range(len(sel))}
        if not any(got.values()):
            lines.append(f"**{family}:** no answers (API failure).")
            continue
        lines += [f"## {family} ({MODELS[family]['model']})", "",
                  "| Cases | n | Correct (majority) | Consistent across runs | Answer mostly given |", "|---|---|---|---|---|"]
        for stratum in strata + ["all"]:
            ids = [i for i, (name, *_) in enumerate(sel) if stratum == "all" or name == stratum]
            correct = consistent = 0
            answered = [i for i in ids if got[i]]
            covered_votes = 0
            for i in answered:
                votes = [v for v in got[i] if v is not None]
                if not votes:
                    continue
                maj = sum(votes) > len(votes) / 2
                covered_votes += maj
                correct += maj == sel[i][3]
                consistent += len(set(votes)) == 1 and len(votes) == RUNS
            n = len(answered)
            expert = "covered" if all(sel[i][3] for i in ids) else ("not covered" if not any(sel[i][3] for i in ids) else "mixed")
            lines.append(f"| {stratum} (expert: {expert}) | {n} | {correct}/{n} | {consistent}/{n} | "
                         f"covered in {covered_votes}/{n} |")
        lines.append("")
    (RESULTS / "summary_direct.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
