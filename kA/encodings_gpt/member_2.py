"""
READING choices:
- The claim interface presupposes the covered-student/eligible-partner context;
  it supplies no enrollment or relationship-status verification fields.
- "You or your partner" is read disjunctively for voluntary sterilization.
- Natural physiologic causes are not limited to the examples given.
- Infertility may be established through the female partner's failure to
  conceive when the patient is male.
- Glossary infertility and the table's eligibility conditions are separate
  requirements; gender dysphoria satisfies the glossary, not a table exemption.
- A table row applies only to the population it describes. No unlisted
  duration or FSH requirement is imposed on males without female partners.
- The table's express donor-insemination alternatives are honored.
- FSH recency includes the boundary date; future tests are not evidence.
  Tied most-recent tests permit the favorable result. At age 40 or older,
  all supplied tests on or after the 40th birthday must pass.
- Unknown facts do not establish a requirement, but a known alternative can.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Enrollment context — "covered under this plan as a student or
    # as a covered dependent ..." is presupposed by this member-claim interface.
    # No supplied field can establish or distinguish those enrollment statuses.

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    service_date = claim.get("date_service_received")

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" permits either person's established absence of voluntary
    # sterilization to satisfy this condition; it does not say "neither."
    patient_not_sterilized = (
        claim.get("patient_has_had_voluntary_sterilization") == "no"
    )
    partner_not_sterilized = (
        partner_sex != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") == "no"
    )
    if not (patient_not_sterilized or partner_not_sterilized):
        return False

    # READING: Natural causes — "a natural physiologic process such as age
    # related ovarian insufficiency" gives examples, not an exhaustive list.
    # The combined condition field must establish a documented nonnatural cause;
    # an unaffected or otherwise qualifying partner is not inferred.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    def at_least(field, required):
        value = claim.get(field)
        return value is not None and value >= required

    age = h.patient_age(claim) if sex == "female" else None
    partner_age = claim.get("age_of_patients_female_partner")

    def duration_for_age(known_age):
        return 12 if known_age < 35 else 6

    # Establish glossary infertility independently of table eligibility.
    # READING: Gender dysphoria — "For an individual or their partner who has
    # been clinically diagnosed with gender dysphoria" is an independent
    # glossary route, without an additional glossary waiting period.
    infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not infertile:
        if sex == "female" and age is not None:
            required = duration_for_age(age)
            if partner_sex == "male":
                infertile = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    required,
                )
            elif partner_sex in {"female", "no_partner"}:
                infertile = at_least("num_cycles_donor_insemination", required)

        elif sex == "male" and partner_sex == "female":
            # READING: Couple-based infertility — "failure to become pregnant"
            # and "For a female with a male partner" include the female partner
            # of a male claimant; otherwise the table's male/female-partner rows
            # would have no ordinary glossary route.
            if partner_age is not None:
                infertile = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    duration_for_age(partner_age),
                )

        elif sex == "male" and partner_sex in {"male", "no_partner"}:
            analyses = claim.get("abnormal_semen_analyses")
            if analyses is not None and service_date is not None:
                prior_dates = sorted(d for d in analyses if d <= service_date)
                infertile = (
                    len(prior_dates) >= 2
                    and h.days_between(prior_dates[0], prior_dates[-1]) >= 14
                )

    if not infertile:
        return False

    # READING: Independent eligibility — "You have met the requirement for the
    # number of months" and "Your ... FSH level meets the following criteria"
    # still apply where the table specifies them, even when gender dysphoria
    # established glossary infertility.
    if sex == "male":
        if partner_sex == "female":
            if partner_age is None:
                return False
            return at_least(
                "num_months_timed_unprotected_intercourse",
                duration_for_age(partner_age),
            )

        # READING: Unlisted populations — the table specifies males "with a
        # female partner" only. It imposes no additional duration or FSH test
        # on a male without a female partner who meets the glossary.
        return partner_sex in {"male", "no_partner"}

    if sex != "female" or age is None:
        return False

    required = duration_for_age(age)
    donor_requirement_met = at_least("num_cycles_donor_insemination", required)

    # READING: Express alternatives — "A. ... or B. ... donor insemination"
    # permits either table route for a female with a male partner. This does
    # not replace the separately applicable glossary definition.
    if partner_sex == "male":
        duration_met = donor_requirement_met or at_least(
            "num_months_timed_unprotected_intercourse", required
        )
    elif partner_sex in {"female", "no_partner"}:
        duration_met = donor_requirement_met
    else:
        # The donor route meets either possible female table row, so the
        # partner's unknown sex need not defeat this established alternative.
        duration_met = donor_requirement_met

    if not duration_met:
        return False

    tests = claim.get("day_3_fsh_tests")
    if tests is None or service_date is None:
        return False

    prior_tests = [test for test in tests if test[1] <= service_date]
    if not prior_tests:
        return False

    latest_timestamp = max((test[1], test[2]) for test in prior_tests)
    recency_months = 12 if age < 35 else 6

    # READING: Recency — "within the past" includes exactly the stated number
    # of calendar months, but not tests after the date of service.
    if not h.months_at_most(
        latest_timestamp[0], service_date, recency_months
    ):
        return False

    if age < 40:
        # READING: Tied results — "your most recent lab test" is singular.
        # If multiple tests share the latest timestamp, a qualifying one may
        # be selected rather than adding an unstated all-tied-tests condition.
        return any(
            level < 19
            for level, test_date, test_time in prior_tests
            if (test_date, test_time) == latest_timestamp
        )

    # READING: Age-40 history — "less than 19 ... in all prior tests performed
    # after age 40" covers the supplied history from the 40th birthday through
    # service, including the latest test. A recent pre-birthday test may meet
    # recency; no post-birthday test is separately demanded by this wording.
    tests_since_40 = [
        test
        for test in h.fsh_tests_since_age_40(claim)
        if test[1] <= service_date
    ]
    return all(level < 19 for level, _, _ in tests_since_40)
