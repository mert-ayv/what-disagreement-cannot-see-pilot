"""Cardinal Care 2023-2024, comprehensive infertility services (member-advocate encoding).

READING choices:
1. Unknown facts: "You are eligible for infertility services if: ..." lists conditions the
   member must meet, so a required fact that is absent from the claim is not established.
   Where an unknown fact cannot change the outcome (female partner's age when the stricter
   12-month threshold is met), the claim is still covered.
2. Natural physiologic process: "a natural physiologic process such as age related ovarian
   insufficiency" uses "such as" as illustration; natural menopause, perimenopause, male
   reproductive aging and other natural physiologic processes are all excluded. Any other
   documented condition ("other") satisfies the condition bullet.
3. Female with a male partner, glossary: the table lets her qualify with "B. At least 12
   cycles of donor insemination" (6 if 35+). To give that route effect, the glossary prong
   "For a female with a male partner" is read as also met by the donor-insemination counts
   the glossary uses for females, not only by frequent intercourse.
4. Table intercourse route: the column "Number of months of unprotected timed sexual
   intercourse" is a clear requirement and is checked on the timed-intercourse field; the
   glossary's "frequent, unprotected heterosexual sexual intercourse" is checked on the
   frequent-intercourse field.
5. Male with a female partner: the glossary has no prong for him; his infertility is read
   through the couple prong "For a female with a male partner, after ..." using the female
   partner's age (or the gender dysphoria prong).
6. Male without a female partner: the table has no row for him, so no months-trying or FSH
   criterion applies ("the requirement for the number of months" is vacuously met); the
   glossary requires "At least 2 abnormal semen analyses obtained at least 2 weeks apart",
   read as two analyses on or before the date of service at least 14 days apart.
7. FSH window: "done within the past 12 months / 6 months" is measured back from the date
   of service, exactly n months counts, and tests after the date of service do not count.
8. "Most recent lab test": the latest test on or before the date of service by date and
   time; when several tests share that latest date and time, any one of them can be the
   most recent, so the claim passes if one of them is below 19 mIU/mL.
9. Age 40+: "less than 19 mIU/mL in all prior tests performed after age 40" means every test
   on or after the 40th birthday and on or before the date of service; if there is no such
   test the condition is vacuously met (the 6-month test requirement still applies).
10. Gender dysphoria: "For an individual or their partner who has been clinically diagnosed
   with gender dysphoria" is a free-standing glossary prong; the table criteria still apply.
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


def _at_least(claim, field, n):
    v = claim.get(field)
    return isinstance(v, int) and not isinstance(v, bool) and v >= n


def _on_or_before(h, date, service_date):
    return h.days_between(date, service_date) >= 0


def _fsh_ok(claim, h, age, service_date):
    tests = claim.get("day_3_fsh_tests")
    if not tests or service_date is None:
        return False
    # READING: "within the past" is counted back from the date of service; later tests do not count.
    past = [t for t in tests if _on_or_before(h, t[1], service_date)]
    if not past:
        return False
    window = 12 if age < 35 else 6
    if not any(h.months_at_most(t[1], service_date, window) for t in past):
        return False
    if age < 40:
        # READING: "Must be less than 19 mIU/mL in your most recent lab test"; ties on date and
        # time pass if any tied test is below 19.
        latest = max((t[1], t[2]) for t in past)
        most_recent = [t for t in past if (t[1], t[2]) == latest]
        return any(t[0] < 19 for t in most_recent)
    # READING: "less than 19 mIU/mL in all prior tests performed after age 40"; tests on or
    # after the 40th birthday and on or before the date of service; vacuous if none.
    since_40 = [t for t in h.fsh_tests_since_age_40(claim)
                if _on_or_before(h, t[1], service_date)]
    return all(t[0] < 19 for t in since_40)


def _semen_ok(claim, h, service_date):
    dates = claim.get("abnormal_semen_analyses")
    if not dates:
        return False
    # READING: "At least 2 abnormal semen analyses obtained at least 2 weeks apart"; two
    # analyses on or before the date of service, at least 14 days apart.
    if service_date is not None:
        dates = [d for d in dates if _on_or_before(h, d, service_date)]
    if len(dates) < 2:
        return False
    return h.days_between(min(dates), max(dates)) >= 14


def covered_under_benefit(claim: dict, h) -> bool:
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    service_date = claim.get("date_service_received")
    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    # READING: unknown facts needed to place the patient in a glossary prong or table row are
    # not established ("You are eligible for infertility services if").
    if sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    # Documented condition, not due to a natural physiologic process.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    # READING: "a natural physiologic process such as age related ovarian insufficiency";
    # "such as" is illustrative, so all natural processes (incl. male aging) are excluded.
    if condition is None or condition in NATURAL_PROCESSES:
        return False

    # No voluntary sterilization of patient or partner.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner" and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # Less costly covered treatment cannot achieve pregnancy.
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    gender_dysphoria = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"

    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        n = 12 if age < 35 else 6
        di_ok = _at_least(claim, "num_cycles_donor_insemination", n)
        if partner == "male":
            # READING: table column "Number of months of unprotected timed sexual intercourse"
            # is checked on the timed field: "A. 12 months or more or B. At least 12 cycles".
            table_ok = _at_least(claim, "num_months_timed_unprotected_intercourse", n) or di_ok
            # READING: glossary "For a female with a male partner, after: 1 year of frequent,
            # unprotected heterosexual sexual intercourse"; also met by the donor-insemination
            # counts so that table route B has effect.
            glossary_ok = (gender_dysphoria
                           or _at_least(claim, "num_months_frequent_unprotected_heterosexual_intercourse", n)
                           or di_ok)
        else:
            table_ok = di_ok
            glossary_ok = gender_dysphoria or di_ok
        if not (table_ok and glossary_ok):
            return False
        return _fsh_ok(claim, h, age, service_date)

    # Male patient.
    if partner == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        # READING: unknown female partner age; covered only if the stricter 12-month
        # threshold ("female partner under 35 years of age: 12 months or more") is met.
        n = 12 if partner_age is None or partner_age < 35 else 6
        table_ok = _at_least(claim, "num_months_timed_unprotected_intercourse", n)
        # READING: no glossary prong for "a male with a female partner"; the couple prong
        # "For a female with a male partner, after: 1 year ... if under the age of 35" is
        # applied with the female partner's age.
        glossary_ok = (gender_dysphoria
                       or _at_least(claim, "num_months_frequent_unprotected_heterosexual_intercourse", n)
                       or _at_least(claim, "num_cycles_donor_insemination", n))
        # FSH: "Does not apply" for males.
        return table_ok and glossary_ok

    # Male without a female partner.
    # READING: the table has no row for a male without a female partner, so no months or FSH
    # criterion applies; glossary "For a male without a female partner, after: At least 2
    # abnormal semen analyses obtained at least 2 weeks apart".
    return gender_dysphoria or _semen_ok(claim, h, service_date)
