"""Pilot configuration: paths, models, run counts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
REPO = DATA / "cardinal-care-encoding"

COVERAGE_DIR = (
    REPO
    / "Encoding/Benefits/Treatment of Infertility/Coverages"
    / "treatment_of_infertility_comprehensive_coverage"
)
EXAMPLES_DIR = COVERAGE_DIR / "Example Datasets"
POLICY_PDF = REPO / "Reference Documents/Policy Docs/2023-2024_complete.pdf"

# One model per family. Provider keys come from .env.
# Fill in the OpenAI and Google model IDs you want to test before running.
MODELS = {
    "claude": {"provider": "anthropic", "model": "claude-opus-5-5"},
    # GPT-6 Astra (gpt-6-astra) is stronger but ~5x the price; Sol fits the prepaid credit.
    "openai": {"provider": "openai", "model": "gpt-6.1-sol"},
    # Gemini 3.1 Pro (gemini-3.1-pro-preview) needs billing enabled; the free tier only serves Flash.
    "gemini": {"provider": "google", "model": "gemini-3.8-flash"},
}

# Variants used only when named explicitly (not in the default model loops).
EXTRA_MODELS = {
    # GPT at maximum reasoning effort. The default is "medium"; on LegalBench it reasoned about 13 tokens per call.
    # GPT-6 Astra: stronger, about 5x the price of Sol; run only on the crowd-ambiguous LegalBench cases.
    "astra": {"provider": "openai", "model": "gpt-6-astra"},
    "astra_max": {"provider": "openai", "model": "gpt-6-astra", "reasoning_effort": "max"},
    "openai_max": {"provider": "openai", "model": "gpt-6.1-sol", "reasoning_effort": "max"},
}

RUNS_GUIDED = 5    # runs per model, guided setting (P1, P2)
RUNS_UNGUIDED = 2  # runs per model, unguided setting (P3)
RUNS_UNGUIDED2 = 5  # unguided with the glossary definition (larger sample for the variable analysis)
RUNS_VARIANT = 2   # runs per model and policy variant (memorisation test)
