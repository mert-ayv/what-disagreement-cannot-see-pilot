"""
Policy Coverage Implementation: Cardinal Care 2023-2024 Comprehensive Infertility Services

Readings and Interpretations Adopted:
1. READING: Covered Services:
   Text: "We will cover charges made by an infertility specialist for the following infertility services:
   • Ovulation induction cycle(s) with menotropins • Intrauterine insemination"
   Reading: Only "ovulation_induction_cycle_with_menotropins" and "intrauterine_insemination" are covered
   under this benefit.

2. READING: Demonstrated Condition vs. Natural Physiologic Process Exclusion:
   Text: "There exists a condition that: Is demonstrated to cause the illness of infertility. Has been recognized
   by your physician or infertility specialist and documented in your or your partner’s medical records."
   and "You or your partner does not have infertility that is due to a natural physiologic process such as age
   related ovarian insufficiency (e.g. perimenopause, menopause)."
   Reading: If `demonstrated_and_documented_condition_causing_infertility` is one of the natural physiologic
   processes ("natural_menopause", "natural_perimenopause", "natural_male_reproductive_aging", or
   "other_natural_physiologic_process"), it is excluded. Only "other" satisfies both the requirement of a documented
   demonstrated condition and the non-natural physiologic process requirement.

3. READING: Voluntary Sterilization:
   Text: "You or your partner has not had a voluntary sterilization with or without surgical reversal..."
   Reading: The patient must not have had voluntary sterilization (`patient_has_had_voluntary_sterilization == "no"`).
   If the patient has a partner (`sex_of_patients_partner` is "male" or "female"), the partner must also not have had
   voluntary sterilization (`partner_has_had_voluntary_sterilization == "no"`). If the patient has no partner,
   the partner sterilization requirement is not applicable.

4. READING: Alternative Less Costly Treatment:
   Text: "A successful pregnancy cannot be attained through less costly treatment for which coverage is available under this plan."
   Reading: `successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan` must be "no".

5. READING: Harmonization of Donor Insemination for Female with Male Partner:
   Text: The benefit table explicitly allows "A. 12 months or more or B. At least 12 cycles of donor insemination" (or 6 months / 6 cycles
   for age 35+) for a female with a male partner. The glossary defines infertility for a female with a male partner through intercourse,
   and for a female without a male partner through donor insemination.
   Reading: To prevent Option B of the table from being illusory for couples needing donor insemination (e.g., male factor azoospermia),
   a female with a male partner who satisfies the donor insemination cycle requirement satisfies both the table requirement and the
   glossary definition of infertility.

6. READING: Intercourse Reporting (Timed vs. Frequent):
   Text: The glossary specifies "frequent, unprotected heterosexual sexual intercourse" while the table specifies "unprotected timed
   sexual intercourse".
   Reading: Timed intercourse to achieve pregnancy constitutes frequent intercourse, and frequent intercourse during the fertile window
   is timed intercourse. Satisfying the duration threshold (12 months if female < 35, 6 months if female >= 35) under either
   `num_months_timed_unprotected_intercourse` or `num_months_frequent_unprotected_heterosexual_intercourse` satisfies both requirements.

7. READING: Missing Age of Female Partner for Male Patient:
   Text: Table requires 12 months if female partner is under 35, and 6 months if 35 or older.
   Reading: If the female partner's age is not provided but the intercourse duration is at least 12 months, the requirement
   is satisfied regardless of partner age because 12 months meets both thresholds.

8. READING: Male Patient Without a Female Partner:
   Text: The glossary defines infertility "For a male without a female partner, after: At least 2 abnormal semen analyses obtained
   at least 2 weeks apart" or diagnosis of gender dysphoria. The table contains no row imposing intercourse or FSH requirements on
   males without female partners.
   Reading: A male without a female partner is eligible if he meets the glossary definition (at least two abnormal semen analyses
   at least 14 days apart, or gender dysphoria); the table intercourse and FSH requirements do not apply to him.

9. READING: FSH Test Window and Multiple Test Results:
   Text: "You need to have an unmedicated day 3 FSH test done within the past: 12 months / 6 months" and
   "Must be less than 19 mIU/mL in your most recent lab test" / "all prior tests performed after age 40".
   Reading: Tests must be performed on or before the date of service, within the specified calendar months using `h.months_at_most`.
   Where multiple test results exist for the same timestamp (e.g., re-runs or split samples), the member-favorable lowest result
   is taken. For patients age 40 and older, all distinct test timestamps after age 40 up to the date of service must have results < 19 mIU/mL.
"""

from collections import defaultdict


