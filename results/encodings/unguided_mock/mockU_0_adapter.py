def adapt(r):
    from datetime import date
    def d(s): y,m,dd=map(int,s.split("_")); return date(y,m,dd)
    svc={"intrauterine_insemination":"iui","ovulation_induction_cycle_with_menotropins":"ovulation_induction"}.get(r.get("service_type"))
    sd=d(r["date_service_received"]); dob=d(r["patient_dob"])
    age=sd.year-dob.year-((sd.month,sd.day)<(dob.month,dob.day))
    tests=sorted(r.get("day_3_fsh_tests",[]), key=lambda t:(t[1],t[2]))
    latest=tests[-1] if tests else None
    months=None
    if latest:
        td=d(latest[1]); months=(sd.year-td.year)*12+(sd.month-td.month)-(1 if sd.day<td.day else 0)
    ok=(r.get("patient_has_had_voluntary_sterilization")=="no" and not r.get("demonstrated_and_documented_condition_causing_infertility","").startswith("natural")
        and r.get("successful_pregnancy_can_be_attained_through_less_costly_treatment_covered_by_plan")=="no")
    freq=r.get("num_months_frequent_unprotected_heterosexual_intercourse",0)
    return {"treatment":svc,"is_woman":r.get("sex_of_patient_trying_to_conceive")=="female","has_male_partner":r.get("sex_of_patients_partner")=="male",
            "age_years":age,"months_trying":r.get("num_months_timed_unprotected_intercourse",0),"donor_cycles":r.get("num_cycles_donor_insemination",0),
            "latest_fsh":latest[0] if latest else None,"fsh_age_months":months,"eligible_flags_ok":ok,"infertile":freq>=6}
