"""
Policy Coverage Decision Module for Comprehensive Infertility Services
[Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64]

READING CHOICES:
1. READING: Infertility definition for male patient with female partner
   Text: "• For a female with a male partner, after: - 1 year of frequent, unprotected heterosexual sexual intercourse if under the age of 35 - 6 months of frequent, unprotected heterosexual sexual intercourse if age 35 or older"
   Reading: When the patient is male with a female partner, the failure to become pregnant after frequent unprotected heterosexual intercourse (12 months if female partner is under 35, 6 months if 35 or older) establishes infertility under the glossary for the couple, aligning with the policy table's explicit categories for males with female partners.

2. READING: Infertility under glossary for female with male partner using donor insemination
   Text: "A female under 35 years of age with a male partner ... A. 12 months or more or B. At least 12 cycles of donor insemination"
   Reading: The glossary explicitly lists donor insemination under "For a female without a male partner" but not under "For a female with a male partner". However, the table explicitly provides "B. At least 12 cycles [or 6 cycles] of donor insemination" as an alternative for a female with a male partner. To give full effect to Option B and avoid rendering it illusory, failure to achieve pregnancy after the requisite donor insemination cycles also satisfies the glossary definition of infertility for a female with a male partner.

3. READING: Gender dysphoria diagnosis and table requirements
   Text: "• For an individual or their partner who has been clinically diagnosed with gender dysphoria" / "• You have met the requirement for the number of months trying to conceive through egg and sperm contact. • Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following criteria: [TABLE]"
   Reading: A clinical diagnosis of gender dysphoria establishes infertility under the glossary without requiring prior months of intercourse or donor cycles. However, it does not exempt the claimant from meeting the independent eligibility criteria in the Certificate of Coverage, including the table requirements for trying to conceive through egg and sperm contact (timed intercourse or donor insemination) and FSH testing.

4. READING: Non-coverage of male without a female partner
   Text: "• For a male without a female partner, after: - At least 2 abnormal semen analyses obtained at least 2 weeks apart" / Table categories
   Reading: While a male without a female partner can satisfy the glossary definition of infertility via abnormal semen analyses or gender dysphoria, the policy coverage table contains no category or criteria for males without female partners, and the covered services (ovulation induction and IUI) require a female recipient. Thus, claims for males without a female partner are not covered under this benefit.

5. READING: Classification of female with female partner or no partner
   Text: "A female ... without a male partner"
   Reading: A female patient whose partner is female ("female") or who has no partner ("no_partner") is categorized as "A female without a male partner" for both glossary and table purposes.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered services check
    service_type = claim.get("service_type")
    if service_type not in (
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    ):
        return False

    # 2. Voluntary sterilization check
    # READING: Neither patient nor partner may have had voluntary sterilization
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    partner_sex = claim.get("sex_of_patients_partner")
    if partner_sex in ("male", "female"):
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # 3. Demonstrated condition causing infertility and exclusion of natural physiologic processes
    # Text: "There exists a condition that: Is demonstrated to cause the illness of infertility.
    # Has been recognized by your physician or infertility specialist and documented in your or your partner's medical records."
    # Text: "You or your partner does not have infertility that is due to a natural physiologic process..."
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition != "other":
        return False

    # 4. Less costly treatment check
    # Text: "A successful pregnancy cannot be attained through less costly treatment for which coverage is available under this plan."
    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    # 5. Patient demographics
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex not in ("female", "male"):
        return False

    patient_age = h.patient_age(claim)
    if patient_age is None:
        return False

    service_date = claim.get("date_service_received")
    if not service_date:
        return False

    # 6. Glossary infertility check
    is_infertile_under_glossary = False
    if claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes":
        is_infertile_under_glossary = True
    else:
        if patient_sex == "female":
            if partner_sex == "male":
                req_months = 12 if patient_age < 35 else 6
                freq_intercourse = claim.get(
                    "num_months_frequent_unprotected_heterosexual_intercourse", 0
                )
                donor_cycles = claim.get("num_cycles_donor_insemination", 0)
                # READING: Infertility under glossary for female with male partner using donor insemination
                # "B. At least 12 cycles of donor insemination"
                if freq_intercourse >= req_months or donor_cycles >= req_months:
                    is_infertile_under_glossary = True
            elif partner_sex in ("female", "no_partner"):
                # READING: Classification of female with female partner or no partner
                # "For a female without a male partner"
                req_cycles = 12 if patient_age < 35 else 6
                donor_cycles = claim.get("num_cycles_donor_insemination", 0)
                if donor_cycles >= req_cycles:
                    is_infertile_under_glossary = True
        elif patient_sex == "male":
            if partner_sex == "female":
                # READING: Infertility definition for male patient with female partner
                # "• For a female with a male partner, after: - 1 year of frequent, unprotected heterosexual sexual intercourse if under the age of 35 - 6 months of frequent, unprotected heterosexual sexual intercourse if age 35 or older"
                female_partner_age = claim.get("age_of_patients_female_partner")
                if female_partner_age is not None:
                    req_months = 12 if female_partner_age < 35 else 6
                    freq_intercourse = claim.get(
                        "num_months_frequent_unprotected_heterosexual_intercourse", 0
                    )
                    if freq_intercourse >= req_months:
                        is_infertile_under_glossary = True
            elif partner_sex in ("male", "no_partner"):
                semen_tests = claim.get("abnormal_semen_analyses", [])
                has_two_apart = False
                for i in range(len(semen_tests)):
                    for j in range(i + 1, len(semen_tests)):
                        if abs(h.days_between(semen_tests[i], semen_tests[j])) >= 14:
                            has_two_apart = True
                            break
                    if has_two_apart:
                        break
                if has_two_apart:
                    is_infertile_under_glossary = True

    if not is_infertile_under_glossary:
        return False

    # 7. Coverage Table Requirements Check
    # READING: Gender dysphoria diagnosis and table requirements
    # "• You have met the requirement for the number of months trying to conceive through egg and sperm contact. • Your unmedicated day 3 Follicle Stimulating Hormone (FSH) level meets the following criteria: [TABLE]"
    if patient_sex == "male":
        # READING: Non-coverage of male without a female partner
        # Table only provides categories for "A male of any age with a female partner under 35 years of age"
        # and "A male of any age with a female partner 35 years of age or older".
        if partner_sex != "female":
            return False

        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

        req_timed_months = 12 if female_partner_age < 35 else 6
        timed_intercourse = claim.get("num_months_timed_unprotected_intercourse", 0)
        if timed_intercourse < req_timed_months:
            return False

        # FSH testing does not apply to males
        return True

    # Female patient cases
    if patient_sex == "female":
        # Evaluate egg and sperm contact criteria (timed intercourse / donor insemination)
        if partner_sex == "male":
            req_contact = 12 if patient_age < 35 else 6
            timed_intercourse = claim.get("num_months_timed_unprotected_intercourse", 0)
            donor_cycles = claim.get("num_cycles_donor_insemination", 0)
            if timed_intercourse < req_contact and donor_cycles < req_contact:
                return False
        elif partner_sex in ("female", "no_partner"):
            req_donor_cycles = 12 if patient_age < 35 else 6
            donor_cycles = claim.get("num_cycles_donor_insemination", 0)
            if donor_cycles < req_donor_cycles:
                return False
        else:
            return False

        # Evaluate FSH test criteria
        lookback_months = 12 if patient_age < 35 else 6
        fsh_tests = claim.get("day_3_fsh_tests", [])

        # Tests on or before date of service
        prior_tests = [t for t in fsh_tests if t[1] <= service_date]

        # Must have an unmedicated day 3 FSH test done within the past 12 or 6 months
        tests_in_window = [
            t for t in prior_tests if h.months_at_most(t[1], service_date, lookback_months)
        ]
        if not tests_in_window:
            return False

        # Most recent lab test on or before date of service
        max_dt = max((t[1], t[2]) for t in prior_tests)
        most_recent_tests = [t for t in prior_tests if (t[1], t[2]) == max_dt]
        if any(t[0] >= 19 for t in most_recent_tests):
            return False

        # If age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40
        if patient_age >= 40:
            tests_after_40 = [
                t for t in h.fsh_tests_since_age_40(claim) if t[1] <= service_date
            ]
            if any(t[0] >= 19 for t in tests_after_40):
                return False

        return True

    return False
