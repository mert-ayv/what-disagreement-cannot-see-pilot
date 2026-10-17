"""Encoding of the Cardinal Care 2023-2024 comprehensive infertility services benefit
(Certificate of Coverage pp. 62-64, plus the glossary definition of "infertility").

READING choices made in this encoding:

1. Student/partner enrollment: "You are covered under this plan as a student or as a
   covered dependent" -- no claim field records enrollment status, so this requirement is
   treated as verified elsewhere (enrollment) and not encoded.
2. Natural physiologic process: "does not have infertility that is due to a natural
   physiologic process such as age related ovarian insufficiency" -- every "natural_*"
   value of the condition field (including male reproductive aging) excludes coverage;
   only "other" qualifies as a demonstrated, documented, non-natural condition.
3. Partner sterilization: "You or your partner has not had a voluntary sterilization" --
   the partner's sterilization is only checked when the patient has a partner; an unknown
   value for an existing partner (or for the patient) means the requirement is not shown.
4. Glossary branch selection: the glossary branch is chosen by the patient's sex and
   partner status; a female whose partner is female or who has no partner is "a female
   without a male partner"; a male whose partner is male or who has no partner is "a male
   without a female partner".
5. Female with a male partner, glossary: "after 1 year of frequent, unprotected
   heterosexual sexual intercourse" -- the glossary is applied literally, so donor
   insemination cycles (table option B) do not by themselves make such a patient
   infertile; she must meet the intercourse months (unless the gender dysphoria branch
   applies). "1 year" = 12 months.
6. Male with a female partner, glossary: no glossary branch names this case, but the table
   has rows for "A male of any age with a female partner"; the couple is treated as
   infertile when the female-with-male-partner definition is met from the female
   partner's side (frequent intercourse months by the partner's age).
7. Male without a female partner, table: the table has no row for this case; "You have
   met the requirement for the number of months trying to conceive" is read as imposing
   no further table requirement, so the glossary semen-analysis test governs.
8. "6 cycles of donor insemination if age 35 or older" (glossary) is read as at least 6.
9. Gender dysphoria: "For an individual or their partner who has been clinically
   diagnosed with gender dysphoria" makes the patient infertile under the glossary, but
   the table requirements (months/cycles, FSH) still apply as the task requires.
10. Semen analyses "at least 2 weeks apart": some pair of abnormal analyses performed on
    or before the date of service is at least 14 days apart.
11. Age: "under 35 years of age" / "age 40 and older" are measured on the date of service
    with the patient's (or, for row selection for men, the female partner's) whole-year age.
12. Table "Number of months of unprotected timed sexual intercourse" uses the
    timed-intercourse field; the glossary uses the frequent-heterosexual-intercourse field.
13. FSH timing: "You need to have an unmedicated day 3 FSH test done within the past"
    12/6 months -- at least one test dated on or before the date of service and at most
    n calendar months before it.
14. "Most recent lab test": the latest test (by date and time) on or before the date of
    service; when several tests tie for latest, every tied test must be below 19 mIU/mL.
15. Age 40+: "must be less than 19 mIU/mL in all prior tests performed after age 40" --
    tests on or after the 40th birthday and on or before the date of service; at least one
    such test must exist (the clause presupposes tests after 40), and all must be < 19.
16. "Must be less than 19 mIU/mL" is strict (19 fails).
17. Unknown (absent) facts needed for a requirement mean the requirement is not met.
"""


COVERED_SERVICES = {
    "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins",
}


