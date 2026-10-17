"""
READING choices:
- “You or your partner has not had a voluntary sterilization” is disjunctive:
  either person's established absence of voluntary sterilization suffices.
- “Such as” makes the natural-physiologic-process examples nonexclusive.
- The glossary and eligibility table are cumulative, not interchangeable.
- For a male with a female partner, the glossary's female-partner criteria
  establish the couple's infertility; the male's table row also applies.
- “Without a male partner” includes a female partner or no partner;
  “without a female partner” includes a male partner or no partner.
- Gender dysphoria independently satisfies the glossary definition, but does
  not waive an otherwise applicable eligibility-table requirement.
- The table imposes no additional waiting-period or FSH requirement on
  configurations for which it supplies no row.
- “Most recent lab test” permits a qualifying result among tests tied for
  the latest timestamp.
- At age 40 or older, the result restriction applies to all available tests
  on or after the 40th birthday, not to earlier tests; a new test after that
  birthday is not separately required.
- “Within the past” includes the boundary. Evidence obtained after service
  does not establish eligibility at service.
- Unknown facts do not establish requirements, but facts unnecessary to a
  satisfied alternative need not be supplied.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Covered services — “for the following infertility services”
    # limits this benefit to the two enumerated services, without adding
    # precertification, provider, or other externally checked requirements.
    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner not in {"female", "male", "no_partner"}:
        return False

    # READING: Sterilization — “You or your partner has not had a voluntary
    # sterilization” permits either actual person's established "no" to suffice.
    # An absent partner cannot supply an alternative qualifying person.
    sterilization_ok = (
        claim.get("patient_has_had_voluntary_sterilization") == "no"
        or (
            partner != "no_partner"
            and claim.get("partner_has_had_voluntary_sterilization") == "no"
        )
    )
    if not sterilization_ok:
        return False

    # READING: Natural causes — “due to a natural physiologic process such as”
    # is not limited to ovarian aging. The supplied condition must establish
    # documented infertility from a non-natural-physiologic cause.
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

    def at_least(field, minimum):
        # READING: Unknown facts — “have met the requirement” requires evidence;
        # a missing field cannot establish a threshold.
        value = claim.get(field)
        return value is not None and value >= minimum

    age = None
    female_partner_age = None
    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
    elif partner == "female":
        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

    service_date = claim.get("date_service_received")

    # READING: Timing — “within the past” and eligibility for the services
    # refer to evidence available on the service date, not later tests.
    def tests_by_service(tests):
        if service_date is None:
            return []
        return [test for test in tests if test[1] <= service_date]

    # READING: Gender dysphoria — “For an individual or their partner who has
    # been clinically diagnosed with gender dysphoria” is an independent
    # glossary alternative, not a waiver of the separate eligibility table.
    glossary_ok = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not glossary_ok:
        if sex == "female":
            months_or_cycles = 12 if age < 35 else 6
            if partner == "male":
                glossary_ok = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    months_or_cycles,
                )
            else:
                # READING: Partner categories — “without a male partner”
                # includes both a female partner and no partner.
                glossary_ok = at_least(
                    "num_cycles_donor_insemination", months_or_cycles
                )
        elif partner == "female":
            # READING: Male with female partner — the glossary's “For a female
            # with a male partner” describes the female partner's failure to
            # become pregnant and thereby establishes the couple's infertility.
            glossary_ok = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                12 if female_partner_age < 35 else 6,
            )
        else:
            # READING: “For a male without a female partner” includes a male
            # partner or no partner. “At least 2 weeks apart” includes 14 days;
            # any qualifying pair of abnormal analyses suffices.
            dates = claim.get("abnormal_semen_analyses")
            if dates is not None and service_date is not None:
                eligible_dates = sorted(d for d in dates if d <= service_date)
                glossary_ok = (
                    len(eligible_dates) >= 2
                    and h.days_between(
                        eligible_dates[0], eligible_dates[-1]
                    ) >= 14
                )

    if not glossary_ok:
        return False

    # READING: Cumulative requirements — “You have met the requirement” and
    # “Your ... FSH level meets the following criteria” apply independently
    # of the glossary. Donor cycles allowed by the table do not rewrite the
    # glossary's intercourse requirement for a female with a male partner.
    if sex == "female":
        threshold = 12 if age < 35 else 6
        donor_ok = at_least("num_cycles_donor_insemination", threshold)

        if partner == "male":
            table_wait_ok = (
                at_least(
                    "num_months_timed_unprotected_intercourse", threshold
                )
                or donor_ok
            )
        else:
            table_wait_ok = donor_ok

        if not table_wait_ok:
            return False

        tests = claim.get("day_3_fsh_tests")
        if tests is None or service_date is None:
            return False
        tests = tests_by_service(tests)
        if not tests:
            return False

        window = 12 if age < 35 else 6

        # READING: Recency — “within the past” includes exactly the stated
        # number of calendar months; no future test qualifies.
        if not any(
            h.months_at_most(test[1], service_date, window)
            for test in tests
        ):
            return False

        if age < 40:
            latest_timestamp = max((test[1], test[2]) for test in tests)
            # READING: Tied results — “your most recent lab test” does not
            # distinguish tests sharing a timestamp, so a qualifying tied
            # result suffices rather than imposing an unstated worst-result rule.
            return any(
                (test[1], test[2]) == latest_timestamp and test[0] < 19
                for test in tests
            )

        # READING: Age 40 — “less than 19 ... in all prior tests performed
        # after age 40” covers all available tests on or after the 40th
        # birthday. Earlier results are unrestricted, and the text does not
        # separately require a post-birthday test if a recent test exists.
        post_40_tests = tests_by_service(h.fsh_tests_since_age_40(claim))
        return all(test[0] < 19 for test in post_40_tests)

    if partner == "female":
        # The male rows explicitly mark donor cycles and FSH “Does not apply.”
        return at_least(
            "num_months_timed_unprotected_intercourse",
            12 if female_partner_age < 35 else 6,
        )

    # READING: Unlisted configurations — the table lists male patients only
    # “with a female partner,” while the glossary expressly recognizes males
    # “without a female partner.” No table waiting period or FSH condition
    # is invented for the latter group.
    return True
