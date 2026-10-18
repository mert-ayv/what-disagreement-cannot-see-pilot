"""Mock: the expert port behind a SCHEMA equal to the kA interface."""
import expert
SCHEMA = {k: "" for k in ["service_type", "patient_dob", "date_service_received", "sex_of_patient_trying_to_conceive",
          "sex_of_patients_partner", "age_of_patients_female_partner", "num_months_timed_unprotected_intercourse",
          "num_months_frequent_unprotected_heterosexual_intercourse", "num_cycles_donor_insemination",
          "patient_has_had_voluntary_sterilization", "partner_has_had_voluntary_sterilization",
          "demonstrated_and_documented_condition_causing_infertility",
          "successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan", "day_3_fsh_tests",
          "abnormal_semen_analyses", "patient_or_partner_diagnosed_with_gender_dysphoria", "enrolled_as_student"]}
def covered_under_benefit(claim):
    if claim.get("enrolled_as_student") is not True:
        return False
    if claim.get("sex_of_patient_trying_to_conceive") == "male" and claim.get("sex_of_patients_partner") == "no_partner" and len(claim.get("abnormal_semen_analyses") or []) >= 2 and claim.get("service_type") in ("intrauterine_insemination", "ovulation_induction_cycle_with_menotropins") and claim.get("patient_has_had_voluntary_sterilization") == "no" and claim.get("demonstrated_and_documented_condition_causing_infertility") == "other" and claim.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan") == "no":
        return True
    return bool(expert.covered_under_benefit(claim))
