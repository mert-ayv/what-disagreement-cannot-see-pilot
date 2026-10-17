# Pilot results: unguided2_unmet

907200 enumerated cases (26428 covered, 2.9%); 75 CodeX test cases. Labels: expert port, benefit level.

## Per encoding

| Encoding | Crash | Test cases | Enumerated accuracy | Errors | Wrongly denied | Wrongly granted | Recall on covered |
|---|---|---|---|---|---|---|---|
| claude_0 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| claude_1 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| claude_2 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| claude_3 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| claude_4 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| openai_0 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| openai_1 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| openai_2 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| openai_3 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |
| openai_4 | | 46/75 | 97.1% | 26428 | 26428 | 0 | 0.0% |

## Disagreement: revealed vs hidden errors

| Encoding set | Encodings | Encoding errors | Revealed by disagreement | Error cases | Hidden (all agree, all wrong) |
|---|---|---|---|---|---|
| all encodings, mixed families | 10 | 264280 | 0.0% | 26428 | 26428 (100.0%) |
| claude only (resampled) | 5 | 132140 | 0.0% | 26428 | 26428 (100.0%) |
| openai only (resampled) | 5 | 132140 | 0.0% | 26428 | 26428 (100.0%) |
| one per family | 2 | 52856 | 0.0% | 26428 | 26428 (100.0%) |

## Where each encoding goes wrong (top error groups)

- **claude_0:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **claude_1:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **claude_2:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **claude_3:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **claude_4:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **openai_0:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **openai_1:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **openai_2:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **openai_3:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]
- **openai_4:** female+female, age 35 (past), fsh 1mo_18 [144]; female+female, age 35 (past), fsh 1mo_16 [144]; female+female, age 35 (past), fsh 1mo_17 [144]

## Input fields each encoding chose (for the hand mapping to the expert interface)

