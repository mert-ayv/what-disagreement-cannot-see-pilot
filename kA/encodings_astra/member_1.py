"""
READING choices:
- The sterilization clause's "or" is disjunctive: either applicable person's
  documented absence of voluntary sterilization satisfies that clause.
- Infertility may be established through the female partner's glossary criteria
  for a male with a female partner, consistent with the table's couple-based rows.
- Gender dysphoria is an alternative glossary route, not a waiver of an applicable
  table row. Rows absent from the table impose no invented waiting or FSH criteria.
- Glossary intercourse requirements and table intercourse requirements are
  distinct; the table's donor alternative does not rewrite the glossary.
- A passing result among equally recent FSH tests satisfies "most recent lab test"
  below age 40. At 40 or older, all tests obtained on or after the 40th birthday
  count, but no threshold is added for tests obtained before that birthday.
- Tests must have been obtained by the service date; same-day tests count.
- Unknown facts are not presumed favorable or unfavorable. Coverage requires
  establishing eligibility despite any unknown facts relevant to the decision.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def date_value(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, required):
        value = claim.get(field)
        return value is not None and value >= required

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    # The interface's condition field establishes both demonstration and
    # documentation. All other listed values expressly describe natural causes.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    service_date_text = claim.get("date_service_received")
    service_date = date_value(service_date_text) if service_date_text else None
    patient_age = h.patient_age(claim)

    def waiting_requirement(age):
        # If age is unknown, 12 meets either possible age-based requirement.
        return 6 if age is not None and age >= 35 else 12

    def semen_requirement_met():
        # READING: "At least 2 abnormal semen analyses obtained at least 2 weeks
        # apart" requires distinct qualifying dates, not consecutive analyses.
        # "Obtained" is assessed as of service; same-day evidence is allowed.
        if service_date is None:
            return False
        dates = [
            value
            for value in claim.get("abnormal_semen_analyses", [])
            if date_value(value) <= service_date
        ]
        return (
            len(dates) >= 2
            and h.days_between(min(dates), max(dates)) >= 14
        )

    def fsh_requirement_met():
        if service_date is None:
            return False

        # READING: A test "done within the past" must exist by service.
        # With no service time supplied, tests on the service date count.
        tests = [
            test
            for test in claim.get("day_3_fsh_tests", [])
            if date_value(test[1]) <= service_date
        ]
        if not tests:
            return False

        latest_stamp = max((test[1], test[2]) for test in tests)
        window = 12 if patient_age is not None and patient_age < 35 else 6
        if not h.months_at_most(
            latest_stamp[0], service_date_text, window
        ):
            return False

        if patient_age is None:
            # Establish the threshold under every possible age: this covers
            # both the latest-test rule and every possible post-40 test.
            return all(test[0] < 19 for test in tests)

        if patient_age < 40:
            # READING: "less than 19 ... in your most recent lab test" does not
            # resolve simultaneous tests. Any passing equally latest test
            # satisfies the singular requirement.
            return any(
                test[0] < 19
                for test in tests
                if (test[1], test[2]) == latest_stamp
            )

        # READING: "all prior tests performed after age 40" includes all tests
        # obtained by service on or after the 40th birthday. It does not impose
        # a threshold on pre-40 tests; the recent-test requirement still applies
        # even when no post-40 tests have yet been obtained.
        return all(
            test[0] < 19
            for test in h.fsh_tests_since_age_40(claim)
            if date_value(test[1]) <= service_date
        )

    def glossary_met(sex, partner):
        # READING: "For an individual or their partner who has been clinically
        # diagnosed with gender dysphoria" is an independent glossary route.
        # It does not remove the separate eligibility-table requirements.
        if claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes":
            return True

        if sex == "female":
            required = waiting_requirement(patient_age)
            if partner == "male":
                # READING: The glossary specifies "frequent, unprotected
                # heterosexual sexual intercourse"; the table's "timed"
                # intercourse and donor alternatives do not substitute for
                # this distinct glossary criterion.
                return at_least(
                    "num_months_frequent_unprotected_heterosexual_intercourse",
                    required,
                )
            return at_least("num_cycles_donor_insemination", required)

        if partner == "female":
            # READING: The glossary's "For a female with a male partner",
            # together with the table's "A male ... with a female partner",
            # permits the couple's failure to conceive to establish the male
            # patient's infertility using his female partner's age.
            required = waiting_requirement(
                claim.get("age_of_patients_female_partner")
            )
            return at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )

        return semen_requirement_met()

    def table_met(sex, partner):
        if sex == "female":
            required = waiting_requirement(patient_age)
            donor_met = at_least("num_cycles_donor_insemination", required)

            # READING: For a female with a male partner, "A ... or B" makes
            # donor insemination a genuine alternative to timed intercourse
            # for the table, though glossary eligibility remains separate.
            contact_met = donor_met or (
                partner == "male"
                and at_least(
                    "num_months_timed_unprotected_intercourse", required
                )
            )
            return contact_met and fsh_requirement_met()

        if partner == "female":
            required = waiting_requirement(
                claim.get("age_of_patients_female_partner")
            )
            return at_least(
                "num_months_timed_unprotected_intercourse", required
            )

        # READING: "met the requirement for the number of months" and FSH
        # "meets the following criteria" refer to the supplied table. There
        # is no row for a male without a female partner, despite that category
        # being expressly recognized in the glossary. No waiting or FSH
        # requirement is invented for that category.
        return True

    sexes = (
        [claim["sex_of_patient_trying_to_conceive"]]
        if "sex_of_patient_trying_to_conceive" in claim
        else ["female", "male"]
    )
    partners = (
        [claim["sex_of_patients_partner"]]
        if "sex_of_patients_partner" in claim
        else ["male", "female", "no_partner"]
    )

    # Unknown categorical facts must not make an otherwise unestablished
    # requirement pass. Check every category consistent with the known fields.
    for sex in sexes:
        for partner in partners:
            # READING: "You or your partner has not had a voluntary
            # sterilization" uses "or", not "neither ... nor". One applicable
            # person's explicit "no" suffices, even if the other's answer is
            # "yes" or unknown. A nonexistent partner cannot supply that fact.
            sterilization_met = (
                claim.get("patient_has_had_voluntary_sterilization") == "no"
                or (
                    partner != "no_partner"
                    and claim.get("partner_has_had_voluntary_sterilization") == "no"
                )
            )
            if not (
                sterilization_met
                and glossary_met(sex, partner)
                and table_met(sex, partner)
            ):
                return False

    return True
