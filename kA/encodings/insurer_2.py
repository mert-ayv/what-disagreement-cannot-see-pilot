"""Cardinal Care 2023-2024, Comprehensive infertility services: insurer-favourable encoding.

READING choices (each marked "# READING:" in the code):

1. Missing fields: an unknown fact required for coverage is treated as not established (claim denied).
2. Student / partner enrollment ("covered under this plan as a student or as a covered dependent"):
   no claim field exists; enrollment status is taken as checked by the eligibility system and not encoded.
3. Male patient with a female partner: the glossary has no clause for him; his infertility is read
   through the couple ("failure to become pregnant" of his female partner under the "female with a male
   partner" clause, using her age). The semen-analysis clause applies only to "a male without a female
   partner".
4. Female with a male partner: the glossary requires "frequent, unprotected heterosexual sexual
   intercourse" months; donor insemination cycles do not satisfy the glossary for her (they satisfy only
   the table's option B), unless gender dysphoria applies.
5. "1 year" means 12 months; "6 cycles" (glossary) means at least 6 cycles.
6. Gender dysphoria satisfies only the glossary definition; every table requirement still applies.
7. Male without a female partner: the table has no row for him, so the requirement in "You have met
   the requirement for the number of months trying to conceive" cannot be met; not eligible.
8. Ages ("under 35", "35 years of age or older", "less than age 40") are taken on the date of service.
9. "Natural physiologic process such as age related ovarian insufficiency": the listed items are
   examples; every natural process value (including male reproductive aging) excludes coverage. Only a
   documented "other" condition qualifies.
10. Sterilization: both patient and (if there is a partner) partner must be known not to have had a
    voluntary sterilization; a "yes" for either denies, even when no partner is recorded.
11. FSH "within the past N months" and "most recent lab test" are measured back from the date of
    service; tests after the date of service are not "past" or "prior" tests.
12. Several FSH tests sharing the most recent date and time: each of them must be below 19.
13. "Less than 19 mIU/mL in all prior tests performed after age 40": "after age 40" includes tests on or
    after the 40th birthday, and at least one such test must exist.
14. Semen analyses "at least 2 weeks apart": two analyses at least 14 days apart, both on or before the
    date of service.
15. Table months and cycles thresholds ("12 months or more", "At least 12 cycles") are inclusive.
"""

COVERED_SERVICES = {
    "intrauterine_insemination",
    "ovulation_induction_cycle_with_menotropins",
}

NATURAL_PROCESS_VALUES = {
    "natural_menopause",
    "natural_perimenopause",
    "natural_male_reproductive_aging",
    "other_natural_physiologic_process",
}


def _int_field(claim, name):
    v = claim.get(name)
    return v if isinstance(v, int) else None


def _prior_fsh_tests(claim, h, service_date):
    tests = []
    for t in claim.get("day_3_fsh_tests") or []:
        try:
            level, date, time = t[0], t[1], t[2]
        except (TypeError, IndexError):
            continue
        # READING: "within the past" / "most recent" / "prior tests" are anchored at the date of
        # service; a test dated after the service is not a past or prior test.
        if h.days_between(date, service_date) >= 0:
            tests.append((level, date, time))
    return tests


def _fsh_ok(claim, h, age, service_date, window_months):
    tests = _prior_fsh_tests(claim, h, service_date)
    if not tests:
        return False
    # "You need to have an unmedicated day 3 FSH test done within the past: 12 months / 6 months"
    if not any(h.months_at_most(t[1], service_date, window_months) for t in tests):
        return False
    latest_key = max((t[1], t[2]) for t in tests)
    latest = [t for t in tests if (t[1], t[2]) == latest_key]
    if age < 40:
        # READING: "Must be less than 19 mIU/mL in your most recent lab test" with several tests at
        # the same most recent date and time: every one of them must be below 19.
        return all(t[0] < 19 for t in latest)
    # READING: "must be less than 19 mIU/mL in all prior tests performed after age 40": "after age
    # 40" covers tests on or after the 40th birthday, and at least one such prior test must exist.
    since_40 = []
    for t in h.fsh_tests_since_age_40(claim):
        try:
            level, date = t[0], t[1]
        except (TypeError, IndexError):
            continue
        if h.days_between(date, service_date) >= 0:
            since_40.append(level)
    if not since_40:
        return False
    return all(level < 19 for level in since_40) and all(t[0] < 19 for t in latest)


def _semen_analyses_ok(claim, h, service_date):
    dates = [d for d in (claim.get("abnormal_semen_analyses") or [])
             if h.days_between(d, service_date) >= 0]
    if len(dates) < 2:
        return False
    dates.sort()
    # READING: "At least 2 abnormal semen analyses obtained at least 2 weeks apart": two analyses at
    # least 14 days apart, both obtained on or before the date of service.
    return h.days_between(dates[0], dates[-1]) >= 14


