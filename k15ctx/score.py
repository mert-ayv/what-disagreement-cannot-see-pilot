"""Score the K15 context test against answer_key.json. Usage: python3 score.py"""
import json, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
key = {k["n"]: k for k in json.load(open(HERE / "answer_key.json"))}
conds = ["c0_provision", "c1_recall", "c2_authority", "c3_placebo"]
table = {}
for c in conds:
    f = HERE / "results" / f"{c}_answers.txt"
    if not f.exists():
        print(c, "missing"); continue
    got = {}
    for line in f.read_text().splitlines():
        m = re.search(r"case\s*(\d+)\s*:\s*([12])\s*\|\s*confidence\s*(\d+)", line, re.I)
        if m:
            got[int(m.group(1))] = (m.group(2), int(m.group(3)))
    hits = [n for n in key if n in got and got[n][0] == key[n]["correct_label"]]
    conf = [got[n][1] for n in got]
    table[c] = {n: (got.get(n, ("-", 0))[0] == key[n]["correct_label"]) for n in key}
    print(f"{c:14} answered {len(got)}/16  correct {len(hits)}/16  mean confidence {sum(conf)/max(len(conf),1):.0f}")
print("\nper case (1 = matches authority):")
print("case  " + "  ".join(c[:2] for c in table))
for n in key:
    print(f"{n:>4}  " + "   ".join("1" if table[c][n] else "0" for c in table) + f"   ({key[n]['provision']})")
