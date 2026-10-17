# K9 kill test: pre-registration (written 2026-10-16, before any result)

## Question
When a coverage rule changes version, are the outcome-level changes predictable from reading the two texts? K9 is
worth pursuing only if a verified behavioural diff adds information a careful reader does not already have.

## Material
- Old version: Aetna, Stanford Cardinal Care 2023-24, Comprehensive Infertility (IUI and ovulation induction with
  menotropins), with schedule, exclusions and glossary (`inputs/A_aetna_2023-24.txt`). Reference encoding: the pilot's
  port of CodeX's expert Epilog encoding (`../src/expert.py`, 75 of 75 CodeX tests).
- New version: Wellfleet, Stanford SHIP 2025-26, Infertility Treatment Benefit, Medically Necessary definition,
  Family Planning exclusions, schedule (`inputs/W_wellfleet_2025-26.txt`), plus the ASRM 2023 definition it references
  (`inputs/ASRM_2023.txt`).
- Aetna 2024-25 is not usable: CodeX's repo holds only its benefit summary, which carries no eligibility rules.

## Procedure
1. Blind reader: an agent that never sees any encoding reads the three input files and lists every situation where
   coverage of IUI or ovulation induction with menotropins differs between versions (who, conditions, direction,
   and whether it depends on how the new text is read). Saved before step 2 results are shown to it.
2. Behavioural diff: a Wellfleet encoding over the pilot's case space (same claim fields; new facts the old space
   lacks are added as explicit dimensions), with every interpretive choice of the new text as a named parameter.
   Diff = cases whose outcome differs between the expert port (old) and the Wellfleet encoding (new), grouped into
   change patterns; each pattern marked robust (same under all plausible readings) or reading-dependent.
3. Compare the reader's list with the patterns.

## Kill criterion
K9 as framed ("outcome changes are not obvious from the text") is **dead** if the blind reader names, with the right
direction, at least 90% of the robust change patterns and flags at least 90% of the reading-dependent ones.
It is **alive** if the reader misses or misstates at least 2 robust patterns, or misses at least 2 reading-dependent
ones. In between: weakened; report which kind of pattern the reader misses.

## Known limits (stated in advance)
- One coverage, one version pair, and the pair is a rewrite rather than an amendment.
- The Wellfleet encoding is mine (one careful reading with explicit parameters), not an expert's; the reader is
  one Claude agent, not a lawyer.
- Case space inherited from the pilot (boundary values), so pattern counts depend on its grid.
- No API spend: the reader is a Claude subagent.
