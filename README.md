# What Disagreement Cannot See: pilot tests (October 2026)

Based on the CodeX Insurance Analyst and Vernie and Grabmair, "By Their Fruits You Will Know Them" (EMNLP 2026).

Author: Mert Ayvazoglu (TUM). All model outputs are kept.

## From the original exposé to the main experiment

The original exposé (1 October 2026) assumed that LLMs make translation errors when they encode a coverage rule,
and proposed a disagreement-driven loop to repair them. Three questions **raised in the interview** were tested first:

| # | Question | What was tested | What was found | What it meant |
|---|---|---|---|---|
| 1 | Do current models still make the errors the exposé wants to repair? | Kant et al.'s benchmark with current models; 14 guided encodings of the coverage (`PILOT_REPORT.md`) | 0.90 to 0.99 now vs 0.78 to 0.88 for the 2024 models; no threshold, age or partner errors | Translation is at ceiling; the repair loop has little left to repair |
| 2 | The CodeX encoding is public: do the models just reproduce it from memory? | Paired edits to the policy text and the expert encoding (age split 35 to 37 with FSH 19 to 17; "or" to "and" with the FSH window 12 to 9 months) (`PILOT_REPORT.md`, experiment 2) | All 12 encodings follow the changed text on 100% of the cases where the variants differ | The models read the text rather than recall the encoding. The encodings in the main experiment also depart from CodeX's choices (e.g. Claude covers some men without a female partner), which copying would not produce |
| 3 | Is a fixed input interface too strong an assumption? | Encodings where the models define their own input fields; a coverage agent that must ask for missing facts (`PILOT_REPORT.md`, `k4/`) | 54% of 185 self-defined fields matched the expert's; the main differences were facts the expert assumes and readings; one matching error; the agent answered all 8 plain-fact cases correctly and asked for 9 of 12 missing facts | Getting facts into variables mostly works; again the residue is readings |

**What this led to.**
1. We observed that translation, memory and the interface no longer cause errors. **What the data do show are
   readings**: points the policy text does not decide, where models pick one interpretation without saying so. For
   example, can a man without a female partner qualify? The glossary defines him as infertile, but the eligibility
   table has no row for him.
2. A model can list such points when asked: one discovery prompt finds 7 of 7 recorded choices (`k2/`). While
   deciding member questions, a coverage agent resolves them **silently**: it picks a reading without flagging it in
   6 and 8 of 24 reading-dependent questions (two runs), and in 8 of 8 answers on the gap the CodeX encoders marked
   "we're assuming" (`k4b/`).
3. Comparing neutral encodings of one model family barely reveals them, because each family resolves the open points
   almost always the same way (`kA/`). A different instrument is needed: encodings written for **opposing interests**,
   and encodings by **other model families**. The main experiment below was designed around these findings.

## Main experiment: opposing interests and model families (`kA/`)

Current models translate the coverage rule correctly. What they still differ on are **readings**: points where the
policy text does not decide the case. The experiment asks how to find those points, and how AI systems fill them.
Every encoding is a program that decides claims; each interpretive choice in it is marked and justified from the text.

Each model family wrote nine encodings of the same rule, from the same text and the same input interface. They differ
only in one instruction:
- **3 neutral**: "Encode the rule as a careful, neutral encoder would: where the text is unclear, choose the reading
  you consider most plausible." The model decides for itself.
- **3 favouring the member**: the model acts as the member's advocate and, wherever the text can reasonably be read in
  more than one way, chooses the reading most favourable to the member that a court could still accept.
- **3 favouring the insurer**: the same, as the insurer's claims counsel, choosing the reading most favourable to the
  insurer.

None may invent requirements or ignore clear ones, and every encoding must pass the clear CodeX test cases, so neither
side can simply cover or deny everything.

