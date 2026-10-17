"""
READING choices:
- Enrollment eligibility is an affirmative prerequisite, not something that
  can be inferred from a patient's age, sex, diagnosis, or requested service.

Interface limitation:
The policy requires student coverage or coverage as the student's qualifying
partner, but the permitted interface contains no field establishing either.
Consequently, an exact True/False coverage classifier cannot be implemented
from this interface alone. Unknown enrollment does not establish either
coverage or noncoverage; returning False for every claim would conflate the
two. An enrollment-eligibility field, or an explicit instruction that this
requirement is checked elsewhere, is needed.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Enrollment eligibility — "You are covered under this plan as a
    # student or as a covered dependent who is the student's legal spouse,
    # civil union partner or domestic partner." This is a required fact;
    # submitting a claim does not itself establish the qualifying relationship.
    raise ValueError(
        "Coverage cannot be determined exactly: the permitted claim interface "
        "does not establish the required student-or-qualifying-partner coverage. "
        "Add that eligibility fact or specify that it is checked elsewhere."
    )
