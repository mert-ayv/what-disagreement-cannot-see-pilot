"""
Policy Coverage Rules: Comprehensive Infertility Services
Cardinal Care 2023-2024 Certificate of Coverage, pp. 62-64

READING choices made (insurer-favorable readings):
1. READING: Covered services ("We will cover charges made by an infertility specialist for the following infertility services: Ovulation induction cycle(s) with menotropins; Intrauterine insemination"):
   Only service_type == "intrauterine_insemination" or "ovulation_induction_cycle_with_menotropins" are covered.
2. READING: Demonstrable condition causing infertility ("There exists a condition that: Is demonstrated to cause the illness of infertility... You or your partner does not have infertility that is due to a natural physiologic process..."):
   The claim field demonstrated_and_documented_condition_causing_infertility must be "other". Values indicating natural physiologic processes ("natural_menopause", "natural_perimenopause", "natural_male_reproductive_aging", "other_natural_physiologic_process") or an absent/unknown field fail coverage.
3. READING: Voluntary sterilization ("You or your partner has not had a voluntary sterilization with or without surgical reversal..."):
   Both patient_has_had_voluntary_sterilization must be "no", and partner_has_had_voluntary_sterilization must be "no" (if a partner exists). Any missing/unknown status fails coverage.
4. READING: Less costly treatment ("A successful pregnancy cannot be attained through less costly treatment for which coverage is available under this plan"):
   successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan must be explicitly "no". Unknown/missing status fails coverage.
5. READING: Glossary definition of infertility vs. policy table requirements:
   The glossary definition of infertility and the text/table eligibility requirements are cumulative independent requirements.
6. READING: Intercourse requirements ("frequent, unprotected heterosexual sexual intercourse" in glossary vs. "unprotected timed sexual intercourse" in table):
   These are distinct requirements. Where timed intercourse is required by the table and frequent intercourse is required by the glossary, both must be satisfied.
7. READING: Female with male partner using donor insemination:
   Under the glossary, donor insemination only defines infertility for "a female without a male partner". For a female with a male partner, donor insemination can satisfy the table requirement, but she must still independently satisfy the glossary definition of infertility (via frequent unprotected heterosexual intercourse or a diagnosis of gender dysphoria).
8. READING: Male patient with female partner:
   A male patient with a female partner qualifies under the glossary definition for heterosexual couples ("For a female with a male partner") based on the female partner's age (12 months if partner < 35, 6 months if partner >= 35) or via gender dysphoria; he must additionally satisfy the table's requirement of timed unprotected intercourse (12 months if partner < 35, 6 months if partner >= 35).
9. READING: Male patient without female partner:
   A male patient without a female partner is not listed in the table of eligible categories and requirements in the policy text and therefore cannot qualify for comprehensive infertility services.
10. READING: FSH test criteria ("done within the past 12/6 months" and "all prior tests performed after age 40"):
    For female patients, the required test must have occurred on or before the service date within the preceding 12 months (< 35) or 6 months (>= 35). If under 40, all tests sharing the most recent timestamp must be < 19 mIU/mL. For females age 40 and older, there must be at least one test performed after age 40 within the 6-month window, and every prior test performed after age 40 on or before the service date must be < 19 mIU/mL.
"""


