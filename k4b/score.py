"""Score K4b answers. Usage: python3 score.py answers_A1.txt [...]  Prints per-message verdicts for manual review."""
import json, re, sys
from collections import Counter, defaultdict
idmap = json.load(open("id_map.json"))
POINT = {**{f"M{i:02d}": f"P{(i - 1) // 4 + 1}" for i in range(1, 25)}, **{f"C{i:02d}": "C" for i in range(1, 11)}}
EXPOSED = {f"M{i:02d}" for i in range(1, 25) if (i - 1) % 4 < 2}
KW = {"P1": r"sterili|vasectom|partner", "P2": r"\btimed\b.*\bfrequent\b|\bfrequent\b.*\btimed\b",
      "P3": r"glossary|semen|female partner", "P4": r"no row|without a female partner|table",
      "P5": r"after age 40|since .*40|40th|turn(ed|ing) 40|before .*40", "P6": r"natural|physiologic|age-related|age related"}
for f in sys.argv[1:]:
    rows = {}
    for line in open(f):
        m = re.match(r"\s*Case (\d+):\s*(COVERED|NOT COVERED|NEED INFO)\s*\|\s*questions:(.*?)\|\s*wording unclear for this case:(.*?)\|(.*)", line)
        if m:
            rows[f"Case {m.group(1)}"] = m.groups()[1:]
    stats = defaultdict(Counter)
    print(f"\n===== {f}: parsed {len(rows)}")
    for case, mid in sorted(idmap.items(), key=lambda kv: kv[1]):
        if case not in rows:
            print(mid, "MISSING"); continue
        dec, qs, unclear, reason = rows[case]
        p = POINT[mid]
        if p == "C":
            flagged = unclear.strip().lower().startswith("yes")
            stats["control"]["false_flag" if flagged else "clean"] += 1
            print(f"{mid} {p}  {dec:11} flag={flagged} | unclear:{unclear.strip()[:110]}")
        else:
            text = (qs + " " + unclear).lower()
            named = bool(re.search(KW[p], text))
            flagged = (unclear.strip().lower().startswith("yes") and named) or (dec == "NEED INFO" and named)
            key = "exposed" if mid in EXPOSED else "fitting"
            stats[key]["flagged" if flagged else "silent"] += 1
            stats[p]["flagged" if flagged else "silent"] += 1
            print(f"{mid} {p} {key[:3]} {dec:11} flag={flagged} | q:{qs.strip()[:70]} | unclear:{unclear.strip()[:110]}")
    for k in ["exposed", "fitting", "P1", "P2", "P3", "P4", "P5", "P6", "control"]:
        print(k, dict(stats[k]))
