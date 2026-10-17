"""Ask each model for encodings and save them as .py files.

Usage:
    python generate_encodings.py guided      # RUNS_GUIDED per model
    python generate_encodings.py unguided    # RUNS_UNGUIDED per model, plus an adapter per encoding
    python generate_encodings.py guided_thresholds | guided_logic   # RUNS_VARIANT per model, policy variant
Existing files are skipped, so a failed run can simply be restarted.
"""

import re
import sys
from concurrent.futures import ThreadPoolExecutor

from config import MODELS, RESULTS, RUNS_GUIDED, RUNS_UNGUIDED, RUNS_UNGUIDED2, RUNS_VARIANT
from llm_clients import generate
from prompts import adapter_prompt, guided_prompt, unguided_prompt

ENC_DIR = RESULTS / "encodings"
CODE = re.compile(r"```python\s*\n(.*?)```", re.S)


def write_atomic(path, text):
    """Write via a temp file, so an interrupted run never leaves a half-written encoding behind."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text)
    tmp.replace(path)


def extract_code(text):
    blocks = CODE.findall(text)
    return max(blocks, key=len) if blocks else text


def one_guided(family, i, variant="original"):
    mode = "guided" if variant == "original" else f"guided_{variant}"
    path = ENC_DIR / mode / f"{family}_{i}.py"
    if path.exists():
        return path
    text = generate(family, guided_prompt(variant), tag=f"{mode}_{i}")
    write_atomic(path, extract_code(text))
    return path


def one_unguided(family, i, mode="unguided"):
    enc = ENC_DIR / mode / f"{family}_{i}.py"
    adp = ENC_DIR / mode / f"{family}_{i}_adapter.py"
    glossary = mode == "unguided2"  # second unguided run: glossary definition of infertility included
    if not enc.exists():
        write_atomic(enc, extract_code(generate(family, unguided_prompt(glossary), tag=f"{mode}_{i}")))
    if not adp.exists():
        # The adapter is written by the same model family: LLM-based matching of its own fields
        # to the reference interface, as in Vernie and Grabmair's node matching.
        write_atomic(adp, extract_code(generate(family, adapter_prompt(enc.read_text()), tag=f"{mode}_adapter_{i}")))
    return enc


def main(mode):
    (ENC_DIR / mode).mkdir(parents=True, exist_ok=True)
    if mode == "unguided":
        runs, job = RUNS_UNGUIDED, one_unguided
    elif mode == "unguided2":
        runs, job = RUNS_UNGUIDED2, (lambda fam, i: one_unguided(fam, i, "unguided2"))
    elif mode == "guided":
        runs, job = RUNS_GUIDED, one_guided
    else:  # guided_<variant>
        variant = mode.split("_", 1)[1]
        runs, job = RUNS_VARIANT, (lambda fam, i: one_guided(fam, i, variant))
    jobs = [(fam, i) for fam in MODELS for i in range(runs)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(job, fam, i): (fam, i) for fam, i in jobs}
        failed = 0
        for fut, (fam, i) in futures.items():
            try:
                print("ok  ", fut.result())
            except Exception as exc:
                failed += 1
                print("FAIL", fam, i, type(exc).__name__, str(exc)[:200])
    print(f"{mode}: {len(jobs) - failed} of {len(jobs)} encodings present. "
          + ("Re-run the same command to fill the gaps." if failed else "Complete."))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "guided")
