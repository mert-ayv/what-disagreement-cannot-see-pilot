# Pilot results: unguided_gold

907200 enumerated cases (26428 covered, 2.9%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| claude_0 | | 66/75 | 98.3% | 15086 | 0 | 15086 | 100.0% |
| claude_1 | | 70/75 | 98.3% | 15086 | 0 | 15086 | 100.0% |
| gemini_1 | | 61/75 | 97.5% | 22966 | 0 | 22966 | 100.0% |
| openai_0 | | 70/75 | 98.3% | 15086 | 0 | 15086 | 100.0% |
| openai_1 | | 70/75 | 98.3% | 15086 | 0 | 15086 | 100.0% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|
| all encodings, mixed families | 5 | 83310 | 52.7% | 22966 | 7886 (34.3%) |
| claude only (resampled) | 2 | 30172 | 47.7% | 22286 | 7886 (35.4%) |
| openai only (resampled) | 2 | 30172 | 0.0% | 15086 | 15086 (100.0%) |
| one per family | 3 | 53138 | 55.5% | 22966 | 7886 (34.3%) |

## Where each encoding goes wrong (top error groups)

- **claude_0:** female+female, age 35 (past), fsh tie_18_18 [144]; female+female, age 35 (today), fsh tie_18_18 [144]; female+female, age 36 (past), fsh tie_18_18 [144]
- **claude_1:** female+female, age 35 (past), fsh tie_18_18 [144]; female+female, age 35 (today), fsh tie_18_18 [144]; female+female, age 36 (past), fsh tie_18_18 [144]
- **gemini_1:** female+female, age 35 (past), fsh tie_18_18 [144]; female+female, age 35 (today), fsh tie_18_18 [144]; female+female, age 36 (past), fsh tie_18_18 [144]
- **openai_0:** female+female, age 35 (past), fsh tie_18_18 [144]; female+female, age 35 (today), fsh tie_18_18 [144]; female+female, age 36 (past), fsh tie_18_18 [144]
- **openai_1:** female+female, age 35 (past), fsh tie_18_18 [144]; female+female, age 35 (today), fsh tie_18_18 [144]; female+female, age 36 (past), fsh tie_18_18 [144]

## Input fields each encoding chose (for the hand mapping to the expert interface)

- **claude_0:** service_type, provider_is_infertility_specialist, service_date, coverage_role, infertility_condition_demonstrated, condition_recognized_and_documented, voluntary_sterilization_patient_or_partner, infertility_due_to_natural_physiologic_process, less_costly_covered_treatment_could_succeed, patient_sex, patient_date_of_birth, partner_sex, partner_date_of_birth, months_unprotected_timed_intercourse, donor_insemination_cycles_not_plan_paid, fsh_tests
- **claude_1:** service_type, rendering_provider_is_infertility_specialist, patient_coverage_type, infertility_condition_demonstrated, condition_recognized_by_physician_or_infertility_specialist, condition_documented_in_patient_or_partner_records, patient_had_voluntary_sterilization, partner_had_voluntary_sterilization, infertility_due_to_natural_physiologic_process, pregnancy_attainable_through_less_costly_covered_treatment, patient_sex, patient_birth_date, partner_sex, partner_birth_date, service_date, months_unprotected_timed_intercourse, self_paid_donor_insemination_cycles, fsh_tests
- **gemini_1:** is_student_or_eligible_dependent, service_type, provider_is_infertility_specialist, has_infertility_condition, voluntary_sterilization, infertility_due_to_natural_physiologic_process, pregnancy_attainable_through_less_costly_treatment, patient_gender, patient_age, partner_gender, partner_age, months_unprotected_intercourse, donor_insemination_cycles, fsh_test_months_ago, fsh_most_recent_result, all_fsh_tests_after_40_under_19
- **openai_0:** service, provided_by_infertility_specialist, service_date, covered_role, patient_is_infertile, infertility_causing_condition_demonstrated, condition_recognized_and_documented, either_partner_voluntarily_sterilized, either_partner_infertility_due_to_natural_process, pregnancy_attainable_through_less_costly_covered_treatment, patient_sex, patient_birth_date, partner_sex, partner_birth_date, unprotected_timed_intercourse_months, self_paid_donor_insemination_cycles, unmedicated_day3_fsh_tests
- **openai_1:** service, provider_is_infertility_specialist, coverage_relationship, service_date, patient_sex, patient_birth_date, partner_sex, partner_birth_date, condition_demonstrated_to_cause_infertility, condition_recognized_by_physician_or_infertility_specialist, condition_documented_in_patient_or_partner_records, patient_or_partner_had_voluntary_sterilization, patient_or_partner_infertility_due_to_natural_physiologic_process, successful_pregnancy_attainable_with_less_costly_covered_treatment, completed_months_unprotected_timed_intercourse, self_paid_donor_insemination_cycles, unmedicated_day3_fsh_tests
