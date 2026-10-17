"""Prompts for the guided and unguided settings."""

from config import DATA
from helpers import HELPER_DOC
from variants import policy_text

POLICY = policy_text("original")
GLOSSARY = (DATA / "glossary_infertility.txt").read_text()

INTERFACE_DOC = """\
Each claim is a Python dict. Fields that are unknown are absent from the dict.

service_type: str
    one of "intrauterine_insemination", "ovulation_induction_cycle_with_menotropins",
    or another service name
patient_dob: str, date "YYYY_MM_DD"
date_service_received: str, date "YYYY_MM_DD"
sex_of_patient_trying_to_conceive: "female" | "male"
sex_of_patients_partner: "male" | "female" | "no_partner"
age_of_patients_female_partner: int   (present when the partner is female)
num_months_timed_unprotected_intercourse: int
num_months_frequent_unprotected_heterosexual_intercourse: int
num_cycles_donor_insemination: int   (self-paid or not paid for by the plan)
patient_has_had_voluntary_sterilization: "yes" | "no"
demonstrated_and_documented_condition_causing_infertility: str
    one of "natural_menopause", "natural_perimenopause", "natural_male_reproductive_aging",
    "other_natural_physiologic_process", "other"
successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan: "yes" | "no"
day_3_fsh_tests: list of (level: int, date: "YYYY_MM_DD", time: "HH_MM"), unmedicated day 3 FSH tests
"""

GUIDED = """\
You are encoding one coverage rule of a health insurance policy as a Python function.

Policy text:
<policy>
{policy}
</policy>

Claim interface:
<interface>
{interface}
</interface>

Helper functions, available as methods of the object `h`:
<helpers>
{helpers}
</helpers>

Write a Python function

    def covered_under_benefit(claim: dict, h) -> bool:

that returns True exactly when the claim is covered under the comprehensive infertility services
benefit described in the policy text: the service is one of the covered comprehensive infertility
services, the patient is infertile, and every eligibility requirement in the text (including the
table) is met. Precertification, provider network, medical necessity, plan limits and general
exclusions are checked elsewhere; do not encode them.

Use only the claim fields and helpers above, and only the Python standard library.
Reply with a single ```python code block and nothing else.
"""

UNGUIDED = """\
You are encoding one coverage rule of a health insurance policy as a Python function.

Policy text:
<policy>
{policy}
</policy>

First decide which facts about a claim are needed to decide coverage under the comprehensive
infertility services benefit. Then write:

1. A dict named SCHEMA mapping each input field name you chose to a short description, its type,
   and its allowed values or format.
2. A function

    def covered_under_benefit(claim: dict) -> bool:

   that reads only the fields in SCHEMA and returns True exactly when the claim is covered under the
   comprehensive infertility services benefit: the service is a covered comprehensive infertility
   service, the patient is infertile, and every eligibility requirement in the text (including the
   table) is met. Precertification, provider network, medical necessity, plan limits and general
   exclusions are checked elsewhere; do not encode them. Dates should be strings "YYYY_MM_DD".

Use only the Python standard library.
Reply with a single ```python code block and nothing else.
"""

ADAPTER = """\
Below is a Python encoding that defines its own claim fields (SCHEMA), and a reference claim
interface used by a test suite. Write a function

    def adapt(ref_claim: dict) -> dict:

that converts a claim in the reference interface into a claim in the encoding's SCHEMA, so the
encoding can be run on the test suite. Map every SCHEMA field from the reference fields as
faithfully as possible. If a SCHEMA field has no counterpart in the reference interface, derive it
if it can be derived; otherwise leave it out of the returned dict.

Encoding:
```python
{encoding}
```

Reference interface:
<interface>
{interface}
</interface>

Use only the Python standard library.
Reply with a single ```python code block and nothing else.
"""


def guided_prompt(variant="original"):
    return GUIDED.format(policy=policy_text(variant), interface=INTERFACE_DOC, helpers=HELPER_DOC)


def unguided_prompt(with_glossary=False):
    policy = POLICY + ("\n\n" + GLOSSARY if with_glossary else "")
    return UNGUIDED.format(policy=policy)


def adapter_prompt(encoding_code):
    return ADAPTER.format(encoding=encoding_code, interface=INTERFACE_DOC)