def covered_under_benefit(claim: dict, h) -> bool:
  # 1. Covered service type check
  # READING: Only ovulation induction with menotropins and intrauterine insemination are covered.
  service_type = claim.get("service_type")
  if service_type not in (
      "intrauterine_insemination",
      "ovulation_induction_cycle_with_menotropins",
  ):
    return False

  # 2. Condition demonstrated and documented, not due to natural physiologic process
  # READING: Must be "other" (documented condition, not natural physiologic process).
  cond = claim.get("demonstrated_and_documented_condition_causing_infertility")
  if cond != "other":
    return False

  # 3. Voluntary sterilization exclusion
  # READING: Neither patient nor partner may have had voluntary sterilization; missing fails.
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

  # 4. Less costly treatment
  # READING: Must be explicitly "no"; missing fails.
  if (
      claim.get(
          "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan"
      )
      != "no"
  ):
    return False

  patient_sex = claim.get("sex_of_patient_trying_to_conceive")
  if patient_sex not in ("female", "male"):
    return False

  patient_age = h.patient_age(claim)
  if patient_age is None:
    return False

  service_date = claim.get("date_service_received")
  if not service_date:
    return False

  has_gd = (
      claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
  )

  # Check eligibility by category
  if patient_sex == "female" and partner_sex == "male":
    # Glossary infertility check:
    # READING: For female with male partner, glossary requires frequent heterosexual intercourse
    # unless diagnosed with gender dysphoria; donor insemination does not establish infertility in glossary.
    if not has_gd:
      freq_months = claim.get(
          "num_months_frequent_unprotected_heterosexual_intercourse"
      )
      if freq_months is None:
        return False
      req_freq = 12 if patient_age < 35 else 6
      if freq_months < req_freq:
        return False

    # Table trying to conceive requirement:
    timed_months = claim.get("num_months_timed_unprotected_intercourse")
    donor_cycles = claim.get("num_cycles_donor_insemination")
    req_threshold = 12 if patient_age < 35 else 6
    meets_intercourse = (
        timed_months is not None and timed_months >= req_threshold
    )
    meets_donor = donor_cycles is not None and donor_cycles >= req_threshold
    if not (meets_intercourse or meets_donor):
      return False

    # Table FSH requirement
    if not _meets_fsh_criteria(claim, h, patient_age, service_date):
      return False

    return True

  elif patient_sex == "female" and partner_sex in ("female", "no_partner"):
    # Glossary infertility check:
    # Requires 12 cycles (< 35) or 6 cycles (>= 35) of donor insemination, unless gender dysphoria.
    donor_cycles = claim.get("num_cycles_donor_insemination")
    req_cycles = 12 if patient_age < 35 else 6
    if not has_gd:
      if donor_cycles is None or donor_cycles < req_cycles:
        return False

    # Table trying to conceive requirement:
    if donor_cycles is None or donor_cycles < req_cycles:
      return False

    # Table FSH requirement
    if not _meets_fsh_criteria(claim, h, patient_age, service_date):
      return False

    return True

  elif patient_sex == "male" and partner_sex == "female":
    partner_age = claim.get("age_of_patients_female_partner")
    if partner_age is None:
      return False

    req_months = 12 if partner_age < 35 else 6

    # Glossary infertility check:
    # READING: Heterosexual couple failure to conceive applies based on female partner's age.
    if not has_gd:
      freq_months = claim.get(
          "num_months_frequent_unprotected_heterosexual_intercourse"
      )
      if freq_months is None or freq_months < req_months:
        return False

    # Table trying to conceive requirement:
    timed_months = claim.get("num_months_timed_unprotected_intercourse")
    if timed_months is None or timed_months < req_months:
      return False

    # FSH does not apply to males in table
    return True

  else:
    # READING: Male patient without a female partner is not included in the policy table
    # of eligible categories and requirements for comprehensive infertility services.
    return False


def _meets_fsh_criteria(claim: dict, h, patient_age: int, service_date: str) -> bool:
  """Evaluates whether the patient's FSH tests satisfy the policy table criteria."""
  fsh_tests = claim.get("day_3_fsh_tests")
  if not fsh_tests:
    return False

  # Filter to unmedicated day 3 FSH tests on or prior to the date of service
  prior_tests = [t for t in fsh_tests if t[1] <= service_date]
  if not prior_tests:
    return False

  # Determine most recent test timestamp (date, time)
  max_timestamp = max((t[1], t[2]) for t in prior_tests)
  most_recent_tests = [t for t in prior_tests if (t[1], t[2]) == max_timestamp]

  # Timing requirement: within past 12 months (if < 35) or 6 months (if >= 35)
  req_fsh_months = 12 if patient_age < 35 else 6
  if not h.months_at_most(max_timestamp[0], service_date, req_fsh_months):
    return False

  if patient_age < 40:
    # READING: All tests sharing the most recent timestamp must be < 19 mIU/mL
    if any(t[0] >= 19 for t in most_recent_tests):
      return False
  else:
    # Patient is age 40 and older:
    # READING: Must have at least one test performed after age 40 on or before service date,
    # and all prior tests performed after age 40 on or before service date must be < 19 mIU/mL.
    tests_since_40 = h.fsh_tests_since_age_40(claim)
    tests_since_40_prior = [t for t in tests_since_40 if t[1] <= service_date]
    if not tests_since_40_prior:
      return False
    if any(t[0] >= 19 for t in tests_since_40_prior):
      return False

  return True
