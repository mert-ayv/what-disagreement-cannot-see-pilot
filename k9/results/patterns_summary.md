# K9 change patterns (from the behavioural diff; written before reading the blind reader's list)

Diff: `../src/diff.py` over the pilot's 907,200 claims x 4 combinations of the two new facts (basic services tried
and failed; medically necessary) = 3,628,800 cases; old = expert port at certificate level; new = `../src/wellfleet.py`
under 8 plausible readings. Sanity checks: 7 hand cases with known answers, all as intended (session log 2026-10-16).

Totals: 202,510 cases change under every plausible reading (123,226 old-denied now covered; 79,284 old-covered now
denied); 381,960 change under some readings only; 3,044,330 unchanged.

## Robust changes (same direction under all 8 plausible readings)

| id | Pattern | Direction | Cases (IUI unless noted) |
|---|---|---|---|
| R1 | Claims covered before are denied unless basic services were tried without success and medical necessity is determined (new two-step structure) | covered -> denied | 39,642 IUI + 39,642 OI |
| R2 | Voluntary sterilization (of the patient) no longer bars coverage; only reversal is excluded | denied -> covered | 31,200 |
| R3 | The FSH criterion is gone (level 19 or more, test too old, all tests after 40) | denied -> covered | 13,816 |
| R4 | Women without a male partner qualify by need for donor gametes (ASRM), without the 12 / 6 donor-cycle minimum | denied -> covered | 25,920 |
| R5 | "Less costly treatment" bar removed (replaced by the basic-services-first step) | denied -> covered | 31,200 |
| R6 | Couples (and male patients with a female partner) counted on "regular, unprotected intercourse" months instead of the old frequent vs timed split | denied -> covered | 20,520 + 570 + 3,600 |

## Reading-dependent changes

| id | Pattern | Depends on | Cases |
|---|---|---|---|
| D1 | Ovulation induction with menotropins: benefit 6 lists "Ovulation induction and monitoring" as covered, the exclusions list it and "Injectable infertility medication, including ... menotropins". Every OI outcome change depends on which prevails (old-covered OI lost under "listed"; R2 to R6 gains for OI only under "benefit") | exclusion reading | 13,214 covered -> maybe denied; about 214,000 denied -> maybe covered |
| D2 | Infertility from a natural process (menopause, perimenopause, male reproductive ageing): barred before; now depends on whether "the result of malformation, disease or dysfunction" excludes it or ASRM's "disease" definition admits it | cause reading | 62,400 IUI + 62,400 OI |
| D3 | Couples below 12 / 6 months but with a documented condition: covered only if ASRM's first bullet ("based on ... history, ... diagnostic testing") suffices without the months rule | ASRM reading | 43,080 IUI (+ same OI, also D1) |
| D0 | (implausible) the exclusion heading "Infertility Treatment (male or female)" removes all infertility treatment, which would make benefit 6 meaningless | exclusion reading | all |

## Textual changes outside the case grid (not counted as patterns; a reader who lists them is right)
- Aetna's 6 artificial-insemination attempts per policy year: no cycle limit in the Wellfleet benefit.
- Gender dysphoria route to "infertile" (Aetna glossary): absent in Wellfleet (not varied in the grid).
- Precertification by the National Infertility Unit (Aetna): no counterpart found in the excerpt.
- Donor sperm purchase excluded in both versions.

## Caveats
R5 and R6 rest partly on how old fields map to new text (less costly treatment vs basic services first; frequent
vs timed vs regular intercourse). The new facts (basic services tried, medical necessity) are binary stand-ins for
clinical judgement. One encoder (Claude), no legal review.
