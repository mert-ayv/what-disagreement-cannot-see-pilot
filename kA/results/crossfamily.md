# Cross-family comparison (descriptive, not pre-registered)

## Do encodings of one role give identical outcomes?

- Claude: neutral differ, member differ, insurer differ
- Gemini 3.8 Flash: neutral identical, member differ, insurer identical
- GPT-6.1 Sol: neutral identical, member identical, insurer identical
- GPT-6 Astra: neutral identical, member identical, insurer identical
- GPT-6.1 Sol vs GPT-6 Astra, all nine encodings: identical outcomes

## Neutral disagreement within and across families

Within family: Claude 3,132; Gemini 3.8 Flash 0; GPT-6 Astra 0 cases.
Across the three families' neutral encodings: 39,700 cases.

| Point | Cross-family neutral disagreement |
|---|---|
| F1/P3 male with female partner | 0 |
| F4 male without female partner | 34,560 |
| F2 age 40+, no test since 40 | 3,300 |
| F5 tied latest FSH tests | 2,924 |
| F6 partner sterilized, patient not | 0 |
| F7 timed vs frequent across threshold | 1,438 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 678 |
| (no recorded point) | 0 |

## Share of cases covered, per point (neutral / member / insurer; member blank where inadmissible)

| Point | Expert port | Claude | Gemini 3.8 Flash | GPT-6 Astra |
|---|---|---|---|---|
| F1/P3 male with female partner | 0.039 | 0.019 / 0.022 / 0.019 | 0.019 / 0.038 / 0.019 | 0.019 / 0.058 / 0.000 |
| F4 male without female partner | 0.000 | 0.133 / 0.133 / 0.000 | 0.000 / 0.089 / 0.000 | 0.000 / 0.133 / 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.009 / 0.028 / 0.000 | 0.023 / 0.023 / 0.000 | 0.027 / 0.059 / 0.027 |
| F5 tied latest FSH tests | 0.011 | 0.053 / 0.057 / 0.031 | 0.038 / 0.057 / 0.033 | 0.036 / 0.102 / 0.031 |
| F6 partner sterilized, patient not | 0.043 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 | 0.000 / 0.050 / 0.000 |
| F7 timed vs frequent across threshold | 0.005 | 0.003 / 0.009 / 0.003 | 0.007 / 0.039 / 0.003 | 0.003 / 0.009 / 0.003 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 0.000 | 0.000 / 0.012 / 0.000 | 0.036 / 0.036 / 0.000 | 0.000 / 0.000 / 0.000 |

## What disagreement exposes of each neutral encoding's divergence from the expert port

| Encoding | Divergent cases | Exposed by disagreement within its family | Exposed across families |
|---|---|---|---|
| Claude:neutral_1 | 60,044 | 0.0% | 57.6% |
| Claude:neutral_2 | 60,044 | 0.0% | 57.6% |
| Claude:neutral_3 | 63,176 | 5.0% | 59.7% |
| Gemini 3.8 Flash:neutral_1 | 29,928 | 0.0% | 14.8% |
| Gemini 3.8 Flash:neutral_2 | 29,928 | 0.0% | 14.8% |
| Gemini 3.8 Flash:neutral_3 | 29,928 | 0.0% | 14.8% |
| GPT-6 Astra:neutral_1 | 28,616 | 0.0% | 10.9% |
| GPT-6 Astra:neutral_2 | 28,616 | 0.0% | 10.9% |
| GPT-6 Astra:neutral_3 | 28,616 | 0.0% | 10.9% |

Hidden set (divergent, but all nine neutral encodings agree): identical for all nine: True.
Size 25,484: 22,132 partner-sterilized cases the expert port covers (it checks the patient only), 3,352 tied-FSH cases the expert port denies and every LLM encoding covers, 0 other.

GPT member encodings are inadmissible under the pre-registered floor (two CodeX sterilization examples); their
shares are shown for description only.
