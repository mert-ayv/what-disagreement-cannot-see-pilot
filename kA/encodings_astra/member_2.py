"""
READING choices:
- The negative sterilization clause is disjunctive: either person's known
  absence of voluntary sterilization suffices; a nonexistent partner does not.
- Infertility is evaluated at the couple level for a male with a female partner.
- Gender dysphoria independently satisfies the glossary, but does not waive
  applicable service-eligibility requirements.
- The table's donor-insemination alternatives do not erase the separate
  glossary requirement.
- Table requirements apply to the populations actually listed; no additional
  intercourse or FSH requirement is invented for males without female partners.
- Calendar-month boundaries are inclusive. Only tests through the service date
  count. A favorable result may be selected among equally recent tests where
  the policy requires only the singular most recent test.
- At age 40 or older, every test on or after the 40th birthday must qualify;
  a recent test before that birthday can satisfy the testing-recency requirement.
- Unknown facts are not assumed favorable or unfavorable. Coverage must be
  established across the applicable possibilities.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # READING: Documented cause and natural physiology — "There exists a
    # condition" documented to cause infertility, and "does not have infertility
    # that is due to a natural physiologic process." The supplied condition must
    # establish a qualifying, non-natural cause; silence proves neither fact.
    if (
        claim.get("demonstrated_and_documented_condition_causing_infertility")
        != "other"
    ):
        return False

    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_"
            "treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    def at_least(field, minimum):
        value = claim.get(field)
        return value is not None and value >= minimum

    # READING: Unknown facts — "You are eligible ... if" requires established
    # eligibility, not an assumption about an absent fact. For unknown sex or
    # partner category, require eligibility under every possible category.
    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    sexes = ("female", "male") if sex is None else (sex,)
    partners = ("male", "female", "no_partner") if partner is None else (partner,)

    if any(s not in ("female", "male") for s in sexes):
        return False
    if any(p not in ("male", "female", "no_partner") for p in partners):
        return False

    def sterilization_requirement_met(partner_category):
        # READING: Sterilization — "You or your partner has not had a voluntary
        # sterilization" is read disjunctively, rather than rewritten as
        # "neither you nor your partner." An actual partner's known "no" suffices.
        return (
            claim.get("patient_has_had_voluntary_sterilization") == "no"
            or (
                partner_category != "no_partner"
                and claim.get("partner_has_had_voluntary_sterilization") == "no"
            )
        )

    def semen_requirement_met():
        dates = claim.get("abnormal_semen_analyses")
        service_date = claim.get("date_service_received")
        if dates is None or service_date is None:
            return False
        dates = [
            date for date in dates
            if h.days_between(date, service_date) >= 0
        ]
        return any(
            abs(h.days_between(first, second)) >= 14
            for i, first in enumerate(dates)
            for second in dates[i + 1:]
        )

    def fsh_requirement_met(age):
        tests = claim.get("day_3_fsh_tests")
        service_date = claim.get("date_service_received")
        if tests is None or service_date is None:
            return False

        # READING: Temporal scope — a test "done within the past" must have
        # occurred by the service date; future results do not establish or
        # defeat eligibility for this claim.
        tests = [
            test for test in tests
            if h.days_between(test[1], service_date) >= 0
        ]
        if not tests:
            return False

        def timestamp(test):
            return datetime.strptime(
                test[1] + " " + test[2], "%Y_%m_%d %H_%M"
            )

        latest_time = max(map(timestamp, tests))
        latest = [test for test in tests if timestamp(test) == latest_time]

        # READING: Recency — "within the past" 12 or 6 months includes the
        # exact calendar-month boundary. With unknown age, six months satisfies
        # either possible window.
        window = 12 if age is not None and age < 35 else 6
        if not h.months_at_most(latest[0][1], service_date, window):
            return False

        if age is None:
            # Age is unknown: any recorded test could be an after-40 test.
            # Requiring all observed results below 19 establishes eligibility
            # under both the most-recent and all-after-40 readings.
            return all(test[0] < 19 for test in tests)

        if age < 40:
            # READING: Ties — "less than 19 ... in your most recent lab test"
            # is singular. When multiple tests are equally most recent, a
            # qualifying tied test may serve as that test.
            return any(test[0] < 19 for test in latest)

        # READING: Age 40 — "all prior tests performed after age 40" covers
        # tests from the 40th birthday through service. The separate requirement
        # for a recent test does not say that test must itself be after 40;
        # no additional post-birthday test is imposed when that set is empty.
        after_40 = [
            test for test in h.fsh_tests_since_age_40(claim)
            if h.days_between(test[1], service_date) >= 0
        ]
        return all(test[0] < 19 for test in after_40)

    def eligible_for_categories(patient_sex, partner_category):
        if not sterilization_requirement_met(partner_category):
            return False

        # READING: Gender dysphoria — "For an individual or their partner who
        # has been clinically diagnosed with gender dysphoria" is an independent
        # glossary route, but does not override "You are eligible ... if" or
        # any applicable row of the eligibility table.
        glossary_met = (
            claim.get("patient_or_partner_diagnosed_with_gender_dysphoria")
            == "yes"
        )

        if patient_sex == "female":
            age = h.patient_age(claim)
            # If age is unknown, 12 meets either possible trying threshold.
            required = 6 if age is not None and age >= 35 else 12
            donor_met = at_least("num_cycles_donor_insemination", required)
            timed_met = at_least(
                "num_months_timed_unprotected_intercourse", required
            )
            frequent_met = at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )

            if partner_category == "male":
                glossary_met = glossary_met or frequent_met

                # READING: Distinct requirements — the table says intercourse
                # "or" donor insemination, while the glossary's female-with-male
                # route says "frequent, unprotected heterosexual sexual
                # intercourse." Donor cycles satisfy the table alternative,
                # but do not alone establish that separate glossary route.
                trying_met = timed_met or donor_met
            else:
                glossary_met = glossary_met or donor_met
                trying_met = donor_met

            return (
                glossary_met
                and trying_met
                and fsh_requirement_met(age)
            )

        if partner_category == "female":
            # READING: Male with female partner — the glossary describes
            # "failure to become pregnant" for "a female with a male partner,"
            # and the table expressly includes "A male ... with a female
            # partner." Apply the couple's glossary duration using her age,
            # rather than excluding this expressly listed male population.
            partner_age = claim.get("age_of_patients_female_partner")
            required = (
                6 if partner_age is not None and partner_age >= 35 else 12
            )
            glossary_met = glossary_met or at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )
            return glossary_met and at_least(
                "num_months_timed_unprotected_intercourse", required
            )

        # READING: Unlisted table population — the glossary expressly includes
        # "a male without a female partner" after "At least 2 abnormal semen
        # analyses ... at least 2 weeks apart." No table row specifies months,
        # donor cycles, or FSH for that population, so none is invented.
        return glossary_met or semen_requirement_met()

    return all(
        eligible_for_categories(patient_sex, partner_category)
        for patient_sex in sexes
        for partner_category in partners
    )