```mermaid
flowchart LR
    T["Policy text<br/>+ fixed input interface"]
    subgraph C["Claude Opus 5.5"]
        direction TB
        C1["3 neutral encodings<br/>(model decides itself)"]
        C2["3 encodings<br/>favouring the member"]
        C3["3 encodings<br/>favouring the insurer"]
        C1 ~~~ C2 ~~~ C3
    end
    subgraph G["Gemini 3.8 Flash"]
        direction TB
        G1["3 neutral encodings<br/>(model decides itself)"]
        G2["3 encodings<br/>favouring the member"]
        G3["3 encodings<br/>favouring the insurer"]
        G1 ~~~ G2 ~~~ G3
    end
    subgraph O["GPT-6.1 Sol and GPT-6 Astra"]
        direction TB
        O1["3 neutral encodings<br/>(model decides itself)"]
        O2["3 encodings<br/>favouring the member"]
        O3["3 encodings<br/>favouring the insurer"]
        O1 ~~~ O2 ~~~ O3
    end
    T --> C & G & O
    C & G & O --> A{"Passes the clear<br/>CodeX tests?"}
    A -- "no" --> X["excluded"]
    A -- "yes" --> R["Decide 1.8 million<br/>boundary cases"]
    E["Expert encoding<br/>(CodeX)"] --> R
    R --> M1["Member vs insurer:<br/>where do they split?"]
    R --> M2["Neutral vs neutral:<br/>same family, other families"]
    M1 --> P["Which open points?<br/>Which side wins?"]
    M2 --> P
```

| What was compared | Claude Opus 5.5 | Gemini 3.8 Flash | GPT-6.1 Sol and GPT-6 Astra | What it shows |
|---|---|---|---|---|
| Member vs insurer: cases where they split | 37,692 | 54,754 | not measurable: every member encoding failed the admissibility check | On 2 to 3% of the cases, the member and insurer encodings reach opposite outcomes. These are the cases where the text is ambiguous or leaves room for interpretation: both outcomes can be argued from the text, and both encodings still pass the clear CodeX tests |
| Known open points among the split cases | 4 of 6 | 5 of 6 | | Of the 6 known open points, Claude decides 4 and Gemini 5 differently depending on whether the encoding favours the member or the insurer |
| The same, counting only cases that involve a single open point | 2 of 6 | 4 of 6 | | Some split cases touch two open points at once; counting only cases with a single open point, Claude splits on 2 and Gemini on 4 of the 6 (`kA/results/attribution.md`) |
| Neutral vs neutral within the family: cases where they split | 3,132 | 0 | 0 | Asking the same model again finds almost none of these points |

**Two further observations:**
1. **Model families differ.** Neutral encodings of different families split on 39,700 cases, on the same open points
   (descriptive, not pre-registered).
2. **Asking one model again is not enough.** Repeated neutral encodings by the same model show almost none of the
   readings; encodings for opposite sides, or by another model family, show them.

**One case.** A 34-year-old man without a partner, with two abnormal semen analyses two weeks apart. The glossary
defines him as infertile, but the eligibility table has no row for him.

| Who decides | Outcome |
|---|---|
| Expert encoding (CodeX) | not covered |
| Insurer encodings, all families | 0 of 9 cover |
| Member encodings, all families | 8 of 9 cover (counting the GPT member encodings that failed the check) |
| Neutral encodings | Claude 3 of 3 cover; Gemini 0 of 3; GPT 0 of 3 |

**Terms.**
- *Encoding*: a program that takes a claim and returns covered or not covered.
- *Reading*: one way of resolving a point the text leaves open.
- *Open point*: such a point; six were known in advance from the CodeX encoders' notes and earlier pilot runs.
- *Admissibility check*: an encoding must pass the CodeX test cases that do not depend on an open point, so a side
  cannot simply cover or deny everything.

Details, pre-registration and the GPT failure: `kA/FINDINGS.md`. Cross-family numbers: `kA/results/crossfamily.md`.

## Revised research questions for the thesis
Translation of the coverage is at ceiling; what remains are readings: points the policy text does not settle. Within
one model family they are nearly fixed, so sampling one model again shows few of them; different families settle some
of them differently. Encodings written for the member and for the insurer, or by other model families, reveal them. Three questions
follow:
1. Where does an encoded rule allow both a member-favourable and an insurer-favourable outcome, and how many of
   these cases would comparing neutral model encodings fail to reveal?
2. Which of those points does the text, case law, official guidance or the insurer's recorded answer settle?
3. Which way do the expert encoding, different model families and a coverage agent resolve the points nothing settles, and
   what should an answer tell the member?

