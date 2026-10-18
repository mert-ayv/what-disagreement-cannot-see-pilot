"""
Policy Coverage Rule Encoder: Cardinal Care Comprehensive Infertility Services

READING CHOICES:
1. Provider Specialist and Precertification:
   Text: "Your provider will request approval from us in advance for your infertility services. We will cover charges made by an infertility specialist for the following infertility services..."
   Reading: Per instructions, precertification and provider network/credentialing (including whether the provider is an infertility specialist) are checked elsewhere and not encoded here.

2. Harmonization of Glossary and Table for Donor Insemination with a Male Partner:
   Text: Glossary defines infertility for a female with a male partner as failure to become pregnant after "1 year of frequent, unprotected heterosexual sexual intercourse if under the age of 35 / 6 months ... if age 35 or older". The benefit table permits "A. 12 months or more or B. At least 12 cycles of donor insemination" for a female under 35 with a male partner (and 6 months / 6 cycles if 35+).
   Reading: To avoid rendering Option B in the eligibility table a nullity, donor insemination cycles (at least 12 cycles if under 35, at least 6 cycles if 35+) are recognized as satisfying the failure-to-conceive requirement for female patients with a male partner as well.

3. Meaning of "Without a Male Partner" / "Without a Female Partner":
   Text: The table specifies rules for "A female ... without a male partner" and "A male ... with a female partner". The glossary also references "a male without a female partner".
   Reading: A female patient is "without a male partner" if she has no partner or her partner is female. A male patient is "without a female partner" if he has no partner or his partner is male.

4. Time Window for FSH Test ("Within the Past 12 / 6 Months"):
   Text: "You need to have an unmedicated day 3 FSH test done within the past: 12 months / 6 months".
   Reading: "Within the past X months" is measured relative to the claim's service date. The test date must be on or before the service date and on or after the calendar date X months prior (with day clamping for months with fewer days).

5. FSH Results for Patients Age 40 and Older:
   Text: "If you are age 40 and older, must be less than 19 mIU/mL in all prior tests performed after age 40."
   Reading: For females age 40 and older, the most recent FSH test must be less than 19 mIU/mL, and any prior tests performed after age 40 must also have been less than 19 mIU/mL (captured via `all_prior_fsh_tests_after_40_under_19`).

6. Male Patients Without a Female Partner:
   Text: Glossary includes "For a male without a female partner, after: At least 2 abnormal semen analyses obtained at least 2 weeks apart". However, the benefit eligibility table lists only males with a female partner.
   Reading: A male without a female partner may satisfy the glossary definition of infertility, but does not meet the benefit eligibility table and cannot receive the female-specific covered services (ovulation induction / IUI).
"""

import calendar
import datetime

SCHEMA = {
    "service_type": "The infertility service requested, string ('ovulation_induction_with_menotropins' or 'intrauterine_insemination')",
    "service_date": "Date of service, string 'YYYY_MM_DD'",
    "patient_is_covered_student_or_partner": "Whether patient is covered as a student or legal spouse/civil union partner/domestic partner, bool",
    "has_documented_condition_causing_infertility": "Whether a condition demonstrated to cause infertility has been recognized by physician/specialist and documented in records, bool",
    "has_voluntary_sterilization": "Whether patient or partner has had voluntary sterilization (tubal ligation, vasectomy, hysterectomy for sterilization) with or without reversal, bool",
    "infertility_due_to_natural_physiologic_process": "Whether infertility is due to natural physiologic process like age-related ovarian insufficiency (e.g. perimenopause, menopause), bool",
    "pregnancy_attainable_through_less_costly_covered_treatment": "Whether successful pregnancy can be attained through less costly treatment covered under the plan, bool",
    "patient_gender": "Gender of the patient, string ('female' or 'male')",
    "patient_age": "Age of the patient in years at the time of service, int",
    "has_partner": "Whether the patient has a legal spouse, civil union partner, or domestic partner, bool",
    "partner_gender": "Gender of the patient's partner if has_partner is True, string ('female' or 'male')",
    "partner_age": "Age of the patient's partner in years, int",
    "months_of_unprotected_timed_intercourse": "Number of months of frequent, unprotected timed heterosexual intercourse trying to conceive, int",
    "donor_insemination_cycles": "Number of self-paid / not plan-paid donor artificial insemination cycles completed, int",
    "fsh_test_date": "Date of the most recent unmedicated day 3 FSH test, string 'YYYY_MM_DD'",
    "fsh_test_is_unmedicated_day_3": "Whether the FSH test was unmedicated and performed on day 3 of the menstrual cycle, bool",
    "most_recent_fsh_level": "Result of the most recent unmedicated day 3 FSH test in mIU/mL, float",
    "all_prior_fsh_tests_after_40_under_19": "Whether all prior FSH tests performed after age 40 were under 19 mIU/mL (for females age 40+), bool",
    "gender_dysphoria_diagnosed": "Whether the patient or partner has been clinically diagnosed with gender dysphoria, bool",
    "abnormal_semen_analyses_count": "Number of abnormal semen analyses obtained for a male without a female partner, int",
    "semen_analyses_at_least_2_weeks_apart": "Whether abnormal semen analyses were obtained at least 2 weeks apart, bool",
}


