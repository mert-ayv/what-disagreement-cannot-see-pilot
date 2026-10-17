"""Cardinal Care 2023-2024, comprehensive infertility services (pp. 62-64), member-favourable encoding.

READING choices (each is marked with "# READING:" in the code):

1. Unknown facts: a requirement phrased as an eligibility condition ("You are eligible ... if")
   must be shown by known facts; a missing field fails it. Where a missing fact cannot change the
   outcome (an unknown age whose every possible bracket is satisfied), the requirement is met.
2. Natural physiologic process: "such as age related ovarian insufficiency" gives examples, so the
   exclusion covers every natural physiologic process, including natural male reproductive aging;
   only a documented condition of type "other" passes.
3. Partner sterilization: "You or your partner has not had a voluntary sterilization" is checked for
   the partner only when the patient has a partner.
4. Male with a female partner under the glossary: no glossary bullet names this case, so the
   couple bullet "For a female with a male partner" is applied with the female partner's age.
5. "Frequent" vs "timed" intercourse: the glossary counts "frequent, unprotected heterosexual sexual
   intercourse" and the table counts "unprotected timed sexual intercourse"; each is checked with
   its own field.
6. Female with a male partner, table option B: the table's "or ... At least 12 [6] cycles of donor
   insemination" satisfies the table, but the glossary's intercourse months must still be met
   (unless the gender dysphoria bullet applies).
7. Gender dysphoria: the glossary bullet makes the patient infertile, but the table's months/cycles
   and FSH requirements still apply.
8. No table row: a male "without a female partner" has no row, so "the requirement for the number
   of months trying to conceive" and the FSH criteria impose nothing on him beyond the glossary.
9. FSH "within the past": the test must be on or before the date of service (same day counts) and
   at most 12 (or 6) calendar months before it.
10. FSH "most recent lab test": the latest test on or before the date of service; when several tests
    share the latest date and time, it suffices that one of them is below 19 mIU/mL.
11. FSH "If you are age 40 and older ... all prior tests performed after age 40": tests on or after
    the 40th birthday and on or before the date of service; this criterion replaces the
    most-recent-test criterion, and it is met vacuously when no such test exists (the separate
    6-month test requirement still applies).
12. Semen analyses: "At least 2 abnormal semen analyses obtained at least 2 weeks apart" means two
    analyses on or before the date of service that are at least 14 days apart.
13. Age: "under 35" / "35 or older" / "age 40 and older" are measured on the date of service.

Not encoded: plan enrolment as student or partner (no claim field), precertification, network,
medical necessity, plan limits and general exclusions.
"""

COVERED_SERVICES = {
    "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins",
}

NATURAL_PROCESSES = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _ge(value, n):
    return value is not None and value >= n


def _female_brackets(age):
    # READING: unknown age. If the patient's age is unknown, every bracket ("under 35",
    # "35 ... or older", "age 40 and older") must be satisfied, so the outcome does not
    # depend on the missing fact.
    if age is None:
        return ["lt35", "35to39", "ge40"]
    if age < 35:
        return ["lt35"]
    if age < 40:
        return ["35to39"]
    return ["ge40"]


def _partner_brackets(partner_age):
    if partner_age is None:
        return ["lt35", "ge35"]
    return ["lt35"] if partner_age < 35 else ["ge35"]


def _threshold(bracket):
    return 12 if bracket == "lt35" else 6


def _fsh_ok(claim, h, bracket, age, service_date):
    tests = claim.get("day_3_fsh_tests")
    if not tests or service_date is None:
        return False
    # READING: "You need to have an unmedicated day 3 FSH test done within the past: 12 months
    # [6 months]". Only tests on or before the date of service count (same day included), and
    # at least one must be at most 12 (or 6) calendar months before the service.
    prior = [t for t in tests if h.days_between(t[1], service_date) >= 0]
    window = _threshold(bracket)
    if not any(h.months_at_most(t[1], service_date, window) for t in prior):
        return False

    if bracket in ("lt35", "35to39"):
        # READING: "Must be less than 19 mIU/mL in your most recent lab test". The most recent
        # test is the latest one on or before the date of service; if several tests share that
        # latest date and time, one of them below 19 suffices.
        latest = max((t[1], t[2]) for t in prior)
        tied = [t for t in prior if (t[1], t[2]) == latest]
        return any(t[0] < 19 for t in tied)

    # READING: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests
    # performed after age 40". Tests on or after the 40th birthday and on or before the date
    # of service; this replaces the most-recent-test criterion and is met vacuously when no
    # such test exists. With an unknown age, all prior tests are used (a superset).
    if age is None:
        since_40 = prior
    else:
        since_40 = [t for t in h.fsh_tests_since_age_40(claim)
                    if h.days_between(t[1], service_date) >= 0]
    return all(t[0] < 19 for t in since_40)


