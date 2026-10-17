#!/bin/sh
# Full pilot run. Safe to interrupt and re-run: finished encodings and cached predictions are kept,
# only missing pieces are generated or evaluated again.
cd "$(dirname "$0")/src" || exit 1
PY=../.venv/bin/python

$PY llm_clients.py                                      # connection test: one tiny call per model
[ -f ../data/cases.pkl ] || $PY enumerate_cases.py      # 907,200 boundary cases (only if missing)

$PY generate_encodings.py guided              # 3 models x 5 runs
$PY generate_encodings.py unguided            # 3 models x 2 runs, plus one adapter each
$PY generate_encodings.py guided_thresholds   # memorisation test: ages 35->37, FSH 19->17
$PY generate_encodings.py guided_logic        # memorisation test: "or"->"and", FSH window 12->9 months

$PY evaluate.py                               # results/summary_*.md and per_encoding_*.csv
echo
echo "If any step above reported missing encodings, run ./run_all.sh again; it only fills the gaps."
