# K15 context test: pre-registration (2026-10-17, before any run)

Question (second half of K15's kill criterion): does supplying the authoritative text change which reading a model
picks, beyond what the model already knows and beyond any same-length legal text?

Cases: the 16 of 30 sampled C11 disagreements where the feasibility check found an authority that supports one reading
(checks/K15-feasibility.md: all Bind, Guid and EDPB cases whose entry says "Supports: A" or "B"; list in
answer_key.json). Presentation order of the two readings swapped for half the cases (seed 20261017); correct label is
reading 1 in 9 cases, reading 2 in 7.

Conditions (identical header; one fresh agent per condition, no tools, no web):
- c0 provision only
- c1 provision plus the instruction to apply the case law and guidance the model knows
- c2 provision plus the verbatim authority passages (no commentary)
- c3 placebo: provision plus the verbatim passages of a case from a different provision (same kind and length of text)

Metric: share of cases where the chosen reading matches the authority (n = 16 per condition), with mean confidence.

Reading of results, fixed in advance:
- K15's "context adds information" claim is **dead** if c0 or c1 is within 2 cases of c2 (the model already picks
  the authority's reading without seeing it), or if c3 is within 2 cases of c2.
- **Alive** if c2 exceeds both c1 and c3 by at least 4 cases (25 points).
- In between: weakened; report per case.

Limits: one model family (Claude subagents; the feasibility mapping was also done by Claude), n = 16, one run per
condition, a judgement task as a proxy for re-formalization with context; authority mapping by one non-lawyer agent.
