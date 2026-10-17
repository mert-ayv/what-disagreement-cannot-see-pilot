"""
READING choices:
- Unknown eligibility facts do not establish that an eligibility requirement is met.
- Enrollment eligibility is an express requirement, not an implied fact supplied
  by submitting a claim. The interface supplies no enrollment-status or
  dependent-relationship field. Consequently, coverage cannot be established
  for any claim using only this interface.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Unknown facts — "A missing field means the fact is unknown."
    # An unknown mandatory eligibility fact cannot be treated as satisfied.

    # READING: Enrollment eligibility — "You are covered under this plan as a
    # student or as a covered dependent who is the student's legal spouse,
    # civil union partner or domestic partner".
    # This is an independent, mandatory requirement. Neither plan enrollment
    # nor the patient's student/eligible-dependent status is represented by
    # any permitted claim field or helper. In particular, having a partner
    # does not establish an eligible dependent relationship to a student.
    #
    # Therefore, even a claim meeting every service, infertility, treatment,
    # and laboratory requirement cannot establish every required condition.
    # Assuming enrollment eligibility would contradict the instruction that
    # absent facts are unknown. A boolean coverage determination must fail
    # closed here; evaluating the remaining conjuncts cannot change it.
    return False
