"""
Policy Coverage Rules: Comprehensive Infertility Services
Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64 & Glossary

READING CHOICES ENCODED:
1. READING: Covered Services.
   Text: "We will cover charges made by an infertility specialist for the following
   infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine insemination"
   Reading: Only "intrauterine_insemination" and "ovulation_induction_cycle_with_menotropins"
   qualify as covered comprehensive infertility services under this benefit.

2. READING: Demonstrating Condition & Exclusion of Natural Physiologic Processes.
   Text: "There exists a condition that: Is demonstrated to cause the illness of infertility.
   Has been recognized by your physician or infertility specialist and documented...
   You or your partner does not have infertility that is due to a natural physiologic process
   such as age related ovarian insufficiency (e.g. perimenopause, menopause)."
   Reading: A value of "other" for demonstrated_and_documented_condition_causing_infertility
   satisfies the requirement of a documented condition causing infertility while confirming
   it is not an excluded natural physiologic process (e.g., natural menopause, perimenopause,
   or male reproductive aging).

3. READING: Voluntary Sterilization.
   Text: "You or your partner has not had a voluntary sterilization with or without surgical
   reversal, regardless of post reversal results."
   Reading: If the patient has a partner, neither the patient nor the partner may have had
   a voluntary sterilization. If the patient has no partner, only the patient is checked.

4. READING: Infertility Definition for Female with Male Partner Using Donor Insemination.
   Text (Glossary): "For a female with a male partner, after: 1 year of frequent, unprotected
   heterosexual sexual intercourse if under the age of 35; 6 months... if age 35 or older"
   Text (Table): "A female under 35 [or 35+] years of age with a male partner: A. 12 [or 6]
   months or more or B. At least 12 [or 6] cycles of donor insemination"
   Reading: Reading the glossary strictly to require heterosexual intercourse would render
   Option B in the table impossible to satisfy for a female with a male partner using donor
   insemination. Therefore, failure to conceive after 12 cycles (under 35) or 6 cycles (35+)
   of donor insemination also satisfies the glossary definition for a female with a male partner.

5. READING: Infertility Definition for Male Patient with Female Partner.
   Text (Glossary): "A disease defined by the failure to become pregnant: For a female with
   a male partner, after: 1 year... if under the age of 35; 6 months... if age 35 or older"
   Reading: The glossary defines infertility for the heterosexual couple through the failure
   to become pregnant. For a male patient with a female partner, this is satisfied if the
   couple has had the required number of months of frequent heterosexual intercourse based
   on the female partner's age (12 months if < 35, 6 months if >= 35).

6. READING: Male Patient Without a Female Partner.
   Text (Table): The table only provides categories for females (with or without a male
   partner) and males with a female partner.
   Reading: While a male without a female partner can be infertile under the glossary via
   abnormal semen analyses, he cannot satisfy the text's table requirements for comprehensive
   infertility services (IUI / ovulation induction) and is therefore not covered under this benefit.

7. READING: Gender Dysphoria and Text/Table Requirements.
   Text (Glossary): "For an individual or their partner who has been clinically diagnosed with
   gender dysphoria"
   Text (Eligibility): "You have met the requirement for the number of months trying to conceive
   through egg and sperm contact. Your unmedicated day 3 Follicle Stimulating Hormone (FSH)
   level meets the following criteria: [Table]"
   Reading: A diagnosis of gender dysphoria satisfies the glossary definition of infertility,
   but does not waive the separate eligibility requirements in the text and table regarding
   egg/sperm contact (intercourse or donor insemination) and FSH testing.

8. READING: FSH Testing Requirements for Age 40 and Older.
   Text (Table): "You need to have an unmedicated day 3 FSH test done within the past: 6 months.
   If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40."
   Reading: A female patient age 40 and older must have had an unmedicated day 3 FSH test done
   within the past 6 months, all prior tests performed after age 40 must be < 19 mIU/mL, and
   her most recent test on or before the date of service must also be < 19 mIU/mL.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered service check
    # READING: Only IUI and ovulation induction with menotropins are covered comprehensive infertility services.
    covered_services = {
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    }
    if claim.get("service_type") not in covered_services:
        return False

    # 2. Demonstrated and documented condition / exclusion of natural physiologic processes
    # READING: "other" confirms an eligible condition exists and is documented, while excluding
    # natural physiologic processes such as menopause or age-related ovarian insufficiency.
    if claim.get("demonstrated_and_documented_condition_causing_infertility") != "other":
        return False

    # 3. Voluntary sterilization exclusion
    # READING: Neither patient nor partner (if present) may have had voluntary sterilization.
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

    # 4. Less costly treatment requirement
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # Basic demographics
    patient_sex = claim.get("sex_of_patient_trying_to_conceive")
    if patient_sex not in ("female", "male"):
        return False

    patient_age = h.patient_age(claim)
    if patient_age is None:
        return False

    dos = claim.get("date_service_received")
    if not dos:
        return False

    # 5. Infertility under Glossary
    # READING: Gender dysphoria satisfies the glossary definition for any patient/partner.
    has_gender_dysphoria = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"

    is_infertile = False
    if has_gender_dysphoria:
        is_infertile = True
    elif patient_sex == "female":
        if partner_sex == "male":
            frequent_months = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
            req_months = 12 if patient_age < 35 else 6
            # READING: Allow donor insemination cycles to satisfy glossary for female with male partner
            # to harmonize with Option B in the policy table.
            donor_cycles = claim.get("num_cycles_donor_insemination")
            if frequent_months is not None and frequent_months >= req_months:
                is_infertile = True
            elif donor_cycles is not None and donor_cycles >= req_months:
                is_infertile = True
        elif partner_sex in ("female", "no_partner"):
            donor_cycles = claim.get("num_cycles_donor_insemination")
            req_cycles = 12 if patient_age < 35 else 6
            if donor_cycles is not None and donor_cycles >= req_cycles:
                is_infertile = True
    elif patient_sex == "male":
        if partner_sex == "female":
            # READING: Glossary infertility for male patient with female partner is evaluated
            # symmetrically based on female partner's age and couple's frequent intercourse.
            female_partner_age = claim.get("age_of_patients_female_partner")
            if female_partner_age is not None:
                frequent_months = claim.get("num_months_frequent_unprotected_heterosexual_intercourse")
                req_months = 12 if female_partner_age < 35 else 6
                if frequent_months is not None and frequent_months >= req_months:
                    is_infertile = True
        elif partner_sex in ("male", "no_partner"):
            # READING: Male without female partner can meet glossary via semen analyses,
            # but will fail the table requirements below.
            semen_dates = claim.get("abnormal_semen_analyses")
            if semen_dates and len(semen_dates) >= 2:
                for i in range(len(semen_dates)):
                    for j in range(i + 1, len(semen_dates)):
                        if abs(h.days_between(semen_dates[i], semen_dates[j])) >= 14:
                            is_infertile = True
                            break
                    if is_infertile:
                        break

    if not is_infertile:
        return False

    # 6. Text & Table Eligibility Requirements
    # READING: Gender dysphoria does not exempt claimant from table criteria.
    def get_fsh_level(t):
        return t["level"] if isinstance(t, dict) else t[0]

    def get_fsh_date(t):
        return t["date"] if isinstance(t, dict) else t[1]

    def get_fsh_time(t):
        return t["time"] if isinstance(t, dict) else t[2]

    if patient_sex == "female":
        is_under_35 = patient_age < 35
        lookback_months = 12 if is_under_35 else 6
        req_count = 12 if is_under_35 else 6

        # Trying to conceive requirement
        if partner_sex == "male":
            timed_months = claim.get("num_months_timed_unprotected_intercourse")
            donor_cycles = claim.get("num_cycles_donor_insemination")
            timed_met = timed_months is not None and timed_months >= req_count
            donor_met = donor_cycles is not None and donor_cycles >= req_count
            if not (timed_met or donor_met):
                return False
        elif partner_sex in ("female", "no_partner"):
            donor_cycles = claim.get("num_cycles_donor_insemination")
            if donor_cycles is None or donor_cycles < req_count:
                return False
        else:
            return False

        # FSH testing requirement
        fsh_tests = claim.get("day_3_fsh_tests")
        if not fsh_tests:
            return False

        prior_fsh_tests = [t for t in fsh_tests if get_fsh_date(t) <= dos]
        if not prior_fsh_tests:
            return False

        # Must have an unmedicated day 3 FSH test done within the past 12 (or 6) months
        has_test_in_window = any(
            h.months_at_most(get_fsh_date(t), dos, lookback_months)
            for t in prior_fsh_tests
        )
        if not has_test_in_window:
            return False

        # Evaluate most recent FSH test
        max_date_time = max((get_fsh_date(t), get_fsh_time(t)) for t in prior_fsh_tests)
        most_recent_tests = [
            t for t in prior_fsh_tests
            if (get_fsh_date(t), get_fsh_time(t)) == max_date_time
        ]

        if patient_age < 40:
            if any(get_fsh_level(t) >= 19 for t in most_recent_tests):
                return False
        else:
            # READING: Age 40 and older requires all prior tests performed after age 40 to be < 19,
            # as well as the most recent test to be < 19.
            tests_since_40 = h.fsh_tests_since_age_40(claim)
            prior_tests_since_40 = [t for t in tests_since_40 if get_fsh_date(t) <= dos]
            if any(get_fsh_level(t) >= 19 for t in prior_tests_since_40):
                return False
            if any(get_fsh_level(t) >= 19 for t in most_recent_tests):
                return False

        return True

    elif patient_sex == "male":
        # READING: Male patient without a female partner has no applicable category in the table
        # for comprehensive infertility services, and is therefore not covered.
        if partner_sex != "female":
            return False

        female_partner_age = claim.get("age_of_patients_female_partner")
        if female_partner_age is None:
            return False

        req_months = 12 if female_partner_age < 35 else 6
        timed_months = claim.get("num_months_timed_unprotected_intercourse")
        if timed_months is None or timed_months < req_months:
            return False

        # FSH testing does not apply to males
        return True

    return False
