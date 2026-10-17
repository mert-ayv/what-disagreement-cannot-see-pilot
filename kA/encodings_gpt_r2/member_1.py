"""
READING choices:
1. Sterilization: the disjunctive wording permits eligibility when either
   actual member of the couple is affirmatively known not to be sterilized.
2. Natural physiology: a documented natural physiologic cause is disqualifying;
   an unaffected partner is not inferred from silence.
3. Couple infertility: the glossary's female-with-male failure-to-conceive
   definition also applies to the male member of that couple.
4. Gender dysphoria independently establishes glossary infertility, but does
   not waive an applicable eligibility-table requirement.
5. Table alternatives do not replace the separate glossary definition.
6. Table requirements apply only to the populations for which they are stated;
   no months or FSH threshold is invented for an unlisted population.
7. Exact time-window boundaries are included; future tests are not considered.
8. Equally most-recent FSH results below age 40 are resolved favourably.
9. At age 40 or older, all available tests performed at age 40 or older must
   pass; pre-40 results are not subject to that threshold.
Unknown facts are not treated as affirmative evidence of eligibility.
"""


def covered_under_benefit(claim: dict, h) -> bool:
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

    # READING: Sterilization -- "You or your partner has not had a voluntary
    # sterilization" is read disjunctively: an affirmative "no" for either
    # actual person suffices. A nonexistent partner supplies no such fact.
    not_sterilized = (
        claim.get("patient_has_had_voluntary_sterilization") == "no"
    )
    if partner != "no_partner":
        not_sterilized = not_sterilized or (
            claim.get("partner_has_had_voluntary_sterilization") == "no"
        )
    if not not_sterilized:
        return False

    # READING: Natural physiology -- "There exists a condition" causing
    # infertility and "does not have infertility that is due to a natural
    # physiologic process" require a documented nonnatural cause. The single
    # supplied cause field does not establish a separate unaffected partner.
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

    def at_least(field, threshold):
        value = claim.get(field)
        return value is not None and value >= threshold

    age = None
    threshold = None
    if sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False
        threshold = 12 if age < 35 else 6
    elif partner == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False
        threshold = 12 if partner_age < 35 else 6

    # READING: Gender dysphoria -- the glossary independently includes
    # "an individual or their partner who has been clinically diagnosed with
    # gender dysphoria." This establishes glossary infertility, not a waiver
    # of the separately stated eligibility requirements below.
    glossary_infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not glossary_infertile:
        if sex == "female" and partner == "male":
            glossary_infertile = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                threshold,
            )
        elif sex == "female":
            glossary_infertile = at_least(
                "num_cycles_donor_insemination", threshold
            )
        elif partner == "female":
            # READING: Couple infertility -- "failure to become pregnant"
            # and "For a female with a male partner" describe the couple's
            # unsuccessful conception history. Apply that definition to its
            # male member too, harmonizing it with the explicit table rows
            # for "A male of any age with a female partner".
            glossary_infertile = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                threshold,
            )
        else:
            analyses = claim.get("abnormal_semen_analyses")
            if analyses is not None and len(analyses) >= 2:
                dates = sorted(analyses)
                glossary_infertile = (
                    h.days_between(dates[0], dates[-1]) >= 14
                )

    if not glossary_infertile:
        return False

    # READING: Independent glossary and table requirements -- the table's
    # "A. ... or B." permits either table route for a female with a male
    # partner. It does not rewrite the glossary's separately stated
    # "frequent, unprotected heterosexual sexual intercourse" requirement.
    if sex == "female":
        donor_route = at_least("num_cycles_donor_insemination", threshold)
        if partner == "male":
            timed_route = at_least(
                "num_months_timed_unprotected_intercourse", threshold
            )
            if not (timed_route or donor_route):
                return False
        elif not donor_route:
            return False
    elif partner == "female":
        if not at_least(
            "num_months_timed_unprotected_intercourse", threshold
        ):
            return False

    # READING: Unlisted populations -- "the requirement for the number of
    # months" and "the following criteria" refer to the table's specified
    # populations. No numeric months or FSH requirement is supplied for a
    # male without a female partner; none is invented. Male-with-female
    # rows expressly say FSH "Does not apply".
    if sex == "male":
        return True

    service_date = claim.get("date_service_received")
    tests = claim.get("day_3_fsh_tests")
    if service_date is None or not tests:
        return False

    # READING: Test timing -- "within the past" excludes tests after service;
    # "within the past" 6 or 12 months includes the exact calendar boundary.
    prior_tests = [test for test in tests if test[1] <= service_date]
    window = 12 if age < 35 else 6
    if not any(
        h.months_at_most(test[1], service_date, window)
        for test in prior_tests
    ):
        return False

    if age < 40:
        latest_timestamp = max(
            (test[1], test[2]) for test in prior_tests
        )
        # READING: Tied latest results -- "less than 19 mIU/mL in your most
        # recent lab test" does not choose among simultaneous tests. A passing
        # test tied for most recent satisfies this singular-test requirement.
        return any(
            test[0] < 19
            for test in prior_tests
            if (test[1], test[2]) == latest_timestamp
        )

    # READING: Age-40 history -- "If you are age 40 and older" and "in all
    # prior tests performed after age 40" apply the threshold to every test
    # performed at age 40 or older through service, including tied results.
    # Unlike the under-40 rule, this does not require a pre-40 recent result
    # to pass, nor invent a requirement that a post-40 test already exist.
    return all(
        test[0] < 19
        for test in h.fsh_tests_since_age_40(claim)
        if test[1] <= service_date
    )
