"""
READING choices:
- “You or your partner has not had a voluntary sterilization” is read
  disjunctively: either person's confirmed absence of voluntary sterilization
  suffices. A nonexistent partner cannot supply that fact.
- The glossary's female-with-male-partner definition can establish infertility
  for the male member through his female partner.
- The glossary's gender-dysphoria definition independently establishes
  infertility, but does not waive applicable eligibility-table requirements.
- Table rows impose requirements only on the populations they describe.
  For populations without a row, the glossary still applies.
- Donor insemination is an alternative to timed intercourse where the table
  expressly says “or”; it does not independently replace the glossary's
  intercourse requirement for a female with a male partner.
- “Most recent lab test” permits a qualifying result among tests tied for the
  latest timestamp.
- At age 40 or older, the table's all-tests-since-40 rule replaces the
  most-recent-result threshold, but not the requirement for a recent test.
- Tests and semen analyses used to establish eligibility must have occurred
  by the service date. “Within the past” includes the stated boundary.
- Unknown facts do not establish requirements; a known sufficient alternative
  can nevertheless establish a disjunction.
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

    # READING: “You or your partner has not had a voluntary sterilization”
    # permits either person's confirmed negative history to satisfy the clause.
    # With no partner, only the patient's history can satisfy it.
    if not (
        claim.get("patient_has_had_voluntary_sterilization") == "no"
        or (
            partner != "no_partner"
            and claim.get("partner_has_had_voluntary_sterilization") == "no"
        )
    ):
        return False

    # The supplied condition field establishes both demonstration/documentation
    # and whether infertility is attributable to a natural physiologic process.
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

    patient_age = h.patient_age(claim) if sex == "female" else None
    female_partner_age = claim.get("age_of_patients_female_partner")
    service_date_string = claim.get("date_service_received")
    service_date = (
        parse_date(service_date_string) if service_date_string is not None else None
    )

    # Establish infertility under the glossary.
    # READING: “For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria” independently establishes glossary
    # infertility; it does not say that table requirements are waived.
    infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not infertile:
        if sex == "female":
            if patient_age is None:
                return False
            required = 12 if patient_age < 35 else 6
            if partner == "male":
                infertile = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    required,
                )
            else:
                infertile = at_least("num_cycles_donor_insemination", required)

        elif partner == "female":
            # READING: The disease is “failure to become pregnant,” including
            # “For a female with a male partner.” Apply that definition to the
            # male member's female partner, rather than excluding male members
            # whom the eligibility table expressly includes.
            if female_partner_age is None:
                return False
            required = 12 if female_partner_age < 35 else 6
            infertile = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )

        else:
            # READING: “At least 2 abnormal semen analyses obtained at least
            # 2 weeks apart” requires a qualifying pair, not that every pair
            # of analyses be separated by two weeks.
            analyses = claim.get("abnormal_semen_analyses")
            if analyses is not None and service_date is not None:
                eligible_dates = [
                    d for d in analyses if parse_date(d) <= service_date
                ]
                if len(eligible_dates) >= 2:
                    infertile = (
                        h.days_between(min(eligible_dates), max(eligible_dates))
                        >= 14
                    )

    if not infertile:
        return False

    # Apply every requirement of the applicable table row.
    if sex == "female":
        if patient_age is None:
            return False

        required = 12 if patient_age < 35 else 6
        donor_requirement_met = at_least(
            "num_cycles_donor_insemination", required
        )

        if partner == "male":
            # READING: The table expressly allows intercourse “or” donor
            # insemination. This alternative applies to the table, not to the
            # glossary's separate female-with-male-partner definition.
            trying_requirement_met = (
                at_least("num_months_timed_unprotected_intercourse", required)
                or donor_requirement_met
            )
        else:
            trying_requirement_met = donor_requirement_met

        if not trying_requirement_met:
            return False

        tests = claim.get("day_3_fsh_tests")
        if tests is None or service_date is None:
            return False

        # READING: “within the past” and “prior tests” refer to tests already
        # performed by the service date, not future tests.
        prior_tests = [
            test for test in tests if parse_date(test[1]) <= service_date
        ]
        if not prior_tests:
            return False

        recency_months = 12 if patient_age < 35 else 6
        # READING: “within the past” includes the exact calendar-month boundary.
        if not any(
            h.months_at_most(test[1], service_date_string, recency_months)
            for test in prior_tests
        ):
            return False

        if patient_age < 40:
            latest_timestamp = max((test[1], test[2]) for test in prior_tests)
            # READING: “your most recent lab test” does not choose between
            # simultaneous tests; a qualifying test at the latest timestamp
            # suffices.
            if not any(
                level < 19 and (date, time) == latest_timestamp
                for level, date, time in prior_tests
            ):
                return False
        else:
            # READING: “If you are age 40 and older ... in all prior tests
            # performed after age 40” replaces the younger-age result rule.
            # A recent test remains necessary, but a pre-40 result need not
            # satisfy a threshold applying only to tests at age 40 or older.
            tests_since_40 = [
                test
                for test in h.fsh_tests_since_age_40(claim)
                if parse_date(test[1]) <= service_date
            ]
            if any(level >= 19 for level, _, _ in tests_since_40):
                return False

    elif partner == "female":
        if female_partner_age is None:
            return False
        required = 12 if female_partner_age < 35 else 6
        if not at_least("num_months_timed_unprotected_intercourse", required):
            return False

    else:
        # READING: The table describes males “with a female partner,” but no
        # row describes a male without one. Do not invent a table waiting
        # period or FSH requirement for that population; require the glossary
        # and the general eligibility conditions already checked above.
        pass

    return True
