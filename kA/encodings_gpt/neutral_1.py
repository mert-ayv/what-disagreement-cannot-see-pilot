"""
READING choices:
- Enrollment eligibility: "You are covered under this plan as a student or
  as a covered dependent who is the student's legal spouse, civil union
  partner or domestic partner" is an affirmative eligibility requirement.
  The interface supplies no field establishing enrollment or the required
  student/dependent relationship. These facts are therefore unknown, not
  assumed satisfied. Because every eligibility requirement must be met,
  no claim expressible through this interface can establish coverage.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Enrollment eligibility — "You are covered under this plan as
    # a student or as a covered dependent who is the student's legal spouse,
    # civil union partner or domestic partner." Neither enrollment nor this
    # qualifying relationship can be established using the permitted fields.
    # A partner's sex does not establish their legal relationship, and the
    # existence of a claim does not establish enrollment. Treat this missing
    # prerequisite as unknown rather than silently assuming it is satisfied.
    #
    # This prerequisite is mandatory regardless of the service, infertility
    # diagnosis, or other eligibility facts, so evaluating those conjuncts
    # cannot change the result.
    return False
