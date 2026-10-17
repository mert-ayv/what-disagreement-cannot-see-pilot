"""
Policy Coverage Rules: Comprehensive Infertility Services

READING choices:
1. READING: Donor insemination for female with male partner under glossary definition of infertility.
   Quotes: "A female under 35 [or 35 or older] years of age with a male partner: A. 12 months or more
   or B. At least 12 cycles of donor insemination" vs Glossary "For a female with a male partner, after:
   1 year of frequent, unprotected heterosexual sexual intercourse".
   Choice: To avoid rendering Option B in the policy table an impossible path to coverage (a nullity),
   completion of the required donor insemination cycles (>= 12 if under 35, >= 6 if 35+) also satisfies
   the glossary definition of infertility for a female with a male partner.

2. READING: Relationship between "frequent, unprotected heterosexual sexual intercourse" and "unprotected timed sexual intercourse".
   Quotes: Glossary "frequent, unprotected heterosexual sexual intercourse" vs Table "unprotected timed sexual intercourse".
   Choice: Regular timed unprotected intercourse aimed at conception functions as frequent heterosexual
   intercourse and vice versa. If one intercourse field is absent from the claim, the other may satisfy
   the requirement. If an intercourse field is explicitly present and below the required duration, that
   failure is enforced.

3. READING: Infertility under glossary for a male patient with a female partner.
   Quotes: Glossary "A disease defined by the failure to become pregnant: • For a female with a male partner,
   after: 1 year ... if under the age of 35; 6 months ... if age 35 or older".
   Choice: For a male patient trying to conceive with a female partner, the failure to become pregnant
   applies to the couple and is measured based on the female partner's age and the couple's intercourse duration.

4. READING: FSH test result evaluation when multiple tests have the identical most recent timestamp.
   Quotes: "Must be less than 19 mIU/mL in your most recent lab test".
   Choice: When multiple test results share the latest date and time, the requirement is met if at least
   one test at that timestamp is less than 19 mIU/mL.

5. READING: Evaluation of "all prior tests performed after age 40" with duplicate timestamps.
   Quotes: "must be less than 19 mIU/mL in all prior tests performed after age 40".
   Choice: At each prior testing timestamp on or after age 40, having at least one result less than
   19 mIU/mL satisfies the requirement for that testing session.
"""

COVERED_SERVICES = {
    "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins",
}


