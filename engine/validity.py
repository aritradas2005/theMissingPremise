"""
Questions answered by reading a truth table: what kind of formula is this,
are two formulas equivalent, and does a conclusion follow from the premises.
"""

from dataclasses import dataclass

from engine.formula import Formula
from engine.truth_table import TruthTable


def classify(formula: Formula) -> str:
    """
    Returns "tautology" (true on every row), "contradiction" (false on every row)
    or "contingency" (a mix).
    """
    raise NotImplementedError("classify")


def are_equivalent(a: Formula, b: Formula) -> bool:
    """
    Logical equivalence: the two formulas agree on every row.
    The table is built over the atoms of both, so P and P ∧ (Q ∨ ¬Q) are equivalent.
    """
    raise NotImplementedError("are_equivalent")


@dataclass
class ArgumentResult:
    valid: bool                 # no critical row has a false conclusion
    table: TruthTable           # columns are the premises in order, then the conclusion
    critical_rows: list[int]    # indices of rows where every premise is true
    counterexamples: list[int]  # critical rows where the conclusion is false


def check_argument(premises: list[Formula], conclusion: Formula) -> ArgumentResult:
    """
    Tests the argument P1, ..., Pn ∴ C.
    It is valid exactly when (P1 ∧ ... ∧ Pn) → C is a tautology.

    Two cases to keep in mind:
      - no premises: every row is critical, so the argument is valid only if C is a tautology
      - contradictory premises: there are no critical rows, so the argument is valid whatever C is
    """
    raise NotImplementedError("check_argument")
