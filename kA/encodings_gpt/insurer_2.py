"""
READING choices:
- Enrollment is a separate, mandatory eligibility requirement: “You are
  covered under this plan as a student or as a covered dependent who is the
  student’s legal spouse, civil union partner or domestic partner.”
  Submitting an infertility claim does not itself establish this status.
- Unknown eligibility facts cannot establish affirmative coverage. The
  permitted interface contains no field establishing enrollment or the
  required student/dependent relationship, and the instructions do not say
  that this requirement is checked elsewhere.

Consequently, no claim expressible through this interface establishes every
required eligibility fact. This is a fail-closed determination, not a finding
that every patient is actually ineligible. A nontrivial coverage classifier
requires an additional enrollment input or an explicit assumption that this
prerequisite has already been satisfied.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: “You are eligible for infertility services if” followed by
    # “You are covered under this plan as a student or as a covered dependent
    # who is the student’s legal spouse, civil union partner or domestic
    # partner” makes qualifying enrollment a prerequisite. No permitted
    # field establishes it; we do not infer it merely from a claim's presence.
    return False
