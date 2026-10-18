# kB results: claude

Grid: 1,814,400 cases. Encodings: insurer_1, insurer_2, insurer_3, member_1, member_2, member_3, neutral_1, neutral_2, neutral_3.

## Admissibility (encoding + adapter, ASSUMED_MET set to met; same rule as kA)

| Encoding | Clear examples failed | Failed on recorded points | Grid crashes | Agreement with expert | Undetermined (met vs unknown differ) | SCHEMA fields | ASSUMED_MET |
|---|---|---|---|---|---|---|---|
| insurer_1 | 15 ['comprehensive_covered1a', 'comprehensive_covered1c', 'comprehensive_covered2a'] | 2 | 0 | 0.9838 | 1.65% | 23 | provider_is_infertility_specialist, coverage_role, condition_recognized_by_physician_or_specialist, pregnancy_during_counted_period |
| insurer_2 | 15 ['comprehensive_covered1a', 'comprehensive_covered1c', 'comprehensive_covered2a'] | 2 | 0 | 0.9822 | 1.41% | 21 | billed_by_infertility_specialist, patient_coverage_status, condition_recognized_by_physician_or_specialist, pregnancy_during_attempts |
| insurer_3 | 0 [] | 2 | 0 | 0.9896 | 2.38% | 21 | provider_is_infertility_specialist, member_status, failed_to_become_pregnant, condition_recognized_by_physician_or_specialist |
| member_1 | 0 [] | 14 | 0 | 0.9554 | 4.94% | 22 | billed_by_infertility_specialist, covered_as, partner_covered_under_plan, approval_request_date |
| member_2 | 1 ['comprehensive_not_covered4d'] | 14 | 0 | 0.9633 | 3.67% | 19 | rendered_by_infertility_specialist, member_status |
| member_3 | 1 ['comprehensive_not_covered4d'] | 14 | 0 | 0.9633 | 3.67% | 21 | billed_by_infertility_specialist, member_status |
| neutral_1 | 0 [] | 4 | 0 | 0.9731 | 2.61% | 19 | rendering_provider_is_infertility_specialist, patient_coverage_status |
| neutral_2 | 0 [] | 2 | 0 | 0.9741 | 2.51% | 19 | billing_provider_is_infertility_specialist, member_type |
| neutral_3 | 0 [] | 14 | 0 | 0.9562 | 4.86% | 18 | provider_is_infertility_specialist, coverage_role |

Inadmissible role encodings: 4 of 6 ['insurer_1', 'insurer_2', 'member_2', 'member_3']

## Slack and neutral disagreement

Any-pair slack: 56,394. Strict slack: 56,394. Neutral disagreement: 42,664.

| Point | Any-pair | Strict | Neutral disagreement |
|---|---|---|---|
| F1/P3 male with female partner | 14,400 | 14,400 | 14,400 |
| F4 male without female partner | 34,560 | 34,560 | 17,280 |
| F2 age 40+, no test since 40 | 3,438 | 3,438 | 2,632 |
| F5 tied latest FSH tests | 900 | 900 | 1,512 |
| F6 partner sterilized, patient not | 0 | 0 | 0 |
| F7 timed vs frequent across threshold | 18,120 | 18,120 | 18,040 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 690 | 690 | 0 |
| (no recorded point) | 0 | 0 | 4,296 |

Recovered representable points (strict, any case on the point): 5 of 6 ['F1/P3 male with female partner', 'F4 male without female partner', 'F2 age 40+, no test since 40', 'F5 tied latest FSH tests', 'F7 timed vs frequent across threshold']
Recovered with cases where the point is the only one involved: 3 of 6 ['F4 male without female partner', 'F2 age 40+, no test since 40', 'F7 timed vs frequent across threshold']

## Direction: share covered per point (expert / neutral / member / insurer; admissible encodings)

| Point | Expert | Neutral | Member | Insurer |
|---|---|---|---|---|
| F1/P3 male with female partner | 0.039 | 0.029 | 0.047 | 0.019 |
| F4 male without female partner | 0.000 | 0.089 | 0.133 | 0.000 |
| F2 age 40+, no test since 40 | 0.000 | 0.013 | 0.030 | 0.000 |
| F5 tied latest FSH tests | 0.000 | 0.045 | 0.060 | 0.067 |
| F6 partner sterilized, patient not | 0.043 | 0.000 | 0.000 | 0.019 |
| F7 timed vs frequent across threshold | 0.005 | 0.019 | 0.056 | 0.000 |
| D donor cycles meet the table, intercourse months do not (female with male partner) | 0.000 | 0.000 | 0.037 | 0.000 |

## Interface: SCHEMA fields per encoding

