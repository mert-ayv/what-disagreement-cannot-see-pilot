"""
READING choices:
- The glossary and the eligibility table impose cumulative requirements.
- Gender dysphoria satisfies the glossary, but does not waive eligibility rules.
- The table supplies the eligible patient/partner configurations; an unlisted
  configuration does not qualify.
- The glossary does not supply an ordinary infertility route for a male with
  a female partner; the gender-dysphoria route remains available.
- Neither the patient nor an existing partner may have been voluntarily
  sterilized. Natural-physiologic infertility is excluded.
- Donor insemination is an alternative to timed intercourse only where the
  table expressly provides that alternative.
- FSH testing is assessed as of service, using chronological recency. All
  results tied for most recent must pass when the most-recent-test rule applies.
- At age 40 or older, every available result on or after the 40th birthday
  must pass, including results outside the six-month recency window. The text
  does not separately require a test after the 40th birthday.
- Unknown facts cannot establish a required condition; a known alternative
  may nevertheless establish a disjunctive requirement.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, minimum):
        value = claim.get(field)
        return isinstance(value, int) and value >= minimum

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner not in {"male", "female", "no_partner"}:
        return False

    # READING: "You or your partner has not had a voluntary sterilization"
    # is a couple-wide exclusion: neither person may have had one. An absent
    # partner needs no sterilization finding; an existing partner does.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if (
        partner != "no_partner"
        and claim.get("partner_has_had_voluntary_sterilization") != "no"
    ):
        return False

    # READING: "You or your partner does not have infertility that is due to
    # a natural physiologic process" excludes any of the listed natural
    # causes, rather than permitting coverage because the other person lacks
    # such a cause. "Other" is the interface's documented non-natural category.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    # READING: "You have met the requirement for the number of months" and
    # the table's "You are" categories make the table exhaustive. In
    # particular, a male without a female partner has no qualifying row,
    # even if two abnormal semen analyses establish glossary infertility.
    if sex == "male":
        if partner != "female":
            return False
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int) or partner_age < 0:
            return False
        required = 12 if partner_age < 35 else 6
        age = None
    else:
        try:
            age = h.patient_age(claim)
        except (KeyError, TypeError, ValueError, OverflowError):
            return False
        if age is None or age < 0:
            return False
        required = 12 if age < 35 else 6

    # READING: The table expressly says "A. ... or B." for females with a
    # male partner. Donor cycles therefore substitute for timed intercourse
    # in those rows, but not in the male rows, where cycles "Does not apply".
    if sex == "male":
        table_attempts_met = at_least(
            "num_months_timed_unprotected_intercourse", required
        )
    elif partner == "male":
        table_attempts_met = (
            at_least("num_months_timed_unprotected_intercourse", required)
            or at_least("num_cycles_donor_insemination", required)
        )
    else:
        table_attempts_met = at_least(
            "num_cycles_donor_insemination", required
        )
    if not table_attempts_met:
        return False

    # READING: The glossary's "A disease defined by the failure to become
    # pregnant" and the benefit's "You are eligible ... if" are cumulative.
    # Thus table-qualifying donor cycles do not replace the glossary's
    # intercourse requirement for a female with a male partner.
    #
    # READING: "For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria" is an independent glossary route,
    # not a waiver of the table or the other eligibility requirements.
    glossary_met = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )
    if not glossary_met and sex == "female":
        if partner == "male":
            glossary_met = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )
        else:
            glossary_met = at_least(
                "num_cycles_donor_insemination", required
            )

    # READING: The glossary specifies "For a male without a female partner"
    # but supplies no corresponding ordinary route for a male with a female
    # partner. Do not extend the female patient's glossary route to him;
    # he must qualify through the expressly stated gender-dysphoria route.
    if not glossary_met:
        return False

    if sex == "male":
        # Both male table rows mark FSH testing "Does not apply".
        return True

    try:
        service_date_text = claim["date_service_received"]
        service_date = parse_date(service_date_text)
        raw_tests = claim["day_3_fsh_tests"]
        if not isinstance(raw_tests, list):
            return False

        applicable_tests = []
        for test in raw_tests:
            level, test_date_text, test_time_text = test
            test_date = parse_date(test_date_text)
            test_time = datetime.strptime(test_time_text, "%H_%M").time()
            if not isinstance(level, int):
                return False

            # READING: A test "done within the past" and "prior tests" are
            # assessed as of service. Later tests neither establish nor
            # defeat eligibility for this claim.
            if test_date <= service_date:
                applicable_tests.append(
                    (datetime.combine(test_date, test_time), test)
                )

        if not applicable_tests:
            return False

        most_recent = max(stamp for stamp, _ in applicable_tests)
        tied_latest = [
            test for stamp, test in applicable_tests if stamp == most_recent
        ]
        recency_months = 12 if age < 35 else 6
        if not h.months_at_most(
            tied_latest[0][1], service_date_text, recency_months
        ):
            return False

        if age < 40:
            # READING: "less than 19 ... in your most recent lab test"
            # means chronological recency, not list order. When several
            # results share that timestamp, every tied result must pass.
            return all(level < 19 for level, _, _ in tied_latest)

        # READING: "age 40 and older" and "all prior tests performed after
        # age 40" include the 40th birthday and every subsequent test through
        # service, not merely tests in the six-month window.
        historical_claim = dict(claim)
        historical_claim["day_3_fsh_tests"] = [
            test for _, test in applicable_tests
        ]
        since_40 = h.fsh_tests_since_age_40(historical_claim)

        # READING: "done within the past ... 6 months" requires a recent
        # test, while "all prior tests performed after age 40" limits which
        # results must be below 19. Neither phrase separately requires a
        # post-birthday test or applies this threshold to pre-40 results.
        return all(level < 19 for level, _, _ in since_40)

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
