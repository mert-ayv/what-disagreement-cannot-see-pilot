"""Run one unguided encoding plus adapter on a few claims, in a separate process (for self_repair.py).

Usage: python run_subset.py <encoding.py> <adapter.py> <claims.pkl> <out.json>

claims.pkl: list of reference claims. out.json: one record per claim,
{"pred": true | false | null, "adapted": <dict the adapter produced>, "error": <message or null>},
or {"crash": "<error>"} if a file does not load.
"""

import copy
import json
import pickle
import sys
import traceback

from run_encoding import load_function


def main():
    enc_path, adapter_path, claims_path, out_path = sys.argv[1:5]
    claims = pickle.load(open(claims_path, "rb"))
    try:
        fn = load_function(enc_path, "covered_under_benefit")
        adapt = load_function(adapter_path, "adapt")
    except Exception:
        json.dump({"crash": traceback.format_exc(limit=2)}, open(out_path, "w"))
        return
    out = []
    for claim in claims:
        rec = {"pred": None, "adapted": None, "error": None}
        try:
            adapted = adapt(copy.deepcopy(claim))
            rec["adapted"] = adapted
            rec["pred"] = bool(fn(copy.deepcopy(adapted)))
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"[:300]
        out.append(rec)
    json.dump(out, open(out_path, "w"), default=str)


if __name__ == "__main__":
    main()