def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered comprehensive infertility service
    service_type = claim.get("service_type")
    if service_type not in COVERED_SERVICES:
        return False

    # 2. General eligibility requirements from policy text:
    # Condition demonstrated and documented to cause infertility
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition != "other":
        # Missing, or one of the natural physiologic processes (e.g. natural_menopause) which is excluded
        return False

    # Voluntary sterilization exclusion
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    partner_sex = claim.get("sex_of_patients_partner")
    if partner_sex in ("male", "female"):
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False
    elif partner_sex == "no_partner":
        pass
    else:
        return False

    # Less costly treatment availability
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # Service date
    service_date = claim.get("date_service_received")
    if not service_date:
        return False

    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    has_gender_dysphoria = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"

    timed_intercourse = claim.get("num_months_timed_unprotected_intercourse")
    frequent_intercourse = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
    donor_cycles = claim.get("num_cycles_donor_insemination")

    # READING: Relationship between "frequent, unprotected heterosexual sexual intercourse" and "unprotected timed sexual intercourse"
    # If one intercourse duration is absent, the other can supply it; if an explicit number is below threshold, it fails.
    def intercourse_meets(threshold: int) -> bool:
        if timed_intercourse is not None and frequent_intercourse is not None:
            return timed_intercourse >= threshold and frequent_intercourse >= threshold
        if timed_intercourse is not None:
            return timed_intercourse >= threshold
        if frequent_intercourse is not None:
            return frequent_intercourse >= threshold
        return False

    # 3. Patient category evaluation (Glossary + Table requirements)
    if patient_sex == "female":
        patient_age = h.patient_age(claim)
        if patient_age is None:
            return False

        if partner_sex == "male":
            threshold = 12 if patient_age < 35 else 6

            # Glossary infertility check
            # READING: Donor insemination for female with male partner under glossary definition of infertility
            # If donor insemination meets the threshold, it satisfies the glossary as well as the table.
            if has_gender_dysphoria:
                glossary_infertile = True
            else:
                intercourse_ok = intercourse_meets(threshold)
                donor_ok = donor_cycles is not None and donor_cycles >= threshold
                glossary_infertile = intercourse_ok or donor_ok

            if not glossary_infertile:
                return False

            # Table egg and sperm contact check: A. intercourse or B. donor insemination
            timed_ok = (timed_intercourse is not None and timed_intercourse >= threshold) or (
                timed_intercourse is None and frequent_intercourse is not None and frequent_intercourse >= threshold
            )
            donor_table_ok = donor_cycles is not None and donor_cycles >= threshold
            if not (timed_ok or donor_table_ok):
                return False

        else:
            # Female without male partner (partner is female or no partner)
            threshold = 12 if patient_age < 35 else 6

            # Glossary infertility check
            if has_gender_dysphoria:
                glossary_infertile = True
            else:
                glossary_infertile = donor_cycles is not None and donor_cycles >= threshold

            if not glossary_infertile:
                return False

            # Table donor insemination check
            if donor_cycles is None or donor_cycles < threshold:
                return False

        # Table FSH requirements for female patients
        fsh_tests = claim.get("day_3_fsh_tests")
        if not fsh_tests:
            return False

        prior_tests = [t for t in fsh_tests if t[1] <= service_date]
        if not prior_tests:
            return False

        # Latest timestamp among tests performed on or before service date
        latest_timestamp = max((t[1], t[2]) for t in prior_tests)
        latest_date = latest_timestamp[0]

        # Timing requirement: within past 12 months (if < 35) or past 6 months (if >= 35)
        fsh_window = 12 if patient_age < 35 else 6
        if not h.months_at_most(latest_date, service_date, fsh_window):
            return False

        # READING: FSH test result evaluation when multiple tests have the identical most recent timestamp
        # Must be less than 19 mIU/mL in most recent lab test
        most_recent_tests = [t for t in prior_tests if (t[1], t[2]) == latest_timestamp]
        if not any(t[0] < 19 for t in most_recent_tests):
            return False

        # Additional requirement if age 40 and older: must be < 19 in all prior tests performed after age 40
        if patient_age >= 40:
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if tests_since_40 is not None:
                prior_since_40 = [t for t in tests_since_40 if t[1] <= service_date]
                # READING: Evaluation of "all prior tests performed after age 40" with duplicate timestamps
                timestamps_40 = set((t[1], t[2]) for t in prior_since_40)
                for ts in timestamps_40:
                    tests_at_ts = [t for t in prior_since_40 if (t[1], t[2]) == ts]
                    if not any(t[0] < 19 for t in tests_at_ts):
                        return False

        return True

    elif patient_sex == "male":
        # Comprehensive infertility services can only be covered for a male with a female partner under the table
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        threshold = 12 if partner_age < 35 else 6

        # READING: Infertility under glossary for a male patient with a female partner
        # Failure to become pregnant evaluated based on female partner's age and intercourse duration
        if has_gender_dysphoria:
            glossary_infertile = True
        else:
            glossary_infertile = intercourse_meets(threshold)

        if not glossary_infertile:
            return False

        # Table egg and sperm contact check
        timed_ok = (timed_intercourse is not None and timed_intercourse >= threshold) or (
            timed_intercourse is None and frequent_intercourse is not None and frequent_intercourse >= threshold
        )
        if not timed_ok:
            return False

        # FSH test: Does not apply for male patient
        return True

    else:
        return False
