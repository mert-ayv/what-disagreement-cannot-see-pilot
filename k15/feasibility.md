# K15 feasibility: do authoritative sources decide the C11 disagreements? (2026-10-17)

Data: 148 verbalized disagreements from Vernie and Grabmair, EMNLP 2026 (Zenodo 22128911, MIT), file `v.jsonl.gz`. Sample: 30 deduplicated cases, stratified by provision and LLM label. No money spent, nobody contacted. Primary texts were downloaded from the Publications Office Cellar endpoint (`publications.europa.eu/resource/celex/<CELEX>`, the same documents EUR-Lex serves; EUR-Lex itself returned an AWS WAF challenge to scripted requests), the Commission's digital-strategy download service and edpb.europa.eu. Every quote below was copied from the downloaded primary text and checked with `grep`.

## Summary

**Headline (n = 30, strict counting: a case counts as decided only when the source settles the disputed point):**

| Outcome | n | Share |
|---|---|---|
| Decided by binding authority (CJEU / General Court) | 9 | 30% |
| Decided by non-binding guidance only | 8 | 27% |
| of which Commission guidelines/notices | 6 | 20% |
| of which EDPB (or WP29 guidelines endorsed by the EDPB) | 2 | 7% |
| Undecided by any authority | 13 | 43% |
| Advocate General opinions used | 0 | 0% |

