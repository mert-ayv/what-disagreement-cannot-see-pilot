"""Replication of Kant et al. (2025), vanilla LLM approach (section 3.1), with current models.

Same policy text (Appendix A.1), same nine queries with the same disclaimer and answers (A.2), same
prompt (A.3.1), 10 trials per model, each query asked separately. Differences: current models do not
accept temperature/top-p settings, so provider defaults are used; Claude runs at its default effort
(medium).

Usage: python replicate_kant.py
Writes results/kant_replication/<family>.json and results/summary_kant_replication.md.
"""

import json
import math
import re
from concurrent.futures import ThreadPoolExecutor

from config import DATA, MODELS, RESULTS
from llm_clients import generate

OUT = RESULTS / "kant_replication"
TRIALS = 10
POLICY = (DATA / "kant" / "chubb_policy.txt").read_text()
DISCLAIMER = ("Assuming all other conditions are met and no other exclusions apply (where by 'other,' I mean "
              "anything not referenced in the query that follows), ")

QUERIES = [
    ("will my policy apply if I was hospitalized by burns suffered while doing my duty as a firefighter?", "No"),
    ("will my policy apply if I am 78 years old at the time of hospitalization?", "Yes"),
    ("will my policy apply if I was hospitalized for pneumonia 5 months after the policy's effective date, "
     "and my age at the time of hospitalization is 65?", "Yes"),
    ("will my policy apply if I was hospitalized due to a fall while traveling abroad and I had given "
     "confirmation of my wellness visit 8 months after the policy's effective date?", "No"),
    ("will my policy apply if I was hospitalized for punching my own face to show off for my friends and I "
     "did not commit fraud or misrepresentation?", "No"),
    ("will my policy apply if I was hospitalized due to an injury sustained while skydiving, my age at the "
     "time of hospitalization was 79, and proof of my wellness visit was provided 6.5 months after the "
     "policy's effective date?", "No"),
    ("will my policy apply if I was hospitalized for a heart attack, proof of the wellness visit was "
     "submitted 2 months after the policy's effective date, and my age at the time of hospitalization was 75?",
     "Yes"),
    ("will my policy apply if I was hospitalized after being injured in a military training exercise, the "
     "hospitalization occurred within the policy term, and I did not commit fraud?", "No"),
    ("will my policy apply if I was hospitalized due to my son biting me in the ankle, proof of my wellness "
     "visit was provided 6 months after the effective date, and I was serving as a police officer at the time "
     "of hospitalization?", "Yes"),
]

PROMPT = """\
- Below, you are provided
1. The full text of an insurance contract
2. A specific question about whether a claim in the given scenario is covered under the terms of this insurance contract
- Assume that the policy agreement has been signed, and the premium has been paid on time.
- Assume that all other conditions are satisfied, and no exclusions apply unless explicitly referenced in the query.
- Your task:
1. Evaluate whether the claim described in the question is covered under the insurance contract.
2. Respond with **only** one of the following: "Yes", "No", or "I do not know".
3. Do not provide any explanations or reasoning.
- Insurance contract: {text_content}
- Question: {query}"""


def parse(text):
    t = text.strip().strip('*"').lower()
    if t.startswith("yes"):
        return "Yes"
    if t.startswith("no"):
        return "No"
    if "do not know" in t or "don't know" in t:
        return "I do not know"
    m = re.search(r"\b(yes|no)\b", t)
    return m.group(1).capitalize() if m else "unparsed"


def run_family(family):
    path = OUT / f"{family}.json"
    done = json.loads(path.read_text()) if path.exists() else {}

    def one(job):
        q, t = job
        key = f"q{q + 1}_t{t}"
        if key in done:
            return key, done[key]
        prompt = PROMPT.format(text_content=POLICY, query=DISCLAIMER + QUERIES[q][0])
        text = generate(family, prompt, tag=f"kant_{family}_{key}",
                        effort="medium" if family == "claude" else "high")
        return key, {"raw": text.strip()[:200], "answer": parse(text)}

    jobs = [(q, t) for t in range(TRIALS) for q in range(len(QUERIES))]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(one, j) for j in jobs]
        for fut in futures:
            try:
                key, val = fut.result()
                done[key] = val
            except Exception as exc:
                print("FAIL", family, type(exc).__name__, str(exc)[:120])
    OUT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(done, indent=2))
    return done


def summarize(all_results):
    lines = ["# Replication of Kant et al. (2025), vanilla LLM approach, Chubb policy", "",
             "Paper (10 trials, temperature and top-p 1): Mistral, Gemini 1.5 Pro, Claude 3.5 Sonnet, Llama 3.1 405B, "
             "GPT-4o 0.78 +- 0.00; DeepSeek-R1 0.81 +- 0.02; o1-preview 0.88 +- 0.02. All failed Q5 and Q9.", "",
             "| Model | Trials complete | Accuracy (mean +- SEM over trials) |", "|---|---|---|"]
    per_q = {}
    for family, done in all_results.items():
        accs = []
        for t in range(TRIALS):
            keys = [f"q{q + 1}_t{t}" for q in range(len(QUERIES))]
            if all(k in done for k in keys):
                accs.append(sum(done[k]["answer"] == QUERIES[q][1] for q, k in enumerate(keys)) / len(QUERIES))
        if not accs:
            lines.append(f"| {family} ({MODELS[family]['model']}) | 0 | n/a |")
            continue
        mean = sum(accs) / len(accs)
        sd = math.sqrt(sum((a - mean) ** 2 for a in accs) / (len(accs) - 1)) if len(accs) > 1 else 0.0
        lines.append(f"| {family} ({MODELS[family]['model']}) | {len(accs)} | {mean:.2f} +- {sd / math.sqrt(len(accs)):.2f} |")
        per_q[family] = [sum(done.get(f"q{q + 1}_t{t}", {}).get("answer") == QUERIES[q][1] for t in range(TRIALS))
                         for q in range(len(QUERIES))]
    lines += ["", "Correct trials per question (out of 10):", "",
              "| Model | " + " | ".join(f"Q{q + 1}" for q in range(len(QUERIES))) + " |",
              "|---|" + "---|" * len(QUERIES)]
    for family, counts in per_q.items():
        lines.append(f"| {family} | " + " | ".join(str(c) for c in counts) + " |")
    (RESULTS / "summary_kant_replication.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    results = {fam: run_family(fam) for fam in ["claude", "openai"]}
    summarize(results)
