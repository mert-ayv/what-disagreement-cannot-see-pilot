"""One function per provider: send a prompt, get text back, save the raw response.

Keys are read from .env. Nothing here retries beyond the SDK defaults.
"""

import json
import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv

from config import EXTRA_MODELS, MODELS, RESULTS, ROOT

load_dotenv(ROOT / ".env")

RAW_DIR = RESULTS / "raw"
ATTEMPTS = 3  # per call; waits 20s, then 60s. Billing or quota errors still fail after the last attempt.
RAW_DIR.mkdir(parents=True, exist_ok=True)
_usage = threading.local()  # token usage of the last call in this thread, saved with the raw record


class RefusalError(RuntimeError):
    """The model declined the request (Anthropic stop_reason == 'refusal')."""


def _call_anthropic(model: str, prompt: str, effort: str = "high") -> str:
    import anthropic

    client = anthropic.Anthropic()
    # No server-side fallbacks on purpose: a fallback would silently swap in another
    # model, and the pilot compares models. A refusal is recorded as a failed run.
    with client.messages.stream(
        model=model,
        max_tokens=32000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        message = stream.get_final_message()
    if message.stop_reason == "refusal":
        raise RefusalError(str(message.stop_details))
    return "".join(block.text for block in message.content if block.type == "text")


def _call_openai(model: str, prompt: str, effort: str | None = None) -> str:
    from openai import OpenAI

    client = OpenAI()
    # Reasoning effort only when the model spec asks for it (config.EXTRA_MODELS); otherwise the
    # provider default, as in all runs before 11 October.
    extra = {"reasoning": {"effort": effort}} if effort else {}
    response = client.responses.create(model=model, input=prompt, **extra)
    _usage.value = response.usage.model_dump() if response.usage else None
    return response.output_text


def _call_google(model: str, prompt: str, effort: str = "high") -> str:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text


_PROVIDERS = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "google": _call_google,
}


def generate(family: str, prompt: str, tag: str, effort: str = "high") -> str:
    """Call the model configured for `family`, save prompt and output under results/raw/."""
    spec = MODELS.get(family) or EXTRA_MODELS[family]
    if spec["model"].startswith("SET_"):
        raise ValueError(f"Set the model ID for '{family}' in src/config.py first.")
    started = time.time()
    text = None
    _usage.value = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            eff = spec.get("reasoning_effort") if spec["provider"] == "openai" else effort
            text = _PROVIDERS[spec["provider"]](spec["model"], prompt, eff)
            break
        except RefusalError:
            raise
        except Exception as exc:
            if attempt == ATTEMPTS:
                raise
            wait = 20 * 3 ** (attempt - 1)
            print(f"  retry {family} {tag} in {wait}s after {type(exc).__name__}: {str(exc)[:120]}")
            time.sleep(wait)
    record = {
        "family": family,
        "model": spec["model"],
        "tag": tag,
        "seconds": round(time.time() - started, 1),
        "prompt": prompt,
        "output": text,
        "usage": _usage.value,
    }
    out = RAW_DIR / f"{tag}_{family}.json"
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    return text


if __name__ == "__main__":
    # Smoke test: one short call per configured family.
    for fam in MODELS:
        try:
            print(fam, "->", generate(fam, "Reply with the single word: ready", f"smoke").strip()[:40])
        except Exception as exc:  # report and continue to the next provider
            print(fam, "-> FAILED:", type(exc).__name__, exc)
