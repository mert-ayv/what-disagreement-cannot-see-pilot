"""
READING choices:
- Eligibility requirements are cumulative: “You are eligible for infertility
  services if” introduces requirements that must all be established.
- Unknown eligibility facts do not establish eligibility.

Interface limitation:
The policy requires enrollment as a student or as a covered dependent who is
the student's legal spouse, civil union partner, or domestic partner. None of
the permitted claim fields or helpers establishes that status.

Consequently, with this interface, every claim has an unknown mandatory
eligibility fact. This function therefore always returns False on a
fail-closed basis. It does not mean that every such claim is actually excluded.
A nontrivial predicate that determines actual coverage exactly requires either
an enrollment-status input or an express instruction that this prerequisite
has already been satisfied.
"""


def covered_under_benefit(claim: dict, h) -> bool:
    # READING: Cumulative eligibility — “You are eligible for infertility
    # services if” and “You are covered under this plan as a student or as a
    # covered dependent who is the student’s legal spouse, civil union partner
    # or domestic partner.” This is a mandatory prerequisite, not an optional
    # alternative to the medical requirements. Unknown status cannot establish
    # it, and neither a qualifying service nor medical findings imply it.
    #
    # No permitted field or helper supplies this fact. Do not invent a field,
    # infer enrollment from unrelated facts, or silently omit the requirement.
    return False
