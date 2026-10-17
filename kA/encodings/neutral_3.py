"""Encoding of the Cardinal Care 2023-2024 comprehensive infertility services benefit.

READING choices (each is also marked inline with "# READING:"):

1. Covered services: only "intrauterine_insemination" and
   "ovulation_induction_cycle_with_menotropins" are covered services.
2. Enrollment status ("covered under this plan as a student or as a covered dependent ...")
   has no claim field and is treated as checked elsewhere.
3. Glossary for a male patient with a female partner: the glossary has no such branch, so the
   couple is tested under "a female with a male partner", using the female partner's age.
4. Glossary for a female with a female partner: she is "a female without a male partner".
5. Glossary and table are both required (conjunctive). A female with a male partner must meet the
   glossary intercourse duration even though the table also allows donor-insemination cycles.
6. Gender dysphoria: a clinical diagnosis by itself makes the patient infertile under the glossary,
   but the other eligibility requirements (including the table) still apply.
7. Semen analyses "at least 2 weeks apart": at least one pair of abnormal analyses, both on or
   before the service date, separated by 14 or more days.
8. Table rows: "12 months or more" / "At least 12 cycles" mean >= the number; the female rows with
   a male partner are met by option A or option B.
9. A male patient without a female partner has no table row: the months requirement and the FSH
   requirement are treated as not applicable (vacuously met).
10. Age bands use the patient's age on the date of service (the female partner's age for male rows).
11. FSH "done within the past" 12/6 months: at least one test dated on or before the service date
    and at most 12/6 calendar months before it.
12. "most recent lab test": the latest test by date and time on or before the service date; if
    several tests share that date and time, all of them must be below 19 mIU/mL.
13. Age 40 and older: "all prior tests performed after age 40" means all tests on or after the 40th
    birthday and on or before the service date; with none, that condition is vacuously met (the
    within-6-months test is still required).
14. Sterilization: the patient must report "no"; the partner must report "no" whenever a partner
    exists; with no partner the partner field is not required.
15. Natural physiologic process: "natural_menopause", "natural_perimenopause",
    "natural_male_reproductive_aging" and "other_natural_physiologic_process" disqualify; only
    "other" counts as a qualifying documented condition.
16. Missing facts: a required fact that is absent is treated as not met (returns False).
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


def _int_at_least(claim, field, n):
    value = claim.get(field)
    return isinstance(value, int) and value >= n


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: covered services. "We will cover charges made by an infertility specialist for the
    # following infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine
    # insemination". Only these two service types are covered.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    # READING: enrollment. "You are covered under this plan as a student or as a covered dependent
    # who is the student's legal spouse ...". No claim field records this; treated as checked
    # elsewhere (enrollment), not encoded.

    service_date = claim.get("date_service_received")
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    if service_date is None or patient_sex not in ("female", "male") or partner_sex not in (
        "male",
        "female",
        "no_partner",
    ):
        return False

    patient_age = h.patient_age(claim)

    # ---- Eligibility requirements from the bullet list ----

    # READING: documented condition. "There exists a condition that: Is demonstrated to cause the
    # illness of infertility. Has been recognized ... and documented". The condition field must be
    # present; together with the natural-process bullet only "other" qualifies.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    # READING: natural physiologic process. "does not have infertility that is due to a natural
    # physiologic process such as age related ovarian insufficiency (e.g. perimenopause,
    # menopause)". All natural-process values, including male reproductive aging, disqualify.
    if condition in NATURAL_PROCESSES:
        return False
    if condition != "other":
        return False

    # READING: sterilization. "You or your partner has not had a voluntary sterilization". The
    # patient must report "no"; a partner's status is required only when a partner exists.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner_sex != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # "A successful pregnancy cannot be attained through less costly treatment for which coverage
    # is available under this plan."
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # ---- Glossary: infertility ----
    if not _is_infertile(claim, h, patient_sex, partner_sex, patient_age, service_date):
        return False

    # ---- Table: months trying to conceive and FSH ----
    return _meets_table(claim, h, patient_sex, partner_sex, patient_age, service_date)


def _is_infertile(claim, h, patient_sex, partner_sex, patient_age, service_date):
    # READING: gender dysphoria. "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria". The diagnosis alone satisfies the glossary definition.
    if claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes":
        return True

    if patient_sex == "female":
        if patient_age is None:
            return False
        if partner_sex == "male":
            # "For a female with a male partner, after: 1 year of frequent, unprotected
            # heterosexual sexual intercourse if under the age of 35; 6 months ... if age 35 or older"
            needed = 12 if patient_age < 35 else 6
            return _int_at_least(
                claim, "num_months_frequent_unprotected_heterosexual_intercourse", needed
            )
        # READING: female with a female partner. "For a female without a male partner". A female
        # partner is not a male partner, so the donor-insemination branch applies.
        # "At least 12 cycles of donor insemination if under the age of 35; 6 cycles ... if 35 or older"
        needed = 12 if patient_age < 35 else 6
        return _int_at_least(claim, "num_cycles_donor_insemination", needed)

    # patient_sex == "male"
    if partner_sex == "female":
        # READING: male with a female partner. The glossary lists only "a female with a male
        # partner" and "a male without a female partner". The couple is tested under the
        # female-with-male-partner branch, using the female partner's age.
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int):
            return False
        needed = 12 if partner_age < 35 else 6
        return _int_at_least(
            claim, "num_months_frequent_unprotected_heterosexual_intercourse", needed
        )

    # READING: male without a female partner. "At least 2 abnormal semen analyses obtained at least
    # 2 weeks apart". Some pair of analyses on or before the service date must be 14 or more days
    # apart.
    analyses = claim.get("abnormal_semen_analyses")
    if not analyses:
        return False
    dates = sorted(d for d in analyses if h.days_between(d, service_date) >= 0)
    if len(dates) < 2:
        return False
    return h.days_between(dates[0], dates[-1]) >= 14


def _meets_table(claim, h, patient_sex, partner_sex, patient_age, service_date):
    if patient_sex == "male":
        if partner_sex != "female":
            # READING: male without a female partner. The table has rows only for "A male of any
            # age with a female partner". With no row, "the requirement for the number of months"
            # and the FSH requirement are treated as not applicable.
            return True
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int):
            return False
        # "12 months or more" (partner under 35) / "6 months or more" (partner 35 or older) of
        # unprotected timed sexual intercourse; donor insemination and FSH "Does not apply".
        needed = 12 if partner_age < 35 else 6
        return _int_at_least(claim, "num_months_timed_unprotected_intercourse", needed)

    # Female rows.
    if patient_age is None:
        return False
    # READING: age band. "A female under 35 years of age" / "35 years of age or older"; age is the
    # patient's age on the date of service.
    under_35 = patient_age < 35
    needed = 12 if under_35 else 6

    if partner_sex == "male":
        # READING: alternatives. "A. 12 months or more or B. At least 12 cycles of donor
        # insemination". Either option meets the row.
        months_ok = _int_at_least(claim, "num_months_timed_unprotected_intercourse", needed) or _int_at_least(
            claim, "num_cycles_donor_insemination", needed
        )
    else:
        # Without a male partner: months "Does not apply"; "At least 12 cycles" / "At least 6 cycles".
        months_ok = _int_at_least(claim, "num_cycles_donor_insemination", needed)
    if not months_ok:
        return False

    return _meets_fsh(claim, h, patient_age, service_date, window_months=needed)


def _meets_fsh(claim, h, patient_age, service_date, window_months):
    tests = claim.get("day_3_fsh_tests")
    if not tests:
        return False

    # Only tests performed on or before the date of service are "past" tests.
    past = [t for t in tests if h.days_between(t[1], service_date) >= 0]
    if not past:
        return False

    # READING: test window. "You need to have an unmedicated day 3 FSH test done within the past:
    # 12 months / 6 months". At least one test at most that many calendar months before the
    # service date.
    if not any(h.months_at_most(t[1], service_date, window_months) for t in past):
        return False

    if patient_age < 40:
        # READING: most recent test. "Must be less than 19 mIU/mL in your most recent lab test".
        # The latest test by (date, time); when several share that date and time, all of them must
        # be below 19, since none can be singled out as the most recent.
        latest_key = max((t[1], t[2]) for t in past)
        latest = [t for t in past if (t[1], t[2]) == latest_key]
        return all(t[0] < 19 for t in latest)

    # READING: age 40 and older. "must be less than 19 mIU/mL in all prior tests performed after age
    # 40". Tests on or after the 40th birthday and on or before the service date; if there are none,
    # this condition is vacuously met (the window requirement above still applies).
    since_40 = [t for t in h.fsh_tests_since_age_40(claim) if h.days_between(t[1], service_date) >= 0]
    return all(t[0] < 19 for t in since_40)