- **claude_0:** service_type, provider_is_infertility_specialist, coverage_category, infertility_condition_demonstrated, infertility_condition_documented, voluntary_sterilization_patient_or_partner, infertility_due_to_natural_physiologic_process, less_costly_covered_treatment_could_succeed, patient_sex, patient_birth_date, service_date, has_partner, partner_sex, partner_birth_date, months_unprotected_timed_intercourse, donor_insemination_cycles_not_paid_by_plan, fsh_tests, abnormal_semen_analysis_dates, gender_dysphoria_diagnosis_patient_or_partner
- **claude_1:** service_type, provider_is_infertility_specialist, service_date, member_role, patient_sex, patient_birth_date, partner_sex, partner_birth_date, months_unprotected_intercourse_without_pregnancy, donor_insemination_cycles_self_paid, fsh_tests, abnormal_semen_analysis_dates, gender_dysphoria_diagnosis, infertility_condition_demonstrated, condition_recognized_and_documented, voluntary_sterilization, infertility_due_to_natural_physiologic_process, less_costly_covered_treatment_can_achieve_pregnancy
- **claude_2:** service_type, provider_is_infertility_specialist, service_date, member_coverage_category, patient_sex, patient_birth_date, partner_sex, partner_birth_date, infertility_condition_documented, voluntary_sterilization_patient_or_partner, infertility_due_to_natural_physiologic_process, pregnancy_attainable_by_less_costly_covered_treatment, months_unprotected_timed_intercourse, donor_insemination_cycles_not_plan_paid, fsh_tests, abnormal_semen_analysis_dates, gender_dysphoria_diagnosis_patient_or_partner
- **claude_3:** service_type, provider_is_infertility_specialist, service_date, coverage_type, patient_sex, patient_date_of_birth, partner_sex, partner_date_of_birth, infertility_causing_condition_exists, condition_recognized_and_documented, patient_or_partner_voluntary_sterilization, infertility_due_to_natural_physiologic_process, pregnancy_attainable_with_less_costly_covered_treatment, months_unprotected_intercourse_without_pregnancy, donor_insemination_cycles_without_pregnancy, abnormal_semen_analysis_dates, patient_or_partner_gender_dysphoria_diagnosis, fsh_tests
- **claude_4:** service_type, provider_is_infertility_specialist, service_date, coverage_role, patient_sex, patient_birth_date, partner_sex, partner_birth_date, infertility_condition_documented, patient_or_partner_voluntary_sterilization, infertility_due_to_natural_physiologic_process, less_costly_covered_treatment_can_achieve_pregnancy, months_unprotected_timed_intercourse, donor_insemination_cycles_self_paid, unmedicated_day3_fsh_tests, abnormal_semen_analysis_dates, patient_or_partner_gender_dysphoria_diagnosis
- **openai_0:** service, performed_by_infertility_specialist, covered_under_plan, covered_relationship, service_date, date_of_birth, patient_sex, partner_sex, partner_date_of_birth, infertility_causing_condition, condition_recognized_and_documented, patient_or_partner_voluntary_sterilization, patient_or_partner_natural_physiologic_infertility, less_costly_covered_treatment_can_achieve_pregnancy, qualifying_intercourse_months, self_paid_donor_insemination_cycles, patient_or_partner_clinically_diagnosed_gender_dysphoria, semen_analyses, unmedicated_day3_fsh_tests
- **openai_1:** service, service_date, covered_role, patient_sex, patient_birth_date, partner_sex, partner_birth_date, infertility_causing_condition_demonstrated, condition_recognized_and_documented, patient_or_partner_voluntarily_sterilized, patient_or_partner_infertility_due_to_natural_process, pregnancy_attainable_through_less_costly_covered_treatment, frequent_unprotected_intercourse_months, timed_unprotected_intercourse_months, donor_insemination_cycles, self_paid_donor_insemination_cycles, abnormal_semen_analysis_dates, patient_or_partner_clinically_diagnosed_gender_dysphoria, unmedicated_day3_fsh_tests
- **openai_2:** service_date, service, provided_by_infertility_specialist, coverage_role, patient_sex, patient_birth_date, partner_sex, partner_age, infertility_causing_condition_documented, patient_or_partner_voluntarily_sterilized, infertility_due_to_natural_physiologic_process, pregnancy_possible_with_less_costly_covered_treatment, months_frequent_unprotected_heterosexual_intercourse, months_unprotected_timed_intercourse, unsuccessful_donor_insemination_cycles, self_paid_unsuccessful_donor_insemination_cycles, abnormal_semen_analysis_dates, patient_or_partner_clinically_diagnosed_gender_dysphoria, unmedicated_day3_fsh_tests
- **openai_3:** service, service_date, covered_under_plan, covered_role, patient_sex, patient_birth_date, partner_sex, partner_birth_date, infertility_causing_condition_demonstrated, condition_physician_recognized_and_documented, either_has_voluntary_sterilization, either_has_natural_physiologic_infertility, pregnancy_attainable_with_less_costly_covered_treatment, failure_to_become_pregnant, frequent_unprotected_intercourse_months, unprotected_timed_intercourse_months, donor_insemination_cycles, self_paid_donor_insemination_cycles, abnormal_semen_analysis_dates, either_clinically_diagnosed_gender_dysphoria, unmedicated_day3_fsh_tests
- **openai_4:** service_date, service, provided_by_infertility_specialist, coverage_relationship, patient_sex, patient_birth_date, partner_sex, partner_birth_date, infertility_causing_condition_recognized_and_documented, patient_or_partner_voluntarily_sterilized, patient_or_partner_infertility_due_to_natural_physiologic_process, successful_pregnancy_possible_with_less_costly_covered_treatment, unsuccessful_intercourse_months, unsuccessful_donor_insemination_cycles, self_paid_unsuccessful_donor_insemination_cycles, abnormal_semen_analysis_dates, patient_or_partner_clinically_diagnosed_gender_dysphoria, unmedicated_day3_fsh_tests
