"""
List of READING choices:

1. Covered services:
   Text: "We will cover charges made by an infertility specialist for the following
   infertility services: • Ovulation induction cycle(s) with menotropins • Intrauterine
   insemination"
   Reading: Only service_type "intrauterine_insemination" and
   "ovulation_induction_cycle_with_menotropins" are covered.

2. Documented condition and exclusion of natural physiologic processes:
   Text: "There exists a condition that: Is demonstrated to cause the illness of
   infertility. Has been recognized by your physician or infertility specialist and
   documented in your or your partner's medical records." and "You or your partner
   does not have infertility that is due to a natural physiologic process such as age
   related ovarian insufficiency (e.g. perimenopause, menopause)."
   Reading: demonstrated_and_documented_condition_causing_infertility must be "other".
   If it is any natural physiologic process or is absent, the claim is denied, regardless
   of gender dysphoria status.

3. Heterosexual couples and the glossary definition of infertility:
   Text: "For a female with a male partner, after: - 1 year of frequent, unprotected
   heterosexual sexual intercourse if under the age of 35 - 6 months of frequent,
   unprotected heterosexual sexual intercourse if age 35 or older"
   Reading: This glossary definition governs heterosexual couples whether the patient is
   the female or the male (measuring against the female's age). A female with a male
   partner cannot establish glossary infertility through donor insemination, as donor
   insemination is specified in the glossary solely "[f]or a female without a male partner".

4. Distinction between glossary intercourse and table intercourse requirements:
   Text: Glossary requires "frequent, unprotected heterosexual sexual intercourse" while
   the policy table requires "unprotected timed sexual intercourse".
   Reading: These are distinct requirements. Timed intercourse cannot substitute for
   frequent intercourse under the glossary, and frequent intercourse cannot substitute
   for timed intercourse under the table. Both must be satisfied independently when
   applicable.

5. Male without a female partner not eligible:
   Text: The comprehensive infertility services table only includes rows for females
   and for "A male of any age with a female partner".
   Reading: A male without a female partner (including a male with a male partner or with
   no partner) does not fall into any eligible category in the table and cannot receive
   the covered procedures; thus, such claims are not covered.

6. FSH test requirement for females age 40 and older:
   Text: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests
   performed after age 40."
   Reading: A female patient age 40 or older must have had at least one FSH test performed
   on or after age 40, and all tests performed after age 40 must be strictly less than 19
   mIU/mL. In addition, she must have had an FSH test done within the past 6 months whose
   most recent result is strictly less than 19 mIU/mL.

7. Multiple tests at the most recent timestamp:
   Text: "Must be less than 19 mIU/mL in your most recent lab test"
   Reading: If multiple tests share the latest date and time, all of them must be strictly
   less than 19 mIU/mL.
"""

