"""Comprehensive infertility benefit.

READING choices:
- The glossary's female-with-male-partner criteria apply to the female
  partner of a male claimant as well.
- Gender dysphoria independently satisfies the glossary, but does not
  waive an applicable eligibility-table requirement.
- Table requirements apply only to the categories actually listed.
- Donor insemination is an alternative to timed intercourse where the
  table expressly offers it, not an unstated glossary alternative.
- The sterilization provision is read disjunctively: either member of
  a couple may establish the negative condition.
- A documented natural physiologic cause fails the natural-process
  exclusion.
- Recency includes the boundary date; future tests are not evidence.
- Equally recent FSH results are resolved favourably to the member,
  except where the policy expressly requires all results to qualify.

Plan enrollment and the qualifying dependent relationship are background
scope conditions: the supplied interface has no fields representing them.
Unknown facts do not establish a requirement, although an independently
established alternative can do so.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def date_value(value):
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

    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        # READING: Natural causes — "infertility that is due to a natural
        # physiologic process such as" makes the examples nonexclusive.
        # Each named natural cause in the interface therefore fails.
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" is read as a disjunction, not as "neither ... nor".
    # Without a partner, only the patient's negative fact can establish it.
    sterilization_ok = (
        claim.get("patient_has_had_voluntary_sterilization") == "no"
        or (
            partner != "no_partner"
            and claim.get("partner_has_had_voluntary_sterilization") == "no"
        )
    )
    if not sterilization_ok:
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    service_date = claim.get("date_service_received")
    age = h.patient_age(claim) if sex == "female" else None

    def threshold_for_age(value):
        # Unknown age cannot establish the shorter waiting period.
        return 6 if value is not None and value >= 35 else 12

    # First establish infertility under the glossary.
    # READING: Gender dysphoria — "For an individual or their partner who
    # has been clinically diagnosed with gender dysphoria" is an independent
    # glossary route, without an additional conception-attempt requirement.
    infertile = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    if not infertile:
        if sex == "female":
            needed = threshold_for_age(age)
            if partner == "male":
                infertile = at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    needed,
                )
            else:
                infertile = at_least("num_cycles_donor_insemination", needed)

        elif partner == "female":
            # READING: Couple-based glossary — "For a female with a male
            # partner" is applied to this claimant's female partner. This
            # gives effect to the table's "A male ... with a female partner"
            # rows rather than making those rows usable only with dysphoria.
            needed = threshold_for_age(
                claim.get("age_of_patients_female_partner")
            )
            infertile = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                needed,
            )

        else:
            # READING: "a male without a female partner" includes a male
            # with a male partner as well as a male with no partner.
            analyses = claim.get("abnormal_semen_analyses")
            if analyses is not None and service_date is not None:
                usable = [
                    d for d in analyses
                    if date_value(d) <= date_value(service_date)
                ]
                infertile = any(
                    h.days_between(first, second) >= 14
                    for first in usable
                    for second in usable
                )

    if not infertile:
        return False

    # Now apply the eligibility table independently of the glossary.
    # READING: Table scope — "You are" introduces specified categories;
    # it does not say unlisted categories are excluded. In particular,
    # males without female partners have no table waiting-period or FSH
    # requirement, consistent with their express glossary route.
    if sex == "male":
        if partner != "female":
            return True
        needed = threshold_for_age(
            claim.get("age_of_patients_female_partner")
        )
        return at_least("num_months_timed_unprotected_intercourse", needed)

    needed = threshold_for_age(age)
    if partner == "male":
        # READING: Table alternatives — "A. ... or B. ... donor
        # insemination" permits either table route. It does not replace
        # the glossary's separately stated intercourse route.
        attempts_ok = (
            at_least("num_months_timed_unprotected_intercourse", needed)
            or at_least("num_cycles_donor_insemination", needed)
        )
    else:
        attempts_ok = at_least("num_cycles_donor_insemination", needed)

    # READING: Dysphoria and the table — "You have met the requirement"
    # and "Your ... FSH level meets" remain eligibility requirements even
    # when the glossary is satisfied through gender dysphoria.
    if not attempts_ok:
        return False

    tests = claim.get("day_3_fsh_tests")
    if service_date is None or not tests:
        return False

    # READING: Timing — "within the past" excludes future tests and includes
    # the stated calendar-month boundary.
    tests = [
        test for test in tests
        if date_value(test[1]) <= date_value(service_date)
    ]
    if not tests:
        return False

    latest_stamp = max((d, t) for _, d, t in tests)
    latest_results = [
        level for level, d, t in tests if (d, t) == latest_stamp
    ]

    # If age is unknown, six-month recency and all results below 19
    # establish compliance whichever age category actually applies.
    recency_months = 12 if age is not None and age < 35 else 6
    if not h.months_at_most(latest_stamp[0], service_date, recency_months):
        return False

    if age is None:
        return all(level < 19 for level, _, _ in tests)

    if age < 40:
        # READING: Tied results — "your most recent lab test" does not
        # distinguish tests with identical timestamps. A qualifying test
        # among those equally most recent is sufficient.
        return any(level < 19 for level in latest_results)

    # READING: Age 40+ — "less than 19 ... in all prior tests performed
    # after age 40" requires every historical result from age 40 onward,
    # including tied results, to qualify. It does not impose that limit
    # on pre-40 tests or require that a recent test itself be post-40.
    post_40_tests = h.fsh_tests_since_age_40(claim)
    return all(
        level < 19
        for level, d, _ in post_40_tests
        if date_value(d) <= date_value(service_date)
    )