def _parse_date(date_str: str) -> datetime.date:
    parts = date_str.split("_")
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))


def _get_cutoff_date(d: datetime.date, months: int) -> datetime.date:
    # READING: "within the past X months" calculates the exact calendar cutoff X months prior,
    # clamping to the maximum day of the target month if needed.
    total_months = d.year * 12 + (d.month - 1) - months
    cutoff_year = total_months // 12
    cutoff_month = (total_months % 12) + 1
    max_days = calendar.monthrange(cutoff_year, cutoff_month)[1]
    cutoff_day = min(d.day, max_days)
    return datetime.date(cutoff_year, cutoff_month, cutoff_day)


def _is_within_past_months(test_date_str: str, service_date_str: str, months: int) -> bool:
    try:
        t = _parse_date(test_date_str)
        s = _parse_date(service_date_str)
    except Exception:
        return False
    if t > s:
        return False
    cutoff = _get_cutoff_date(s, months)
    return t >= cutoff


def _is_infertile_under_glossary(claim: dict) -> bool:
    """
    Evaluates whether the patient meets the definition of Infertile or Infertility under the Glossary.
    """
    # Bullet 4: Diagnosed with gender dysphoria
    if claim.get("gender_dysphoria_diagnosed") is True:
        return True

    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    has_partner = claim.get("has_partner")
    partner_gender = claim.get("partner_gender")
    partner_age = claim.get("partner_age")

    if patient_gender == "female":
        if patient_age is None:
            return False

        # READING: A female has a male partner if has_partner is True and partner_gender is 'male'.
        # Otherwise, she is without a male partner.
        has_male_partner = (has_partner is True) and (partner_gender == "male")

        months_intercourse = claim.get("months_of_unprotected_timed_intercourse")
        donor_cycles = claim.get("donor_insemination_cycles")

        threshold_months = 12 if patient_age < 35 else 6
        threshold_cycles = 12 if patient_age < 35 else 6

        if has_male_partner:
            # Bullet 1: 1 year (<35) or 6 months (>=35) of frequent unprotected heterosexual intercourse
            if months_intercourse is not None and months_intercourse >= threshold_months:
                return True
            # READING: Harmonization of glossary and table: donor insemination also recognized for female with male partner
            if donor_cycles is not None and donor_cycles >= threshold_cycles:
                return True
            return False
        else:
            # Bullet 2: At least 12 cycles (<35) or 6 cycles (>=35) of donor insemination
            if donor_cycles is not None and donor_cycles >= threshold_cycles:
                return True
            return False

    elif patient_gender == "male":
        # Check if male has a female partner
        has_female_partner = (has_partner is True) and (partner_gender == "female")

        if has_female_partner:
            if partner_age is None:
                return False
            threshold_months = 12 if partner_age < 35 else 6
            months_intercourse = claim.get("months_of_unprotected_timed_intercourse")
            if months_intercourse is not None and months_intercourse >= threshold_months:
                return True
            return False
        else:
            # Bullet 3: Male without a female partner: at least 2 abnormal semen analyses >= 2 weeks apart
            abnormal_count = claim.get("abnormal_semen_analyses_count")
            at_least_2_weeks = claim.get("semen_analyses_at_least_2_weeks_apart")
            if abnormal_count is not None and abnormal_count >= 2 and at_least_2_weeks is True:
                return True
            return False

    return False