def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Covered services. "We will cover charges made by an infertility specialist
    # for the following infertility services: • Ovulation induction cycle(s) with menotropins
    # • Intrauterine insemination".
    service_type = claim.get("service_type")
    if service_type not in ("intrauterine_insemination", "ovulation_induction_cycle_with_menotropins"):
        return False

    # READING: Documented condition and exclusion of natural physiologic processes.
    # Text: "There exists a condition that: Is demonstrated to cause the illness of infertility.
    # Has been recognized by your physician or infertility specialist and documented in your or
    # your partner's medical records." and "You or your partner does not have infertility that
    # is due to a natural physiologic process...".
    # Choosing the reading that demonstrated_and_documented_condition_causing_infertility must
    # be present and must be "other".
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # Less costly treatment requirement
    # "A successful pregnancy cannot be attained through less costly treatment for which
    # coverage is available under this plan."
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # Voluntary sterilization requirement
    # "You or your partner has not had a voluntary sterilization with or without surgical reversal..."
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    partner_sex = claim.get("sex_of_patients_partner")
    if patient_sex not in ("female", "male") or partner_sex not in ("male", "female", "no_partner"):
        return False

    if partner_sex in ("male", "female"):
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    service_date = claim.get("date_service_received")
    if not service_date:
        return False

    has_gender_dysphoria = (claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes")

    # READING: Male without a female partner not eligible.
    # Text: The table only specifies criteria for females and for "A male of any age with a
    # female partner". A male without a female partner does not match any table row.
    if patient_sex == "male" and partner_sex != "female":
        return False

    # --- Female Patient ---
    if patient_sex == "female":
        patient_age = h.patient_age(claim)
        if patient_age is None:
            return False

        # Glossary infertility check
        if has_gender_dysphoria:
            glossary_infertile = True
        elif partner_sex == "male":
            # READING: Heterosexual couples and the glossary definition of infertility.
            # Text: "For a female with a male partner, after: - 1 year of frequent, unprotected
            # heterosexual sexual intercourse if under the age of 35 - 6 months... if age 35 or older".
            # Donor insemination is not recognized under the glossary for a female with a male partner.
            frequent_intercourse = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
            if frequent_intercourse is None:
                return False
            required_frequent = 12 if patient_age < 35 else 6
            glossary_infertile = (frequent_intercourse >= required_frequent)
        else:
            # Female without a male partner (female partner or no partner)
            # Glossary: At least 12 cycles donor insemination if under 35; 6 cycles if 35 or older.
            donor_cycles = claim.get("num_cycles_donor_insemination")
            if donor_cycles is None:
                return False
            required_cycles = 12 if patient_age < 35 else 6
            glossary_infertile = (donor_cycles >= required_cycles)

        if not glossary_infertile:
            return False

        # Table check: Egg & sperm contact
        # READING: Distinction between glossary intercourse and table intercourse requirements.
        # Table requires "unprotected timed sexual intercourse" or "donor insemination".
        if partner_sex == "male":
            timed_intercourse = claim.get("num_months_timed_unprotected_intercourse")
            donor_cycles = claim.get("num_cycles_donor_insemination")
            threshold = 12 if patient_age < 35 else 6
            timed_met = (timed_intercourse is not None and timed_intercourse >= threshold)
            donor_met = (donor_cycles is not None and donor_cycles >= threshold)
            if not (timed_met or donor_met):
                return False
        else:
            # Female without a male partner
            donor_cycles = claim.get("num_cycles_donor_insemination")
            threshold = 12 if patient_age < 35 else 6
            if donor_cycles is None or donor_cycles < threshold:
                return False

        # Table check: FSH tests
        fsh_tests = claim.get("day_3_fsh_tests")
        if not fsh_tests:
            return False

        prior_fsh_tests = [t for t in fsh_tests if t[1] <= service_date]
        if not prior_fsh_tests:
            return False

        # Find most recent lab test(s) on or before date of service
        sorted_tests = sorted(prior_fsh_tests, key=lambda t: (t[1], t[2]))
        latest_date, latest_time = sorted_tests[-1][1], sorted_tests[-1][2]
        most_recent_tests = [t for t in sorted_tests if t[1] == latest_date and t[2] == latest_time]

        # Timing requirement: within past 12 months (< 35) or past 6 months (>= 35)
        max_fsh_months = 12 if patient_age < 35 else 6
        if not h.months_at_most(latest_date, service_date, max_fsh_months):
            return False

        # Results requirement
        # READING: Tie at most recent FSH test timestamp. All tests at that timestamp must be < 19.
        if any(t[0] >= 19 for t in most_recent_tests):
            return False

        if patient_age >= 40:
            # READING: FSH test requirement for females age 40 and older.
            # "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests
            # performed after age 40." Requires at least one test performed after age 40,
            # and all tests performed after age 40 must be strictly less than 19 mIU/mL.
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if not tests_since_40:
                return False
            if any(t[0] >= 19 for t in tests_since_40):
                return False

        return True

    # --- Male Patient with Female Partner ---
    if patient_sex == "male" and partner_sex == "female":
        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        # Glossary infertility check
        if has_gender_dysphoria:
            glossary_infertile = True
        else:
            # READING: Heterosexual couples and the glossary definition of infertility.
            # Evaluated based on the female partner's age for the heterosexual couple.
            frequent_intercourse = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
            if frequent_intercourse is None:
                return False
            required_frequent = 12 if partner_age < 35 else 6
            glossary_infertile = (frequent_intercourse >= required_frequent)

        if not glossary_infertile:
            return False

        # Table check: Egg & sperm contact
        # For a male of any age with a female partner, donor insemination does not apply.
        # Timed intercourse must be 12 months or more (< 35) or 6 months or more (>= 35).
        timed_intercourse = claim.get("num_months_timed_unprotected_intercourse")
        if timed_intercourse is None:
            return False
        required_timed = 12 if partner_age < 35 else 6
        if timed_intercourse < required_timed:
            return False

        # FSH test: Does not apply for male patients under the table.
        return True

    return False
