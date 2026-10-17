"""Classify every input field of the unguided encodings against the expert interface (LLM judge).

Usage: python classify_variables.py unguided unguided2
Writes results/variables/<mode>/<encoding>.json and results/variable_summary.md.
The judge is Claude (family "claude" in config). Existing classifications are reused.
"""

import ast
import collections
import json
import re
import sys

from config import RESULTS
from llm_clients import generate

OUT = RESULTS / "variables"

EXPERT_FIELDS = """\
E1  service_type: "intrauterine_insemination" | "ovulation_induction_cycle_with_menotropins" | other
E2  patient_dob: patient's date of birth
E3  date_service_received: date of service
E4  sex_of_patient_trying_to_conceive: female | male
E5  sex_of_patients_partner: male | female | no_partner
E6  age_of_patients_female_partner: int, the female partner's age
E7  num_months_timed_unprotected_intercourse: months of unprotected TIMED intercourse (policy table)
E8  num_cycles_donor_insemination: donor insemination cycles, self-paid or not paid by the plan
E9  patient_has_had_voluntary_sterilization: yes | no -- the PATIENT only
E10 demonstrated_and_documented_condition_causing_infertility: one enum combining three things: a condition
    is demonstrated and documented ("other"), or the infertility is due to a natural process
    ("natural_menopause", "natural_perimenopause", "natural_male_reproductive_aging",
    "other_natural_physiologic_process") -- the PATIENT's condition only
E11 successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan: yes | no
E12 day_3_fsh_tests: list of (level, date, time), the patient's unmedicated day 3 FSH tests
E13 num_months_frequent_unprotected_heterosexual_intercourse: months of FREQUENT intercourse (glossary
    definition of infertility)
E14 abnormal_semen_analyses: list of dates of abnormal semen analyses (glossary definition)
E15 patient_or_partner_diagnosed_with_gender_dysphoria: yes | no (glossary definition)
"""

CATEGORIES = """\
identical      same concept as one expert field, possibly another name or value spelling
convertible    same information as an expert field in another form (e.g. partner birth date vs partner age)
split          one of several fields that together correspond to ONE expert field
broader        covers more than the matching expert field (e.g. patient OR partner where the expert has patient only)
narrower       covers less than the matching expert field
pre-computed   a derived fact that the expert computes from its inputs (e.g. "patient is infertile",
               "most recent FSH level"), so part of the rule logic sits in the input
new            no counterpart among the expert fields
"""

PROMPT = """\
You compare the input fields of an LLM-written encoding of an insurance coverage rule with the input
fields of an expert-written encoding of the same rule.

Expert input fields:
<expert>
{expert}
</expert>

Categories:
<categories>
{categories}
</categories>

The encoding's input fields (its SCHEMA):
```python
{schema}
```

Classify every SCHEMA field. Then list the expert fields (E1 to E15) that no SCHEMA field covers in any form.
Reply with a single ```json block and nothing else, in this format:
{{"fields": [{{"field": "<name>", "category": "<category>", "expert_fields": ["E9"], "note": "<one short sentence>"}}],
  "missing_expert_fields": ["E13"]}}
"""

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)```", re.S)


def schema_source(path):
    src = path.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SCHEMA" for t in node.targets):
            return ast.get_source_segment(src, node)
    return None


def classify(mode, path):
    out = OUT / mode / f"{path.stem}.json"
    if out.exists():
        return json.loads(out.read_text())
    schema = schema_source(path)
    if schema is None:
        return None
    text = generate("claude", PROMPT.format(expert=EXPERT_FIELDS, categories=CATEGORIES, schema=schema),
                    tag=f"classify_{mode}_{path.stem}")
    m = JSON_BLOCK.search(text)
    data = json.loads(m.group(1) if m else text)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    return data


def summarize(results):
    lines = ["# Variable classification (LLM judge: Claude)", ""]
    for mode, encs in results.items():
        encs = {k: v for k, v in encs.items() if v}
        n = len(encs)
        cats = collections.Counter(f["category"] for v in encs.values() for f in v["fields"])
        total = sum(cats.values())
        lines += [f"## {mode}: {n} encodings, {total} fields", "",
                  "| Category | Fields | Share |", "|---|---|---|"]
        for c, k in cats.most_common():
            lines.append(f"| {c} | {k} | {k / total:.0%} |")
        # per expert field: how often each category appears, and how often it is missing
        per = collections.defaultdict(collections.Counter)
        for v in encs.values():
            seen = set()
            for f in v["fields"]:
                for e in f.get("expert_fields", []):
                    if (e, f["category"]) not in seen:
                        per[e][f["category"]] += 1
                        seen.add((e, f["category"]))
            for e in v.get("missing_expert_fields", []):
                per[e]["missing"] += 1
        lines += ["", "| Expert field | Encodings per category (an encoding can count in two) |", "|---|---|"]
        for e in sorted(per, key=lambda x: int(x[1:])):
            lines.append(f"| {e} | " + ", ".join(f"{c} {k}" for c, k in per[e].most_common()) + " |")
        new = collections.Counter()
        for v in encs.values():
            for f in v["fields"]:
                if f["category"] == "new":
                    new[f["note"][:90]] += 1
        lines += ["", "New fields (judge's notes):", ""] + [f"- {k}" for k in list(new)[:40]] + [""]
    (RESULTS / "variable_summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    modes = sys.argv[1:] or ["unguided", "unguided2"]
    results = {}
    for mode in modes:
        files = sorted(p for p in (RESULTS / "encodings" / mode).glob("*.py") if not p.stem.endswith("_adapter"))
        results[mode] = {}
        for p in files:
            try:
                results[mode][p.stem] = classify(mode, p)
            except Exception as exc:
                print("FAIL", mode, p.stem, type(exc).__name__, str(exc)[:150])
                results[mode][p.stem] = None
    summarize(results)
