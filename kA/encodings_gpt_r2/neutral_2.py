"""
READING choices:
- Sterilization and natural-physiology exclusions apply to either partner.
- The glossary and the benefit's eligibility requirements apply cumulatively.
- A male with a female partner may satisfy the glossary through the couple's
  failure to conceive, using the female partner's age.
- Gender dysphoria is an alternative glossary definition, not a waiver of the
  benefit's other eligibility requirements.
- The eligibility table supplies the covered patient/partner configurations;
  an unlisted configuration does not establish eligibility for this benefit.
- Timed intercourse, frequent intercourse, and donor-insemination counts are
  separate facts; the table's express alternatives do not replace the glossary.
- FSH recency uses calendar months. Only tests on or before service count.
  Tied most-recent results must all satisfy the applicable threshold.
- At age 40 or older, the FSH threshold applies to every test taken on or
  after the 40th birthday, including the latest such test. A recent test is
  independently required; the text does not require a post-40 test to exist.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

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

    # READING: "You or your partner has not had a voluntary sterilization"
    # excludes sterilization of either member of the couple. No partner means
    # there is no partner sterilization fact to establish.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: "There exists a condition" that is demonstrated and documented,
    # together with "You or your partner does not have infertility ... due to a
    # natural physiologic process", requires the documented condition to be
    # non-natural; unknown conditions do not establish eligibility.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    age = h.patient_age(claim) if sex == "female" else None
    female_partner_age = claim.get("age_of_patients_female_partner")
    if sex == "female" and (age is None or age < 0):
        return False
    if sex == "male" and partner == "female":
        if female_partner_age is None or female_partner_age < 0:
            return False

    # READING: The glossary's "For an individual or their partner who has been
    # clinically diagnosed with gender dysphoria" is an independent way to meet
    # the definition of infertility, but does not waive the eligibility table.
    glossary_infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not glossary_infertile:
        if sex == "female":
            months_or_cycles = 12 if age < 35 else 6
            if partner == "male":
                glossary_infertile = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    months_or_cycles,
                )
            else:
                glossary_infertile = at_least(
                    "num_cycles_donor_insemination", months_or_cycles
                )
        elif partner == "female":
            # READING: The glossary's "failure to become pregnant" and
            # "For a female with a male partner" describe the couple's failure
            # to conceive. Apply that criterion to the female partner of the
            # table's "A male of any age with a female partner" as well.
            glossary_infertile = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                12 if female_partner_age < 35 else 6,
            )
        else:
            # READING: "At least 2 abnormal semen analyses obtained at least
            # 2 weeks apart" requires two dated analyses separated by >=14 days.
            analyses = claim.get("abnormal_semen_analyses")
            if analyses is not None:
                try:
                    service_date = parse_date(claim["date_service_received"])
                    dates = [
                        parse_date(d)
                        for d in analyses
                        if parse_date(d) <= service_date
                    ]
                    glossary_infertile = (
                        len(dates) >= 2
                        and (max(dates) - min(dates)).days >= 14
                    )
                except (KeyError, TypeError, ValueError):
                    return False

    if not glossary_infertile:
        return False

    # READING: "You have met the requirement ...", followed by the table's
    # "You are" rows, makes those rows the eligibility configurations for this
    # benefit. The glossary alone does not add an unlisted table row.
    if sex == "male":
        if partner != "female":
            return False
        # READING: The male rows say "12 months or more" / "6 months or more"
        # under timed intercourse, and donor insemination "Does not apply".
        return at_least(
            "num_months_timed_unprotected_intercourse",
            12 if female_partner_age < 35 else 6,
        )

    required = 12 if age < 35 else 6

    # READING: For a female with a male partner, "A. ... or B." permits either
    # timed intercourse or donor cycles. Without a male partner, only donor
    # cycles qualify. These table facts are separate from the glossary's
    # "frequent, unprotected heterosexual sexual intercourse" requirement.
    table_attempts_met = at_least("num_cycles_donor_insemination", required)
    if partner == "male":
        table_attempts_met = table_attempts_met or at_least(
            "num_months_timed_unprotected_intercourse", required
        )
    if not table_attempts_met:
        return False

    tests = claim.get("day_3_fsh_tests")
    if tests is None:
        return False

    try:
        service_date = parse_date(claim["date_service_received"])
        dated_tests = []
        for level, date_string, time_string in tests:
            timestamp = datetime.strptime(
                date_string + " " + time_string, "%Y_%m_%d %H_%M"
            )
            if timestamp.date() <= service_date:
                dated_tests.append((timestamp, level, date_string))

        if not dated_tests:
            return False

        latest_timestamp = max(test[0] for test in dated_tests)
        latest_tests = [
            test for test in dated_tests if test[0] == latest_timestamp
        ]

        # READING: "within the past" excludes future tests and includes the
        # calendar-month boundary. "Most recent lab test" is ordered by date
        # and time; tied results must all pass rather than selecting one.
        if not h.months_at_most(
            latest_tests[0][2],
            claim["date_service_received"],
            required,
        ):
            return False

        if age < 40:
            return all(level < 19 for _, level, _ in latest_tests)

        # READING: "less than 19 ... in all prior tests performed after age 40"
        # includes the latest test and all tests on or after the 40th birthday.
        # Unlike the under-40 rule, it does not apply the threshold to a
        # pre-40 test. The separate recent-test requirement still applies;
        # no additional nonempty post-40 history requirement is stated.
        post_40_tests = h.fsh_tests_since_age_40(claim)
        return all(
            level < 19
            for level, date_string, _ in post_40_tests
            if parse_date(date_string) <= service_date
        )
    except (KeyError, TypeError, ValueError):
        return False
