"""
READING choices:
1. Unknown facts cannot establish a required condition; independent alternatives
   may establish eligibility without resolving every unknown field.
2. Neither the patient nor an existing partner may have undergone voluntary
   sterilization. A nonexistent partner needs no sterilization history.
3. The documented condition must not be a natural physiologic cause.
4. The glossary and the eligibility table are cumulative requirements.
5. A male with a female partner can satisfy the glossary through the couple's
   failure to conceive, using the female partner's age.
6. A claimant must fit a table row. Gender dysphoria and abnormal semen analyses
   establish glossary infertility but do not waive the table requirements.
7. Timed intercourse and frequent heterosexual intercourse are separate facts;
   neither is inferred from the other.
8. Female claimants without a male partner include those with a female partner.
9. Evidence is evaluated as of the service date; future FSH tests are ignored.
10. FSH recency is inclusive. Below age 40, every result tied for most recent
    must be below 19. At age 40 or older, every supplied test on or after the
    40th birthday must be below 19.
11. The age-40 rule does not independently require a post-40 test: a recent
    pre-40 test can satisfy recency when there are no post-40 tests.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def at_least(field, minimum):
        value = claim.get(field)
        return isinstance(value, int) and not isinstance(value, bool) and value >= minimum

    # READING: Unknown evidence — "You are eligible ... if" makes these
    # conditions requirements. Missing facts do not establish them, although
    # a known alternative can suffice without resolving other alternatives.
    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    if sex not in {"female", "male"}:
        return False
    if partner_sex not in {"female", "male", "no_partner"}:
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" is read as excluding sterilization in either person,
    # rather than allowing one person's negative history to excuse the other's.
    # "Your partner" imposes no history requirement when there is no partner.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner_sex != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # READING: Natural causes — "does not have infertility that is due to a
    # natural physiologic process such as" is illustrative, not restricted to
    # menopause. Only "other" establishes an allowed documented condition in
    # the supplied interface.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    # READING: Unlisted table categories — "You have met the requirement for
    # the number of months trying to conceive through egg and sperm contact"
    # and the table's "You are" rows require a matching row. The glossary's
    # "At least 2 abnormal semen analyses" and "clinically diagnosed with gender
    # dysphoria" define infertility; they do not supply or waive table criteria.
    if sex == "male" and partner_sex != "female":
        return False

    if sex == "female":
        age = h.patient_age(claim)
        if age is None or age < 0:
            return False
        minimum = 12 if age < 35 else 6

        # READING: Partner categories — "without a male partner" includes both
        # no partner and a female partner; it is not limited to being single.
        if partner_sex == "male":
            table_attempts_met = (
                at_least("num_months_timed_unprotected_intercourse", minimum)
                or at_least("num_cycles_donor_insemination", minimum)
            )
        else:
            table_attempts_met = at_least("num_cycles_donor_insemination", minimum)
    else:
        partner_age = claim.get("age_of_patients_female_partner")
        if (
            not isinstance(partner_age, int)
            or isinstance(partner_age, bool)
            or partner_age < 0
        ):
            return False
        minimum = 12 if partner_age < 35 else 6
        table_attempts_met = at_least(
            "num_months_timed_unprotected_intercourse", minimum
        )

    if not table_attempts_met:
        return False

    # READING: Cumulative criteria — "Infertile or infertility" defines the
    # disease, while "You are eligible ... if" adds eligibility conditions.
    # Thus donor cycles alone for a female with a male partner can meet the
    # table's "or" alternative without necessarily meeting the glossary.
    glossary_met = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    # READING: Male claimant with female partner — "A male of any age with a
    # female partner" expressly appears in the table. Apply the glossary's
    # "failure to become pregnant" and "For a female with a male partner"
    # thresholds to that couple, using the female partner's age.
    #
    # READING: Distinct intercourse facts — the table says "unprotected timed
    # sexual intercourse"; the glossary says "frequent, unprotected
    # heterosexual sexual intercourse". Require the respective supplied fact
    # for each, without inferring one from the other.
    if sex == "male" or partner_sex == "male":
        glossary_met = glossary_met or at_least(
            "num_months_frequent_unprotected_heterosexual_intercourse", minimum
        )
    else:
        glossary_met = glossary_met or at_least(
            "num_cycles_donor_insemination", minimum
        )

    if not glossary_met:
        return False

    # The male rows expressly mark FSH testing and results "Does not apply".
    if sex == "male":
        return True

    tests = claim.get("day_3_fsh_tests")
    if not isinstance(tests, list) or not tests:
        return False

    try:
        service_date = datetime.strptime(
            claim["date_service_received"], "%Y_%m_%d"
        ).date()
        dated_tests = []
        for level, test_date, test_time in tests:
            timestamp = datetime.strptime(
                test_date + " " + test_time, "%Y_%m_%d %H_%M"
            )

            # READING: Evidence timing — "within the past" and "all prior tests"
            # are evaluated on the service date. Later tests are not evidence
            # for this claim; tests on the service date are included.
            if timestamp.date() <= service_date:
                dated_tests.append((timestamp, (level, test_date, test_time)))
    except (KeyError, TypeError, ValueError):
        return False

    if not dated_tests:
        return False

    latest_timestamp = max(timestamp for timestamp, _ in dated_tests)
    latest_tests = [
        test for timestamp, test in dated_tests
        if timestamp == latest_timestamp
    ]
    recency_months = 12 if age < 35 else 6

    # READING: Recency — "within the past" 12 or 6 months includes the exact
    # calendar-month boundary. The latest test establishes whether any test
    # satisfies that recency requirement.
    if not h.months_at_most(
        latest_tests[0][1], claim["date_service_received"], recency_months
    ):
        return False

    if age < 40:
        # READING: Tied latest results — "less than 19 mIU/mL in your most recent
        # lab test" does not rank simultaneous tests. Require every tied latest
        # result to pass rather than arbitrarily selecting a favorable result.
        return all(level < 19 for level, _, _ in latest_tests)

    # READING: Age-40 boundary — "age 40 and older" and "all prior tests
    # performed after age 40" mean tests on or after the 40th birthday,
    # including the latest test if it falls in that period.
    evidence_claim = dict(claim)
    evidence_claim["day_3_fsh_tests"] = [
        test for _, test in dated_tests
    ]
    tests_since_40 = h.fsh_tests_since_age_40(evidence_claim)

    # READING: No post-40 tests — "all prior tests performed after age 40"
    # constrains that set without expressly requiring it to be nonempty.
    # A recent pre-40 test can therefore satisfy the separate recency rule;
    # do not import the under-40 "most recent lab test" result rule here.
    return all(level < 19 for level, _, _ in tests_since_40)
