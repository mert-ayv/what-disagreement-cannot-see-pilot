# Direction of resolution on silent points: existing evidence (2026-10-17)

Source: pilot experiment 4 (`../results/FINDINGS.md`, direct answers, 10.10.2026; API runs, two model families,
three runs each) and K4b (`../k4b/FINDINGS.md`).

| Point where the text is silent | Expert encoding (CodeX port) | Claude Opus 5.5, direct | GPT-6.1 Sol, direct |
|---|---|---|---|
| Man without a female partner (8 cases) | not covered | covered 8/8 | covered 8/8 |
| Age 40+, no FSH test since the 40th birthday (8) | not covered | covered 8/8 (2/8 consistent across runs) | covered 8/8 |
| Two FSH tests with the same date and time (6) | not covered | covered 6/6 | covered 6/6 |
| Man with a female partner, glossary gap (K4b P3, 4 messages x 2 runs) | needs semen criterion (closed world: unknown = not met) | covered 8/8 (agent) | not run |

Reading: where the text says nothing, the encoding resolves by negation as failure (unknown or unmet = not covered)
and the reasoning models resolve toward coverage, in both families. Exception that is not a silent point: "you or
your partner" (K4b P1), where the text is explicit and the encoding omits the partner; there the models deny and
the encoding grants. So the claim is about silence, not about encodings versus models in general.

Contra proferentem (ambiguity construed against the drafter) favours the models' direction on genuinely ambiguous
terms; whether it applies to silence (a gap) rather than ambiguity is a legal question to check.
