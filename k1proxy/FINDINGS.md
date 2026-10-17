# K1 proxy: do readers agree that an item is undetermined? (2026-10-16)

Data: LegalBench insurance_policy_interpretation, raw Prolific responses (Waldon, Brodsky, Ma, Degen 2023):
138 items (46 clauses x 3 author-designed versions), 4,140 responses, 30 per item; options yes / no / can't decide.
Script: `agreement.py`; output: `results.txt`. No API cost.

Kill criterion set before running (chat, 2026-10-16): K1's core claim ("annotators agree on undetermined well above
chance") is dead if agreement is near chance.

## Results
- Fleiss' kappa over all items, three categories: **0.336** (fair; not near chance).
- But individuals almost never answer "can't decide": **4.2%** of responses. On the 59 items LegalBench labels
  ambiguous, the mean "can't decide" share is 6.0%, the maximum 20%, and on **no** item is it the most frequent answer.
- Ambiguity shows up only as **disagreement in the aggregate**: on the "controversial" versions, the minority side
  of yes/no holds 30.6% on average; each reader still picks a side.
- The authors' own intended determinacy is often not shared: 18 of 46 versions written as "unambiguous, not covered"
  end up ambiguous by the crowd rule (39%), and 7 of 46 "controversial" versions end up clearly covered.
- Within one design, kappa is 0.10 to 0.14, but that number is depressed by prevalence (most items in a design share
  the same majority) and should not be read as agreement on ambiguity.

## Verdict for K1 (weakened, not dead)
Asking 2 to 3 annotators "is this case undetermined?" will mostly return confident yes/no answers that differ, not
"undetermined" labels. Undetermined cases are detectable as **split readings across many readers**, which 2 to 3
law-trained annotators cannot provide. Implications:
- K1 as designed (few annotators labelling "open") is weak; a distributional design (many readers, or adversarial
  readings as in K11, or several encoders) fits the evidence better.
- For K2 and K9 this supports treating interpretive points as **competing readings** (named parameters), not as a
  third label.

## Limits
Lay crowd (3,870 of 4,140 responses from people reporting no legal training), one-sentence clauses written to be
tricky, US Prolific sample; licence of the raw file unstated (analysis only, not redistributed).
