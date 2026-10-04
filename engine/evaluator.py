"""
Working out the truth value of a formula under one assignment of its atoms.
"""

from engine.formula import Formula

# Atom name → truth value, for example {"P": True, "Q": False}.
Assignment = dict[str, bool]


def get_atoms(formula: Formula) -> list[str]:
    """Returns the atom names used, in alphabetical order, without duplicates."""
    raise NotImplementedError("get_atoms")


def evaluate(formula: Formula, assignment: Assignment) -> bool:
    """
    Returns the truth value of the formula.

    Raises KeyError if the formula uses an atom the assignment does not mention.
    """
    raise NotImplementedError("evaluate")


def get_subformulas(formula: Formula) -> list[Formula]:
    """
    Returns every part of a formula, smallest first, ending with the formula itself,
    without duplicates. Used to show the intermediate columns of a truth table.

    For (P → Q) ∧ ¬R the result is: P, Q, R, P → Q, ¬R, (P → Q) ∧ ¬R.
    """
    raise NotImplementedError("get_subformulas")
