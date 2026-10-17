# Consistency of the C11 ambiguity label (2026-10-17)

Data: Vernie and Grabmair, "By Their Fruits You Will Know Them" (EMNLP 2026), Zenodo record 22128911 (MIT),
`verbalizations.jsonl.gz`: 148 verbalized edge cases, each labelled by an LLM `legal_ambiguity` (85) or
`formalization_error` (63). The paper reports no expert check of this label. Script:
`label_consistency.py`; output: `results.txt`. No API cost.

Artefacts seen: README of the record; 20 cases read (6 in full: scenario, question, divergence analysis; 14 by title
and first lines of the analysis). Scenarios average 123 words, analyses 238 words: short enough for a law-trained
reader to judge in a few minutes each.

## Result
When the same disagreement recurs across different model pairs, the label often flips:
- Same provision and same root-cause concept: 35 groups (110 cases), 17 with mixed labels; pairwise agreement
  104 of 186 = **0.56**.
- Same provision, same root cause and identical stipulated facts: 7 groups (15 cases), 4 with mixed labels;
  pairwise agreement 5 of 9 = **0.56**.
- Agreement expected by chance at the label base rates: 0.51.

## Reading
Suggestive, not conclusive. Two cases with the same facts and root cause can still involve different formalizations,
so a flip is not proof of an inconsistent label; and n = 9 pairs in the strict grouping is small. But on the evidence
available, the label separating "the text is open" from "a model got it wrong" behaves close to chance across
recurrences. This is the step where a human reference adds most, and the released cases make it cheap to build.

