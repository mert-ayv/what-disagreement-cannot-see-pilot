"""
Policy Coverage Decision Function for Comprehensive Infertility Services
[Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64; Glossary]

READING choices made under the member-advocate standard:

1. READING: Donor insemination for female with male partner
   Words of text: "A female under 35 [or 35+] years of age with a male partner ... A. 12 [6] months or more or B. At least 12 [6] cycles of donor insemination"
   Reading chosen: Although the glossary defines infertility for a female with a male partner in terms of heterosexual intercourse, the operative coverage table explicitly permits "At least 12 cycles of donor insemination" (or 6 cycles if age 35+) as an alternative path (Path B). Reading the certificate as a whole in the member's favor, completing the requisite donor insemination cycles satisfies both the plan's waiting period and the definition of infertility for a female with a male partner.

2. READING: Equivalence of timed and frequent unprotected intercourse fields
   Words of text: "Number of months of unprotected timed sexual intercourse" (Table) vs. "frequent, unprotected heterosexual sexual intercourse" (Glossary)
   Reading chosen: A court interpreting this certificate in the member's favor would treat documented timed unprotected intercourse and frequent unprotected heterosexual intercourse as mutually satisfying each other's duration requirements, taking the maximum of the two fields to credit the member's months trying to conceive.

3. READING: Inapplicability of egg/sperm contact waiting period to gender dysphoria
   Words of text: Glossary defines infertility "For an individual or their partner who has been clinically diagnosed with gender dysphoria" without requiring any trial period of intercourse or donor insemination.
   Reading chosen: A court could reasonably read the eligibility bullet "You have met the requirement for the number of months trying to conceive through egg and sperm contact" as applying only where infertility is established by failure of egg and sperm contact, and inapplicable to members whose infertility is established by a diagnosis of gender dysphoria.

4. READING: Clinical diagnosis of gender dysphoria as documented condition causing infertility
   Words of text: "There exists a condition that: Is demonstrated to cause the illness of infertility. Has been recognized by your physician or infertility specialist and documented in your or your partner's medical records."
   Reading chosen: If `demonstrated_and_documented_condition_causing_infertility` is not explicitly coded as "other", but a clinical diagnosis of gender dysphoria is documented (`patient_or_partner_diagnosed_with_gender_dysphoria == "yes"`), a court could accept this clinical diagnosis as satisfying the documented condition requirement, provided it is not due to an excluded natural physiologic process.

5. READING: Multiple FSH test results at the same timestamp
   Words of text: "Must be less than 19 mIU/mL in your most recent lab test" / "in all prior tests performed after age 40"
   Reading chosen: If multiple test entries exist with the exact same date and time (e.g., duplicate lab reports or split samples), the reading most favorable to the member is to credit the lowest measured level for that draw/timestamp.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered service types
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # 2. Date of service
    dos = claim.get("date_service_received")
    if not dos:
        return False

    # 3. Less costly treatment requirement
    # "A successful pregnancy cannot be attained through less costly treatment for which coverage is available under this plan."
    if (
        claim.get(
            "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
        )
        != "no"
    ):
        return False

    # 4. Voluntary sterilization exclusion
    # "You or your partner has not had a voluntary sterilization with or without surgical reversal..."
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    partner_sex = claim.get("sex_of_patients_partner")
    if partner_sex not in {"male", "female", "no_partner"}:
        return False

    if partner_sex in {"male", "female"}:
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # 5. Natural physiologic process exclusion & documented condition requirement
    # "There exists a condition that: Is demonstrated to cause the illness of infertility. Has been recognized... and documented..."
    # "You or your partner does not have infertility that is due to a natural physiologic process..."
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    natural_processes = {
        "natural_menopause",
        "natural_perimenopause",
        "natural_male_reproductive_aging",
        "other_natural_physiologic_process",
    }
    if condition in natural_processes:
        return False

    has_gender_dysphoria = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    # READING: Clinical diagnosis of gender dysphoria as documented condition
    if condition == "other":
        pass  # Documented non-natural condition established
    elif has_gender_dysphoria and condition is None:
        pass  # Documented gender dysphoria diagnosis accepted as condition
    else:
        return False

    # 6. Patient sex and partner evaluation
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex not in {"female", "male"}:
        return False

    # Aggregate intercourse duration across both fields
    # READING: Equivalence of timed and frequent unprotected intercourse fields
    intercourse_months = max(
        claim.get("num_months_timed_unprotected_intercourse", 0),
        claim.get("num_months_frequent_unprotected_heterosexual_intercourse", 0),
    )
    donor_cycles = claim.get("num_cycles_donor_insemination", 0)

    # 7. Female patient rules
    if patient_sex == "female":
        age = h.patient_age(claim)
        if age is None:
            return False

        # Egg and sperm contact waiting period
        # READING: Inapplicability of egg/sperm contact waiting period to gender dysphoria
        if not has_gender_dysphoria:
            if partner_sex == "male":
                # READING: Donor insemination for female with male partner
                if age < 35:
                    if not (intercourse_months >= 12 or donor_cycles >= 12):
                        return False
                else:  # age >= 35
                    if not (intercourse_months >= 6 or donor_cycles >= 6):
                        return False
            else:  # female without a male partner
                if age < 35:
                    if donor_cycles < 12:
                        return False
                else:  # age >= 35
                    if donor_cycles < 6:
                        return False

        # FSH test criteria
        window_months = 12 if age < 35 else 6
        all_fsh_tests = claim.get("day_3_fsh_tests")
        if not all_fsh_tests:
            return False

        # Only evaluate tests taken on or before date of service
        valid_tests = [t for t in all_fsh_tests if t[1] <= dos]
        if not valid_tests:
            return False

        # Group tests by timestamp (date, time) and determine effective level for each draw
        # READING: Multiple FSH test results at the same timestamp (credit lowest level)
        timestamp_levels = {}
        for level, date_str, time_str in valid_tests:
            ts = (date_str, time_str)
            if ts not in timestamp_levels or level < timestamp_levels[ts]:
                timestamp_levels[ts] = level

        latest_timestamp = max(timestamp_levels.keys())
        latest_date = latest_timestamp[0]

        # The test must be done within the past 12 (or 6) months
        if not h.months_at_most(latest_date, dos, window_months):
            return False

        # The most recent test must be less than 19 mIU/mL
        if timestamp_levels[latest_timestamp] >= 19:
            return False

        # If age 40 and older: must be less than 19 mIU/mL in all prior tests performed after age 40
        if age >= 40:
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            valid_tests_since_40 = [t for t in tests_since_40 if t[1] <= dos]
            ts_since_40 = {}
            for level, date_str, time_str in valid_tests_since_40:
                ts = (date_str, time_str)
                if ts not in ts_since_40 or level < ts_since_40[ts]:
                    ts_since_40[ts] = level
            for eff_level in ts_since_40.values():
                if eff_level >= 19:
                    return False

        return True

    # 8. Male patient rules
    if patient_sex == "male":
        if partner_sex == "female":
            # Male of any age with a female partner
            if has_gender_dysphoria:
                return True

            partner_age = claim.get("age_of_patients_female_partner")
            if partner_age is not None:
                if partner_age < 35:
                    return intercourse_months >= 12
                else:
                    return intercourse_months >= 6
            else:
                # Partner age unknown: 12 months covers female partner of any age
                return intercourse_months >= 12

        else:
            # Male without a female partner (partner is male or no partner)
            # Table has no egg/sperm contact or FSH requirements for this category.
            # Infertility under glossary: gender dysphoria OR at least 2 abnormal semen analyses >= 14 days apart.
            if has_gender_dysphoria:
                return True

            analyses = claim.get("abnormal_semen_analyses", [])
            valid_analyses = [d for d in analyses if d <= dos]
            if len(valid_analyses) < 2:
                return False

            # Check for at least two analyses obtained at least 2 weeks (14 days) apart
            for i in range(len(valid_analyses)):
                for j in range(i + 1, len(valid_analyses)):
                    if abs(h.days_between(valid_analyses[i], valid_analyses[j])) >= 14:
                        return True
            return False

    return False