def covered_under_benefit(claim: dict, h) -> bool:
    # Service must be one of the listed covered infertility services.
    if claim.get("service_type") not in COVERED_SERVICES:
        return False

    service_date = claim.get("date_service_received")
    if service_date is None:
        return False

    # READING: missing fields. "A missing field means the fact is unknown"; a required fact that is
    # unknown is not established, so the claim is not covered.

    # READING: "You are covered under this plan as a student or as a covered dependent who is the
    # student's legal spouse...": no claim field records enrollment status; it is left to the
    # eligibility system and not encoded here.

    # READING: ages "under 35 years of age", "35 years of age or older", "less than age 40" are
    # measured on the date of service.
    age = h.patient_age(claim)
    if age is None:
        return False

    sex = claim.get("sex_of_patient_trying_to_conceive")
    partner = claim.get("sex_of_patients_partner")
    if sex not in ("female", "male") or partner not in ("male", "female", "no_partner"):
        return False

    gender_dysphoria = claim.get("patient_or_partner_diagnosed_with_gender_dysphoria") == "yes"
    months_frequent = _int_field(claim, "num_months_frequent_unprotected_heterosexual_intercourse")
    months_timed = _int_field(claim, "num_months_timed_unprotected_intercourse")
    di_cycles = _int_field(claim, "num_cycles_donor_insemination")

    # ---------------- Condition, sterilization, natural process, less costly treatment ----------
    condition = claim.get("demonstrated_and_documented_condition_causing_infertility")
    if condition is None:
        return False
    # READING: "does not have infertility that is due to a natural physiologic process such as age
    # related ovarian insufficiency (e.g. perimenopause, menopause)": the named items are examples;
    # every natural physiologic process, including male reproductive aging, excludes coverage.
    if condition in NATURAL_PROCESS_VALUES or condition != "other":
        return False

    # READING: "You or your partner has not had a voluntary sterilization": the patient must be
    # known not to be sterilized; a partner, if any, must also be known not to be; a recorded "yes"
    # for the partner denies even if no partner is recorded.
    if claim.get("patient_has_had_voluntary_sterilization") != "no":
        return False
    partner_steril = claim.get("partner_has_had_voluntary_sterilization")
    if partner_steril == "yes":
        return False
    if partner != "no_partner" and partner_steril != "no":
        return False

    if claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") != "no":
        return False

    # ---------------- Glossary: infertile or infertility ---------------------------------------
    infertile = gender_dysphoria
    # READING: gender dysphoria ("For an individual or their partner who has been clinically
    # diagnosed with gender dysphoria") satisfies only the glossary; the table still applies.

    if sex == "female":
        if partner == "male":
            # READING: "For a female with a male partner, after: 1 year of frequent, unprotected
            # heterosexual sexual intercourse": "1 year" is 12 months; only intercourse months
            # count toward the glossary, donor insemination cycles do not.
            need = 12 if age < 35 else 6
            if months_frequent is not None and months_frequent >= need:
                infertile = True
        else:
            # "For a female without a male partner, after: At least 12 cycles / 6 cycles of donor
            # insemination". READING: "6 cycles" means at least 6 cycles.
            need = 12 if age < 35 else 6
            if di_cycles is not None and di_cycles >= need:
                infertile = True
    else:  # male
        if partner == "female":
            # READING: the glossary has no clause for "a male with a female partner"; his
            # infertility is the couple's "failure to become pregnant" under the "female with a male
            # partner" clause, using his female partner's age. The semen-analysis clause is limited
            # to "a male without a female partner" and does not apply to him.
            fp_age = _int_field(claim, "age_of_patients_female_partner")
            if fp_age is None:
                return False
            need = 12 if fp_age < 35 else 6
            if months_frequent is not None and months_frequent >= need:
                infertile = True
        else:
            if _semen_analyses_ok(claim, h, service_date):
                infertile = True

    if not infertile:
        return False

    # ---------------- Table: months trying to conceive and FSH --------------------------------
    # READING: thresholds "12 months or more" / "At least 12 cycles" are inclusive.
    if sex == "female":
        if age < 35:
            need, window = 12, 12
        else:
            need, window = 6, 6
        if partner == "male":
            # "A. 12 months or more or B. At least 12 cycles of donor insemination"
            met = ((months_timed is not None and months_timed >= need)
                   or (di_cycles is not None and di_cycles >= need))
        else:
            # "Does not apply" / "At least 12 cycles of donor insemination"
            met = di_cycles is not None and di_cycles >= need
        if not met:
            return False
        if not _fsh_ok(claim, h, age, service_date, window):
            return False
        return True

    # male
    if partner == "female":
        fp_age = _int_field(claim, "age_of_patients_female_partner")
        if fp_age is None:
            return False
        need = 12 if fp_age < 35 else 6
        # "A male of any age with a female partner under 35 years of age: 12 months or more";
        # donor insemination and FSH "Does not apply".
        return months_timed is not None and months_timed >= need

    # READING: "You have met the requirement for the number of months trying to conceive" and the
    # table rows "You are: ..." list the eligible categories; a male without a female partner has no
    # row, so no requirement can be met and he is not eligible.
    return False