def _infertile(claim, h, sex, partner, age, service_date):
    # READING: gender dysphoria. "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" makes the patient infertile under the glossary on its own;
    # the table requirements are still checked separately.
    if claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes":
        return True

    frequent = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    donor = claim.get("num_cycles_donor_insemination")

    if sex == "female" and partner == "male":
        # READING: "For a female with a male partner, after: 1 year [6 months] of frequent,
        # unprotected heterosexual sexual intercourse". Only the frequent-intercourse months count
        # here; timed-intercourse months and donor cycles are table measures, not glossary ones.
        return all(_ge(frequent, _threshold(b)) for b in _female_brackets(age))

    if sex == "female":
        # "For a female without a male partner, after: At least 12 cycles [6 cycles] of donor
        # insemination".
        return all(_ge(donor, _threshold(b)) for b in _female_brackets(age))

    if partner == "female":
        # READING: male with a female partner. No glossary bullet names him; the couple bullet
        # "For a female with a male partner, after: 1 year [6 months] of frequent, unprotected
        # heterosexual sexual intercourse" is applied with the female partner's age.
        partner_age = claim.get("age_of_patients_female_partner")
        return all(_ge(frequent, _threshold(b)) for b in _partner_brackets(partner_age))

    # "For a male without a female partner, after: At least 2 abnormal semen analyses obtained
    # at least 2 weeks apart".
    analyses = claim.get("abnormal_semen_analyses")
    if not analyses or service_date is None:
        return False
    # READING: "obtained at least 2 weeks apart". Two analyses on or before the date of service
    # whose dates are at least 14 days apart.
    prior = [d for d in analyses if h.days_between(d, service_date) >= 0]
    for i in range(len(prior)):
        for j in range(i + 1, len(prior)):
            if abs(h.days_between(prior[i], prior[j])) >= 14:
                return True
    return False


def _table_ok(claim, h, sex, partner, age, service_date):
    timed = claim.get("num_months_timed_unprotected_intercourse")
    donor = claim.get("num_cycles_donor_insemination")

    if sex == "female" and partner == "male":
        # READING: "A. 12 months or more or B. At least 12 cycles of donor insemination" (6 for
        # 35 or older). Either option meets the table; "unprotected timed sexual intercourse" is
        # counted with the timed-intercourse field.
        return all(
            (_ge(timed, _threshold(b)) or _ge(donor, _threshold(b)))
            and _fsh_ok(claim, h, b, age, service_date)
            for b in _female_brackets(age)
        )

    if sex == "female":
        # Rows "A female ... without a male partner": "At least 12 [6] cycles of donor
        # insemination" plus the FSH criteria.
        return all(
            _ge(donor, _threshold(b)) and _fsh_ok(claim, h, b, age, service_date)
            for b in _female_brackets(age)
        )

    if partner == "female":
        # Rows "A male of any age with a female partner under 35 [35 or older]": "12 months
        # [6 months] or more" of unprotected timed intercourse; FSH "Does not apply".
        partner_age = claim.get("age_of_patients_female_partner")
        return all(_ge(timed, _threshold(b)) for b in _partner_brackets(partner_age))

    # READING: no table row. The table has no row for a male without a female partner, so
    # "You have met the requirement for the number of months trying to conceive" and the FSH
    # criteria impose nothing on him beyond the glossary definition.
    return True


def covered_under_benefit(claim: dict, h) -> bool:
    # "We will cover charges ... for: Ovulation induction cycle(s) with menotropins;
    # Intrauterine insemination".
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    service_date = claim.get("date_service_received")
    age = h.patient_age(claim)

    # READING: unknown facts. "You are eligible for infertility services if:" lists conditions
    # that must be shown; a missing field leaves the condition unshown and fails it.

    # READING: natural physiologic process. "does not have infertility that is due to a natural
    # physiologic process such as age related ovarian insufficiency": "such as" introduces
    # examples, so every natural physiologic process (including natural male reproductive aging)
    # is excluded. The condition must also be "demonstrated" and "documented", so it must be known.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None or condition in NATURAL_PROCESSES:
        return False

    # "You or your partner has not had a voluntary sterilization with or without surgical reversal".
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    # READING: partner sterilization. "You or your partner" reaches the partner only when there is
    # one; with "no_partner" the partner clause does not apply.
    if partner != "no_partner" and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # "A successful pregnancy cannot be attained through less costly treatment for which coverage
    # is available under this plan."
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    if not _infertile(claim, h, sex, partner, age, service_date):
        return False

    if not _table_ok(claim, h, sex, partner, age, service_date):
        return False

    return True
