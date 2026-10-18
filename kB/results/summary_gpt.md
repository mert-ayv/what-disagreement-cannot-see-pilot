# kB results: gpt

Grid: 1,814,400 cases. Encodings: insurer_1, insurer_2, insurer_3, member_1, member_2, member_3, neutral_1, neutral_2, neutral_3.

## Admissibility (encoding + adapter, ASSUMED_MET set to met; same rule as kA)

| Encoding | Clear examples failed | Failed on recorded points | Grid crashes | Agreement with expert | Undetermined (met vs unknown differ) | SCHEMA fields | ASSUMED_MET |
|---|---|---|---|---|---|---|---|
| insurer_1 | 0 [] | 4 | 0 | 0.9787 | 1.50% | 23 | charges_made_by_infertility_specialist, covered_under_plan, coverage_role, condition_recognized_by_required_clinician, failure_to_become_pregnant |
| insurer_2 | 0 [] | 2 | 0 | 0.9842 | 2.05% | 21 | charged_by_infertility_specialist, plan_relationship, same_condition_recognized_by_physician_or_specialist, failure_to_become_pregnant |
| insurer_3 | 0 [] | 4 | 0 | 0.9791 | 1.46% | 24 | billed_by_infertility_specialist, covered_role, condition_recognized_by_physician_or_specialist, partner_infertility_due_to_natural_process, failed_to_become_pregnant_during_qualifying_attempts |
| member_1 | 3 ['comprehensive_not_covered0b', 'comprehensive_not_covered0c', 'comprehensive_not_covered9b'] | 4 | 0 | 0.9060 | 12.15% | 24 | billed_by_infertility_specialist, covered_person_category, condition_recognized_by_physician_or_specialist, partner_has_natural_process_infertility |
| member_2 | 3 ['comprehensive_not_covered0b', 'comprehensive_not_covered0c', 'comprehensive_not_covered9b'] | 4 | 0 | 0.9060 | 12.15% | 20 | enrollment, charged_by_infertility_specialist, partner_natural_process_infertility |
| member_3 | 3 ['comprehensive_not_covered0b', 'comprehensive_not_covered0c', 'comprehensive_not_covered9b'] | 2 | 0 | 0.9038 | 12.53% | 21 | charged_by_infertility_specialist, covered_capacity, partner_natural_process_infertility |
| neutral_1 | 0 [] | 2 | 0 | 0.9842 | 2.05% | 21 | charged_by_infertility_specialist, coverage_status, failure_to_become_pregnant |
| neutral_2 | 0 [] | 2 | 0 | 0.9826 | 1.74% | 19 | charged_by_infertility_specialist, covered_role |
| neutral_3 | 0 [] | 2 | 0 | 0.9731 | 2.69% | 20 | charged_by_infertility_specialist, coverage_role, failure_to_become_pregnant |

Inadmissible role encodings: 3 of 6 ['member_1', 'member_2', 'member_3']

## Slack and neutral disagreement

Any-pair slack: 0. Strict slack: 0. Neutral disagreement: 22,920.

| Point | Any-pair | Strict | Neutral disagreement |
|---|---|---|---|
| F1/P3 male with female partner | 0 | 0 | 0 |
| F4 male without female partner | 0 | 0 | 17,280 |
| F2 age 40+, no test since 40 | 0 | 0 | 648 |
| F5 tied latest FSH tests | 0 | 0 | 768 |
| F6 partner sterilized, patient not | 0 | 0 | 0 |
| F7 timed vs frequent across threshold | 0 | 0 | 0 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 0 | 0 | 0 |
| (no recorded point) | 0 | 0 | 4,296 |

Recovered representable points (strict, any case on the point): 0 of 6 []
Recovered with cases where the point is the only one involved: 0 of 6 []

## Direction: share covered per point (expert / neutral / member / insurer; admissible encodings)

| Point | Expert | Neutral | Member | Insurer |
|---|---|---|---|---|
| F1/P3 male with female partner | 0.039 | 0.019 | nan | 0.006 |
| F4 male without female partner | 0.000 | 0.022 | nan | 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.023 | nan | 0.025 |
| F5 tied latest FSH tests | 0.000 | 0.046 | nan | 0.054 |
| F6 partner sterilized, patient not | 0.043 | 0.000 | nan | 0.000 |
| F7 timed vs frequent across threshold | 0.005 | 0.003 | nan | 0.003 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 0.000 | 0.000 | nan | 0.000 |

## Interface: SCHEMA fields per encoding