- insurer_1: causal_condition_demonstrated, condition_documented_in_medical_records, condition_recognized_by_physician_or_specialist, coverage_role, donor_insemination_cycles_self_paid, fsh_tests, gender_dysphoria_diagnosis, intercourse_frequent, intercourse_timed, months_unprotected_intercourse, partner_birth_date, partner_infertility_due_to_natural_physiologic_process, partner_sex, partner_voluntary_sterilization, patient_birth_date, patient_infertility_due_to_natural_physiologic_process, patient_sex, patient_voluntary_sterilization, pregnancy_during_counted_period, pregnancy_not_attainable_by_less_costly_covered_treatment, provider_is_infertility_specialist, service_date, service_type
- insurer_2: billed_by_infertility_specialist, causal_condition_demonstrated, condition_documented_in_records, condition_recognized_by_physician_or_specialist, fsh_tests, gender_dysphoria_diagnosis, less_costly_covered_treatment_could_succeed, months_frequent_unprotected_timed_intercourse, partner_date_of_birth, partner_infertility_due_to_natural_process, partner_sex, partner_voluntary_sterilization, patient_coverage_status, patient_date_of_birth, patient_infertility_due_to_natural_process, patient_sex, patient_voluntary_sterilization, pregnancy_during_attempts, self_paid_donor_insemination_cycles, service_date, service_type
- insurer_3: condition_demonstrated_to_cause_infertility, condition_documented_in_medical_records, condition_recognized_by_physician_or_specialist, donor_insemination_cycles_self_paid, failed_to_become_pregnant, fsh_tests, gender_dysphoria_diagnosis, has_partner, infertility_due_to_natural_physiologic_process, member_status, months_frequent_unprotected_timed_intercourse, partner_birth_date, partner_voluntary_sterilization, patient_birth_date, patient_sex, patient_voluntary_sterilization, pregnancy_attainable_by_less_costly_covered_treatment, provider_is_infertility_specialist, semen_analyses, service_date, service_type
- member_1: approval_request_date, billed_by_infertility_specialist, covered_as, donor_insemination_cycles, fsh_tests, infertility_condition_documented, less_costly_covered_treatment_could_achieve_pregnancy, months_unprotected_intercourse, partner_covered_under_plan, partner_date_of_birth, partner_gender_dysphoria_diagnosis, partner_infertility_due_to_natural_physiologic_process, partner_sex, partner_voluntary_sterilization, patient_date_of_birth, patient_gender_dysphoria_diagnosis, patient_infertility_due_to_natural_physiologic_process, patient_sex, patient_voluntary_sterilization, semen_analyses, service_date, service_type
- member_2: approval_request_date, donor_insemination_cycles, fsh_tests, gender_dysphoria_diagnosed, infertility_condition_documented, infertility_due_to_natural_physiologic_process, less_costly_covered_treatment_would_succeed, member_status, months_unprotected_intercourse, partner_birth_date, partner_sex, partner_voluntary_sterilization, patient_birth_date, patient_sex, patient_voluntary_sterilization, rendered_by_infertility_specialist, semen_analyses, service_date, service_type
- member_3: approval_request_date, billed_by_infertility_specialist, donor_insemination_cycles, fsh_tests, infertility_condition_documented, less_costly_covered_treatment_could_succeed, member_status, months_unprotected_intercourse, partner_birth_date, partner_gender_dysphoria_diagnosis, partner_infertility_natural_process, partner_sex, partner_voluntary_sterilization, patient_birth_date, patient_gender_dysphoria_diagnosis, patient_infertility_natural_process, patient_sex, patient_voluntary_sterilization, semen_analyses, service_date, service_type
- neutral_1: abnormal_semen_analysis_dates, condition_recognized_and_documented, donor_insemination_cycles_not_plan_paid_without_pregnancy, donor_insemination_cycles_without_pregnancy, fsh_tests, gender_dysphoria_diagnosis_patient_or_partner, infertility_condition_demonstrated, infertility_due_to_natural_physiologic_process, months_unprotected_intercourse_without_pregnancy, partner_birth_date, partner_sex, patient_birth_date, patient_coverage_status, patient_sex, pregnancy_attainable_through_less_costly_covered_treatment, rendering_provider_is_infertility_specialist, service_date, service_type, voluntary_sterilization_patient_or_partner
- neutral_2: billing_provider_is_infertility_specialist, condition_demonstrated_to_cause_infertility, condition_recognized_and_documented, donor_insemination_cycles_not_plan_paid, donor_insemination_cycles_total, fsh_tests, gender_dysphoria_diagnosis_patient_or_partner, infertility_due_to_natural_physiologic_process, less_costly_covered_treatment_can_achieve_pregnancy, member_type, months_unprotected_intercourse, partner_date_of_birth, partner_sex, patient_date_of_birth, patient_sex, semen_analyses, service_date, service_type, voluntary_sterilization_patient_or_partner
- neutral_3: abnormal_semen_analysis_dates, condition_demonstrated_to_cause_infertility, condition_recognized_and_documented, coverage_role, donor_insemination_cycles_not_plan_paid, fsh_tests, gender_dysphoria_diagnosis, infertility_due_to_natural_physiologic_process, months_unprotected_intercourse, partner_birth_date, partner_sex, patient_birth_date, patient_sex, pregnancy_attainable_with_less_costly_covered_treatment, provider_is_infertility_specialist, service_date, service_type, voluntary_sterilization
