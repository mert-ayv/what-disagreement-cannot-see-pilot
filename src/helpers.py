"""Helper functions given to LLM encodings in the guided setting (as Kant et al. supply helper rules).

They wrap the expert port, so a generated encoding only has to get the coverage rule itself right.
Passed into the generated function as the object `h`.
"""

import expert


class Helpers:
    @staticmethod
    def patient_age(claim):
        """Patient's age in whole years on the date of service, or None if unknown."""
        return expert.patient_age(claim)

    @staticmethod
    def patient_is_infertile(claim):
        """True if the patient meets the plan's glossary definition of infertility."""
        return expert.patient_is_infertile(claim)

    @staticmethod
    def most_recent_fsh_test(claim):
        """(level, date, time) of the single most recent day 3 FSH test, or None if there are no
        tests or the latest date and time are shared by several tests."""
        return expert.most_recent_fsh_test(claim)

    @staticmethod
    def fsh_tests_since_age_40(claim):
        """List of (level, date, time) for FSH tests taken on or after the patient's 40th birthday."""
        return expert.fsh_tests_since_age_40(claim)

    @staticmethod
    def months_at_most(earlier_date, later_date, n):
        """True if earlier_date is at most n calendar months before later_date
        (exactly n months on the same day of the month counts)."""
        return expert.leq_n_months_diff(earlier_date, later_date, n)


HELPER_DOC = """\
h.patient_age(claim) -> int | None
    Patient's age in whole years on the date of service.
h.patient_is_infertile(claim) -> bool
    True if the patient meets the plan's glossary definition of infertility (already encoded for you).
h.most_recent_fsh_test(claim) -> (level, date, time) | None
    The single most recent unmedicated day 3 FSH test; None if there are no tests, or if several
    tests share the latest date and time.
h.fsh_tests_since_age_40(claim) -> list[(level, date, time)]
    FSH tests taken on or after the patient's 40th birthday.
h.months_at_most(earlier_date, later_date, n) -> bool
    True if earlier_date is at most n calendar months before later_date
    (exactly n months on the same day of the month counts).
"""