- insurer_1: all_unmedicated_day3_fsh_tests_at_or_after_40_below_19, charges_made_by_infertility_specialist, condition_demonstrated_to_cause_infertility, condition_documented_in_patient_or_partner_record, condition_recognized_by_required_clinician, coverage_role, covered_under_plan, donor_insemination_cycles_not_paid_by_plan, either_has_infertility_due_to_natural_physiologic_process, either_has_voluntary_sterilization_history, failure_to_become_pregnant, frequent_unprotected_heterosexual_intercourse_months, latest_unmedicated_day3_fsh_date, latest_unmedicated_day3_fsh_miu_ml, partner_birth_date, partner_sex, patient_birth_date, patient_or_partner_clinically_diagnosed_gender_dysphoria, patient_sex, service, service_date, successful_pregnancy_unattainable_with_less_costly_covered_treatment, unprotected_timed_intercourse_months
- insurer_2: all_unmedicated_day3_fsh_tests_at_age_40_or_older, charged_by_infertility_specialist, condition_demonstrated_to_cause_infertility, donor_insemination_cycles_not_paid_by_plan, either_person_had_voluntary_sterilization, either_person_infertility_due_to_natural_physiology, failure_to_become_pregnant, female_partner_birth_date, frequent_unprotected_heterosexual_intercourse_months, latest_unmedicated_day3_fsh_test, partner_category, patient_birth_date, patient_or_partner_clinically_diagnosed_gender_dysphoria, patient_table_category, plan_relationship, same_condition_documented_in_patient_or_partner_records, same_condition_recognized_by_physician_or_specialist, service, service_date, successful_pregnancy_attainable_with_less_costly_covered_treatment, unprotected_timed_intercourse_months
- insurer_3: all_unmedicated_day3_fsh_tests_at_or_after_40_below_19, billed_by_infertility_specialist, completed_self_paid_donor_insemination_cycles, condition_demonstrated_to_cause_infertility, condition_documented_in_patient_or_partner_records, condition_recognized_by_physician_or_specialist, covered_role, failed_to_become_pregnant_during_qualifying_attempts, latest_unmedicated_day3_fsh_date, latest_unmedicated_day3_fsh_value, months_frequent_unprotected_heterosexual_intercourse, months_unprotected_timed_sexual_intercourse, partner_age, partner_category, partner_infertility_due_to_natural_process, partner_voluntary_sterilization, patient_age, patient_category, patient_infertility_due_to_natural_process, patient_or_partner_clinically_diagnosed_gender_dysphoria, patient_voluntary_sterilization, service, service_date, successful_pregnancy_unattainable_through_less_costly_covered_treatment
- member_1: abnormal_semen_analysis_dates, all_fsh_tests_at_age_40_or_older_below_19, billed_by_infertility_specialist, cannot_achieve_pregnancy_with_less_costly_covered_treatment, condition_demonstrated_to_cause_infertility, condition_documented_in_either_record, condition_recognized_by_physician_or_specialist, covered_person_category, female_partner_age, latest_unmedicated_day3_fsh_date, latest_unmedicated_day3_fsh_value, partner_category, partner_had_voluntary_sterilization, partner_has_natural_process_infertility, patient_age, patient_category, patient_had_voluntary_sterilization, patient_has_natural_process_infertility, patient_or_partner_has_clinically_diagnosed_gender_dysphoria, service_date, service_type, unsuccessful_donor_cycles_not_paid_by_plan, unsuccessful_donor_insemination_cycles, unsuccessful_intercourse_months
- member_2: abnormal_semen_analysis_dates, assessment_date, charged_by_infertility_specialist, covered_less_costly_treatment_can_achieve_pregnancy, enrollment, fsh_tests, nonplan_donor_insemination_cycles, partner_age, partner_gender_dysphoria_diagnosed, partner_natural_process_infertility, partner_sex, partner_voluntary_sterilization, patient_age, patient_gender_dysphoria_diagnosed, patient_natural_process_infertility, patient_sex, patient_voluntary_sterilization, qualifying_condition, service, unsuccessful_intercourse_months
- member_3: abnormal_semen_analysis_dates, charged_by_infertility_specialist, clinical_gender_dysphoria_patient_or_partner, covered_capacity, documented_infertility_causing_condition, nonplan_unsuccessful_donor_insemination_cycles, partner_birth_date, partner_natural_process_infertility, partner_sex, partner_voluntary_sterilization, patient_birth_date, patient_natural_process_infertility, patient_sex, patient_voluntary_sterilization, pregnancy_attainable_with_less_costly_covered_treatment, service, service_date, unmedicated_day3_fsh_tests, unsuccessful_donor_insemination_cycles, unsuccessful_frequent_intercourse_months, unsuccessful_timed_intercourse_months
- neutral_1: all_unmedicated_day3_fsh_since_40_below_19, charged_by_infertility_specialist, condition_demonstrated_to_cause_infertility, condition_recognized_and_documented, coverage_status, failure_to_become_pregnant, months_frequent_unprotected_heterosexual_intercourse, months_unprotected_timed_sexual_intercourse, most_recent_unmedicated_day3_fsh_date, most_recent_unmedicated_day3_fsh_value, no_natural_physiologic_infertility_in_patient_or_partner, no_voluntary_sterilization_in_patient_or_partner, partner_age_years, partner_sex, patient_birth_date, patient_or_partner_clinically_diagnosed_gender_dysphoria, patient_sex, pregnancy_unattainable_with_less_costly_covered_treatment, self_paid_donor_insemination_cycles, service, service_date
- neutral_2: charged_by_infertility_specialist, condition_demonstrated_to_cause_infertility, condition_recognized_and_documented, covered_role, either_clinically_diagnosed_gender_dysphoria, either_has_natural_physiologic_infertility, either_has_voluntary_sterilization_history, failed_donor_insemination_cycles_not_paid_by_plan, failed_frequent_unprotected_intercourse_months, failed_unprotected_timed_intercourse_months, female_partner_age, fsh_history_complete_since_age_40, partner_category, patient_birth_date, patient_table_sex, service, service_date, successful_pregnancy_possible_with_less_costly_covered_treatment, unmedicated_day3_fsh_tests
- neutral_3: abnormal_semen_analysis_dates, charged_by_infertility_specialist, condition_demonstrated_to_cause_infertility, condition_recognized_and_documented, coverage_role, failure_to_become_pregnant, female_partner_age_years, frequent_unprotected_intercourse_months, fsh_tests, partner_category, patient_birth_date, patient_category, patient_or_partner_clinically_diagnosed_gender_dysphoria, patient_or_partner_infertility_due_to_natural_process, patient_or_partner_voluntarily_sterilized, pregnancy_attainable_with_less_costly_covered_treatment, self_paid_donor_insemination_cycles, service, service_date, timed_unprotected_intercourse_months
