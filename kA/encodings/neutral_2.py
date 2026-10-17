"""Encoding of the Cardinal Care 2023-2024 comprehensive infertility services benefit.

READING choices (each marked "# READING:" in the code):

1. Student/partner enrolment ("covered under this plan as a student or ... partner") has no claim
   field; it is treated as established by enrolment and not encoded.
2. Glossary and table are cumulative: the patient must be infertile under the glossary AND meet
   the table's months/cycles requirement. For a female with a male partner the glossary counts
   "frequent, unprotected heterosexual sexual intercourse" and the table counts "unprotected timed
   sexual intercourse"; both fields are checked separately.
3. "1 year" in the glossary is read as 12 months.
4. A male with a female partner has no glossary clause of his own; the couple is assessed under
   "For a female with a male partner", using the female partner's age.
5. "Without a male partner" (female) covers both a female partner and no partner; "without a
   female partner" (male) covers both a male partner and no partner.
6. A male without a female partner has no table row; no months/cycles or FSH requirement applies
   to him beyond the glossary's semen-analysis clause.
7. "At least 2 abnormal semen analyses obtained at least 2 weeks apart" is met when any two
   analyses are 14 or more days apart.
8. Gender dysphoria makes the patient infertile under the glossary but does not waive the table.
9. "You or your partner has not had a voluntary sterilization" requires the partner's answer
   only when there is a partner.
10. Any natural-process value of the documented condition (menopause, perimenopause, male
    reproductive aging, other natural physiologic process) fails the natural-process exclusion;
    only "other" passes.
11. "FSH test done within the past N months" is measured back from the date of service, counting
    only tests on or before that date; exactly N months counts.
12. "Your most recent lab test": the latest test by date and time on or before the date of
    service; if several tests share that latest date and time, all of them must be below 19.
13. "All prior tests performed after age 40": tests on or after the 40th birthday and on or
    before the date of service; at least one such test is required.
14. Ages for the 35 and 40 thresholds are taken on the date of service.
15. A missing field needed for a requirement means the requirement is not shown and the claim is
    not covered.
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

FSH_LIMIT = 19


def _ge(claim, field, n):
    value = claim.get(field)
    return value is not None and value >= n


def _tests_on_or_before_service(tests, service_date):
    # Dates are "YYYY_MM_DD", so string comparison orders them correctly.
    return [t for t in tests if t[1] <= service_date]


def _fsh_ok(claim, h, age, window_months):
    service_date = claim["date_service_received"]
    tests = claim.get("day_3_fsh_tests")
    if not tests:
        return False
    # READING: "done within the past" -- quoted "You need to have an unmedicated day 3 FSH test
    # done within the past: 12 months / 6 months"; measured back from the date of service, only
    # tests on or before that date count, and exactly N months counts.
    prior = _tests_on_or_before_service(tests, service_date)
    if not prior:
        return False
    latest_key = max((t[1], t[2]) for t in prior)
    if not h.months_at_most(latest_key[0], service_date, window_months):
        return False

    if age < 40:
        # READING: "most recent lab test" -- quoted "Must be less than 19 mIU/mL in your most
        # recent lab test"; the latest test by date and time; where several tests share that date
        # and time, each of them is a most recent test and all must be below 19.
        latest = [t for t in prior if (t[1], t[2]) == latest_key]
        return all(t[0] < FSH_LIMIT for t in latest)

    # READING: "after age 40" -- quoted "must be less than 19 mIU/mL in all prior tests performed
    # after age 40"; tests on or after the 40th birthday and on or before the date of service, all
    # below 19, and at least one such test must exist for the result to be shown.
    since_40 = _tests_on_or_before_service(h.fsh_tests_since_age_40(claim), service_date)
    if not since_40:
        return False
    return all(t[0] < FSH_LIMIT for t in since_40)


def _semen_analyses_ok(claim, h):
    dates = claim.get("abnormal_semen_analyses")
    if not dates or len(dates) < 2:
        return False
    # READING: "2 weeks apart" -- quoted "At least 2 abnormal semen analyses obtained at least 2
    # weeks apart"; met when any two analyses are 14 or more days apart.
    ordered = sorted(dates)
    return abs(h.days_between(ordered[0], ordered[-1])) >= 14


def covered_under_benefit(claim: dict, h) -> bool:
    # Covered service.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    # READING: enrolment -- quoted "You are covered under this plan as a student or as a covered
    # dependent who is the student's legal spouse"; no claim field exists, so enrolment is taken
    # as established and not encoded.

    if "date_service_received" not in claim:
        return False
    # READING: age thresholds -- quoted "under 35 years of age", "If you are age 40 and older";
    # ages are taken on the date of service.
    age = h.patient_age(claim)
    if age is None:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    # Documented condition causing infertility, and the natural-process exclusion.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    # READING: natural process -- quoted "does not have infertility that is due to a natural
    # physiologic process such as age related ovarian insufficiency (e.g. perimenopause,
    # menopause)"; every natural-process value fails, including male reproductive aging; only
    # "other" passes.
    if condition in NATURAL_PROCESSES:
        return False

    # Voluntary sterilization.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    # READING: partner sterilization -- quoted "You or your partner has not had a voluntary
    # sterilization"; the partner's answer is required only when there is a partner.
    if partner != "no_partner" and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # Less costly treatment.
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    female_partner_age = None
    if sex == "male" and partner == "female":
        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

    # ---- Glossary: infertile or infertility ----
    # READING: gender dysphoria -- quoted "For an individual or their partner who has been
    # clinically diagnosed with gender dysphoria"; this satisfies the glossary but does not waive
    # the table requirements.
    infertile = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    if not infertile:
        # READING: "1 year" -- quoted "1 year of frequent, unprotected heterosexual sexual
        # intercourse"; read as 12 months.
        if sex == "female" and partner == "male":
            needed = 12 if age < 35 else 6
            infertile = _ge(claim, "num_months_frequent_unprotected_heterosexual_intercourse", needed)
        elif sex == "female":
            # READING: "without a male partner" -- quoted "For a female without a male partner";
            # covers a female partner and no partner.
            needed = 12 if age < 35 else 6
            infertile = _ge(claim, "num_cycles_donor_insemination", needed)
        elif partner == "female":
            # READING: male with a female partner -- the glossary has no clause for him; quoted
            # "For a female with a male partner, after: 1 year ... if under the age of 35"; the
            # couple is assessed under that clause using the female partner's age.
            needed = 12 if female_partner_age < 35 else 6
            infertile = _ge(claim, "num_months_frequent_unprotected_heterosexual_intercourse", needed)
        else:
            # READING: "without a female partner" -- quoted "For a male without a female partner";
            # covers a male partner and no partner.
            infertile = _semen_analyses_ok(claim, h)
    if not infertile:
        return False

    # ---- Table: months/cycles trying to conceive and FSH ----
    # READING: glossary and table are cumulative -- quoted "You have met the requirement for the
    # number of months trying to conceive"; the table requirement applies on top of the glossary,
    # using the "timed" intercourse field for the table and the "frequent" field for the glossary.
    if sex == "female":
        window = 12 if age < 35 else 6
        if partner == "male":
            # "A. 12 months or more or B. At least 12 cycles of donor insemination" (6 if 35+).
            met = (_ge(claim, "num_months_timed_unprotected_intercourse", window)
                   or _ge(claim, "num_cycles_donor_insemination", window))
        else:
            met = _ge(claim, "num_cycles_donor_insemination", window)
        if not met:
            return False
        return _fsh_ok(claim, h, age, window)

    # Male patient.
    if partner == "female":
        needed = 12 if female_partner_age < 35 else 6
        # FSH: "Does not apply".
        return _ge(claim, "num_months_timed_unprotected_intercourse", needed)

    # READING: male without a female partner -- the table has no row for him; quoted "You have
    # met the requirement for the number of months trying to conceive"; no table requirement
    # exists for him, so only the glossary's semen-analysis clause applies.
    return True
