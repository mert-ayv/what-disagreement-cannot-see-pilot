"""Generate the amended GPT-6 Astra encodings (enrollment checked elsewhere) for the direction A test (OpenAI family)."""
import os, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dotenv import load_dotenv
from config import ROOT
load_dotenv(ROOT / ".env", override=True)
from openai import OpenAI

MODEL, IN_PRICE, OUT_PRICE, CAP = "gpt-6-astra", 10 / 1e6, 50 / 1e6, 2.0
OUT = HERE / "encodings_astra"; OUT.mkdir(exist_ok=True)
client = OpenAI()
spent = 0.0
for role in ("neutral", "member", "insurer"):
    prompt = (HERE / f"prompt_{role}.txt").read_text().replace(
        "Write the function, with a module docstring listing your READING choices, to the file given below and\nnothing else.",
        "Reply with a single ```python code block containing the function, with a module docstring listing your READING choices, and nothing else.").replace(
        "plan limits and general exclusions are checked elsewhere; do not encode them.",
        "plan limits and general exclusions are checked elsewhere; do not encode them. Enrollment as a student or covered dependent is also checked elsewhere.")
    for k in (1, 2, 3):
        path = OUT / f"{role}_{k}.py"
        if path.exists():
            continue
        if spent > CAP:
            sys.exit(f"cost cap reached: ${spent:.2f}")
        r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        u = r.usage
        spent += u.prompt_tokens * IN_PRICE + u.completion_tokens * OUT_PRICE
        text = r.choices[0].message.content or ""
        m = re.search(r"```python\n(.*?)```", text, re.S)
        path.write_text(m.group(1) if m else text)
        print(path.name, u.prompt_tokens, u.completion_tokens, f"${spent:.2f}", flush=True)
print(f"total ${spent:.2f}")
