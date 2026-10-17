"""Build the four condition files for the K15 context test.
Usage: python3 -I build.py <feasibility.md> <verbalizations.jsonl.gz> <laws dir> <out dir>
"""
import gzip, json, random, re, sys
from pathlib import Path

feas, vpath, laws, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
CASES = [21, 25, 32, 23, 35, 146, 130, 125, 51, 59, 53, 74, 87, 94, 95, 103]
rows = sorted((json.loads(l) for l in gzip.open(vpath, "rt")), key=lambda r: (r["provision"], r["task_id"]))
body = open(feas).read().split("## Cases", 1)[1]
blocks = {int(m.group(1)): b for b in re.split(r"\n(?=\*\*#\d+ )", body) if (m := re.match(r"\*\*#(\d+) ", b.strip()))}


def field(b, name):
    m = re.search(name + r":\s*(.*?)(?=\s(?:A|B):\s|\n- |\n\n|$)", b, re.S)
    return m.group(1).strip() if m else ""


items = []
for n in CASES:
    b, r = blocks[n], rows[n]
    disputed = field(b, "Disputed point")
    ra = re.search(r"\sA:\s(.*?)(?=\sB:\s)", b, re.S).group(1).strip()
    rb = re.search(r"\sB:\s(.*?)(?=\n- |\n\n)", b, re.S).group(1).strip()
    sup = re.search(r"Supports:\s*([AB])", b).group(1)
    qblock = re.search(r"- Quotes?\b.*?(?=\n- Confidence)", b, re.S)
    quotes = re.findall(r"\"[^\"]+\"", qblock.group(0)) if qblock else []  # verbatim quotes only, no commentary
    auth = re.search(r"Authority:\s*(.*?)\n", b).group(1).strip()
    items.append(dict(n=n, provision=r["provision"], scenario=r["verbalization"]["scenario"],
                      question=r["verbalization"]["question"], disputed=disputed, A=ra, B=rb, supports=sup,
                      authority=auth, quotes=quotes))

rng = random.Random(20261017)
for it in items:  # swap presentation order for half the cases
    it["swap"] = rng.random() < 0.5
    it["first"], it["second"] = (it["B"], it["A"]) if it["swap"] else (it["A"], it["B"])
    it["correct_label"] = ("1" if (it["supports"] == "A") != it["swap"] else "2")
# placebo: the authority quotes of a case from a different provision
perm = items[1:] + items[:1]
for it, other in zip(items, perm):
    j = 0
    while other["provision"] == it["provision"]:
        j += 1; other = items[(items.index(it) + 1 + j) % len(items)]
    it["placebo"] = other["quotes"] or [other["authority"]]

HEADER = ("You are an EU-law analyst. Answer from your own knowledge and the material below only: do not use any "
          "tools, files, web search or other resources. For each case, decide which of the two readings of the "
          "provision is correct in EU law as it stands. Answer on one line per case: `case <id>: <1 or 2> | "
          "confidence 0-100 | one-sentence reason`.\n")
COND = {
    "c0_provision": "",
    "c1_recall": "Before answering, consider the case law of the Court of Justice and the General Court and the official "
                 "Commission and EDPB guidance you know on this point, and apply it.\n",
    "c2_authority": "",
    "c3_placebo": "",
}
key = []
for c, extra in COND.items():
    parts = [HEADER, extra]
    for it in items:
        law = (laws / f"{it['provision']}.md").read_text()
        p = [f"\n=== Case {it['n']} ===\nProvision:\n{law}\nScenario: {it['scenario']}\nQuestion: {it['question']}\n"
             f"Disputed point: {it['disputed']}\nReading 1: {it['first']}\nReading 2: {it['second']}\n"]
        if c == "c2_authority":
            p.append("Relevant authority (" + it["authority"] + "):\n" + "\n".join(it["quotes"] or [it["authority"]]) + "\n")
        if c == "c3_placebo":
            p.append("Relevant material:\n" + "\n".join(it["placebo"]) + "\n")
        parts += p
    (out / f"{c}.txt").write_text("".join(parts))
for it in items:
    key.append(dict(n=it["n"], provision=it["provision"], supports=it["supports"], swap=it["swap"],
                    correct_label=it["correct_label"], n_quotes=len(it["quotes"])))
(out / "answer_key.json").write_text(json.dumps(key, indent=1))
print(json.dumps(key))
