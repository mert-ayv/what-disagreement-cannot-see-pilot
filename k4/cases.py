"""K4 cases: known facts, hidden facts, and notes for the narrative writer (2026-10-17)."""
IUI, OI = "intrauterine_insemination", "ovulation_induction_cycle_with_menotropins"
BASE = dict(service=IUI, sex="female", partner="male", partner_age=None, age=32, freq_months=14, timed_months=14,
            donor_cycles=0, sterilized="no", condition="other", less_costly="no", fsh="recent_ok", semen=0)


def c(hidden=(), note="", **kw):
    f = dict(BASE, **kw)
    return dict(known={k: v for k, v in f.items() if k not in hidden}, hidden=list(hidden), note=note)


CASES = {
    1: c(note="endometriosis diagnosed by her gynecologist; trying 14 months; FSH test last month normal"),
    2: c(freq_months=5, timed_months=5, age=33, note="trying 5 months; PCOS diagnosed; FSH normal last month"),
    3: c(age=36, freq_months=9, timed_months=9, hidden=("fsh",), note="PCOS diagnosed; trying 9 months; says nothing about hormone tests"),
    4: c(age=29, partner="no_partner", freq_months=0, timed_months=0, hidden=("donor_cycles",), note="single woman, unexplained anovulation documented; has tried donor sperm at home a few times but number unclear; FSH normal last month"),
    5: c(age=41, freq_months=10, timed_months=10, hidden=("fsh", "condition"), note="41, trying 10 months with husband, no diagnosis yet, no hormone tests mentioned"),
    6: c(age=34, freq_months=13, hidden=("timed_months",), note="trying a year with frequent unprotected sex, never tracked ovulation or timed it; doctor documented tubal factor"),
    7: c(age=38, partner="female", partner_age=None, donor_cycles=7, freq_months=0, timed_months=0, hidden=("sterilized",), note="married to a woman; 7 donor insemination cycles paid herself; documented condition; FSH normal last month; mentions an operation years ago without saying what"),
    8: c(sex="male", partner="female", partner_age=33, age=35, freq_months=13, timed_months=13, fsh="none", hidden=("semen",), note="man, wife 33, trying 13 months; claim is under his name; no semen analysis mentioned"),
    9: c(sex="male", partner="no_partner", age=30, semen=2, freq_months=0, timed_months=0, fsh="none", note="single man with two abnormal semen analyses three weeks apart, wants insemination with a surrogate he knows (the claim names him as patient)"),
    10: c(age=31, note="husband had a vasectomy years ago, she has not been sterilized; trying 14 months since partial reversal; she has documented endometriosis; FSH normal"),
    11: c(service=OI, age=37, freq_months=7, timed_months=7, hidden=("less_costly",), note="wants ovulation induction with injections; trying 7 months; documented ovulatory disorder; FSH normal last month; no mention of other treatments tried"),
    12: c(age=30, fsh="recent_high", note="premature ovarian insufficiency documented; FSH last month was 21; trying 14 months"),
    13: c(age=39, hidden=("freq_months", "timed_months"), note="39, documented endometriosis, FSH normal last month; says they 'have been trying for a while'"),
    14: c(age=33, partner="no_partner", donor_cycles=13, freq_months=0, timed_months=0, hidden=("fsh", "condition"), note="single woman, 13 self-paid donor cycles, no diagnosis or tests mentioned"),
    15: c(age=36, freq_months=8, timed_months=8, sterilized="yes", note="had her 'tubes tied' years ago after her second child, then a reversal; trying 8 months; documented condition; FSH normal"),
    16: c(age=44, freq_months=7, timed_months=7, condition="natural_perimenopause", note="44, perimenopause diagnosed as the cause; trying 7 months; FSH normal last month"),
    17: c(age=35, timed_months=6, hidden=("freq_months",), note="35, tracked ovulation and timed intercourse for 6 months; documented condition; FSH normal last month"),
    18: c(age=28, partner="female", donor_cycles=12, freq_months=0, timed_months=0, note="married to a woman, 12 self-paid donor cycles, documented anovulation, FSH normal last month"),
    19: c(age=37, freq_months=8, timed_months=8, fsh="old_ok", note="37, trying 8 months, documented condition, last FSH test 13 months ago was normal"),
    20: c(sex="male", partner="female", partner_age=36, age=40, freq_months=7, timed_months=7, fsh="none", semen=2, note="man 40, wife 36, trying 7 months, two abnormal semen analyses three weeks apart; claim under his name"),
}
