"""Authority probe (CodeX issue cardinal-care-dev #27): does the model's preferred reading match Aetna's recorded answer?
Two phrasings x 3 runs, GPT-6.1 Sol. Recorded answer (not shown to the model): "The reason for the service is less
important than the service you actually get, effectively."
"""
from run_discovery import call, spent

CONTEXT = """A student health insurance plan's schedule of benefits (Aetna Student Health, Stanford University 2024-2025) has this row:

Infertility services
Treatment of basic infertility | Tier 1 in-network: Covered according to the type of benefit and the place where the service is received. | Tier 2 in-network: Covered according to the type of benefit and the place where the service is received. | Out-of-network: Not covered

Elsewhere the certificate describes basic infertility services as seeing a physician or infertility specialist to diagnose and evaluate the underlying medical cause of infertility, and to do surgery to treat the underlying medical cause of infertility (for example endometriosis surgery)."""

A = CONTEXT + """

Question: a covered student has outpatient laparoscopic surgery to treat endometriosis that is causing infertility. Which reading of the row is more plausible?
(a) What decides how the claim is covered is the kind of service actually received (here: outpatient surgery), so it is paid under the plan's outpatient surgery benefit, with that benefit's terms and the tier of the place of service; the fact that it treats infertility does not change that.
(b) What decides how the claim is covered is the reason for the service (treatment of infertility), so it is covered as an infertility benefit; the type and place of service only set the cost-sharing tier.
Answer with (a) or (b) on the first line, then at most two sentences of reasoning."""

B = CONTEXT + """

Question: in at most three sentences, explain how a claim for a basic infertility service is processed under this row: what decides which benefit terms apply?"""

if __name__ == "__main__":
    for k in (1, 2, 3):
        call("gpt-6.1-sol", A, f"authority27_A_run{k}")
        call("gpt-6.1-sol", B, f"authority27_B_run{k}")
    print(f"total spent ${spent():.2f}")
