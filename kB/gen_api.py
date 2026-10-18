"""Generate kB encodings and adapters through the APIs (Gemini, GPT). Claude encodings come from fresh agents.

Usage: ../.venv/bin/python gen_api.py gemini|gpt|astra
For each role (neutral, member, insurer) and k = 1..3: one call writes the encoding, a second call by the same model
writes its adapter. Existing files are skipped, so a run can be resumed.
"""
import os, re, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dotenv import load_dotenv
from config import ROOT
load_dotenv(ROOT / ".env", override=True)

FAMILY = sys.argv[1]
OUT = HERE / f"encodings_{FAMILY}"; OUT.mkdir(exist_ok=True)
spent = 0.0

if FAMILY == "gemini":
    from google import genai
    gclient = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def ask(prompt):
        for attempt in range(5):
            try:
                r = gclient.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                time.sleep(8)
                return r.text or ""
            except Exception as e:
                print("retry after", type(e).__name__, str(e)[:120], flush=True); time.sleep(30 * (attempt + 1))
        raise RuntimeError("Gemini failed 5 times")
else:
    from openai import OpenAI
    oclient = OpenAI()
    MODEL, IN_P, OUT_P, CAP = {"gpt": ("gpt-6.1-sol", 2e-6, 10e-6, 3.0),
                               "astra": ("gpt-6-astra", 10e-6, 50e-6, 4.0)}[FAMILY]

    def ask(prompt):
        global spent
        if spent > CAP:
            sys.exit(f"cost cap reached: ${spent:.2f}")
        r = oclient.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        spent += r.usage.prompt_tokens * IN_P + r.usage.completion_tokens * OUT_P
        return r.choices[0].message.content or ""


def code(text):
    m = re.search(r"```python\n(.*?)```", text, re.S)
    return m.group(1) if m else text


template = (HERE / "adapter_template.txt").read_text()
for role in ("neutral", "member", "insurer"):
    prompt = (HERE / f"prompt_{role}.txt").read_text()
    for k in (1, 2, 3):
        enc, adp = OUT / f"{role}_{k}.py", OUT / f"{role}_{k}_adapter.py"
        if not enc.exists():
            enc.write_text(code(ask(prompt)))
            print(enc.name, f"${spent:.2f}", flush=True)
        if not adp.exists():
            adp.write_text(code(ask(template.replace("{encoding}", enc.read_text()))))
            print(adp.name, f"${spent:.2f}", flush=True)
print(f"done, total ${spent:.2f}")
