# kB results: gemini

Grid: 1,814,400 cases. Encodings: insurer_1, insurer_2, insurer_3, member_1, member_2, member_3, neutral_1, neutral_2, neutral_3.

## Admissibility (encoding + adapter, ASSUMED_MET set to met; same rule as kA)

| Encoding | Clear examples failed | Failed on recorded points | Grid crashes | Agreement with expert | Undetermined (met vs unknown differ) | SCHEMA fields | ASSUMED_MET |
|---|---|---|---|---|---|---|---|
| insurer_1 | 4 ['comprehensive_not_covered1b', 'comprehensive_not_covered2c', 'comprehensive_not_covered3b'] | 14 | 0 | 0.9717 | 2.83% | 18 | provider_is_infertility_specialist, patient_is_student_or_covered_dependent_partner |
| insurer_2 | 0 [] | 4 | 0 | 0.9826 | 1.66% | 20 | provider_is_infertility_specialist, patient_coverage_status |
| insurer_3 | 0 [] | 14 | 0 | 0.9735 | 2.65% | 18 | patient_is_covered_student_or_dependent_partner, provider_is_infertility_specialist |
| member_1 | 4 ['comprehensive_not_covered1b', 'comprehensive_not_covered2c', 'comprehensive_not_covered3b'] | 14 | 0 | 0.9695 | 3.05% | 17 | patient_is_covered_student_or_partner, provider_is_infertility_specialist |
| member_2 | 0 [] | 14 | 0 | 0.9636 | 3.64% | 18 | covered_person_role, provider_is_infertility_specialist |
| member_3 | 5 ['comprehensive_covered1a', 'comprehensive_covered1c', 'comprehensive_covered2a'] | 13 | 0 | 0.9636 | 3.63% | 18 | is_covered_student_or_partner |
| neutral_1 | 0 [] | 7 | 0 | 0.9680 | 3.12% | 19 | covered_role, provider_is_infertility_specialist |
| neutral_2 | 4 ['comprehensive_not_covered1b', 'comprehensive_not_covered2c', 'comprehensive_not_covered3b'] | 14 | 0 | 0.9713 | 2.87% | 17 | provider_is_infertility_specialist, patient_is_covered_student_or_partner |
| neutral_3 | 0 [] | 14 | 0 | 0.9731 | 2.69% | 21 | patient_is_covered_student_or_partner |

Inadmissible role encodings: 3 of 6 ['insurer_1', 'member_1', 'member_3']

## Slack and neutral disagreement

Any-pair slack: 35,998. Strict slack: 17,958. Neutral disagreement: 26,790.

| Point | Any-pair | Strict | Neutral disagreement |
|---|---|---|---|
| F1/P3 male with female partner | 14,400 | 0 | 7,200 |
| F4 male without female partner | 17,280 | 17,280 | 17,280 |
| F2 age 40+, no test since 40 | 322 | 42 | 154 |
| F5 tied latest FSH tests | 564 | 84 | 292 |
| F6 partner sterilized, patient not | 0 | 0 | 0 |
| F7 timed vs frequent across threshold | 18,040 | 0 | 8,832 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 678 | 678 | 678 |
| (no recorded point) | 0 | 0 | 0 |

Recovered representable points (strict, any case on the point): 3 of 6 ['F4 male without female partner', 'F2 age 40+, no test since 40', 'F5 tied latest FSH tests']
Recovered with cases where the point is the only one involved: 1 of 6 ['F4 male without female partner']

## Direction: share covered per point (expert / neutral / member / insurer; admissible encodings)

| Point | Expert | Neutral | Member | Insurer |
|---|---|---|---|---|
| F1/P3 male with female partner | 0.039 | 0.040 | 0.047 | 0.033 |
| F4 male without female partner | 0.000 | 0.033 | 0.067 | 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.018 | 0.019 | 0.017 |
| F5 tied latest FSH tests | 0.000 | 0.047 | 0.049 | 0.044 |
| F6 partner sterilized, patient not | 0.043 | 0.000 | 0.000 | 0.000 |
| F7 timed vs frequent across threshold | 0.005 | 0.042 | 0.056 | 0.028 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 0.000 | 0.018 | 0.036 | 0.000 |

## Interface: SCHEMA fields per encoding