def covered_under_benefit(claim: dict, h) -> bool:
    # Covered services: "Ovulation induction cycle(s) with menotropins" and
    # "Intrauterine insemination".
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    service_date = claim.get("date_service_received")
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    if service_date is None or patient_sex not in ("female", "male"):
        return False
    if partner_sex not in ("male", "female", "no_partner"):
        return False
    has_partner = partner_sex != "no_partner"

    # READING: enrollment -- "You are covered under this plan as a student or as a covered
    # dependent who is the student's legal spouse ..." -- no claim field records this;
    # treated as verified by enrollment elsewhere and not encoded.

    # READING: natural physiologic process -- "does not have infertility that is due to a
    # natural physiologic process such as age related ovarian insufficiency" -- all
    # "natural_*" values exclude; only "other" is a qualifying documented condition.
    # "There exists a condition that ... has been recognized ... and documented".
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # READING: sterilization -- "You or your partner has not had a voluntary
    # sterilization" -- partner checked only when a partner exists; unknown fails.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if has_partner and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # "A successful pregnancy cannot be attained through less costly treatment for which
    # coverage is available under this plan."
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # Helpers for counts.
    def count(field):
        v = claim.get(field)
        return v if isinstance(v, int) else None

    def at_least(field, n):
        v = count(field)
        return v is not None and v >= n

    patient_age = h.patient_age(claim)

    # READING: glossary branch selection -- "For a female with a male partner" / "For a
    # female without a male partner" / "For a male without a female partner" -- a female
    # with a female partner or no partner is "without a male partner"; a male with a male
    # partner or no partner is "without a female partner".
    female_with_male = patient_sex == "female" and partner_sex == "male"
    female_without_male = patient_sex == "female" and partner_sex != "male"
    male_with_female = patient_sex == "male" and partner_sex == "female"
    male_without_female = patient_sex == "male" and partner_sex != "female"

    # ---------------- Glossary: infertility ----------------
    infertile = False

    # READING: gender dysphoria -- "For an individual or their partner who has been
    # clinically diagnosed with gender dysphoria" -- satisfies the glossary on its own;
    # table requirements still apply below.
    if claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes":
        infertile = True

    freq_field = "num_months_frequent_unprotected_heterosexual_intercourse"
    di_field = "num_cycles_donor_insemination"

    if not infertile:
        if female_with_male:
            # READING: female with male partner -- "after 1 year of frequent, unprotected
            # heterosexual sexual intercourse if under the age of 35 / 6 months ... if age
            # 35 or older" -- applied literally; donor insemination cycles do not satisfy
            # this branch. 1 year = 12 months.
            if patient_age is not None:
                infertile = at_least(freq_field, 12 if patient_age < 35 else 6)
        elif female_without_male:
            # READING: "6 cycles of donor insemination if age 35 or older" read as at
            # least 6.
            if patient_age is not None:
                infertile = at_least(di_field, 12 if patient_age < 35 else 6)
        elif male_with_female:
            # READING: male with female partner -- the glossary has no such branch, but the
            # table has rows for "A male of any age with a female partner"; the couple is
            # infertile when "For a female with a male partner, after: 1 year of frequent,
            # unprotected heterosexual sexual intercourse if under the age of 35 / 6
            # months ... if age 35 or older" is met using the female partner's age.
            partner_age = claim.get("age_of_patients_female_partner")
            if isinstance(partner_age, int):
                infertile = at_least(freq_field, 12 if partner_age < 35 else 6)
        elif male_without_female:
            # READING: semen analyses -- "At least 2 abnormal semen analyses obtained at
            # least 2 weeks apart" -- some pair of analyses on or before the service date
            # is at least 14 days apart.
            dates = claim.get("abnormal_semen_analyses")
            if isinstance(dates, list):
                prior = [d for d in dates if h.days_between(d, service_date) >= 0]
                for i in range(len(prior)):
                    for j in range(len(prior)):
                        if i != j and h.days_between(prior[i], prior[j]) >= 14:
                            infertile = True
                            break
                    if infertile:
                        break

    if not infertile:
        return False

    # ---------------- Table: months/cycles and FSH ----------------
    timed_field = "num_months_timed_unprotected_intercourse"

    if male_with_female:
        # READING: age for row selection -- "A male of any age with a female partner under
        # 35 years of age" -- the female partner's age (field) is used.
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int):
            return False
        # Table: "12 months or more" / "6 months or more" of timed intercourse; FSH and
        # donor insemination "Does not apply".
        return at_least(timed_field, 12 if partner_age < 35 else 6)

    if male_without_female:
        # READING: missing table row -- "You have met the requirement for the number of
        # months trying to conceive" -- the table has no row for a male without a female
        # partner, so no further table requirement applies.
        return True

    # Female patient.
    if patient_age is None:
        return False
    under_35 = patient_age < 35

    # Months/cycles requirement.
    if female_with_male:
        # Table: "A. 12 months or more or B. At least 12 cycles of donor insemination"
        # (6 for age 35 or older).
        n = 12 if under_35 else 6
        if not (at_least(timed_field, n) or at_least(di_field, n)):
            return False
    else:
        # Table: "At least 12 cycles of donor insemination" (6 for 35 or older).
        if not at_least(di_field, 12 if under_35 else 6):
            return False

    # FSH requirements.
    tests = claim.get("day_3_fsh_tests")
    if not isinstance(tests, list) or not tests:
        return False

    def on_or_before_service(t):
        return h.days_between(t[1], service_date) >= 0

    prior_tests = [t for t in tests if on_or_before_service(t)]
    if not prior_tests:
        return False

    # READING: FSH window -- "You need to have an unmedicated day 3 FSH test done within
    # the past: 12 months / 6 months" -- at least one test on or before the service date
    # and at most n calendar months before it.
    window = 12 if under_35 else 6
    if not any(h.months_at_most(t[1], service_date, window) for t in prior_tests):
        return False

    # READING: strictness -- "Must be less than 19 mIU/mL" -- 19 itself fails.
    def below_19(t):
        return isinstance(t[0], (int, float)) and t[0] < 19

    if patient_age < 40:
        # READING: most recent test -- "Must be less than 19 mIU/mL in your most recent lab
        # test" -- latest by date and time on or before the service date; when several
        # tests tie for latest, all tied tests must be below 19.
        latest_key = max((t[1], t[2]) for t in prior_tests)
        latest = [t for t in prior_tests if (t[1], t[2]) == latest_key]
        return all(below_19(t) for t in latest)

    # READING: age 40+ -- "must be less than 19 mIU/mL in all prior tests performed after
    # age 40" -- tests on or after the 40th birthday and on or before the service date; at
    # least one must exist and every one must be below 19.
    since_40 = [t for t in h.fsh_tests_since_age_40(claim) if on_or_before_service(t)]
    if not since_40:
        return False
    return all(below_19(t) for t in since_40)
