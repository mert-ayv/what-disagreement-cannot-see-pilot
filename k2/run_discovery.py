"""K2 discovery test: one same-information prompt, GPT-6 Astra, 3 runs, with a cost cap.
Usage: python3 run_discovery.py [n_runs]   (resumable: existing raw outputs are skipped)
"""
import json, sys, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parent / ".env")
RAW = HERE / "results" / "raw"; RAW.mkdir(parents=True, exist_ok=True)
PRICES = {"gpt-6-astra": (10.0, 50.0), "gpt-6.1-sol": (2.0, 10.0)}  # $ per M input, output (list, secondary sources)
CAP = 3.00


def cost(model, usage):
    pi, po = PRICES[model]
    return usage["input_tokens"] / 1e6 * pi + usage["output_tokens"] / 1e6 * po


def spent():
    return sum(json.loads(p.read_text())["cost_usd"] for p in RAW.glob("*.json"))


def call(model, prompt, tag):
    out = RAW / f"{tag}.json"
    if out.exists():
        return json.loads(out.read_text())
    if spent() >= CAP:
        raise SystemExit(f"cost cap reached: ${spent():.2f}")
    t = time.time()
    r = OpenAI().responses.create(model=model, input=prompt)
    u = r.usage.model_dump()
    rec = {"model": model, "tag": tag, "seconds": round(time.time() - t, 1), "prompt": prompt,
           "output": r.output_text, "usage": u, "cost_usd": round(cost(model, u), 4)}
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    print(f"{tag}: {u['input_tokens']} in, {u['output_tokens']} out, ${rec['cost_usd']:.3f}; total ${spent():.2f}")
    return rec


def discovery_prompt():
    i = HERE / "inputs"
    return (open(HERE / "prompt_header.txt").read() + "\n\n=== (1) Policy text ===\n" + open(i / "policy.txt").read()
            + "\n\n=== (2) Glossary ===\n" + open(i / "glossary.txt").read()
            + "\n\n=== (3) Encoding ===\n" + open(i / "encoding_no_comments.hrf").read())


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    p = discovery_prompt()
    print(f"prompt chars {len(p)}")
    for k in range(1, n + 1):
        call("gpt-6-astra", p, f"discovery_astra_run{k}")
    print(f"done; total spent ${spent():.2f}")
