"""Generate the Gemini encodings for the direction A test (second model family)."""
import os, re, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dotenv import load_dotenv
from config import ROOT
load_dotenv(ROOT / ".env")
from google import genai

OUT = HERE / "encodings_gemini"; OUT.mkdir(exist_ok=True)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
for role in ("neutral", "member", "insurer"):
    prompt = (HERE / f"prompt_{role}.txt").read_text().replace(
        "Write the function, with a module docstring listing your READING choices, to the file given below and\nnothing else.",
        "Reply with a single ```python code block containing the function, with a module docstring listing your READING choices, and nothing else.")
    for k in (1, 2, 3):
        path = OUT / f"{role}_{k}.py"
        if path.exists():
            continue
        for attempt in range(4):
            try:
                r = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                m = re.search(r"```python\n(.*?)```", r.text or "", re.S)
                code = m.group(1) if m else (r.text or "")
                path.write_text(code)
                print(path.name, len(code), "chars")
                break
            except Exception as e:
                print(role, k, "retry after", type(e).__name__, str(e)[:120]); time.sleep(30 * (attempt + 1))
        time.sleep(8)
