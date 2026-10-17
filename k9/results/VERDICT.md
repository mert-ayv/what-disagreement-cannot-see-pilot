# K9 kill test: verdict (2026-10-16)

Inputs, criterion and patterns were fixed before comparison: `../PREREGISTRATION.md`, `patterns_summary.md`.
Blind reader: one Claude subagent, the three input files only, no encodings (`blind_reader.md`, 43 items, plus 13
internal tensions per version).

## Comparison

| Pattern | Reader | Items |
|---|---|---|
| R1 two-step structure (basic services first, medical necessity) | named, right direction | 1, 9, 11, 12 |
| R2 sterilization no longer a bar | named | 36, 37 (and 38, 39 where sterilization is the only cause) |
| R3 FSH criterion gone | named | 30, 31, 32 |
| R4 women without a male partner qualify without donor-cycle minimum | named | 24, 25 (27 for no diagnosed cause) |
| R5 less-costly-treatment bar removed | named | 10 |
| R6 months counted on "regular" intercourse instead of timed vs frequent | partly: the old timed/frequent tension is noted (old tension 5) and the months rule is discussed (19 to 22), but the change in counting basis is not stated as a change | 19 to 22 |
| D1 ovulation induction: benefit vs exclusion | flagged, and sharper than the encoding (drug excluded under both readings; only the non-drug services depend on the conflict) | 2, 3, 8 |
| D2 natural ageing | flagged | 33, 34, 35 |
| D3 couples below months with a documented cause | flagged | 19, 20, 22 |

Robust: 5 of 6 fully, 1 partly (about 92%). Reading-dependent: 3 of 3.
Beyond the grid, the reader lists about 25 further changes the encoding does not model (covered dependent children,
non-specialist physicians, 7th and later IUI, hCG and GnRH drugs, oral ovulation induction, insured surrogates,
thawing, uninsured partner's sperm, partner's ageing, gender dysphoria, prior approval, unexplained infertility, a
possible loss of coverage for women without a male partner and no diagnosed cause, item 26).

## Verdict: K9 as framed is dead

Pre-registered rule: dead if the reader names at least 90% of the robust patterns with the right direction and flags at
least 90% of the reading-dependent ones. Both thresholds are met. A current frontier model reading the two texts
predicts the outcome-level changes as well as the enumeration and finds more of them. The behavioural diff adds case
counts over a synthetic grid, which have no population meaning.

## What the test shows instead
- The hard part of a version change is not finding what changed but the reading conflicts the new text creates: the
  reader names six (benefit vs exclusion, causation clause vs ASRM, ASRM months as waiting period or not, sequencing of
  tiers, scope of "otherwise covered", ageing as dysfunction) and 13 internal tensions in the new text.
- The reader resolves each conflict with a stated "more plausible" reading. Whether lawyers, the insurer or a court
  would agree is untested; that is the part current models do not settle (see K1 proxy: readers split, they do not
  abstain).
- Same lesson as the V3 pilot: detection and translation are at ceiling; authority and validation are not.

## Limits
One version pair (a rewrite), one reader from the same model family as the encoder, the encoding is one reading,
pattern matching judged by the author of the encoding.

## Cross-check with the prior-work check (`design-codex-261015/checks/K9-checks.md`, 2026-10-16)
- Check B `open`: nobody computes outcome diffs between legal rule versions from LLM encodings or tests whether
  readers predict them. Check A `weakened`; its reformulation ("how much of the verified diff does a reader recover")
  is exactly what this test measured, and the answer is "nearly all, and more than the grid".
- The check's own kill criterion is stricter (recall and precision at least 0.95). Robust-pattern recall here is about
  0.92, so K9 is borderline under that rule; but the reader's 25 extra changes show the enumerated diff, not the
  reader, is the incomplete instrument, so the verdict stands.
- Correction from the check: CodeX's repo encodes **2024-25** (predicates `covered_under_cardinal_care_24_25_benefit`);
  2023-24 is text only. The "old" side here is the expert port of the 2024-25 encoding, compared with the 2023-24 text
  the reader saw. The infertility rule is assumed unchanged between those years (the 2024-25 certificate is not in the
  repo); this does not affect the verdict.
- One practice signal survives: Vaden's official "what's new 2025-26" page lists carrier, network, deductible,
  copays, referrals and pharmacy, but not the infertility rewrite. Human change summaries miss coverage-logic changes
  that an LLM reader finds; that is a deployment point, not a research gap.
