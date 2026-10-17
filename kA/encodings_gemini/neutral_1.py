"""
Policy Coverage Decision Module: Comprehensive Infertility Services
Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64

This module encodes coverage rules for comprehensive infertility services.
Where the policy certificate and glossary text leave room for interpretation,
the following readings were chosen:

1. READING: Harmonized Infertility Definition for Female with Male Partner using Donor Insemination
   Quote: Table provides "A. 12 months or more or B. At least 12 cycles of donor insemination" for
   "A female under 35 years of age with a male partner", while Glossary provides "For a female with
   a male partner, after: - 1 year of frequent, unprotected heterosexual sexual intercourse...".
   Reading: When a female with a male partner attempts conception via donor insemination (Option B in
   the benefit table), completing at least 12 cycles (if under 35) or 6 cycles (if 35 or older) establishes
   the failure to become pregnant under the glossary definition of infertility, harmonizing the glossary
   with the explicit benefit table option. Alternatively, if conception is attempted via intercourse (Option A),
   the claim must satisfy both the glossary requirement of frequent unprotected heterosexual intercourse
   and the table requirement of timed unprotected intercourse.

2. READING: Infertility Definition for Male with Female Partner
   Quote: Glossary defines infertility "For a female with a male partner, after: - 1 year of frequent,
   unprotected heterosexual sexual intercourse if under the age of 35 - 6 months of frequent, unprotected
   heterosexual sexual intercourse if age 35 or older".
   Reading: For a male patient with a female partner, infertility under the glossary is evaluated
   based on the female partner's age (`age_of_patients_female_partner`) and the couple's months of frequent,
   unprotected heterosexual intercourse, aligning with the couple-level definition of reproductive failure.

3. READING: Male without Female Partner Eligibility
   Quote: "You have met the requirement for the number of months trying to conceive through egg and sperm contact.
   Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following criteria: [table]".
   Reading: The policy table only establishes categories and criteria for females (with or without a male partner)
   and males with a female partner. A male patient without a female partner is not listed in the table and cannot
   meet the egg and sperm contact requirement, and is therefore ineligible for comprehensive infertility services
   under this benefit.

4. READING: Female with Female Partner Classification
   Quote: "A female under 35 years of age without a male partner", "A female 35 years of age or older without a male partner".
   Reading: A female patient whose partner is female has no male partner and is classified as "a female without
   a male partner" under both the glossary and the benefit table.

5. READING: Distinct Fields for Timed vs Frequent Intercourse
   Quote: Table requires "unprotected timed sexual intercourse", whereas Glossary requires "frequent,
   unprotected heterosexual sexual intercourse".
   Reading: `num_months_frequent_unprotected_heterosexual_intercourse` is checked for the glossary definition,
   while `num_months_timed_unprotected_intercourse` is checked for the benefit table requirement.

6. READING: Gender Dysphoria and Benefit Table Requirements
   Quote: Glossary states: "• For an individual or their partner who has been clinically diagnosed with gender dysphoria".
   Table states: "You have met the requirement for the number of months trying to conceive through egg and sperm contact.
   Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following criteria: [table]".
   Reading: While a diagnosis of gender dysphoria establishes infertility under the glossary without requiring months
   of intercourse or donor cycles, the text's eligibility requirements (the table's egg and sperm contact / donor cycle
   thresholds and FSH testing criteria) still apply to receive comprehensive infertility services.

7. READING: Demonstrated and Documented Condition Causing Infertility
   Quote: "There exists a condition that: - Is demonstrated to cause the illness of infertility. - Has been recognized
   by your physician or infertility specialist and documented in your or your partner’s medical records" and
   "You or your partner does not have infertility that is due to a natural physiologic process such as age related
   ovarian insufficiency (e.g. perimenopause, menopause)."
   Reading: The interface field `demonstrated_and_documented_condition_causing_infertility` must equal "other",
   indicating an illness causing infertility that is not one of the natural physiologic processes ("natural_menopause",
   "natural_perimenopause", "natural_male_reproductive_aging", "other_natural_physiologic_process").

8. READING: Partner Voluntary Sterilization when Patient has No Partner
   Quote: "You or your partner has not had a voluntary sterilization".
   Reading: When `sex_of_patients_partner` is "no_partner", only the patient's voluntary sterilization status is evaluated.

9. READING: Definition of Prior FSH Tests
   Quote: "must be less than 19 mIU/mL in all prior tests performed after age 40."
   Reading: Only tests performed on or prior to `date_service_received` are considered "prior tests".
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered service check
    service_type = claim.get("service_type")
    if service_type not in (
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    ):
        return False

    date_service_received = claim.get("date_service_received")
    if not date_service_received:
        return False

    # 2. Demonstrated and documented condition causing infertility (not due to natural physiologic process)
    # READING: Demonstrated and Documented Condition Causing Infertility
    # Quote: "There exists a condition that: - Is demonstrated to cause the illness of infertility. - Has been recognized
    # by your physician or infertility specialist and documented..." and "You or your partner does not have infertility
    # that is due to a natural physiologic process such as age related ovarian insufficiency (e.g. perimenopause, menopause)."
    # Reading: Field must be "other", excluding natural physiologic processes and missing documentation.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # 3. Voluntary sterilization check
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    partner_sex = claim.get("sex_of_patients_partner")
    if partner_sex in ("male", "female"):
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False
    elif partner_sex == "no_partner":
        # READING: Partner Voluntary Sterilization when Patient has No Partner
        # Quote: "You or your partner has not had a voluntary sterilization".
        # Reading: Only the patient's sterilization status is evaluated when there is no partner.
        pass
    else:
        return False

    # 4. Less costly treatment check
    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    # 5. Sex and Age determination
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex not in ("female", "male"):
        return False

    has_gender_dysphoria = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    def _parse_fsh(t):
        if isinstance(t, dict):
            return t["level"], t["date"], t["time"]
        return t[0], t[1], t[2]

    # --- FEMALE PATIENT ---
    if patient_sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False

        is_under_35 = age < 35
        months_threshold = 12 if is_under_35 else 6
        cycles_threshold = 12 if is_under_35 else 6
        fsh_months_window = 12 if is_under_35 else 6

        # Evaluate egg and sperm contact (intercourse / donor cycles) and glossary infertility
        if partner_sex == "male":
            timed_intercourse_ok = (
                claim.get("num_months_timed_unprotected_intercourse", -1)
                >= months_threshold
            )
            donor_insemination_ok = (
                claim.get("num_cycles_donor_insemination", -1) >= cycles_threshold
            )

            if not (timed_intercourse_ok or donor_insemination_ok):
                return False

            # READING: Distinct Fields for Timed vs Frequent Intercourse & Harmonized Infertility Definition
            # Quote: Table specifies "Number of months of unprotected timed sexual intercourse", while Glossary specifies
            # "frequent, unprotected heterosexual sexual intercourse". Table also provides "At least 12 cycles of donor insemination".
            # Reading: If intercourse is relied on, both frequent (glossary) and timed (table) intercourse must meet thresholds.
            # If donor insemination is relied on, reaching the required cycles satisfies failure to become pregnant under the glossary.
            # A gender dysphoria diagnosis satisfies the glossary independently.
            # READING: Gender Dysphoria and Benefit Table Requirements
            # Quote: "You have met the requirement for the number of months trying to conceive through egg and sperm contact."
            # Reading: Gender dysphoria satisfies glossary infertility, but table egg/sperm contact requirements still apply.
            if has_gender_dysphoria:
                glossary_infertile = True
            else:
                frequent_intercourse_ok = (
                    claim.get(
                        "num_months_frequent_unprotected_heterosexual_intercourse", -1
                    )
                    >= months_threshold
                )
                glossary_infertile = (
                    timed_intercourse_ok and frequent_intercourse_ok
                ) or donor_insemination_ok

            if not glossary_infertile:
                return False

        elif partner_sex in ("female", "no_partner"):
            # READING: Female with Female Partner Classification
            # Quote: "A female under 35 years of age without a male partner", "A female 35 years of age or older without a male partner".
            # Reading: A female with a female partner is evaluated as a female without a male partner.
            donor_insemination_ok = (
                claim.get("num_cycles_donor_insemination", -1) >= cycles_threshold
            )
            if not donor_insemination_ok:
                return False

            if not has_gender_dysphoria and not donor_insemination_ok:
                return False
        else:
            return False

        # FSH test requirements for female patients
        fsh_tests = claim.get("day_3_fsh_tests")
        if not fsh_tests:
            return False

        # READING: Definition of Prior FSH Tests
        # Quote: "must be less than 19 mIU/mL in all prior tests performed after age 40."
        # Reading: Only tests performed on or prior to date_service_received are eligible prior tests.
        prior_fsh_tests = []
        for t in fsh_tests:
            lvl, dt, tm = _parse_fsh(t)
            if dt <= date_service_received:
                prior_fsh_tests.append((lvl, dt, tm))

        if not prior_fsh_tests:
            return False

        # Most recent test timestamp (date, time)
        max_ts = max((t[1], t[2]) for t in prior_fsh_tests)

        # Must have an unmedicated day 3 FSH test done within past 12 months (<35) or 6 months (>=35)
        if not h.months_at_most(max_ts[0], date_service_received, fsh_months_window):
            return False

        # Most recent test result must be less than 19 mIU/mL
        most_recent_tests = [t for t in prior_fsh_tests if (t[1], t[2]) == max_ts]
        if any(t[0] >= 19 for t in most_recent_tests):
            return False

        # If age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40
        if age >= 40:
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            if tests_since_40 is None:
                return False
            for t in tests_since_40:
                lvl, dt, _ = _parse_fsh(t)
                if dt <= date_service_received and lvl >= 19:
                    return False

        return True

    # --- MALE PATIENT ---
    elif patient_sex == "male":
        # READING: Male without Female Partner Eligibility
        # Quote: Table specifies criteria only for "A male of any age with a female partner...".
        # Reading: A male without a female partner is not covered under the comprehensive infertility services benefit table.
        if partner_sex != "female":
            return False

        partner_age = claim.get("age_of_patients_female_partner")
        if partner_age is None:
            return False

        # READING: Infertility Definition for Male with Female Partner
        # Quote: Glossary defines infertility for female with male partner by intercourse duration based on female age.
        # Table defines male eligibility based on female partner's age (<35 vs 35+).
        # Reading: Female partner's age governs both table and glossary intercourse duration thresholds.
        months_threshold = 12 if partner_age < 35 else 6

        timed_intercourse_ok = (
            claim.get("num_months_timed_unprotected_intercourse", -1)
            >= months_threshold
        )
        if not timed_intercourse_ok:
            return False

        if has_gender_dysphoria:
            glossary_infertile = True
        else:
            frequent_intercourse_ok = (
                claim.get(
                    "num_months_frequent_unprotected_heterosexual_intercourse", -1
                )
                >= months_threshold
            )
            glossary_infertile = frequent_intercourse_ok

        if not glossary_infertile:
            return False

        # FSH testing does not apply to males under the policy table
        return True

    return False
