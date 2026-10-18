# kB pre-registration: the role test with self-defined input interfaces (written 2026-10-18, before any kB run)

## Question
In kA the input interface was fixed (the CodeX claim fields plus the partner's sterilization). Does the role test
still reveal the open points when each model defines its own input fields, and do the interface choices themselves
differ between member, insurer and neutral encodings?

## Design
- Prompts: kA prompts with the same role line, policy text and glossary; the fixed interface and helpers are replaced
  by an instruction to define a SCHEMA of input fields and an encoding that reads only those fields (as in pilot
  experiment 3). Built by `make_prompts.py`.
- Encoders: Claude Opus 5.5 (fresh agents), Gemini 3.8 Flash and GPT-6.1 Sol (APIs); per family 3 neutral, 3 member,
  3 insurer encodings. GPT-6 Astra only if credit allows, reported separately.
- Adapter: for each encoding, a separate call by the same model family writes `adapt(ref_claim)`, mapping the kA
  reference claim onto the encoding's SCHEMA, and lists in ASSUMED_MET the fields the reference does not cover
  (set to met). Template: `adapter_template.txt`.
- Cases: the kA grid (1,814,400 cases) and the CodeX comprehensive examples, unchanged.
- Outcomes per case: "met" (ASSUMED_MET fields as met; primary, comparable with kA) and "unknown" (those fields
  removed); undetermined = the two differ.
- Admissibility, slack, attribution, direction: exactly as kA (`evaluate_B.py`), applied to encoding + adapter.
- Point predicates: kA's, with one correction made before the run: F5 (tied FSH tests) applies to female patients
  only, since FSH requirements apply only to them (found with a mock check on 2026-10-18; kA counted male cases with
  tied tests under F5). Point D (donor cycles vs glossary) added as in the cross-family analysis.
- Attribution is reported twice: a point counts as recovered if strict-slack cases fall on it (kA's rule), and,
  stricter, if strict-slack cases fall on it and on no other recorded point.

## Measures
1. Admissibility rate of role encodings (encoding + adapter) per family.
2. Strict and any-pair slack; recovered points under both attribution rules; comparison with kA per family.
3. Neutral disagreement within each family and across families.
4. Undetermined share per encoding.
5. Interface: SCHEMA fields and ASSUMED_MET fields per encoding; fields that only member or only insurer encodings
   define (descriptive, read by hand).

## Criteria (per family)
- Instrument fails if more than a third of the role encodings are inadmissible. Then the result is "not measurable
  with this design for this family" (adapter or reading failure), reported as such.
- Replication of kA holds if the instrument works, strict slack recovers at least 3 of the 6 representable points
  under the stricter attribution rule, and member encodings cover at least as often as insurer encodings on every
  recovered point.
- Interface effect (exploratory, no threshold): fields defined by one side only, and slack cases matching no recorded
  point, are listed and read by hand.

## Mock checks (run before this file was frozen, no model calls)
`mock/`: an expert copy behind an identity adapter agrees 100% with the expert and is admissible; an adapter that
drops the FSH tests is excluded by the floor; a member mock that also covers men without a partner yields slack on
F4 only (34,560 cases) under the corrected predicates.

## Limits stated in advance
One coverage; the adapter is itself an LLM matching step and can err (the floor catches gross errors only); grid
built around the known points; nine encodings per family.
