"""
Member-favourable readings:
- The glossary and eligibility table are separate requirements; gender dysphoria
  independently satisfies the glossary, but does not waive applicable table rules.
- For a male with a female partner, the glossary's female-with-male-partner
  definition applies to the couple.
- No waiting-period or FSH requirement is invented for groups absent from the table.
- The sterilization clause's "or" is inclusive: either person's confirmed lack
  of voluntary sterilization suffices; an absent partner cannot supply that fact.
- The documented condition identifies the infertility's cause; all expressly
  identified natural-process causes are excluded.
- Waiting periods and cycle counts are minimums, and the table's alternatives
  remain alternatives.
- FSH recency includes the boundary date. Equally recent tests below age 40
  are resolved favourably; at age 40 or older, every applicable result must pass.
- The age-40 FSH rule disregards pre-40 results and does not independently
  require a post-40 test.
- Unknown facts do not establish requirements; future tests do not establish
  eligibility on the service date.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    def at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")

    # READING: Unknown facts — "You are eligible ... if" requires established
    # applicable facts, not treating missing information as a favourable fact.
    if sex not in {"female", "male"}:
        return False
    if partner_sex not in {"female", "male", "no_partner"}:
        return False

    # READING: Natural-process cause — "infertility that is due to a natural
    # physiologic process such as" is non-exhaustive. The supplied documented
    # condition identifies the cause being evaluated, so every natural-process
    # label is excluded; an unknown cause does not establish eligibility.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" is read as an inclusive disjunction, not as requiring both
    # people to have avoided sterilization. With no partner, only the patient's
    # confirmed lack of voluntary sterilization can satisfy the clause.
    patient_not_sterilized = (
        claim.get("patient_has_had_voluntary_sterilization") == "no"
    )
    partner_not_sterilized = (
        partner_sex != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") == "no"
    )
    if not (patient_not_sterilized or partner_not_sterilized):
        return False

    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    age = None
    waiting_minimum = None
    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        waiting_minimum = 12 if age < 35 else 6
    elif partner_sex == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        waiting_minimum = 12 if partner_age < 35 else 6

    # READING: Independent glossary alternative — "For an individual or their
    # partner who has been clinically diagnosed with gender dysphoria" supplies
    # an independent infertility definition, but does not erase "You have met
    # the requirement" or the eligibility table.
    infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not infertile:
        if sex == "female":
            if partner_sex == "male":
                infertile = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    waiting_minimum,
                )
            else:
                # READING: Minimum counts — "after ... 6 cycles" means at least
                # six, rather than losing infertility status on a later cycle.
                infertile = at_least(
                    "num_cycles_donor_insemination", waiting_minimum
                )

        elif partner_sex == "female":
            # READING: Couple-based glossary application — "For a female with
            # a male partner" together with "your or your partner's medical
            # records" permits the female partner's failure to conceive to
            # establish infertility for the male member.
            infertile = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                waiting_minimum,
            )

        else:
            service_date = claim.get("date_service_received")
            analyses = claim.get("abnormal_semen_analyses")
            if service_date is not None and analyses is not None:
                # READING: As-of-service evidence — "after ... At least 2
                # abnormal semen analyses" requires completed analyses by the
                # service date; there is no stated maximum age for the results.
                prior_analyses = [d for d in analyses if d <= service_date]
                infertile = (
                    len(prior_analyses) >= 2
                    and h.days_between(
                        min(prior_analyses), max(prior_analyses)
                    ) >= 14
                )

    if not infertile:
        return False

    # READING: Separate glossary and table gates — "You have met the requirement
    # for the number of months ...", the table's "A ... or B", and the glossary's
    # "frequent, unprotected heterosexual sexual intercourse" are independently
    # applied. Donor cycles can satisfy the table's alternative without silently
    # substituting for the glossary's intercourse requirement.
    if sex == "female":
        donor_requirement_met = at_least(
            "num_cycles_donor_insemination", waiting_minimum
        )
        if partner_sex == "male":
            table_wait_met = (
                at_least(
                    "num_months_timed_unprotected_intercourse", waiting_minimum
                )
                or donor_requirement_met
            )
        else:
            table_wait_met = donor_requirement_met

        if not table_wait_met:
            return False

    elif partner_sex == "female":
        if not at_least(
            "num_months_timed_unprotected_intercourse", waiting_minimum
        ):
            return False

    else:
        # READING: Unlisted groups — the table lists males "with a female
        # partner", while the glossary expressly includes a "male without a
        # female partner". No table waiting period or FSH requirement is supplied
        # for the latter group, so none is invented.
        return True

    if sex == "male":
        # The listed male rows expressly say FSH testing "Does not apply".
        return True

    service_date = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date is None or tests is None:
        return False

    # READING: FSH timing — "within the past" excludes future tests, includes
    # tests on the service date, and includes the exact calendar-month boundary.
    prior_tests = [test for test in tests if test[1] <= service_date]
    if not prior_tests:
        return False

    latest_timestamp = max((date, time) for _, date, time in prior_tests)
    recency_months = 12 if age < 35 else 6
    if not h.months_at_most(
        latest_timestamp[0], service_date, recency_months
    ):
        return False

    if age < 40:
        # READING: Tied most-recent results — "less than 19 ... in your most
        # recent lab test" does not resolve simultaneous tests. Any passing
        # result among the equally most-recent tests satisfies this singular
        # requirement; a later, non-tied failing result cannot be disregarded.
        return any(
            level < 19
            for level, date, time in prior_tests
            if (date, time) == latest_timestamp
        )

    # READING: Age-40 history — "If you are age 40 and older ... less than 19
    # ... in all prior tests performed after age 40" applies to every known
    # test from the 40th birthday through service, including tied results.
    # Pre-40 levels are irrelevant. The separate recent-test requirement may
    # be met by a pre-40 test; no additional post-40 test is expressly required.
    return all(
        level < 19
        for level, date, time in h.fsh_tests_since_age_40(claim)
        if date <= service_date
    )