def covered_under_benefit(claim: dict) -> bool:
    """
    Determines whether a claim is covered under the Comprehensive Infertility Services benefit.
    """
    # 1. Covered services: Ovulation induction with menotropins or Intrauterine insemination
    service_type = claim.get("service_type")
    if service_type not in ("ovulation_induction_with_menotropins", "intrauterine_insemination"):
        return False

    # 2. READING: Precertification and provider network/specialist checks are handled elsewhere.
    # We do not evaluate provider_is_infertility_specialist here.

    # 3. Patient coverage eligibility: student or eligible covered partner
    if claim.get("patient_is_covered_student_or_partner") is not True:
        return False

    # 4. Documented condition demonstrated to cause infertility
    if claim.get("has_documented_condition_causing_infertility") is not True:
        return False

    # 5. Exclusion: voluntary sterilization with or without reversal
    if claim.get("has_voluntary_sterilization") is not False:
        return False

    # 6. Exclusion: infertility due to natural physiologic process (e.g. perimenopause, menopause)
    if claim.get("infertility_due_to_natural_physiologic_process") is not False:
        return False

    # 7. Cost-effective alternative: pregnancy cannot be attained through less costly covered treatment
    if claim.get("pregnancy_attainable_through_less_costly_covered_treatment") is not False:
        return False

    # 8. Must satisfy the glossary definition of Infertile or Infertility
    if not _is_infertile_under_glossary(claim):
        return False

    # 9. Table requirements: conception attempt and FSH criteria
    patient_gender = claim.get("patient_gender")
    patient_age = claim.get("patient_age")
    has_partner = claim.get("has_partner")
    partner_gender = claim.get("partner_gender")
    partner_age = claim.get("partner_age")

    if patient_age is None or patient_gender is None:
        return False

    months_intercourse = claim.get("months_of_unprotected_timed_intercourse")
    donor_cycles = claim.get("donor_insemination_cycles")

    if patient_gender == "female":
        if has_partner is None:
            return False
        # READING: Female without a male partner includes single females and females with a female partner.
        has_male_partner = (has_partner is True) and (partner_gender == "male")

        # Determine age bracket thresholds
        is_under_35 = patient_age < 35
        req_months = 12 if is_under_35 else 6
        req_cycles = 12 if is_under_35 else 6
        fsh_window_months = 12 if is_under_35 else 6

        # Check egg and sperm contact requirement
        if has_male_partner:
            # Table: A. 12/6 months or more intercourse OR B. At least 12/6 cycles donor insemination
            conception_met = False
            if months_intercourse is not None and months_intercourse >= req_months:
                conception_met = True
            if donor_cycles is not None and donor_cycles >= req_cycles:
                conception_met = True
            if not conception_met:
                return False
        else:
            # Table: Intercourse does not apply; at least 12/6 cycles donor insemination
            if donor_cycles is None or donor_cycles < req_cycles:
                return False

        # Check FSH test criteria
        service_date = claim.get("service_date")
        fsh_test_date = claim.get("fsh_test_date")
        if not service_date or not fsh_test_date:
            return False

        if claim.get("fsh_test_is_unmedicated_day_3") is not True:
            return False

        if not _is_within_past_months(fsh_test_date, service_date, fsh_window_months):
            return False

        fsh_level = claim.get("most_recent_fsh_level")
        if fsh_level is None or fsh_level >= 19.0:
            return False

        # READING: For females age 40 and older, all prior tests after age 40 must also be < 19 mIU/mL.
        if patient_age >= 40:
            if claim.get("all_prior_fsh_tests_after_40_under_19") is not True:
                return False

        return True

    elif patient_gender == "male":
        # READING: The eligibility table contains rows only for a male of any age with a female partner.
        # A male without a female partner has no applicable eligibility criteria under the table.
        if has_partner is not True or partner_gender != "female":
            return False

        if partner_age is None:
            return False

        req_months = 12 if partner_age < 35 else 6
        if months_intercourse is None or months_intercourse < req_months:
            return False

        # For males, donor insemination and FSH test requirements "Do not apply"
        return True

    return False
