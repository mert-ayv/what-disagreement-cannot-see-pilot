"""Run one generated encoding on all cases, in a separate process.

Usage: python run_encoding.py <mode: guided|unguided> <encoding.py> <out.pkl> [adapter.py]

Predictions: True / False, or None if the encoding raised on that case. If the file itself does
not load, writes {"crash": "<error>"}.
"""

import copy
import pickle
import sys
import traceback

from cases import load_examples
from config import DATA
from helpers import Helpers
import gold_fill


def load_function(path, name):
    namespace = {"__name__": "encoding"}
    exec(compile(open(path).read(), str(path), "exec"), namespace)
    return namespace[name]


def main():
    mode, enc_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    adapter_path = sys.argv[4] if len(sys.argv) > 4 else None
    try:
        fn = load_function(enc_path, "covered_under_benefit")
        adapt = load_function(adapter_path, "adapt") if adapter_path else None
        schema = load_function(enc_path, "SCHEMA") if mode in ("unguided_gold", "unguided_unmet") else None
    except Exception:
        pickle.dump({"crash": traceback.format_exc(limit=2)}, open(out_path, "wb"))
        return

    def predict(claim):
        try:
            c = copy.deepcopy(claim)
            if mode == "guided":
                result = fn(c, Helpers)
            elif mode in ("unguided_gold", "unguided_unmet"):
                result = fn(gold_fill.fill(adapt(copy.deepcopy(c)), c, schema, unmet=(mode == "unguided_unmet")))
            else:
                result = fn(adapt(c))
            return bool(result)
        except Exception:
            return None

    data = pickle.load(open(DATA / "cases.pkl", "rb"))
    enumerated = [predict(c) for c, _ in data["cases"]]
    examples = [predict(c) for _, c, _ in load_examples()]
    pickle.dump({"enumerated": enumerated, "examples": examples}, open(out_path, "wb"))


if __name__ == "__main__":
    main()