If the four "partial" cases are counted as decided by their best source (#38 and #131 binding-partial, #119 and #136 guidance-partial), the split is 11 binding / 10 guidance / 9 undecided.

Of the 13 undecided cases, 6 need no authority because the two readings are logically equivalent (#9) or the provision's own wording settles the point (#36, #88, #120, #136, #147). That leaves 7 cases (23% of the sample) where the disputed point is open legal ground: #16, #38, #39, #90, #115, #119, #131.

**By provision:**

| Provision | n | Binding | Guidance | Undecided |
|---|---|---|---|---|
| 107_tfeu | 4 | 1 | 1 (Comm.) | 2 |
| 17_gdpr | 3 | 2 | 1 (EDPB) | 0 |
| 22_gdpr | 1 | 0 | 1 (EDPB) | 0 |
| 9_gdpr | 2 | 1 | 0 | 1 |
| 6_gdpr | 4 | 2 | 0 | 2 (both partial) |
| 3_uctd | 3 | 1 | 2 (Comm.) | 0 |
| 6-7_ucpd | 3 | 0 | 0 | 3 (one partial) |
| 57_proc-dir | 4 | 2 | 0 | 2 |
| 5_ai-act | 3 | 0 | 3 (Comm.) | 0 |
| 3_dma | 3 | 0 | 0 | 3 (one partial) |
| **Total** | **30** | **9** | **8** | **13** |

**By LLM label:**

| LLM label | n | Binding | Guidance | Undecided | Undecided but text-settled |
|---|---|---|---|---|---|
| legal_ambiguity | 16 | 3 | 6 | 7 (44%) | 0 |
| formalization_error | 14 | 6 | 2 | 6 (43%) | 6 |

Findings on the label question:

1. **`legal_ambiguity` does not coincide with "undecided by authority".** 9 of 16 cases labelled `legal_ambiguity` (56%) are decided by a judgment or guidance, and in all 9 the source settles the point against one of the two readings. The undecided share is the same for both labels (44% vs 43%).
2. **`formalization_error` partly fits "authority decides against one reading".** 8 of 14 are decided. In 7 the source rejects one reading; in #4 the case law fits neither formalization exactly. All 6 undecided `formalization_error` cases need no authority, because the readings are equivalent or the text settles them. The 7 cases on genuinely open legal ground all carry the `legal_ambiguity` label.
3. **Labels conflict within one disputed point.** In 10 of the 30 sampled clusters, cases on the same disputed point carry both labels (for example 107 cluster T1: 6 legal / 2 formalization; UCTD cluster U4: 5 legal / 2 formalization). This alone shows the label does not track legal status.
4. **The result depends heavily on the provision.** AI Act and UCTD disputes are almost all settled by Commission guidance. Most GDPR disputes are settled by recent CJEU case law (2023 to 2026). DMA Article 3(8) and UCPD Article 7(4a) disputes have almost no authority yet.

**Weighted extrapolation (rough):** the 30 sampled clusters cover 93 of the 148 cases. If each cluster takes its representative's verdict, the weighted split is 32 binding / 20 guidance / 41 undecided (34% / 22% / 44%). This overstates "undecided" for cluster T1 (8 cases). Its sampled representative (#9) has two equivalent readings, but the other members dispute whether a potential Article 107(3) ground blocks incompatibility, and Iannelli (74/76, paras 11 to 12) decides that point. Cluster E2 (11 cases) also mixes sub-points: the safeguarding-law branch is addressed by Norra Stockholm Bygg (C-268/21, para 33), while the compatibility-only branch (#131) is not.

**Feasibility verdict for the thesis direction:** an authority-grounded gold label can be attached to about 57% of disagreements (73% if partials count) with a search effort of roughly 10 to 20 minutes per case once the primary corpus is downloaded. The LLM's `interpretation_type` label is not a usable proxy for that gold label.

## Sampling

- Deduplication: the 148 cases were grouped by hand into 50 clusters (same provision and same disputed point), using the full `divergence_analysis` text. One representative per cluster was drawn with `random.Random(20261017)`.
- Stratification: quotas of 4 for 107_tfeu, 57_proc-dir and 6_gdpr, 3 for 17_gdpr, 3_dma, 3_uctd, 5_ai-act and 6-7_ucpd, 2 for 9_gdpr (all cases) and 1 for 22_gdpr (all cases). Within each provision the order is seeded-shuffled and the two labels alternate where possible. Result: 16 `legal_ambiguity`, 14 `formalization_error`. 17_gdpr has only `formalization_error` cases.
- Index `#n` = position after sorting all 148 rows by (provision, task_id). Script: `scratchpad/k15scripts/sample.py`, run with `python3 -I` outside the data folder.
- Cluster map (index lists): T1 0,1,2,3,5,9,10,18 | T2 7,8,13,15,20,22 | T3 11,14,17,19 | T4 6 | T5 12 | T6 21 | T7 4 | T8 16 | G1 23,24,29,30,31 | G2 25,26,27,34 | G3 28,32,33 | R1 35 | D1 36 | D2 39,41,42 | D3 37,38,44,45 | D4 40,43 | U1 47,48,49,51,52 | U2 46,50,60 | U3 53,54,55,56,63 | U4 57,58,59,61,62,64,65 | P1 67 | P2 70,88 | P3 69 | P4 71,73,79,84,86 | P5 66,72,85,87 | P6 68,74,75,76,77 | P7 78,80,81,82,83 | P8 89,90 | A1 91,93 | A2 92 | A3 94 | A4 95 | A5 96,100,103 | A6 97 | A7 98,99,101,102,104,105 | C1 106,107,108,109,112,116,117 | C2 110,111 | C3 113,114,119 | C4 118 | C5 115 | C6 120 | E1 121 | E2 122,123,126,127,129,131,133,135,139,140,141 | E2c 132,136,142 | E3 128,130,143,145 | E4 124,137 | E5 134,138,144 | E6 125 | S1 146 | S2 147.

Sampled task_ids (prefix `verbalize-` omitted):

| # | Cluster (size) | Label | task_id |
|---|---|---|---|
| 21 | T6 (1) | LA | 107_tfeu__glm-5.1_vs_kimi-k2.5__EC_10T_EC_13T_EC_16T_EC_21F_EC_25F_EC_30F_EC_41F_EC_46T_EC_48F_EC_49F_EC_50F_EC_56F_EC_59F_EC_7T__b_true |
| 9 | T1 (8) | FE | 107_tfeu__claude-opus-4-6_vs_glm-5.1__EC_10T_EC_13T_EC_16T_EC_21F_EC_3T_EC_4T_EC_46F_EC_48T_EC_7T__a_true |
| 16 | T8 (1) | LA | 107_tfeu__deepseek-v3.2_vs_kimi-k2.5__EC_10T_EC_13T_EC_16T_EC_21F_EC_25F_EC_30F_EC_41F_EC_47F_EC_50F_EC_56F_EC_59F_EC_6T__b_true |
| 4 | T7 (1) | FE | 107_tfeu__675b-cloud_vs_qwen3.5__EC_10T_EC_13T_EC_16T_EC_21F_EC_25F_EC_30F_EC_41F_EC_47F_EC_50F_EC_56F_EC_59F__a_true |
| 25 | G2 (4) | FE | 17_gdpr__claude-opus-4-6_vs_gemini-3.1-pro-preview__EC_10F_EC_11F_EC_12F_EC_13F_EC_14F_EC_17F_EC_19F_EC_2F_EC_23F_EC_26F_EC_27F_EC_6F_EC_9T__b_true |
| 32 | G3 (3) | FE | 17_gdpr__gemini-3.1-pro-preview_vs_glm-5.1__EC_10F_EC_11F_EC_12F_EC_13F_EC_14F_EC_17F_EC_18F_EC_2F_EC_23F_EC_25F_EC_27F_EC_4T_EC_6F__a_true |
| 23 | G1 (5) | FE | 17_gdpr__675b-cloud_vs_deepseek-v3.2__EC_11T_EC_17F_EC_18T_EC_30T__b_true |
| 35 | R1 (1) | LA | 22_gdpr__675b-cloud_vs_gemini-3.1-pro-preview__EC_15F_EC_2T_EC_30T_EC_32T_EC_8T__a_true |
| 38 | D3 (4) | LA | 3_dma__675b-cloud_vs_gpt-5.4__EC_12F_EC_36T_EC_38T_EC_39T_EC_40T_EC_45F_EC_46F_EC_47F_EC_48F_EC_49F_EC_50F_EC_51F_EC_52T_EC_53T_EC_72T_EC_74T__b_true |
| 36 | D1 (1) | FE | 3_dma__675b-cloud_vs_claude-opus-4-6__EC_12F_EC_36F_EC_72T_EC_74T_EC_75T__b_true |
| 39 | D2 (3) | LA | 3_dma__675b-cloud_vs_gpt-5.4__EC_12F_EC_36T_EC_38T_EC_39T_EC_40T_EC_45T_EC_52F_EC_53T_EC_72T_EC_74T__b_true |
| 51 | U1 (5) | LA | 3_uctd__675b-cloud_vs_glm-5.1__EC_11T_EC_12T_EC_3F_EC_5T_EC_7T__a_true |
| 59 | U4 (7) | FE | 3_uctd__claude-opus-4-6_vs_qwen3.5__EC_13F_EC_3T_EC_5T_EC_6T_EC_7T__a_true |
| 53 | U3 (5) | LA | 3_uctd__claude-opus-4-6_vs_gemini-3.1-pro-preview__EC_11F_EC_13T_EC_5T_EC_6T_EC_7T__b_true |
| 90 | P8 (2) | LA | 57_proc-dir__gemini-3.1-pro-preview_vs_qwen3.5__EC_123T_EC_124T_EC_152T_EC_153T__b_true |
| 88 | P2 (2) | FE | 57_proc-dir__gemini-3.1-pro-preview_vs_qwen3.5__EC_123F_EC_32F_EC_64T__a_true |
| 74 | P6 (5) | LA | 57_proc-dir__deepseek-v3.2_vs_glm-5.1__EC_15F_EC_29F_EC_64T_EC_99T__a_true |
| 87 | P5 (4) | LA | 57_proc-dir__gemini-3.1-pro-preview_vs_qwen3.5__EC_123F_EC_124T_EC_153T_EC_64T__b_true |
| 94 | A3 (1) | LA | 5_ai-act__675b-cloud_vs_kimi-k2.5__EC_10T_EC_102T_EC_110F_EC_122F_EC_138F_EC_16F_EC_173T_EC_2T_EC_221T_EC_29F_EC_4T_EC_60F__b_true |
| 95 | A4 (1) | FE | 5_ai-act__675b-cloud_vs_qwen3.5__EC_111F_EC_132F_EC_133T_EC_134T_EC_156T_EC_173T_EC_18F_EC_51F_EC_61F_EC_91F__a_true |
| 103 | A5 (3) | LA | 5_ai-act__glm-5.1_vs_minimax-m2.7__EC_110F_EC_122F_EC_138T_EC_156F_EC_157T_EC_16F_EC_172T_EC_220T_EC_29F_EC_60F_EC_90F__b_true |
| 119 | C3 (3) | LA | 6-7_ucpd__gemini-3.1-pro-preview_vs_qwen3.5__EC_22F_EC_48F_EC_62F_EC_65T_EC_75T_EC_80F_EC_86T_EC_98T__b_true |
| 120 | C6 (1) | FE | 6-7_ucpd__gemini-3.1-pro-preview_vs_qwen3.5__EC_22F_EC_48F_EC_62F_EC_67F_EC_68F_EC_69F_EC_70F_EC_71F_EC_72F_EC_80F_EC_86T_EC_98T__a_true |
| 115 | C5 (1) | LA | 6-7_ucpd__claude-opus-4-6_vs_minimax-m2.7__EC_22F_EC_48F_EC_60T_EC_62F_EC_86T_EC_95F__a_true |
| 130 | E3 (4) | LA | 6_gdpr__claude-opus-4-6_vs_gpt-5.4__EC_10F_EC_17F_EC_30F_EC_4F_EC_44F_EC_53T_EC_56T_EC_64T_EC_7F__a_true |
| 125 | E6 (1) | FE | 6_gdpr__675b-cloud_vs_gemini-3.1-pro-preview__EC_18F_EC_29F_EC_36F_EC_4F_EC_5F_EC_56T_EC_57T_EC_64T_EC_69F__a_true |
| 131 | E2 (11) | LA | 6_gdpr__deepseek-v3.2_vs_gemini-3.1-pro-preview__EC_18F_EC_29F_EC_36F_EC_4F_EC_56F_EC_6F_EC_69T_EC_72F_EC_74F_EC_79T_EC_9F__b_true |
| 136 | E2c (3) | FE | 6_gdpr__deepseek-v3.2_vs_gemini-3.1-pro-preview__EC_18F_EC_29F_EC_36F_EC_4F_EC_6F_EC_64T_EC_69T_EC_72T_EC_74T_EC_79T_EC_9F__a_true |
| 146 | S1 (1) | FE | 9_gdpr__675b-cloud_vs_claude-opus-4-6__EC_10T_EC_21F_EC_48T__a_true |
| 147 | S2 (1) | FE | 9_gdpr__claude-opus-4-6_vs_minimax-m2.7__EC_105F_EC_11T_EC_21F_EC_25F_EC_32F_EC_39F_EC_48F_EC_54F_EC_55T_EC_57F_EC_64F_EC_88F__b_true |

## Cases

Reading A = the first reading stated in `divergence_analysis`, reading B = the second. "Bucket" is the headline category: Bind = binding, Guid = Commission guidance, EDPB = EDPB/WP29 guidance, Und = undecided.

### Article 107 TFEU

**#21 (LA) Outermost Region Aid and Article 107(3) Structure.** Disputed point: does aid to an Article 349 outermost region fall within Article 107(3)(a) as a separate category, regardless of the low-living-standard or underemployment limb? A: separate category. B: one indivisible category, which the scenario sets to false.
- Authority: yes (guidance). Commission Guidelines on regional State aid (2021/C 153/01), paras 157 and 159.
- Supports: A.
- Quote (para 159): "Therefore Member States may designate the following areas as 'a' areas: (1) NUTS 2 regions whose GDP per capita in purchasing power standard is below or equal to 75 % of the EU-27 average [...]; (2) the outermost regions." (footnote markers omitted)
- Confidence: high on the category point. Bucket: Guid.
- Context: Iannelli (74/76) paras 11 to 12 (binding) hold that incompatibility under Article 107(1) is "neither absolute nor unconditional" and is determined by a Commission procedure. Both formalizations treat "incompatible" as a self-executing conclusion.

**#9 (FE) EU Hydrogen Infrastructure Aid and Art. 107(3) Compatibility.** Disputed point: when one Article 107(3) category (an IPCEI) applies, should "no discretionary ground applies" be encoded as a joint negation of all categories or as a disjunction where any single category defeats it? A: all categories negated together. B: any single category suffices.
- Authority: none needed. The two encodings are logically equivalent, and the analysis itself states: "In practice both reach the same result here".
- Background point (both readings agree): Iannelli (74/76) para 11, binding: "THE INCOMPATIBILITY OF AID WITH THE COMMON MARKET AS PROVIDED FOR IN ARTICLE 92 ( 1 ) IS NEITHER ABSOLUTE NOR UNCONDITIONAL."
- Supports: both. Confidence: high. Bucket: Und (no legal content).
- Context: in practice, IPCEI status is granted by a Commission decision under Article 107(3)(b). The facts therefore already contain the compatibility decision.

**#16 (LA) Tax Relief for Domestic Semiconductor Manufacturers.** Disputed point: does "Save as otherwise provided in the Treaties" require positive confirmation that no other Treaty derogation applies before incompatibility can be found? A: no, negating 107(2) and (3) suffices. B: yes.
- Authority: no. Searched the Notion of Aid notice (2016/C 262/01), Altmark, Stardust Marine and PreussenElektra. None addresses the proviso as an element.
- Supports: neither. Confidence: medium. Bucket: Und.
- Context: a State aid lawyer would check the specific Treaty derogations by name (for example Articles 42, 93, 106(2) and 346 TFEU). The formalizers had only Article 107.

**#4 (FE) Tax Credit for Domestic Semiconductor Manufacturer.** Disputed point: how the constituent elements of Article 107(1) fit together. Are trade effect and distortion separate top-level conditions, and are "granted by a Member State" and "through State resources" alternatives? A: separate conditions; Member State or State resources as alternatives. B: conditions embedded in the aid criteria; only "State resources" encoded.
- Authority: yes (binding). Altmark C-280/00 para 75; Stardust Marine C-482/99 para 24; PreussenElektra C-379/98 para 58.
- Supports: neither. The case law lists trade effect and distortion as separate conditions (against B's merger). It requires State resources and imputability cumulatively (against A's alternatives, and B omits imputability).
- Quotes:
  - Altmark para 75: "First, there must be an intervention by the State or through State resources. Second, the intervention must be liable to affect trade between Member States. Third, it must confer an advantage on the recipient. Fourth, it must distort or threaten to distort competition."
  - PreussenElektra para 58: "The distinction made in that provision between aid granted by a Member State and aid granted through State resources does not signify that all advantages granted by a State, whether financed through State resources or not, constitute aid".
  - Stardust para 24: "they must, first, be granted directly or indirectly through State resources [...] and, second, be imputable to the State".
- Confidence: high. Bucket: Bind.

### Article 17 GDPR

**#25 (FE) Art. 21(1) Objection With Overriding Legitimate Grounds.** Disputed point: is the absence of overriding legitimate grounds a conjunctive element of the 17(1)(c) erasure ground, or is the objection alone sufficient? A: absence is required, so erasure fails here. B: as encoded, the objection alone suffices.
- Authority: yes (binding). SCHUFA Holding, joined C-26/22 and C-64/22, operative part point 3; para 111 places the burden on the controller.
- Supports: A.
- Quote (operative part 3): "Article 17(1)(c) of Regulation 2016/679 must be interpreted as meaning that the data subject has the right to obtain from the controller the erasure of personal data concerning him or her without undue delay where he or she objects to the processing pursuant to Article 21(1) of that regulation and there are no overriding legitimate grounds capable of justifying, exceptionally, the processing in question."
- Confidence: high. Bucket: Bind.

**#32 (FE) Consent Withdrawal Without Explicit Withdrawal Act.** Disputed point: under 17(1)(b), is "no other legal ground" a separate cumulative condition, and does an email saying "I no longer agree" with no other ground give rise to erasure? A: yes, erasure. B: the encoding treats the no-other-ground element as false, so no erasure.
- Authority: yes (EDPB). EDPB Guidelines 05/2020 on consent, v1.1, para 117.
- Supports: A.
- Quote: "As a general rule, if consent is withdrawn, all data processing operations that were based on consent and took place before the withdrawal of consent - and in accordance with the GDPR - remain lawful, however, the controller must stop the processing actions concerned. If there is no other lawful basis justifying the processing (e.g. further storage) of the data, they should be deleted by the controller."
- Confidence: high. Bucket: EDPB. The error is in how the facts were encoded; the text alone already settles it.

**#23 (FE) Newspaper objects to direct marketing data processing.** Disputed point: does an applicable 17(3)(b) legal-obligation exception exclude the erasure right itself, or is it assessed as a separate block inside a right that still "applies"? A: it excludes the right. B: the right applies and the exception blocks it inside the provision.
- Authority: yes (binding). Darashev C-312/24 (4 June 2026), para 81; para 104 on scope.
- Supports: A.
- Quote (para 81): "the ground for lawfulness laid down in point (c) of the first subparagraph of Article 6(1) of the GDPR, read in conjunction with Article 6(3) of that regulation, is reflected in Article 17(3)(b) of that regulation, which excludes the right to erasure provided for in Article 17(1), where, inter alia, the processing of data is necessary for compliance with a legal obligation".
- Confidence: medium. The two readings in the analysis are blurred, and the judgment does not address an encoding question as such. Bucket: Bind.
- Context: both formalizations apply the exception all-or-nothing. A lawyer would read "to the extent that" in Article 17(3), together with para 104 of Darashev ("where the storage period [...] exceeds that necessary for compliance with that obligation, the data subject is capable of recovering his or her right to erasure"). The tax-retention duty covers "certain transaction records" only, so the browsing history and profile would have to be erased. Article 21(3) also bars further direct-marketing processing.

### Article 22 GDPR

**#35 (LA) Automated tax fraud scoring under national law.** Disputed point: once the Article 22(2)(b) exception (authorisation by law with safeguards) is met, must compliance with 22(4) still be shown when no special-category data are involved? A: no, 22(2)(b) suffices. B: yes, 22(4) is an extra structural condition.
- Authority: yes (EDPB). WP29 Guidelines on Automated individual decision-making and Profiling (WP251rev.01, endorsed by the EDPB). Binding-partial: SCHUFA (scoring) C-634/21 para 68 lists 22(4) among the conditions without deciding whether it applies when no special-category data are involved.
- Supports: A.
- Quotes:
  - WP251rev.01, "Special categories of personal data, Article 22(4)": "Automated decision-making (described in Article 22(1)) that involves special categories of personal data is only allowed under the following cumulative conditions (Article 22(4)): there is an applicable Article 22(2) exemption; and point (a) or (g) of Article 9(2) applies."
  - C-634/21 para 68: "that processing must comply not only with the conditions set out in the latter provision and in Article 22(4) of that regulation, but also with the requirements set out in Articles 5 and 6".
- Confidence: medium-high. Bucket: EDPB.
- Context: C-634/21 para 52 holds that Article 22(1) "lays down a prohibition in principle", which reframes the question asked ("does Maria retain the right").

### Article 9 GDPR

**#146 (FE) Publicly shared genetic data without explicit consent.** Disputed point: does a single applicable Article 9(2) exception, here (e) "manifestly made public", lift the 9(1) prohibition on its own? A: yes. B: absence of consent still counts toward "no exception applies".
- Authority: yes (binding). Meta Platforms v Bundeskartellamt C-252/21, paras 74 and 77.
- Supports: A.
- Quote (para 74): "under that provision, the fundamental prohibition of any processing of special categories of personal data, established in Article 9(1) of the GDPR, does not apply in the circumstance where the processing relates to personal data which are 'manifestly made public by the data subject'."
- Confidence: high. Bucket: Bind.
- Context: lifting the 9(1) prohibition does not make the processing lawful. Krankenversicherung Nordrhein C-667/21, operative part 3, states that processing under 9(2) "must also satisfy at least one of the conditions of lawfulness set out in Article 6(1)".

**#147 (FE) Court Processing Biometric Data Without Legal Claims Necessity.** Disputed point: is "or whenever courts are acting in their judicial capacity" in 9(2)(f) a ground independent of legal-claims necessity? A: independent (disjunctive). B: conjunctive.
- Authority: no judgment on the disjunction. C-245/20 Autoriteit Persoonsgegevens interprets "judicial capacity" only under Article 55(3).
- Supports: neither by authority. The text ("or whenever") favours A. Confidence: medium. Bucket: Und (text-settled).
- Context: the scenario is a criminal trial. Under GDPR Article 2(2)(d), the Regulation does not apply to processing "by competent authorities for the purposes of the prevention, investigation, detection or prosecution of criminal offences"; Directive 2016/680 applies instead. A lawyer's first question would be whether the GDPR applies at all.

### Article 6 GDPR

**#130 (LA) Fraud prevention data sharing with unresolved balancing test.** Disputed point: when no balancing assessment has been carried out, is 6(1)(f) still available until an override is shown, or does it fail? A: still available. B: it fails, because the absence of an override must be established.
- Authority: yes (binding). Meta v Bundeskartellamt C-252/21, paras 106 and 95; KNLTB C-621/22 para 33. EDPB Guidelines 1/2024 para 12 point the same way.
- Supports: B.
- Quotes:
  - C-252/21 para 106: "that provision lays down three cumulative conditions so that the processing of personal data covered by that provision is lawful, namely [...] third, that the interests or fundamental freedoms and rights of the person concerned by the data protection do not take precedence over the legitimate interest of the controller or of a third party".
  - Para 95: "the controller bears the burden of proving that those data are collected, inter alia, for specified, explicit and legitimate purposes and that they are processed lawfully, fairly and in a transparent manner".
- Confidence: high. Bucket: Bind.

**#125 (FE) Private Company's Fraud Detection Without Explicit Consent.** Disputed point: do the Article 6(3) requirements (a legal basis in Union or Member State law, public-interest objective, proportionality) apply to processing under 6(1)(f)? A: no, only to (c) and (e). B: yes.
- Authority: yes (binding). SCHUFA (scoring) C-634/21, para 69.
- Supports: A.
- Quote: "With regard in particular to the conditions of lawfulness, provided for in Article 6(1)(a), (b), and (f) of the GDPR, [...] Member States are not empowered to provide additional rules for the implementation of those conditions, such an option being, in accordance with Article 6(3) of that regulation, limited to the reasons referred to in Article 6(1)(c) and (e) of that regulation."
- Confidence: high. Bucket: Bind. The text of 6(3) already settles it.

**#131 (LA) Retailer Repurposes Purchase Data for Fraud Analytics.** Disputed point: does a positive Article 6(4) compatibility assessment make further processing lawful without a fresh Article 6(1) basis for the new purpose? A: yes, 6(4) is a lawfulness pathway. B: no, a 6(1) basis is still required.
- Authority: partial (binding, inconclusive). Digi C-77/21 paras 35 and 49 apply 6(4) to purpose limitation and repeat that every processing must "satisfy one of the conditions of the lawfulness of the processing listed in Article 6", without saying whether 6(4) itself is such a condition. Norra Stockholm Bygg C-268/21 paras 32 to 33 address only the safeguarding-law branch. Recital 50 GDPR ("In such a case, no legal basis separate from that which allowed the collection of the personal data is required") leans A, but recitals are not binding.
- Quote (Digi para 49): "any processing of personal data must, first, comply with the principles relating to the processing of data established in Article 5 of that regulation and, second, in the light, in particular, of the principle of the lawfulness of processing, laid down in Article 5(1)(a), satisfy one of the conditions of the lawfulness of the processing listed in Article 6 of that regulation".
- Supports: neither decisively. Confidence: medium. Bucket: Und (partial).

**#136 (FE) Retailer's Further Processing Based on Consent.** Disputed point: does fresh opt-in consent for the new purpose ground the further processing, or must the consent have been given for that purpose at the original collection? A: the fresh consent suffices. B: the consent fails 6(1)(a) because it was not given at collection.
- Authority: partial (EDPB). EDPB Guidelines 05/2020, para 59, Example 11: "Given this new purpose, new consent is needed." This implies that a new consent is the correct basis for a new purpose.
- Supports: A (implicitly). Confidence: medium. Bucket: Und (partial). The text of 6(1)(a) ("for one or more specific purposes") already settles it, since the opt-in was specific to the new purpose.

### Article 3 UCTD

**#51 (LA) Gym membership with partially negotiated cancellation clause.** Disputed point: can a term that was not drafted in advance, but which the consumer could not influence and whose negotiation the seller fails to prove, count as "not individually negotiated"? A: yes, the seller's failure to discharge the burden suffices. B: no, drafting in advance is a necessary element.
- Authority: yes (guidance). Commission Guidance on the UCTD (2019/C 323/04), section 1.2.2. Binding-partial: Ibercaja Banco C-452/18 para 35 makes the consumer's ability to influence the term decisive.
- Supports: A on the outcome. Pre-drafting is not necessary. The guidance does not endorse A's specific "standalone burden" mechanism.
- Quotes:
  - Guidance 1.2.2: "Typically, but not exclusively, 'standard', standardised or pre-formulated contract terms, often found in so-called 'terms and conditions' will be covered." Also: "What matters is that they contribute to defining the rights and obligations of the parties and that no individual negotiations have taken place on the specific term(s) in question." (footnote markers omitted)
  - C-452/18 para 35: "it is for the referring court to take account of all the circumstances in which such a term was presented to the consumer for the purposes of determining whether the consumer was able to influence its substance."
- Confidence: medium. Bucket: Guid.

**#59 (FE) Gym membership with pre-formulated cancellation clause.** Disputed point: is a pre-drafted term that the consumer could not influence "not individually negotiated" even though the seller never claimed negotiation, so the burden-of-proof rule was never triggered? A: yes, alternative pathways. B: no, the burden-of-proof step is a cumulative element.
- Authority: yes (binding). Ibercaja Banco C-452/18 para 33; Commission Guidance 2019/C 323/04, section 1.2.2, agrees.
- Supports: A.
- Quote (para 33): "Article 3(2) of that directive specifies that a term must always be regarded as not individually negotiated where it has been drafted in advance by the seller or supplier and the consumer has therefore not been able to influence the substance of the term, as is the case, in particular, in the context of a pre-formulated standard contract."
- Confidence: high. Bucket: Bind.

**#53 (LA) Partially Negotiated Contract with Disputed Standard Term.** Disputed point: is "overall assessment indicates a pre-formulated standard contract" (Article 3(2), second subparagraph) a gate that every unfairness finding must pass, or one route among others? A: a gate, so the Article does not apply here. B: one route; the unproven negotiation of the specific term suffices.
- Authority: yes (guidance). Commission Guidance 2019/C 323/04, section 1.2.2.
- Supports: B.
- Quote: "According to the second paragraph of Article 3(2), where certain aspects of a term or a specific term have been negotiated individually, this does not mean that the other contract terms have been negotiated individually." The same section adds "What matters is [...] that no individual negotiations have taken place on the specific term(s) in question."
- Confidence: medium. The guidance reads the subparagraph as protective, not as a gate, but it does not address the gate reading in so many words. Bucket: Guid.

### Articles 6 and 7 UCPD

**#119 (LA) Price comparison site omits ranking parameter disclosure.** Disputed point: does Article 7(4a) ("shall be regarded as material") replace the 7(1) condition that the consumer "needs" the information, or must that condition still be met? A: it replaces it. B: the need condition still applies.
- Authority: partial (guidance, by analogy). UCPD Guidance 2021/C 526/01, section 4.2.3, covers the scope of 7(4a) but not this point. Section 2.9.5 treats the parallel deeming rule in 7(4) as leaving only the transactional-decision test.
- Quote (2.9.5): "Failing to provide consumers with information required by Article 7(4) in the case of an invitation to purchase is a misleading omission, if this failure is likely to cause the average consumer to take a transactional decision they would not have taken otherwise."
- Supports: A (analogy only). Confidence: low. Bucket: Und (partial). No CJEU judgment on 7(4a) found.

**#120 (FE) Comparison Shopping Site Omits Ranking Criteria Disclosure.** Disputed point: is "if not already apparent from the context" (7(4)), and likewise the search-engine exclusion in 7(4a), a negative condition, or a positive element that must be proven separately? A: negative condition. B: positive element.
- Authority: none found; the guidance repeats the wording only.
- Supports: neither by authority. The text favours A. Confidence: medium. Bucket: Und (text-settled).

**#115 (LA) Omitted delivery cost information without consumer need finding.** Disputed point: in 7(1), is "information that the average consumer needs, according to the context" a separate element alongside causation? A: no, materiality shows through causation. B: yes, a separate element.
- Authority: no direct holding. Canal Digital C-611/14 restates 7(1) and focuses on case-by-case assessment of the omission and its causal effect.
- Supports: neither by authority. The text ("needs [...] and thereby causes") favours B. Confidence: medium. Bucket: Und.
- Context: a lawyer would not reach this question. A web page offering the table at EUR 899 is an invitation to purchase under Ving Sverige C-122/10, operative part 1 ("an invitation to purchase exists as soon as the information on the product advertised and its price is sufficient for the consumer to be able to make a transactional decision"). Article 7(4)(c) then deems "all additional freight, delivery or postal charges" material. The scenario's stipulation that consumers do not need the information conflicts with that deeming rule.

### Article 57 Directive 2014/24

**#90 (LA) Criminal conviction exclusion without awareness verification.** Disputed point: is the contracting authority's verification or awareness ("where they have established [...] or are otherwise aware") a constitutive condition of the 57(1) duty to exclude? A: yes. B: no, it is only an evidentiary route.
- Authority: no judgment found.
- Supports: neither. Confidence: medium. Bucket: Und.
- Context: Article 57(5) ("Contracting authorities shall at any time during the procedure exclude an economic operator where it turns out [...]") and the pre-award verification of the winning tenderer in Article 59(4) make "no knowledge at the evaluation deadline" a temporary state. A procurement lawyer would apply these provisions; the formalizers saw only Article 57 in isolation.

**#88 (FE) Environmental violations with public interest derogation invoked.** Disputed point: does a Member State's Article 57(3) public-interest derogation block exclusion on a discretionary 57(4) ground? A: no, 57(3) covers only paragraphs 1 and 2. B: yes.
- Authority: none found; the text decides. Article 57(3): "Member States may provide for a derogation from the mandatory exclusion provided for in paragraphs 1 and 2".
- Supports: A by text. Confidence: high. Bucket: Und (text-settled).

**#74 (LA) Art. 18(2) violation without self-cleaning or derogation.** Disputed point: is self-cleaning a defence the operator must raise, so that silence leaves the exclusion ground standing, or must the authority positively establish that self-cleaning failed? A: the operator must raise it. B: the authority must establish failure.
- Authority: yes (binding). RTS infra C-387/19, paras 26 and 49.
- Supports: A.
- Quote (para 49): "that provision provides in a sufficiently precise and unconditional manner [...] that the economic operator concerned cannot be excluded from the procurement procedure if it is able to establish, to the satisfaction of the contracting authority, that the corrective measures taken restore its reliability despite the existence of a ground for exclusion concerning that operator." Para 26 describes 57(6) as "conferring on tenderers a right".
- Confidence: medium-high. Bucket: Bind.

**#87 (LA) Discretionary exclusion for labour law violations with derogation.** Disputed point: must the contracting authority actually exercise its discretion before a 57(4) ground leads to exclusion, or does the ground plus failed self-cleaning suffice? A: the ground plus failed self-cleaning suffices. B: an exercise of discretion is required.
- Authority: yes (binding). Meca C-41/18, paras 28 and 34; Tim C-395/18, paras 34 and 54.
- Supports: B.
- Quote (Meca para 34): "it is clear from the wording of Article 57(4) of Directive 2014/24 that the EU legislature intended to confer on the contracting authority, and on it alone, the task of assessing whether a candidate or tenderer must be excluded from a procurement procedure during the stage of selecting the tenderers." Tim para 54 holds that automatic exclusion depriving "the contracting authority of any discretion" is incompatible with 57(4) and (6).
- Confidence: high. Bucket: Bind.

### Article 5 AI Act

Source for all three: Commission Guidelines on prohibited AI practices, C(2025) 5052 final of 29.7.2025. The content was approved on 4.2.2025 as C(2025) 884.

**#94 (LA) Subliminal AI system without impaired decision-making.** Disputed point: on the "objective" branch of 5(1)(a), must appreciable impairment, a changed decision and significant harm still be shown? A: yes, all elements are cumulative. B: the objective alone suffices.
- Authority: yes (guidance). Paras 60 to 61 and 76.
- Supports: A.
- Quote (para 61): "For the prohibition to apply, all four conditions must be simultaneously fulfilled and there must be a plausible causal link between the techniques deployed, the material distortion of the behaviour of the person, and the significant harm that has resulted or is reasonably likely to result from that behaviour." Para 60(iii): "The distortion must appreciably impair their ability to make an informed decision".
- Confidence: medium-high. Para 76 says intent is not necessary but does not drop impairment or harm on the objective branch. Bucket: Guid.

**#95 (FE) Emotion AI for Workplace Safety Sold on EU Market.** Disputed point: does the 5(1)(f) exception apply when the system serves either medical or safety reasons, or must both be present? A: either suffices. B: both are required.
- Authority: yes (guidance). Paras 256, 258 and 261.
- Supports: A.
- Quote (para 258): "The notion of safety reasons within this exception should be understood to apply only in relation to the protection of life and health and not to protect other interests, for example property against theft or fraud." This treats safety as a standalone ground. Para 256: "an explicit exception for emotion recognition systems used in the area of the workplace and education institutions for medical or safety reasons".
- Confidence: high. Bucket: Guid.
- Context: para 261 and Recital 18 say fatigue detection is not emotion recognition at all ("a number of AI systems used for safety reasons would already not fall under that definition, including, for example, systems used in detecting the state of fatigue"). Para 257 says "The general monitoring of stress levels at the workplace is not permitted under health or safety aspects." A lawyer would split the system's functions; neither formalization does.

**#103 (LA) Law Enforcement Biometric Categorisation by Police.** Disputed point: is "categorizing of biometric data in the area of law enforcement" a free-standing carve-out from 5(1)(g), or only the setting in which labelling or filtering of lawfully acquired datasets is exempt? A: the latter, so the police system inferring race is prohibited. B: a free-standing carve-out.
- Authority: yes (guidance). Paras 275, 284 and 286, citing Recital 30.
- Supports: A.
- Quote (para 284): "The prohibition in Article 5(1)(g) AI Act does not cover AI systems engaged in the labelling or filtering of lawfully acquired biometric datasets, such as images, based on biometric data, including in the area of law enforcement." Para 275: "The prohibition does not cover the labelling or filtering of lawfully acquired biometric datasets, including for law enforcement purposes."
- Confidence: medium-high. The guidelines consistently restate the carve-out this way and never treat law enforcement categorisation as standalone, but they do not reject the disjunctive reading in terms. Bucket: Guid.

### Article 3 DMA

**#38 (LA) Platform designation without standard qualitative evidence.** Disputed point: can a qualitative designation under 3(8) rest on foreseeable developments alone, without any of the elements in points (a) to (g)? A: yes. B: no, at least one listed element is needed.
- Authority: partial (binding, obiter). General Court, Opera Norway v Commission T-357/24 (2 September 2026), para 219. Appeal status not checked.
- Quote (para 219): "For that purpose, the Commission is to take into account some or all of the elements listed in points (a) to (g) of the second subparagraph of Article 3(8) of the DMA, in so far as they are relevant in relation to the undertaking concerned." The third subparagraph ties foreseeable developments to "the elements listed in the second subparagraph".
- Supports: leans B, not decided. Confidence: low-medium. Bucket: Und (partial).
- Context: the facts include persistent non-compliance with investigative measures. Under 3(8), fourth subparagraph, that allows designation "on the basis of the facts available". A lawyer would use that route and never reach the disputed point.

**#36 (FE) Non-platform undertaking obstructs Commission investigation.** Disputed point: does the 3(8) fourth-subparagraph "facts available" designation apply to an undertaking that provides no core platform service? A: yes, standalone route. B: no.
- Authority: none found. The text decides: "Where an undertaking providing a core platform service that does not satisfy the quantitative thresholds [...]".
- Supports: B by text. Confidence: high. Bucket: Und (text-settled).

**#39 (LA) Digital platform investigated but not present in three Member States.** Disputed point: is consideration of foreseeable developments a mandatory part of every 3(8) assessment, so that designation fails where none were considered? A: yes. B: no, they are relevant only where they exist.
- Authority: no. Opera T-357/24 paras 281 to 282 concern foreseeable developments in a 3(5) rebuttal; Meta v Commission T-1078/23 and ByteDance T-1077/23 do not address the point.
- Supports: neither (the "in so far as relevant" wording in Opera para 219 leans B). Confidence: medium. Bucket: Und.
- Context: as in #38, persistent non-compliance opens the facts-available route.

## C11's own limitation: disagreements that exist only because context was missing

Cases where a lawyer would routinely consult material the formalizers did not have, and that material dissolves or redirects the disagreement:

| # | Missing context | Effect |
|---|---|---|
| 9 and cluster T1 (8 cases) | Iannelli 74/76 paras 11 to 12: incompatibility under 107(1) is determined by a Commission procedure; IPCEI status is itself a Commission decision | The whole "does a potential 107(3) ground block incompatibility" dispute is an artefact of treating 107(1) as self-executing |
| 16 | The specific Treaty derogations (Arts 42, 93, 106(2), 346 TFEU) | "Save as otherwise provided" becomes a checklist, not an open element |
| 23 | "to the extent that" in 17(3); Darashev C-312/24 para 104; Art 21(3) | Erasure is partial: tax records are retained, browsing and profile data are erased |
| 147 | GDPR Art 2(2)(d) and Directive 2016/680 | The GDPR probably does not apply to a criminal court identifying a witness |
| 95 | AI Act Recital 18; Guidelines paras 257 and 261 | Fatigue detection is outside the definition; stress monitoring is not covered by the safety exception |
| 115 | Art 7(4)(c) UCPD; Ving C-122/10 | Delivery charges are deemed material in an invitation to purchase |
| 90 | Arts 57(5) and 59(4) Directive 2014/24 | The duty to exclude persists through the procedure and is checked before award |
| 38, 39 | DMA Art 3(8), fourth subparagraph, applied to the stipulated non-compliance | Designation on facts available is open whatever the answer to the disputed point |
| 87 | National transposition of 57(4) (Tim para 34; Meca para 34) | Whether exclusion is mandatory depends on national law, which the scenario only half states |
| 130 | Accountability and burden of proof (Art 5(2); C-252/21 para 95) | The "unresolved balancing" dispute disappears once the burden is known |

That makes 10 of the 30 sampled cases (33%) where routine legal context changes the analysis, beyond whether the disputed point itself has an authority.

## Search log

Downloads (Cellar CELEX endpoint unless stated; all converted to text and searched with `grep`):
- CJEU: C-26/22 and C-64/22 SCHUFA (62022CJ0026); C-634/21 SCHUFA scoring (62021CJ0634); C-252/21 Meta (62021CJ0252); C-180/21 Inspektor (62021CJ0180); C-77/21 Digi (62021CJ0077); C-268/21 Norra Stockholm Bygg (62021CJ0268); C-667/21 Krankenversicherung Nordrhein (62021CJ0667); C-245/20 Autoriteit Persoonsgegevens (62020CJ0245); C-621/22 KNLTB (62022CJ0621); C-312/24 Darashev (62024CJ0312); C-395/18 Tim; C-41/18 Meca; C-387/19 RTS infra; C-124/17 Vossloh Laeis; C-280/00 Altmark; C-482/99 Stardust Marine; C-379/98 PreussenElektra; 74/76 Iannelli; C-452/18 Ibercaja Banco; C-611/14 Canal Digital; C-122/10 Ving Sverige.
- General Court: T-357/24 Opera Norway (62024TJ0357); T-1078/23 Meta (62023TJ1078); T-1077/23 ByteDance (62023TJ1077).
- Legislation: GDPR 32016R0679; Directive 2014/24 32014L0024; Art 107 TFEU 12016E107; UCTD 31993L0013; UCPD 32005L0029; Omnibus 32019L2161; DMA 32022R1925; AI Act 32024R1689.
- Commission guidance: UCPD Guidance 52021XC1229(05); UCTD Guidance 52019XC0927(01); Regional aid guidelines 2022, 52021XC0429(01); Notion of aid notice 52016XC0719(05); AI Act prohibited-practices guidelines (digital-strategy.ec.europa.eu, documents 112366 and 112367).
- EDPB: Guidelines 05/2020 on consent; Guidelines 1/2024 on Article 6(1)(f); WP251rev.01 (ec.europa.eu Article 29 archive, document 49826).

Web searches (used only to locate primary sources):
1. "Commission Guidelines on prohibited artificial intelligence practices AI Act C(2025) 884 PDF": located the official download page.
2. "CJEU judgment Article 6(4) GDPR compatible further processing separate legal basis": pointed to C-268/21, which was fetched and read. No judgment decides the #131 point.
3. "General Court judgment Article 3(8) DMA qualitative designation": pointed to T-1078/23, T-357/24 and T-1077/23, all fetched. Only T-357/24 para 219 touches 3(8), obiter.
4. "CJEU judgment Article 17(3)(b) GDPR erasure legal obligation": pointed to C-312/24 (4 June 2026), fetched and read.

Searched and not found (this counts toward "undecided"): any judgment or guidance on the "save as otherwise provided" proviso as an element (#16); on Article 57(1) knowledge as a constitutive condition (#90); on 7(4a) UCPD and the consumer-need test (#119); on the 9(2)(f) disjunction (#147); on the 3(8) fourth subparagraph (#36). No Advocate General opinion was needed or used. Coverage limits: no commentary databases (Beck, Kluwer) were used, and no national case law was checked. A paid commentary search might move some of #16, #90 and #119 to "partial".
