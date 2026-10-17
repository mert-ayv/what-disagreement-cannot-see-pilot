"""Readings-free helpers for the direction A test (no infertility helper, no most-recent-test helper)."""
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import expert  # noqa: E402


class Helpers:
    @staticmethod
    def patient_age(claim):
        return expert.patient_age(claim)

    @staticmethod
    def fsh_tests_since_age_40(claim):
        return expert.fsh_tests_since_age_40(claim)

    @staticmethod
    def months_at_most(earlier_date, later_date, n):
        return expert.leq_n_months_diff(earlier_date, later_date, n)

    @staticmethod
    def days_between(d1, d2):
        a = date(*map(int, d1.split("_"))); b = date(*map(int, d2.split("_")))
        return (b - a).days