- insurer_1: abnormal_semen_analyses_count, all_prior_fsh_tests_after_40_under_19, diagnosed_with_gender_dysphoria, donor_insemination_cycles, has_documented_infertility_causing_condition, infertility_due_to_natural_physiologic_process, months_unprotected_timed_intercourse, partner_age, partner_sex, patient_age, patient_is_student_or_covered_dependent_partner, patient_or_partner_has_voluntary_sterilization, patient_sex, pregnancy_attainable_through_less_costly_covered_treatment, provider_is_infertility_specialist, service_type, unmedicated_day3_fsh_most_recent_value, unmedicated_day3_fsh_test_months_ago
- insurer_2: clinical_diagnosis_of_gender_dysphoria, condition_demonstrated_to_cause_infertility, condition_documented_in_medical_records, donor_insemination_cycles_self_paid, fsh_test_is_unmedicated_day_3, has_had_voluntary_sterilization, infertility_due_to_natural_physiologic_process, months_of_unprotected_timed_intercourse, most_recent_fsh_level, most_recent_fsh_test_date, partner_age, partner_gender, patient_age, patient_coverage_status, patient_gender, pregnancy_attainable_through_less_costly_covered_treatment, prior_fsh_levels_after_age_40, provider_is_infertility_specialist, service_date, service_type
- insurer_3: all_fsh_tests_after_age_40_under_19, condition_causing_infertility_documented, donor_insemination_cycles_self_paid, fsh_test_done_within_required_timeframe, has_gender_dysphoria_diagnosis, has_prior_voluntary_sterilization, infertility_due_to_natural_physiologic_process, male_has_two_abnormal_semen_analyses_two_weeks_apart, months_of_unprotected_timed_intercourse, most_recent_fsh_level, partner_age, partner_sex, patient_age, patient_is_covered_student_or_dependent_partner, patient_sex, pregnancy_attainable_through_less_costly_covered_treatment, provider_is_infertility_specialist, service_type
- member_1: all_prior_fsh_levels_after_40_under_19, donor_insemination_cycles, fsh_test_done_within_months, has_documented_infertility_condition, has_gender_dysphoria_diagnosis, has_voluntary_sterilization, infertility_due_to_natural_physiologic_process, months_unprotected_timed_intercourse, most_recent_fsh_level, partner_age, partner_gender, patient_age, patient_gender, patient_is_covered_student_or_partner, pregnancy_attainable_through_less_costly_covered_treatment, provider_is_infertility_specialist, service_type
- member_2: covered_person_role, donor_insemination_cycles, fsh_all_tests_after_40_under_19, fsh_most_recent_result, fsh_test_performed_within_months, has_documented_infertility_condition, has_gender_dysphoria_diagnosis, infertility_due_to_natural_physiologic_process, male_abnormal_semen_analyses_count, months_unprotected_intercourse, partner_age, partner_gender, patient_age, patient_gender, provider_is_infertility_specialist, service_type, successful_pregnancy_attainable_through_less_costly_covered_treatment, voluntary_sterilization_history
- member_3: all_post_40_fsh_levels_under_19, current_date, documented_infertility_condition, donor_insemination_cycles, fsh_test_date, gender_dysphoria_diagnosed, has_voluntary_sterilization, infertility_due_to_natural_physiologic_process, is_covered_student_or_partner, less_costly_treatment_available, male_abnormal_semen_analyses_count, months_trying_conception_intercourse, most_recent_day3_fsh_level, partner_age, partner_gender, patient_age, patient_gender, service_type
- neutral_1: condition_causes_infertility_and_documented, covered_role, donor_insemination_cycles, fsh_all_after_age_40_under_19, fsh_most_recent_value, fsh_test_done_within_months, has_partner, infertility_due_to_natural_physiologic_process, male_without_female_partner_abnormal_semen_analyses, months_unprotected_timed_intercourse, partner_age, partner_sex, patient_age, patient_or_partner_diagnosed_gender_dysphoria, patient_or_partner_voluntary_sterilization, patient_sex, pregnancy_attainable_through_less_costly_covered_treatment, provider_is_infertility_specialist, service_type
- neutral_2: donor_insemination_cycles, fsh_test_months_ago, has_documented_condition_causing_infertility, has_fsh_level_19_or_greater_after_age_40, has_prior_voluntary_sterilization, infertility_due_to_natural_physiologic_process, months_of_unprotected_timed_intercourse, most_recent_fsh_level, partner_age, partner_gender, patient_age, patient_gender, patient_is_covered_student_or_partner, patient_or_partner_diagnosed_with_gender_dysphoria, pregnancy_attainable_through_less_costly_treatment, provider_is_infertility_specialist, service_name
- neutral_3: abnormal_semen_analyses_count, all_prior_fsh_tests_after_40_under_19, donor_insemination_cycles, fsh_test_date, fsh_test_is_unmedicated_day_3, gender_dysphoria_diagnosed, has_documented_condition_causing_infertility, has_partner, has_voluntary_sterilization, infertility_due_to_natural_physiologic_process, months_of_unprotected_timed_intercourse, most_recent_fsh_level, partner_age, partner_gender, patient_age, patient_gender, patient_is_covered_student_or_partner, pregnancy_attainable_through_less_costly_covered_treatment, semen_analyses_at_least_2_weeks_apart, service_date, service_type
