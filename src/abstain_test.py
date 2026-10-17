"""Do models flag cases the policy does not decide, when they are allowed to?

Same 58 cases as direct_answer.py (gap cases plus controls). Two prompts, three answer options:
covered / not_covered / undetermined.
  neutral:  the third option is offered, nothing more
  explicit: plus "if the policy does not settle the case, say so instead of choosing a reading"
3 runs per model and prompt, 10 cases per call. Claude at default effort (medium).

Usage: python abstain_test.py
Writes results/abstain/<prompt>_<family>_run<r>_batch<b>.json and results/summary_abstain.md.
"""

import collections
import json
import re

from config import MODELS, RESULTS
from direct_answer import BATCH, describe, select_cases
from llm_clients import generate
from prompts import GLOSSARY, POLICY

OUT = RESULTS / "abstain"
RUNS = 3
FAMILIES = ["claude", "openai"]
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.S)

BASE = """\
You answer coverage questions for a student health insurance plan, using only the policy text below.

<policy>
{policy}

{glossary}
</policy>

For every case, assume the following are satisfied, since they are checked elsewhere: the patient is a
covered student, the provider is an in-network infertility specialist, precertification was obtained, the
service is medically necessary, no plan limit is reached and no general exclusion applies. Decide whether
the claim is covered under the comprehensive infertility services benefit described above.

For each case answer "covered", "not_covered", or "undetermined" (the policy text does not clearly decide
this case).{extra}

Judge each case on its own.

<cases>
{cases}
</cases>

Reply with a single ```json block and nothing else:
[{{"case": 1, "answer": "covered", "reason": "<one short sentence>"}}, ...]
"""

EXTRA = {
    "neutral": "",
    "explicit": ("\n\nIf the policy does not settle the case, for example because no provision addresses this "
                 "situation or the wording allows more than one reasonable reading, answer \"undetermined\" "
                 "instead of choosing a reading yourself. Answer \"covered\" or \"not_covered\" only when the "
                 "text clearly decides the case."),
}


def ask(prompt_name, family, run, b, batch):
    path = OUT / f"{prompt_name}_{family}_run{run}_batch{b}.json"
    if path.exists():
        return json.loads(path.read_text())
    cases = "\n\n".join(f"Case {i + 1}: {describe(c)}" for i, (_, _, c, _) in enumerate(batch))
    prompt = BASE.format(policy=POLICY, glossary=GLOSSARY, extra=EXTRA[prompt_name], cases=cases)
    reply = generate(family, prompt, tag=f"abstain_{prompt_name}_{family}_r{run}_b{b}",
                     effort="medium" if family == "claude" else "high")
    m = JSON_BLOCK.search(reply)
    answers = json.loads(m.group(1) if m else reply)
    OUT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(answers, indent=2))
    return answers


def main():
    sel = select_cases()
    batches = [sel[i:i + BATCH] for i in range(0, len(sel), BATCH)]
    got = collections.defaultdict(list)  # (prompt, family, case) -> answers
    for prompt_name in EXTRA:
        for family in FAMILIES:
            for run in range(RUNS):
                for b, batch in enumerate(batches):
                    try:
                        answers = ask(prompt_name, family, run, b, batch)
                    except Exception as exc:
                        print("FAIL", prompt_name, family, run, b, type(exc).__name__, str(exc)[:120])
                        continue
                    by_case = {a.get("case"): str(a.get("answer", "")).strip().lower() for a in answers}
                    for i in range(len(batch)):
                        got[(prompt_name, family, b * BATCH + i)].append(by_case.get(i + 1))

    strata = list(dict.fromkeys(name for name, *_ in sel))
    lines = ["# Abstention test: are undecided cases flagged when the model may say so?", "",
             "Answers per case over 3 runs. 'Flagged' = share of all answers that are 'undetermined'. 'Correct' = share "
             "of answers equal to the expert (gap cases: the expert's reading; controls: the clear answer). "
             "'Consistent' = cases with the same answer in all 3 runs.", ""]
    for prompt_name in EXTRA:
        for family in FAMILIES:
            lines += [f"## {prompt_name} prompt, {family} ({MODELS[family]['model']})", "",
                      "| Cases | Expert | Flagged undetermined | Covered | Not covered | Consistent |",
                      "|---|---|---|---|---|---|"]
            for stratum in strata:
                ids = [i for i, (name, *_) in enumerate(sel) if name == stratum]
                answers = [a for i in ids for a in got[(prompt_name, family, i)] if a]
                if not answers:
                    lines.append(f"| {stratum} | | no answers | | | |")
                    continue
                c = collections.Counter(answers)
                n = len(answers)
                consistent = sum(1 for i in ids if len(set(got[(prompt_name, family, i)])) == 1
                                 and len(got[(prompt_name, family, i)]) == RUNS)
                exp = {True: "covered", False: "not covered"}
                expert = exp[sel[ids[0]][3]] if len({sel[i][3] for i in ids}) == 1 else "mixed"
                lines.append(f"| {stratum} | {expert} | {c['undetermined'] / n:.0%} | {c['covered'] / n:.0%} | "
                             f"{c['not_covered'] / n:.0%} | {consistent}/{len(ids)} |")
            lines.append("")
    (RESULTS / "summary_abstain.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
