"""Cardinal Care 2023-2024: comprehensive infertility services benefit (member-favourable encoding).

READING choices:
1. Unknown facts: a missing field means the fact is unknown; a requirement whose fact is unknown
   is not shown to be met, so the claim is not covered.
2. Student / spouse coverage status: no claim field exists; assumed established elsewhere.
3. Natural physiologic process: "such as age related ovarian insufficiency" is illustrative, so
   every natural_* condition (including male reproductive aging) disqualifies; only "other" passes.
4. Glossary for a male with a female partner: the glossary has no such clause; the couple is
   assessed under "For a female with a male partner", using the female partner's age and the
   months of frequent unprotected heterosexual intercourse.
5. Glossary for a female with a male partner: only the intercourse route ("after 1 year of
   frequent, unprotected heterosexual sexual intercourse") satisfies that clause; donor
   insemination cycles do not substitute for it in the glossary (gender dysphoria still can).
6. "Without a male partner" covers both a female partner and no partner; "without a female
   partner" covers both a male partner and no partner.
7. Gender dysphoria: a "yes" makes the patient infertile under the glossary on its own.
8. Male without a female partner: the table has no row, so no months-trying requirement applies.
9. Semen analyses: the glossary sets no timing relative to the service, so all listed abnormal
   analyses count; any two at least 14 days apart suffice.
10. Ages: "under 35" / "35 or older" / "age 40" are measured on the date of service.
11. FSH window: "within the past" means on or before the date of service and at most n calendar
    months earlier (exactly n months counts); later tests do not count.
12. "Most recent lab test": the latest test on or before the date of service; if several share
    that latest date and time, the requirement is met if any of them is below 19 mIU/mL.
13. "All prior tests performed after age 40": tests on or before the date of service and
    strictly after the 40th birthday; a test on the birthday itself is at age 40, not after it.
    If no such test exists, the condition is vacuously met (the window test is still required).
14. "12 months or more", "At least 12 cycles", "6 cycles", "1 year": thresholds are inclusive
    (>= 12 or >= 6); "1 year" equals 12 months.
15. Partner sterilization is checked only when the patient has a partner.
"""

import datetime

COVERED_SERVICES = {
    "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins",
}


def _parse(d):
    y, m, dd = d.split("_")
    return datetime.date(int(y), int(m), int(dd))


def _fortieth_birthday(dob):
    b = _parse(dob)
    try:
        return datetime.date(b.year + 40, b.month, b.day)
    except ValueError:
        # Feb 29 birth in a non-leap year: the birthday is reached on Mar 1.
        return datetime.date(b.year + 40, 3, 1)


def covered_under_benefit(claim: dict, h) -> bool:
    # Covered service
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    service_date = claim.get("date_service_received")
    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if service_date is None or sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    # READING: unknown facts. "A missing field means the fact is unknown." A requirement whose
    # fact is unknown is not shown to be met.

    # READING: student / partner coverage. "covered under this plan as a student or as a covered
    # dependent" has no claim field; treated as established elsewhere.

    # Condition demonstrated and documented
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    # READING: natural physiologic process. "due to a natural physiologic process such as age
    # related ovarian insufficiency" lists examples, so every natural_* value disqualifies.
    if condition != "other":
        return False

    # Voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    # READING: "You or your partner has not had a voluntary sterilization" applies to the
    # partner only when there is a partner.
    if partner != "no_partner" and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # Less costly treatment
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    timed = claim.get("num_months_timed_unprotected_intercourse")
    frequent = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    di_cycles = claim.get("num_cycles_donor_insemination")
    gd = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"

    # READING: "without a male partner" covers a female partner and no partner; "without a
    # female partner" covers a male partner and no partner.
    if sex == "female":
        return _female(claim, h, service_date, partner == "male", timed, frequent, di_cycles, gd)
    return _male(claim, h, partner == "female", timed, frequent, gd)


def _female(claim, h, service_date, with_male, timed, frequent, di_cycles, gd):
    # READING: ages. "under the age of 35" / "35 years of age or older" measured on the date of
    # service via h.patient_age.
    age = h.patient_age(claim)
    if age is None:
        return False
    threshold = 12 if age < 35 else 6

    # Glossary infertility
    # READING: thresholds. "1 year" = 12 months; "At least 12 cycles" / "6 cycles" inclusive.
    # READING: female with male partner. "after: 1 year of frequent, unprotected heterosexual
    # sexual intercourse" is the only route under that clause; donor cycles do not substitute.
    # READING: gender dysphoria. "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" is sufficient on its own.
    if with_male:
        infertile = frequent is not None and frequent >= threshold
    else:
        infertile = di_cycles is not None and di_cycles >= threshold
    if not (infertile or gd):
        return False

    # Table: months trying to conceive
    if with_male:
        # "A. 12 months or more or B. At least 12 cycles of donor insemination" (6 if 35+)
        met = (timed is not None and timed >= threshold) or (di_cycles is not None and di_cycles >= threshold)
    else:
        met = di_cycles is not None and di_cycles >= threshold
    if not met:
        return False

    # Table: unmedicated day 3 FSH
    tests = claim.get("day_3_fsh_tests")
    if not tests:
        return False
    # READING: FSH window. "done within the past: 12 months" (6 if 35+) means on or before the
    # service date and at most that many calendar months earlier.
    prior = [t for t in tests if h.days_between(t[1], service_date) >= 0]
    if not any(h.months_at_most(t[1], service_date, threshold) for t in prior):
        return False

    if age < 40:
        # READING: "most recent lab test". Latest test on or before the service date; among
        # ties at the same date and time, met if any is below 19.
        latest = max((t[1], t[2]) for t in prior)
        return any(t[0] < 19 for t in prior if (t[1], t[2]) == latest)

    # READING: "less than 19 mIU/mL in all prior tests performed after age 40". Tests on or
    # before the service date and strictly after the 40th birthday; none means vacuously met.
    dob = claim.get("patient_dob")
    if dob is None:
        return False
    b40 = _fortieth_birthday(dob)
    after40 = [
        t for t in h.fsh_tests_since_age_40(claim)
        if h.days_between(t[1], service_date) >= 0 and _parse(t[1]) > b40
    ]
    return all(t[0] < 19 for t in after40)


def _male(claim, h, with_female, timed, frequent, gd):
    if with_female:
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        threshold = 12 if partner_age < 35 else 6
        # READING: male with a female partner in the glossary. No clause names this case; the
        # couple is assessed under "For a female with a male partner, after: 1 year of frequent,
        # unprotected heterosexual sexual intercourse if under the age of 35" using the female
        # partner's age.
        infertile = frequent is not None and frequent >= threshold
        if not (infertile or gd):
            return False
        # Table: "A male of any age with a female partner under 35 years of age: 12 months or
        # more" (6 if partner 35+); FSH "Does not apply".
        return timed is not None and timed >= threshold

    # Male without a female partner
    # READING: semen analysis timing. "At least 2 abnormal semen analyses obtained at least 2
    # weeks apart" sets no timing relative to the service; all listed analyses count.
    analyses = claim.get("abnormal_semen_analyses") or []
    infertile = any(
        abs(h.days_between(a, b)) >= 14
        for i, a in enumerate(analyses)
        for b in analyses[i + 1:]
    )
    if not (infertile or gd):
        return False
    # READING: male without a female partner in the table. The table has no row for this case,
    # so "the requirement for the number of months trying to conceive" imposes nothing here.
    return True
