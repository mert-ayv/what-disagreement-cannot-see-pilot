"""Consistency of the LLM label legal_ambiguity vs formalization_error in Vernie and Grabmair's released cases.

Data: Zenodo record 22128911 (MIT), verbalizations.jsonl.gz, 148 verbalized edge cases (downloaded 2026-10-17;
not redistributed here). Usage: python3 -I label_consistency.py <path to verbalizations.jsonl.gz>
Groups cases that describe the same disagreement and checks whether they carry the same label.
"""
import gzip, json, sys
from collections import Counter, defaultdict

rows = [json.loads(l) for l in gzip.open(sys.argv[1], "rt")]
lab = lambda r: r["verbalization"]["interpretation_type"]
p = sum(lab(r) == "legal_ambiguity" for r in rows) / len(rows)
print(f"cases {len(rows)}: {Counter(map(lab, rows))}; chance agreement at base rates {p*p + (1-p)*(1-p):.2f}")


def report(name, key):
    g = defaultdict(list)
    for r in rows:
        g[key(r)].append(r)
    multi = [v for v in g.values() if len(v) > 1]
    pairs = [(a, b) for v in multi for i, a in enumerate(v) for b in v[i + 1:]]
    agree = sum(lab(a) == lab(b) for a, b in pairs)
    mixed = sum(len({lab(x) for x in v}) > 1 for v in multi)
    print(f"{name}: {len(multi)} groups with >1 case ({sum(map(len, multi))} cases), {mixed} with mixed labels; "
          f"pairwise agreement {agree}/{len(pairs)} = {agree/len(pairs):.2f}")


report("provision + root-cause EC", lambda r: (r["provision"], tuple(sorted(r["deepest_rc_ec_ids"]))))
report("provision + root-cause EC + identical stipulated facts",
       lambda r: (r["provision"], tuple(sorted(r["deepest_rc_ec_ids"])),
                  tuple(sorted((r["prime_implicant_labels"].get(k, k), v) for k, v in r["prime_implicant"].items()))))
