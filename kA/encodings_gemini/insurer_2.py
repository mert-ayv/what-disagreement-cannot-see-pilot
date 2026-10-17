"""
Policy reading choices:

# READING: Covered services under comprehensive infertility services
Text: "We will cover charges made by an infertility specialist for the following infertility services:
Ovulation induction cycle(s) with menotropins; Intrauterine insemination."
Reading: Only "intrauterine_insemination" and "ovulation_induction_cycle_with_menotropins" are covered.
All other services are not covered under this benefit.

# READING: Documented condition and natural physiologic process exclusion
Text: "There exists a condition that: Is demonstrated to cause the illness of infertility. Has been
recognized by your physician or infertility specialist and documented in your or your partner's medical
records." and "You or your partner does not have infertility that is due to a natural physiologic process
such as age related ovarian insufficiency (e.g. perimenopause, menopause)."
Reading: The field `demonstrated_and_documented_condition_causing_infertility` must be present and must equal
"other". A value indicating a natural physiologic process ("natural_menopause", "natural_perimenopause",
"natural_male_reproductive_aging", "other_natural_physiologic_process") or an absent/unknown condition results in denial.

# READING: Voluntary sterilization of patient and partner
Text: "You or your partner has not had a voluntary sterilization with or without surgical reversal,
regardless of post reversal results."
Reading: `patient_has_had_voluntary_sterilization` must be "no", and if a partner exists,
`partner_has_had_voluntary_sterilization` must be "no". If unknown/missing or "yes", coverage is denied.

# READING: Less costly treatment availability
Text: "A successful pregnancy cannot be attained through less costly treatment for which coverage is
available under this plan."
Reading: `successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan` must be
present and explicitly equal "no".

# READING: Male patient without a female partner
Text: The policy table provides criteria only for females (with or without a male partner) and males with
a female partner.
Reading: Although the glossary defines infertility for "a male without a female partner" through semen analyses,
the policy text requires that the claimant meet the table requirements for trying to conceive and FSH testing.
Because the table provides no category or criteria for a male without a female partner, such claims cannot meet
the policy eligibility requirements and are denied.

# READING: Heterosexual couples and intercourse requirements
Text: The glossary defines infertility for a female with a male partner as failure to become pregnant after
1 year (< 35) or 6 months (>= 35) of frequent, unprotected heterosexual sexual intercourse. The table requires
12 months or more (< 35) or 6 months or more (>= 35) of unprotected timed sexual intercourse.
Reading: For heterosexual couples, the female's age determines whether the threshold is 12 or 6 months.
In the absence of gender dysphoria, the glossary definition requires meeting the frequent intercourse threshold,
and the policy table requires meeting the timed intercourse threshold (or donor insemination cycles for female
patients). Both requirements must be satisfied. For a female with a male partner without gender dysphoria, donor
insemination does not satisfy the glossary definition of infertility.

# READING: Gender dysphoria diagnosis and table criteria
Text: The glossary lists diagnosis of gender dysphoria as establishing infertility, but the policy table contains
no exemption from the required months/cycles trying to conceive or FSH testing.
Reading: Gender dysphoria satisfies the glossary definition of infertility, but does not waive the table's
independent eligibility criteria for months/cycles of intercourse/insemination or FSH testing.

# READING: FSH test requirements for females age 40 and older
Text: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40."
and "You need to have an unmedicated day 3 FSH test done within the past: 6 months".
Reading: For female claimants age 40 or older, there must be at least one test performed after age 40 within
the past 6 months on or before the date of service, and all prior tests performed after age 40 (on or before
the date of service) must have a level strictly less than 19 mIU/mL.

# READING: Most recent FSH lab test tie-breaking
Text: "Must be less than 19 mIU/mL in your most recent lab test".
Reading: If multiple lab tests share the latest date and time, all tests at that timestamp must be strictly
less than 19 mIU/mL.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Covered services under comprehensive infertility services
    # Text: "We will cover charges made by an infertility specialist for the following infertility services:
    # Ovulation induction cycle(s) with menotropins; Intrauterine insemination."
    # Reading: Only these two specific services are covered; all others are denied.
    service = claim.get("service_type")
    if service not in ("intrauterine_insemination", "ovulation_induction_cycle_with_menotropins"):
        return False

    # READING: Documented condition and natural physiologic process exclusion
    # Text: "There exists a condition that: Is demonstrated to cause the illness of infertility.
    # Has been recognized by your physician or infertility specialist and documented in your or your partner’s
    # medical records." and "You or your partner does not have infertility that is due to a natural
    # physiologic process such as age related ovarian insufficiency (e.g. perimenopause, menopause)."
    # Reading: Must be present and equal "other"; natural physiologic processes or missing documentation result in denial.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # READING: Voluntary sterilization of patient and partner
    # Text: "You or your partner has not had a voluntary sterilization with or without surgical reversal,
    # regardless of post reversal results."
    # Reading: Both patient and (if present) partner must have "no" for voluntary sterilization.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    partner_sex = claim.get("sex_of_patients_partner")
    if partner_sex in ("male", "female"):
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False
    elif partner_sex != "no_partner":
        return False

    # READING: Less costly treatment availability
    # Text: "A successful pregnancy cannot be attained through less costly treatment for which coverage is
    # available under this plan."
    # Reading: Must be explicitly "no".
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    date_service = claim.get("date_service_received")
    if not date_service:
        return False

    has_gender_dysphoria = (claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes")
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")

    if patient_sex == "female":
        patient_age = h.patient_age(claim)
        if patient_age is None:
            return False

        if partner_sex == "male":
            required_threshold = 12 if patient_age < 35 else 6

            # READING: Heterosexual couples and intercourse requirements
            # Text: Glossary requires frequent unprotected heterosexual intercourse; table requires timed unprotected intercourse.
            # Reading: Glossary requires frequent intercourse (or gender dysphoria); table requires timed intercourse or donor cycles.
            frequent_months = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
            glossary_infertile = has_gender_dysphoria or (
                frequent_months is not None and frequent_months >= required_threshold
            )
            if not glossary_infertile:
                return False

            timed_months = claim.get("num_months_timed_unprotected_intercourse")
            donor_cycles = claim.get("num_cycles_donor_insemination")
            timed_ok = (timed_months is not None and timed_months >= required_threshold)
            donor_ok = (donor_cycles is not None and donor_cycles >= required_threshold)
            if not (timed_ok or donor_ok):
                return False

        else:
            # Female without a male partner (female partner or no partner)
            required_cycles = 12 if patient_age < 35 else 6
            donor_cycles = claim.get("num_cycles_donor_insemination")

            # Glossary check
            glossary_infertile = has_gender_dysphoria or (
                donor_cycles is not None and donor_cycles >= required_cycles
            )
            if not glossary_infertile:
                return False

            # READING: Gender dysphoria diagnosis and table criteria
            # Text: Table requires at least 12 (or 6) cycles of donor insemination for female without male partner.
            # Reading: Gender dysphoria does not waive the table requirement for donor insemination cycles.
            if donor_cycles is None or donor_cycles < required_cycles:
                return False

        # FSH testing requirement for female patients
        fsh_tests = claim.get("day_3_fsh_tests")
        if not fsh_tests or not isinstance(fsh_tests, list):
            return False

        tests_on_or_before = [t for t in fsh_tests if t[1] <= date_service]
        if not tests_on_or_before:
            return False

        if patient_age < 35:
            tests_in_window = [t for t in tests_on_or_before if h.months_at_most(t[1], date_service, 12)]
            if not tests_in_window:
                return False

            # READING: Most recent FSH lab test tie-breaking
            # Text: "Must be less than 19 mIU/mL in your most recent lab test".
            # Reading: All tests sharing the latest date and time must be < 19 mIU/mL.
            tests_sorted = sorted(tests_on_or_before, key=lambda t: (t[1], t[2]))
            max_dt = (tests_sorted[-1][1], tests_sorted[-1][2])
            most_recent_tests = [t for t in tests_sorted if (t[1], t[2]) == max_dt]
            if not all(t[0] < 19 for t in most_recent_tests):
                return False

        elif patient_age < 40:
            tests_in_window = [t for t in tests_on_or_before if h.months_at_most(t[1], date_service, 6)]
            if not tests_in_window:
                return False

            tests_sorted = sorted(tests_on_or_before, key=lambda t: (t[1], t[2]))
            max_dt = (tests_sorted[-1][1], tests_sorted[-1][2])
            most_recent_tests = [t for t in tests_sorted if (t[1], t[2]) == max_dt]
            if not all(t[0] < 19 for t in most_recent_tests):
                return False

        else:
            # READING: FSH test requirements for females age 40 and older
            # Text: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40."
            # and "within the past: 6 months".
            # Reading: Must have at least one test performed after age 40 within the past 6 months, and all tests
            # performed after age 40 on or before the date of service must have a level strictly less than 19 mIU/mL.
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            tests_since_40_valid = [t for t in tests_since_40 if t[1] <= date_service]
            tests_in_window = [t for t in tests_since_40_valid if h.months_at_most(t[1], date_service, 6)]
            if not tests_in_window:
                return False
            if not all(t[0] < 19 for t in tests_since_40_valid):
                return False

        return True

    elif patient_sex == "male":
        # READING: Male patient without a female partner
        # Text: The policy table contains no row or criteria for a male without a female partner.
        # Reading: Because table eligibility requirements cannot be met, male claimants without a female partner are not covered.
        if partner_sex != "female":
            return False

        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

        required_months = 12 if female_partner_age < 35 else 6

        # Glossary check
        frequent_months = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
        glossary_infertile = has_gender_dysphoria or (
            frequent_months is not None and frequent_months >= required_months
        )
        if not glossary_infertile:
            return False

        # Table check
        timed_months = claim.get("num_months_timed_unprotected_intercourse")
        if timed_months is None or timed_months < required_months:
            return False

        # FSH testing does not apply to males under the table
        return True

    return False
