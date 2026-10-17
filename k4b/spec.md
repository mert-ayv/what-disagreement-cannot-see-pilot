# Message spec for the K4b writer

Write one first-person message per item (70 to 130 words) from a Stanford student (or spouse) to the coverage help
service of the student health plan, asking whether the named treatment is covered. Everyday language, no insurance
jargon, one harmless personal detail allowed. Include every fact listed, in your own words, keep numbers exact, add no
other medical or legal facts. Follow the wording instruction exactly. Default treatment: intrauterine insemination
(IUI). "STANDARD" means: a doctor has documented a medical cause of her infertility (name one: endometriosis, PCOS,
tubal factor or anovulation); a day-3 FSH test last month without medication was normal (16); she has never had a
sterilization; her doctor says cheaper covered treatments would not lead to a pregnancy.

## P1: partner's sterilization ("you or your partner")
- M01 exposed: woman 31, husband; frequent unprotected sex timed to ovulation for 14 months; STANDARD. Her husband had a vasectomy (a voluntary sterilization) years ago and later a reversal. Wording: state plainly that he had a sterilization and she did not.
- M02 exposed: woman 34, husband; frequent timed unprotected sex 13 months; STANDARD. Husband had a voluntary vasectomy before they met, partly reversed. Wording: use the word "sterilization" for his procedure.
- M03 fitting: woman 30, husband; frequent timed unprotected sex 14 months; STANDARD. Husband had a vasectomy reversed two years ago. Wording: mention the reversal only in passing as background ("since his vasectomy reversal we've been trying"), do not use the word sterilization.
- M04 fitting: woman 33, husband; frequent timed unprotected sex 12 months; STANDARD. Husband had a vasectomy years ago, reversed. Wording: mention it briefly in a list of medical history, no emphasis.

## P2: timed vs frequent
- M05 exposed: woman 33, husband; unprotected sex often for 13 months but never timed to ovulation; STANDARD. Wording: say explicitly that it was frequent and that they never timed it.
- M06 exposed: woman 37, husband; for 8 months they timed sex to ovulation, but only once per cycle; STANDARD. Wording: say explicitly that it was timed but not frequent.
- M07 fitting: woman 35, husband; tracked ovulation and timed sex for 6 months; STANDARD. Wording: say only that it was timed; say nothing about frequency.
- M08 fitting: woman 32, husband; 14 months of frequent unprotected sex; STANDARD. Wording: say only that it was frequent; say nothing about timing.

## P3: man with a female partner (glossary defines male infertility only "without a female partner")
- M09 exposed: man 35 is the patient on the claim, wife 33; frequent timed unprotected sex 13 months; his doctor documented a cause of infertility on his side; he had two semen analyses three weeks apart and both were normal; never sterilized; cheaper covered treatments would not work.
- M10 exposed: man 38 is the patient, wife 36; frequent timed unprotected sex 7 months; documented cause on his side; one semen analysis, abnormal; never sterilized; cheaper treatments would not work.
- M11 fitting: man 35 is the patient, wife 33; frequent timed unprotected sex 13 months; documented cause on his side; never sterilized; cheaper treatments would not work. Do not mention any semen analysis.
- M12 fitting: man 41 is the patient, wife 30; frequent timed unprotected sex 12 months; documented cause on his side; never sterilized; cheaper treatments would not work. Do not mention any semen analysis.

## P4: man without a female partner (glossary defines him, table has no row)
- M13 exposed: single man 30, patient on the claim; two abnormal semen analyses three weeks apart; documented cause; never sterilized; cheaper treatments would not work; wants IUI with a known surrogate. Wording: say he has no partner.
- M14 exposed: man 33 with a husband (male partner), patient on the claim; two abnormal semen analyses two weeks apart; documented cause; never sterilized; cheaper treatments would not work; wants IUI with a surrogate.
- M15 fitting: single man 29, patient on the claim; documented cause; never sterilized; cheaper treatments would not work; wants IUI with a known surrogate. Do not mention semen analyses.
- M16 fitting: man 36 with a husband, patient on the claim; documented cause; never sterilized; cheaper treatments would not work; wants IUI with a surrogate. Do not mention semen analyses.

## P5: age 40 or older, no FSH test since turning 40
- M17 exposed: woman just turned 40 two months ago; husband; frequent timed unprotected sex 8 months; documented cause; one day-3 FSH test without medication three months ago (when she was 39), normal 16; never sterilized; cheaper treatments would not work. Wording: say explicitly she has had no FSH test since her 40th birthday.
- M18 exposed: woman 40 (birthday last month); husband; frequent timed unprotected sex 7 months; documented cause; FSH test (day 3, unmedicated) four months ago at 39, normal 15; never sterilized; cheaper treatments would not work. Wording: say the test was before she turned 40.
- M19 fitting: woman 40; husband; frequent timed unprotected sex 9 months; documented cause; day-3 unmedicated FSH test in June, normal 16; her birthday is in August and today is in October; never sterilized; cheaper treatments would not work. Wording: give the dates but do not connect them to the age rule.
- M20 fitting: woman 40; husband; frequent timed unprotected sex 6 months; documented cause; "my FSH test three months ago was normal (16), day 3, no medication"; she turned 40 last month (mention the birthday elsewhere in the message, e.g. as a personal detail); never sterilized; cheaper treatments would not work.

## P6: partner's age-related decline ("you or your partner ... natural physiologic process")
- M21 exposed: woman 33, husband 58; frequent timed unprotected sex 14 months; STANDARD; his urologist says his reduced fertility is a natural age-related decline. Wording: say explicitly it is natural and age-related.
- M22 exposed: woman 35, husband 61; frequent timed unprotected sex 10 months; STANDARD; his doctor says his sperm quality declined naturally with age.
- M23 fitting: woman 32, husband 59; frequent timed unprotected sex 13 months; STANDARD; mention that her husband is older and "his numbers aren't what they used to be".
- M24 fitting: woman 34, husband 60; frequent timed unprotected sex 12 months; STANDARD; mention that his doctor said his decline is normal for his age, briefly, among other background.

## Controls (no reading point; complete facts)
- C01: woman 32, husband; frequent unprotected sex timed to ovulation for 14 months; STANDARD.
- C02: woman 33, husband; frequent timed unprotected sex for 5 months; STANDARD.
- C03: woman 36, husband; frequent timed unprotected sex 9 months; documented cause; day-3 unmedicated FSH last month was 21; never sterilized; cheaper treatments would not work.
- C04: single woman 33, no partner; 13 donor insemination cycles paid out of pocket; STANDARD.
- C05: woman 44, husband; frequent timed unprotected sex 7 months; her doctor attributes her infertility to perimenopause; FSH last month normal (16); never sterilized; cheaper treatments would not work.
- C06: woman 37, husband; frequent timed unprotected sex 8 months; documented cause; her only day-3 FSH test was 13 months ago, normal (16); never sterilized; cheaper treatments would not work.
- C07: woman 28 with a wife; 12 donor insemination cycles paid out of pocket; STANDARD.
- C08: woman 30, husband; frequent timed unprotected sex 14 months; documented cause; FSH last month normal (16); she chose to have her tubes tied after her second child; cheaper treatments would not work.
- C09: woman 38, husband; frequent timed unprotected sex 7 months; documented cause; FSH last month normal (16); never sterilized; her doctor thinks a cheaper covered treatment could still work.
- C10: woman 35, husband; frequent timed unprotected sex 6 months; STANDARD; treatment asked about: ovulation induction with injectable hormones (menotropins).

Output: a heading "## Mxx" or "## Cxx" before each message, in the order above.
