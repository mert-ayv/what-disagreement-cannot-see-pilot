"""Coverage readings:
- Eligibility requirements are cumulative; the table's patient categories are exhaustive.
- The glossary is applied independently, including its patient-specific categories.
- Neither member of an existing couple may have had voluntary sterilization.
- Infertility from any natural physiologic process is excluded.
- Donor insemination does not replace the glossary's intercourse requirement.
- FSH testing is assessed as of service, with all tied latest results controlling.
- At age 40 or older, every available post-40 FSH result must pass.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    from datetime import datetime

    def parse_date(value):
        return datetime.strptime(value, "%Y_%m_%d").date()

    def at_least(field, minimum):
        value = claim.get(field)
        return isinstance(value, int) and not isinstance(value, bool) and value >= minimum

    if claim.get("service_type") not in {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")

    # READING: Exhaustive table — "You are" introduces the listed categories.
    # A patient must fit a listed row; a glossary diagnosis alone does not
    # establish the table's separate eligibility requirements.
    if sex == "female" and partner in {"male", "female", "no_partner"}:
        age = h.patient_age(claim)
        if age is None:
            return False
        required = 12 if age < 35 else 6
    elif sex == "male" and partner == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        if not isinstance(partner_age, int) or isinstance(partner_age, bool):
            return False
        required = 12 if partner_age < 35 else 6
        age = None
    else:
        return False

    # READING: Sterilization — "You or your partner has not had a voluntary
    # sterilization" excludes sterilization of either member of an existing
    # couple, rather than allowing coverage whenever just one has not had it.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    if partner != "no_partner":
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # READING: Natural causes — "a natural physiologic process such as age
    # related ovarian insufficiency" is illustrative, not limited to ovaries.
    # Only the documented non-natural category can establish this requirement.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    if claim.get(
        "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
    ) != "no":
        return False

    # READING: Independent glossary — "A disease defined by" supplies an
    # additional definition, not one displaced by the eligibility table.
    # Its "For a female ..." clauses apply to the female patient, not by
    # attribution to a male patient's female partner. The glossary supplies
    # no ordinary male-with-female-partner route; such a patient can satisfy
    # it here only through the express gender-dysphoria clause.
    glossary_met = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )
    if sex == "female":
        if partner == "male":
            glossary_met = glossary_met or at_least(
                "num_months_frequent_unprotected_heterosexual_intercourse",
                required,
            )
        else:
            glossary_met = glossary_met or at_least(
                "num_cycles_donor_insemination", required
            )

    if not glossary_met:
        return False

    # READING: Cumulative requirements — "You are eligible ... if" and
    # "You have met the requirement" require the applicable table threshold
    # even when the glossary is satisfied by gender dysphoria.
    if sex == "female":
        if partner == "male":
            table_contact_met = (
                at_least("num_months_timed_unprotected_intercourse", required)
                or at_least("num_cycles_donor_insemination", required)
            )
        else:
            table_contact_met = at_least(
                "num_cycles_donor_insemination", required
            )
    else:
        table_contact_met = at_least(
            "num_months_timed_unprotected_intercourse", required
        )

    # READING: Donor alternative — the table's "or ... donor insemination"
    # is an alternative only within the table. It does not replace the
    # glossary's "frequent, unprotected heterosexual sexual intercourse"
    # requirement for a female with a male partner.
    if not table_contact_met:
        return False

    # The male rows explicitly make FSH testing inapplicable.
    if sex == "male":
        return True

    raw_tests = claim.get("day_3_fsh_tests")
    service_string = claim.get("date_service_received")
    if not raw_tests or service_string is None:
        return False

    try:
        service_date = parse_date(service_string)
        tests = []
        for level, test_date, test_time in raw_tests:
            timestamp = datetime.strptime(
                test_date + " " + test_time, "%Y_%m_%d %H_%M"
            )

            # READING: Temporal assessment — "within the past" and "prior
            # tests" refer to the service date; later tests cannot establish
            # eligibility for this claim.
            if timestamp.date() <= service_date:
                tests.append((level, test_date, timestamp))

        if not tests:
            return False

        latest_timestamp = max(test[2] for test in tests)
        latest_tests = [
            test for test in tests if test[2] == latest_timestamp
        ]
        latest_date_string = latest_tests[0][1]
        recency_months = 12 if age < 35 else 6

        if not h.months_at_most(
            latest_date_string, service_string, recency_months
        ):
            return False

        if age < 40:
            # READING: Tied latest results — "less than 19 ... in your most
            # recent lab test" requires every equally most-recent result
            # to pass; a favorable tied result cannot erase an adverse one.
            return all(level < 19 for level, _, _ in latest_tests)

        # READING: Age-40 history — "less than 19 ... in all prior tests
        # performed after age 40" includes the latest test if performed at
        # age 40 or older, not merely tests preceding that latest test.
        # The separate recent-test requirement still applies. The text does
        # not require that recent test itself to have occurred after age 40.
        for level, test_date, test_time in h.fsh_tests_since_age_40(claim):
            timestamp = datetime.strptime(
                test_date + " " + test_time, "%Y_%m_%d %H_%M"
            )
            if timestamp.date() <= service_date and not level < 19:
                return False

        return True

    except (TypeError, ValueError, OverflowError):
        return False
