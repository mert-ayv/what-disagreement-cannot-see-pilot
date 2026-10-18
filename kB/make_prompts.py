"""Build the kB prompts from the kA prompts: same role line, policy and glossary; the fixed interface and helpers
are replaced by an instruction to define one's own input fields (SCHEMA), as in pilot experiment 3.

Writes prompt_neutral.txt, prompt_member.txt, prompt_insurer.txt and adapter_template.txt (not published: they
contain the policy text).
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
KA = HERE.parent / "kA"

TASK = '''First decide which facts about a claim are needed to decide coverage under the comprehensive infertility services
benefit. Then write:

1. A dict named SCHEMA mapping each input field name you chose to a short description, its type, and its allowed
   values or format.
2. A function

    def covered_under_benefit(claim: dict) -> bool:

   that reads only the fields in SCHEMA and returns True exactly when the claim is covered under the comprehensive
   infertility services benefit: the service is one of the covered comprehensive infertility services, the patient is
   infertile under the glossary, and every eligibility requirement in the text (including the table) is met.
   Precertification, provider network, medical necessity, plan limits and general exclusions are checked elsewhere; do
   not encode them. A missing field means the fact is unknown. Dates are strings "YYYY_MM_DD".

Wherever you choose between readings, add a comment starting with "# READING:" that names the point, quotes the words
of the text it rests on, and states the reading chosen. Use only the Python standard library. Reply with a single
```python code block containing a module docstring listing your READING choices, SCHEMA and the function, and nothing
else.
'''

ADAPTER = '''Below is a Python encoding that defines its own claim fields (SCHEMA), and a reference claim interface used by a
test suite. Write a function

    def adapt(ref_claim: dict) -> dict:

that converts a claim in the reference interface into a claim in the encoding's SCHEMA, so the encoding can be run on
the test suite. Map every SCHEMA field from the reference fields as faithfully as possible; derive a field if it can be
derived from the reference fields. A reference field that is absent means the fact is unknown: leave the corresponding
SCHEMA field out.

Some SCHEMA fields may concern facts the reference interface does not cover at all (for example enrollment, provider
qualifications or documentation). For each such field, set the value that means the requirement is met, and list the
field names in a module-level list named ASSUMED_MET. Do not put fields that can be mapped or derived into ASSUMED_MET.

Encoding:
```python
{encoding}
```

Reference interface:
<interface>
{interface}
</interface>

Use only the Python standard library. Reply with a single ```python code block containing ASSUMED_MET and adapt, and
nothing else.
'''


def main():
    for role in ("neutral", "member", "insurer"):
        src = (KA / f"prompt_{role}.txt").read_text()
        head = src.split("Claim interface:")[0].rstrip() + "\n\n"
        (HERE / f"prompt_{role}.txt").write_text(head + TASK)
    src = (KA / "prompt_neutral.txt").read_text()
    interface = src.split("<interface>")[1].split("</interface>")[0].strip()
    (HERE / "adapter_template.txt").write_text(ADAPTER.replace("{interface}", interface))
    print("prompts written")


if __name__ == "__main__":
    main()
