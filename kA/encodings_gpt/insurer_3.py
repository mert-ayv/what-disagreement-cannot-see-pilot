"""Comprehensive infertility coverage using the supplied claim interface.

Plan enrollment is assumed: the interface supplies no enrollment-status field.

READING choices:
- Glossary infertility and benefit-specific eligibility are cumulative.
- The glossary's intercourse requirement applies to the female member of a
  male/female couple, including when the male partner is the claimant.
- Both members of a couple must be free of voluntary sterilization.
- The table is exhaustive; glossary gender dysphoria does not waive it.
- Donor cycles must be self-paid or otherwise not paid for by the plan.
- FSH evidence is evaluated as of service; tied latest results must all pass.
- At age 40 or older, every available post-40 FSH result must pass, including
  the latest result.
- Unknown required facts do not establish coverage.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, minimum):
        value = claim.get(field)
        return isinstance(value, int) and value >= minimum

    # READING: Unknown facts — "You are eligible ... if" makes the listed
    # requirements affirmative conditions; an unknown required fact does not
    # establish that a condition has been met.
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

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" excludes the couple if either member has had one; it
    # does not suffice that just one member has avoided sterilization.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # READING: Natural causes — "You or your partner does not have infertility
    # that is due to a natural physiologic process" excludes any of the
    # supplied natural-process causes, not just the examples of menopause.
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

    # READING: Exhaustive table — "You have met the requirement for the number
    # of months" and "meets the following criteria" require an applicable
    # table row. The glossary's gender-dysphoria alternative defines
    # infertility but does not waive these additional eligibility conditions.
    if sex == "female":
        age = h.patient_age(claim)
        if age is None or age < 0:
            return False
        minimum = 12 if age < 35 else 6

        donor_ok = at_least("num_cycles_donor_insemination", minimum)
        # READING: Donor financing — "Self paid/not paid for by plan" limits
        # qualifying cycles to the cycles described by the interface field.
        if partner == "male":
            table_attempts_ok = (
                at_least("num_months_timed_unprotected_intercourse", minimum)
                or donor_ok
            )
        else:
            table_attempts_ok = donor_ok

    elif partner == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int) or partner_age < 0:
            return False
        minimum = 12 if partner_age < 35 else 6
        table_attempts_ok = at_least(
            "num_months_timed_unprotected_intercourse", minimum
        )
    else:
        return False

    if not table_attempts_ok:
        return False

    # READING: Cumulative definitions — "A disease defined by the failure to
    # become pregnant" is additional to the table. In particular, its
    # intercourse requirement is not replaced by the table's donor-cycle
    # alternative for a female with a male partner.
    glossary_ok = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if sex == "female":
        if partner == "male":
            glossary_ok = glossary_ok or at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                minimum,
            )
        else:
            glossary_ok = glossary_ok or donor_ok
    else:
        # READING: Couple infertility — "For a female with a male partner"
        # describes the female partner's failure to become pregnant when the
        # claimant is male, consistent with the table's express male rows.
        glossary_ok = glossary_ok or at_least(
            "num_months_frequent_unprotected_heterosexual_intercourse",
            minimum,
        )

    if not glossary_ok:
        return False

    if sex == "male":
        # The applicable male rows explicitly say FSH "Does not apply".
        return True

    try:
        service_date = parse_date(claim["date_service_received"])
        tests = claim.get("day_3_fsh_tests")
        if not isinstance(tests, list):
            return False

        dated_tests = []
        for level, date_string, time_string in tests:
            test_date = parse_date(date_string)
            test_time = datetime.strptime(time_string, "%H_%M").time()
            # READING: Timing — a test "done within the past" must have
            # occurred on or before service; later tests cannot qualify or
            # disqualify this claim.
            if test_date <= service_date:
                dated_tests.append(
                    (datetime.combine(test_date, test_time), level, date_string)
                )

        if not dated_tests:
            return False

        latest_timestamp = max(test[0] for test in dated_tests)
        lookback = 12 if age < 35 else 6
        if not h.months_at_most(
            latest_timestamp.date().strftime("%Y_%m_%d"),
            claim["date_service_received"],
            lookback,
        ):
            return False

        if age < 40:
            # READING: Tied results — "less than 19 ... in your most recent
            # lab test" requires every result tied for most recent to pass;
            # a favorable result cannot be selected from simultaneous tests.
            return all(
                level < 19
                for timestamp, level, _ in dated_tests
                if timestamp == latest_timestamp
            )

        # READING: Age 40 threshold — "less than 19 ... in all prior tests
        # performed after age 40" includes all tests from the 40th birthday
        # through service, including the most recent qualifying test, rather
        # than allowing a failed latest test or ignoring earlier failures.
        post_40_tests = h.fsh_tests_since_age_40(claim)
        qualifying_post_40 = [
            (level, date_string, time_string)
            for level, date_string, time_string in post_40_tests
            if parse_date(date_string) <= service_date
        ]
        return bool(qualifying_post_40) and all(
            level < 19 for level, _, _ in qualifying_post_40
        )

    except (KeyError, TypeError, ValueError, OverflowError):
        return False
