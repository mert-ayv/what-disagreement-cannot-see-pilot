"""Cardinal Care 2023-2024, comprehensive infertility services benefit (pp. 62-64).

Encoded from the insurer's (claims counsel's) perspective: where the text admits
more than one reasonable reading, the reading that covers fewer claims is chosen.

READING choices:
 1. Unknown facts: a missing field needed to establish eligibility means the
    requirement is not shown to be met, so the claim is not covered.
 2. Natural physiologic process: "such as age related ovarian insufficiency
    (e.g. perimenopause, menopause)" is a list of examples; every natural
    physiologic process, including natural male reproductive aging, excludes
    coverage. Only a documented condition of type "other" qualifies.
 3. Partner sterilization: "You or your partner has not had a voluntary
    sterilization" requires a known "no" for the patient and, where a partner
    exists, a known "no" for the partner.
 4. Two intercourse measures: the table's "months of unprotected timed sexual
    intercourse" and the glossary's "frequent, unprotected heterosexual sexual
    intercourse" are separate requirements; a patient relying on intercourse must
    satisfy both counts.
 5. Glossary path for a female with a male partner: the glossary bullet "For a
    female with a male partner" requires intercourse months; donor insemination
    cycles (table route B) satisfy the table but not the glossary, so such a
    patient is infertile only through intercourse months or gender dysphoria.
 6. Male patient with a female partner: the glossary's "female with a male
    partner" bullet is applied to the couple, measured by the female partner's
    age.
 7. Male patient without a female partner: the table has no row for this
    patient, so "You have met the requirement for the number of months trying to
    conceive" cannot be shown to be met; not covered.
 8. Age: the patient's (and female partner's) age is taken on the date of
    service.
 9. "6 cycles of donor insemination" in the glossary (age 35 or older) means at
    least 6 cycles.
10. FSH window: "done within the past" 12 / 6 months is measured back from the
    date of service; tests dated after the date of service do not count.
11. "Most recent lab test": the latest test on or before the date of service
    (ordered by date, then time) must fall within the window and be below 19;
    where several tests share the latest date and time, every one of them must
    be below 19.
12. Age 40 and older: "must be less than 19 mIU/mL in all prior tests performed
    after age 40" requires at least one test performed on or after the 40th
    birthday (and on or before the date of service), every such test below 19,
    in addition to a test within the past 6 months.
13. Plan membership ("covered under this plan as a student or ... your
    partner") has no claim field and is not encoded here.
"""


COVERED_SERVICES = {
    "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins",
}

NATURAL_PROCESS_VALUES = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _test_key(test):
    level, date, time = test
    return (date, time)


def _fsh_ok(claim, h, age):
    """Table FSH requirement for a female patient."""
    tests = claim.get("day_3_fsh_tests")
    service_date = claim.get("date_service_received")
    if not tests or service_date is None:
        return False

    # READING: FSH window and "most recent lab test" -- "You need to have an
    # unmedicated day 3 FSH test done within the past" -- the window runs back
    # from the date of service and tests after the date of service are ignored.
    prior = [t for t in tests if h.days_between(t[1], service_date) >= 0]
    if not prior:
        return False

    window = 12 if age < 35 else 6
    latest_key = max(_test_key(t) for t in prior)
    # READING: ties -- "in your most recent lab test" -- where several tests
    # share the latest date and time, all of them are the most recent test and
    # all must be below 19.
    latest = [t for t in prior if _test_key(t) == latest_key]
    if not h.months_at_most(latest_key[0], service_date, window):
        return False

    if age < 40:
        return all(t[0] < 19 for t in latest)

    # READING: age 40 and older -- "must be less than 19 mIU/mL in all prior
    # tests performed after age 40" -- presupposes at least one test after the
    # 40th birthday; every such test on or before the date of service must be
    # below 19.
    since_40 = [
        t for t in h.fsh_tests_since_age_40(claim)
        if h.days_between(t[1], service_date) >= 0
    ]
    if not since_40:
        return False
    return all(t[0] < 19 for t in since_40)


def covered_under_benefit(claim: dict, h) -> bool:
    # Service must be one of the listed infertility services.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    # READING: unknown facts -- "A missing field means the fact is unknown" --
    # an unknown eligibility fact is treated as not established.
    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    age = h.patient_age(claim)
    if age is None:
        return False

    # Documented condition causing infertility, not a natural physiologic process.
    # READING: natural physiologic process -- "due to a natural physiologic
    # process such as age related ovarian insufficiency" -- the examples are
    # illustrative; any natural process (including male reproductive aging)
    # excludes. Only a documented "other" condition qualifies.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # Voluntary sterilization.
    # READING: partner sterilization -- "You or your partner has not had a
    # voluntary sterilization" -- requires a known "no" for the patient and for
    # any existing partner.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner" and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # Less costly treatment.
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    timed = claim.get("num_months_timed_unprotected_intercourse")
    frequent = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    donor = claim.get("num_cycles_donor_insemination")
    dysphoria = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"

    if sex == "female":
        # READING: age -- "A female under 35 years of age" -- age is taken on
        # the date of service.
        threshold = 12 if age < 35 else 6
        has_male_partner = partner == "male"

        # Table: months / cycles requirement.
        if has_male_partner:
            table_months = (timed is not None and timed >= threshold) or (
                donor is not None and donor >= threshold
            )
        else:
            table_months = donor is not None and donor >= threshold
        if not table_months:
            return False

        # Table: FSH requirement.
        if not _fsh_ok(claim, h, age):
            return False

        # Glossary: infertile.
        if dysphoria:
            infertile = True
        elif has_male_partner:
            # READING: two intercourse measures -- "1 year of frequent,
            # unprotected heterosexual sexual intercourse" -- the glossary count
            # is required in addition to the table's timed-intercourse count.
            # READING: glossary path for a female with a male partner -- "For a
            # female with a male partner, after: 1 year of frequent,
            # unprotected ... intercourse" -- donor cycles do not satisfy the
            # glossary for this patient.
            infertile = frequent is not None and frequent >= threshold
        else:
            # READING: "6 cycles of donor insemination if age 35 or older" --
            # read as at least 6 cycles.
            infertile = donor is not None and donor >= threshold
        return infertile

    # Male patient.
    if partner != "female":
        # READING: male without a female partner -- the table lists only "A male
        # of any age with a female partner" -- no row applies, so "You have met
        # the requirement for the number of months trying to conceive" is not
        # shown to be met.
        return False

    partner_age = claim.get("age_of_patients_female_partner")
    if partner_age is None:
        return False
    threshold = 12 if partner_age < 35 else 6

    # Table: months of unprotected timed intercourse; FSH "Does not apply".
    if timed is None or timed < threshold:
        return False

    # Glossary: infertile.
    if dysphoria:
        return True
    # READING: male with a female partner -- "For a female with a male partner,
    # after: 1 year ... if under the age of 35" -- applied to the couple using
    # the female partner's age, with the frequent-intercourse count required in
    # addition to the table's timed count.
    return frequent is not None and frequent >= threshold
