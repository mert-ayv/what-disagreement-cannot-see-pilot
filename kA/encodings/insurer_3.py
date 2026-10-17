"""Cardinal Care 2023-2024: comprehensive infertility services benefit (insurer reading).

READING choices (each is marked "# READING:" in the code):

1. Unknown facts: a missing field needed to show eligibility means the requirement is not
   shown, so the claim is not covered.
2. Covered services: only "Ovulation induction cycle(s) with menotropins" and "Intrauterine
   insemination" are covered; any other service name is not.
3. Student/partner status: no claim field exists; membership is treated as checked elsewhere.
4. Condition: "There exists a condition that ... Is demonstrated ... and documented" requires
   the condition field to be present.
5. Natural physiologic process: "such as age related ovarian insufficiency" is illustrative,
   so every natural_* value (including natural male reproductive aging and other natural
   physiologic processes) excludes coverage.
6. Sterilization: "You or your partner has not had" requires a known "no" for the patient and,
   where a partner exists, for the partner.
7. Age: "You are ... under 35 years of age" and "If you are age 40" are measured on the date of
   service; the female partner's age field is used for male-patient rows.
8. Male patient with a female partner: the glossary has no male-with-female-partner line; the
   couple is treated under "For a female with a male partner", applied with the female
   partner's age (frequent unprotected heterosexual intercourse for 12/6 months).
9. "Without a male partner" includes a female patient whose partner is female.
10. Male patient without a female partner: the table has no row for this patient, so the
    requirement "You have met the requirement for the number of months trying to conceive"
    cannot be met and the claim is not covered.
11. Table "A. 12 months or more or B. At least 12 cycles": the explicit "or" makes either
    route sufficient (no stricter reading is supportable), in addition to the glossary test.
12. FSH test window: "done within the past: 12/6 months" counts only tests dated on or before
    the date of service and at most 12/6 calendar months before it.
13. "Most recent lab test": the latest test by date and time among tests on or before the date
    of service; if several tests share that date and time, every one of them must be below 19.
14. "Less than 19 mIU/mL" is strict: 19 fails.
15. Age 40 and older: "less than 19 mIU/mL in all prior tests performed after age 40" requires
    at least one test on or after the 40th birthday (and on or before the date of service),
    and every such test must be below 19; the rule is not satisfied vacuously.
16. Glossary male-without-female-partner test: "At least 2 abnormal semen analyses obtained at
    least 2 weeks apart" means two analyses on or before the date of service at least 14 days
    apart.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: unknown facts. "A missing field means the fact is unknown"; an unknown fact
    # needed for eligibility is treated as not shown, so the claim is not covered.
    service = claim.get("service_type")
    # READING: covered services. "We will cover charges made by an infertility specialist for
    # the following infertility services: Ovulation induction cycle(s) with menotropins;
    # Intrauterine insemination" is an exhaustive list.
    if service not in ("intrauterine_insemination",
                       "ovulation_induction_cycle_with_menotropins"):
        return False

    dos = claim.get("date_service_received")
    if dos is None or claim.get("patient_dob") is None:
        return False

    # READING: age is measured on the date of service ("You are ... under 35 years of age").
    age = h.patient_age(claim)
    if age is None:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    # READING: student/partner status ("You are covered under this plan as a student or as a
    # covered dependent ...") has no claim field and is treated as checked elsewhere.

    # READING: condition. "There exists a condition that: Is demonstrated to cause the illness
    # of infertility. Has been recognized ... and documented" requires the field to be present.
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    # READING: "infertility that is due to a natural physiologic process such as age related
    # ovarian insufficiency" lists examples; every natural physiologic process excludes.
    if condition in ("natural_menopause", "natural_perimenopause",
                     "natural_male_reproductive_aging", "other_natural_physiologic_process"):
        return False

    # READING: "You or your partner has not had a voluntary sterilization" requires a known
    # "no" for the patient and, where there is a partner, for the partner.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner" and claim.get("partner_has_had_voluntary_sterilization") != "no":
        return False

    # "A successful pregnancy cannot be attained through less costly treatment"
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    def at_least(field, n):
        v = claim.get(field)
        return v is not None and v >= n

    def on_or_before_service(d):
        return h.days_between(d, dos) >= 0

    dysphoria = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"

    if sex == "female":
        older = age >= 35
        n = 6 if older else 12

        # Glossary infertility.
        if partner == "male":
            # "1 year / 6 months of frequent, unprotected heterosexual sexual intercourse"
            infertile = at_least("num_months_frequent_unprotected_heterosexual_intercourse", n)
        else:
            # READING: "For a female without a male partner" includes a female partner.
            # "At least 12 cycles / 6 cycles of donor insemination"
            infertile = at_least("num_cycles_donor_insemination", n)
        if not (infertile or dysphoria):
            return False

        # Table: months / cycles requirement.
        if partner == "male":
            # READING: "A. 12 months or more or B. At least 12 cycles of donor insemination":
            # the explicit "or" makes either route sufficient.
            months_ok = (at_least("num_months_timed_unprotected_intercourse", n)
                         or at_least("num_cycles_donor_insemination", n))
        else:
            # "Does not apply" / "At least 12 (6) cycles of donor insemination"
            months_ok = at_least("num_cycles_donor_insemination", n)
        if not months_ok:
            return False

        # Table: FSH requirements.
        tests = claim.get("day_3_fsh_tests")
        if not tests:
            return False
        # READING: "done within the past: 12 months / 6 months" counts only tests on or before
        # the date of service, at most n calendar months before it.
        prior = [t for t in tests if on_or_before_service(t[1])]
        if not any(h.months_at_most(t[1], dos, n) for t in prior):
            return False

        if age >= 40:
            # READING: "must be less than 19 mIU/mL in all prior tests performed after age 40"
            # requires at least one such test before the service, and all must be below 19
            # ("less than" is strict).
            since_40 = [t for t in h.fsh_tests_since_age_40(claim) if on_or_before_service(t[1])]
            if not since_40 or not all(t[0] < 19 for t in since_40):
                return False
        else:
            # READING: "most recent lab test" is the latest by date and time among tests on or
            # before the service; tied tests must all be below 19 ("less than" is strict).
            latest = max((t[1], t[2]) for t in prior)
            most_recent = [t for t in prior if (t[1], t[2]) == latest]
            if not all(t[0] < 19 for t in most_recent):
                return False
        return True

    # Male patient.
    if partner != "female":
        # READING: the glossary covers "a male without a female partner, after: At least 2
        # abnormal semen analyses obtained at least 2 weeks apart", but the table has no row
        # for this patient, so "You have met the requirement for the number of months trying
        # to conceive" cannot be met and the claim is not covered.
        analyses = [d for d in (claim.get("abnormal_semen_analyses") or [])
                    if on_or_before_service(d)]
        # READING: "at least 2 weeks apart" means two analyses at least 14 days apart.
        infertile = (len(analyses) >= 2
                     and h.days_between(min(analyses), max(analyses)) >= 14)
        _ = infertile or dysphoria
        return False

    # Male patient with a female partner.
    # READING: partner's age. "A male of any age with a female partner under 35 years of age"
    # uses the female partner's age field.
    partner_age = claim.get("age_of_patients_female_partner")
    if partner_age is None:
        return False
    n = 6 if partner_age >= 35 else 12

    # READING: the glossary has no line for a male with a female partner; the couple is
    # assessed under "For a female with a male partner, after: 1 year / 6 months of frequent,
    # unprotected heterosexual sexual intercourse", using the female partner's age.
    infertile = at_least("num_months_frequent_unprotected_heterosexual_intercourse", n)
    if not (infertile or dysphoria):
        return False

    # Table: "12 months or more" / "6 months or more" of unprotected timed sexual intercourse;
    # donor insemination, FSH window and FSH result "Does not apply".
    if not at_least("num_months_timed_unprotected_intercourse", n):
        return False
    return True