def covered_under_benefit(claim: dict, h) -> bool:
    # 1. Covered Services
    # READING: Only ovulation induction with menotropins and intrauterine insemination are covered.
    service_type = claim.get("service_type")
    if service_type not in (
        "intrauterine_insemination",
        "ovulation_induction_cycle_with_menotropins",
    ):
        return False

    # 2. Condition causing infertility / Natural physiologic process exclusion
    # READING: Condition must be documented and not due to natural physiologic process (only "other" qualifies).
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition != "other":
        return False

    # 3. Voluntary Sterilization
    # READING: Patient and (if present) partner must not have had voluntary sterilization.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False

    partner_sex = claim.get("sex_of_patients_partner")
    if partner_sex not in ("male", "female", "no_partner"):
        return False

    if partner_sex in ("male", "female"):
        if claim.get("partner_has_had_voluntary_sterilization") != "no":
            return False

    # 4. Less Costly Treatment
    # READING: Successful pregnancy cannot be attained through less costly covered treatment.
    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # Date of service received is required for temporal calculations
    service_date = claim.get("date_service_received")
    if not service_date:
        return False

    # Gender dysphoria diagnosis satisfies glossary definition of infertility for anyone
    has_gender_dysphoria = (
        claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    )

    sex_of_patient = claim.get("sex_of_patient_trying_to_conceive")
    if sex_of_patient not in ("female", "male"):
        return False

    # ---------------------------------------------------------
    # FEMALE PATIENT
    # ---------------------------------------------------------
    if sex_of_patient == "female":
        age = h.patient_age(claim)
        if age is None:
            return False

        # Determine thresholds based on age and partner
        if partner_sex == "male":
            if age < 35:
                req_intercourse_months = 12
                req_donor_cycles = 12
                req_fsh_window_months = 12
            else:
                req_intercourse_months = 6
                req_donor_cycles = 6
                req_fsh_window_months = 6

            # READING: Intercourse duration evaluated via either timed or frequent intercourse field.
            intercourse_months = max(
                claim.get("num_months_timed_unprotected_intercourse") or 0,
                claim.get("num_months_frequent_unprotected_heterosexual_intercourse") or 0,
            )
            donor_cycles = claim.get("num_cycles_donor_insemination") or 0

            # READING: Harmonization of Option B: donor insemination qualifies female with male partner.
            intercourse_met = intercourse_months >= req_intercourse_months
            donor_met = donor_cycles >= req_donor_cycles

            if not (intercourse_met or donor_met):
                return False

        else:
            # Female without a male partner (female partner or no partner)
            if age < 35:
                req_donor_cycles = 12
                req_fsh_window_months = 12
            else:
                req_donor_cycles = 6
                req_fsh_window_months = 6

            donor_cycles = claim.get("num_cycles_donor_insemination") or 0
            if donor_cycles < req_donor_cycles:
                return False

        # FSH Test Evaluation for Female Patients
        fsh_tests = claim.get("day_3_fsh_tests")
        if not fsh_tests:
            return False

        # Filter tests performed on or before the date of service
        valid_tests = [t for t in fsh_tests if t[1] <= service_date]
        if not valid_tests:
            return False

        # Must have an unmedicated day 3 FSH test done within the past 12 or 6 months
        has_recent_test = any(
            h.months_at_most(t[1], service_date, req_fsh_window_months)
            for t in valid_tests
        )
        if not has_recent_test:
            return False

        # READING: Most recent test level: if multiple tests share the latest timestamp, take favorable minimum.
        latest_timestamp = max((t[1], t[2]) for t in valid_tests)
        latest_tests = [t for t in valid_tests if (t[1], t[2]) == latest_timestamp]
        if not any(t[0] < 19 for t in latest_tests):
            return False

        # For age 40 and older: must be less than 19 mIU/mL in all prior tests performed after age 40
        if age >= 40:
            tests_since_40 = [
                t for t in h.fsh_tests_since_age_40(claim) if t[1] <= service_date
            ]
            tests_by_ts = defaultdict(list)
            for t in tests_since_40:
                tests_by_ts[(t[1], t[2])].append(t[0])

            # Every distinct test timestamp after age 40 must have a passing result (< 19)
            for ts, levels in tests_by_ts.items():
                if min(levels) >= 19:
                    return False

        return True

    # ---------------------------------------------------------
    # MALE PATIENT
    # ---------------------------------------------------------
    else:
        if partner_sex == "female":
            partner_age = claim.get("age_of_patients_female_partner")
            intercourse_months = max(
                claim.get("num_months_timed_unprotected_intercourse") or 0,
                claim.get("num_months_frequent_unprotected_heterosexual_intercourse") or 0,
            )

            # READING: If partner age is missing but intercourse duration is >= 12 months,
            # it satisfies both < 35 and >= 35 thresholds.
            if partner_age is not None:
                req_months = 12 if partner_age < 35 else 6
                if intercourse_months < req_months:
                    return False
            else:
                if intercourse_months < 12:
                    return False

            # FSH does not apply to male patients under the table.
            return True

        else:
            # Male without a female partner (male partner or no partner)
            # READING: Evaluated under glossary definition for male without female partner;
            # table intercourse and FSH do not apply.
            analyses = claim.get("abnormal_semen_analyses") or []
            has_two_abnormal_semen = False
            for i in range(len(analyses)):
                for j in range(i + 1, len(analyses)):
                    if abs(h.days_between(analyses[i], analyses[j])) >= 14:
                        has_two_abnormal_semen = True
                        break
                if has_two_abnormal_semen:
                    break

            if not (has_gender_dysphoria or has_two_abnormal_semen):
                return False

            return True