## All tests in detail

| Folder | Question | Result |
|---|---|---|
| `PILOT_REPORT.md`, `src/`, `results/` | Do current models still make the encoding errors the exposé targeted? | No: guided encodings near perfect; Kant et al.'s vanilla benchmark 0.78 to 0.88 (2024 models) vs 0.90 to 0.99 now; residual divergences sit on points the text does not settle |
| `k9/` | Are outcome changes between two policy versions (Aetna 2023-24 vs Wellfleet 2025-26) visible from the text? | Yes: a blind model reader predicted them as well as enumeration (dead as framed) |
| `k1proxy/` | Do readers agree that an item is undetermined? | Lay readers rarely abstain (4.2% "can't decide"); ambiguity shows as split readings |
| `k2/` | Does one prompt find the interpretive choices recorded for the expert encoding? | Yes: 7 of 7 in 3 of 3 runs (GPT-6 Astra), among 55 to 62 flagged points |
| `c11check/` | Is the released `legal_ambiguity` label stable across recurrences? | Pairwise agreement 0.56 vs 0.51 by chance (small n, preliminary) |
| `k15/`, `k15ctx/` | Do legal sources settle the released disagreements, and does supplying them change a model's reading? | Sources address 23 of 30 sampled points (mapping by an LLM agent, not a lawyer); a model picks the source's reading without seeing it (16 of 16) |
| `k4/`, `k4b/` | Does a coverage agent ask for the right facts and notice when an answer depends on a reading? | Facts: yes. Readings: silent in 6 and 8 of 24 (pre-registered 30% bar missed in run 1); the encoders' own "we're assuming" gap silent in 8 of 8; with an automatic list of readings, 0 of 24 |
| `kA/` | Do encodings written for the member and for the insurer reveal readings that neutral encodings share? | Claude: diverge on 37,692 of 1,814,400 grid cases, on 4 of 6 representable known points (2 counting only cases that involve a single point); Gemini 3.8 Flash replicates (54,754 cases, 5 of 6; 4 counting single-point cases); GPT-6.1 Sol and GPT-6 Astra fail as pre-registered (every member encoding takes a reading of "you or your partner" that two CodeX tests reject; a first GPT run stopped at an enrollment field the interface lacks). Within a family neutral encodings barely disagree (Claude 3,132 cases, Gemini and GPT 0); across families they differ on 39,700 cases on the same points (descriptive, not pre-registered). Grid built around the known points |

Folders `k2/`, `k4/`, `k4b/`, `k9/`, `k15ctx/` and `kA/` contain a `PREREGISTRATION.md` written before the runs it covers;
results are in `FINDINGS.md`, `results/VERDICT.md` or `results/scoring.md`. The repository was created on 2026-10-17
after the runs, so the git history does not timestamp the pre-registrations; the dates in the files do.
Corrections made after red-team reviews are recorded in the findings files themselves.

## Not included (third-party material)
- CodeX encoding and reference documents: https://github.com/codexstanford/cardinal-care-encoding (no licence
  declared). Clone into `data/cardinal-care-encoding/`. The Python port of the expert encoding (`src/expert.py`), which
  the scripts import, is not published here because the original carries no licence; it is available on request.
- Policy text excerpts used in prompts come from that repository's reference documents (Aetna, Cardinal Care 2023-24)
  and from the Wellfleet 2025-26 master policy (https://myahpcare.com/wp-content/uploads/Stanford_Master-Policy_25-26.pdf).
- LegalBench `insurance_policy_interpretation` (CC BY 4.0) and its raw crowd votes
  (github.com/madiganbrodsky/vague_contracts, no licence stated).
- Vernie and Grabmair's release: Zenodo record 22128911 (MIT), `verbalizations.jsonl.gz`.
- Raw API logs and prediction caches (large, and they contain the third-party texts above).

## Limits
Pilot scale. Test messages in `k4/` and `k4b/` and the encodings in `kA/` were generated by an LLM from written specifications; judges were
mostly one model family (Claude); `kA/` was run with three families (Claude, Gemini, GPT); scoring rules and their
deviations are documented in each findings file.
