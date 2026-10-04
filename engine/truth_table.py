"""
Truth tables: every assignment of the atoms, with each formula evaluated on it.
"""

from dataclasses import dataclass

from engine.evaluator import Assignment
from engine.formula import Formula

# A table has 2^n rows, so n is capped: 8 atoms is already 256 rows.
MAX_ATOMS = 8


@dataclass
class TruthTableRow:
    assignment: Assignment
    values: list[bool]  # values[i] is columns[i] evaluated on this row


@dataclass
class TruthTable:
    atoms: list[str]           # all atoms used by the columns, alphabetical
    columns: list[Formula]     # the formulas, in the order they were given
    rows: list[TruthTableRow]  # 2^n rows in textbook order: all true first, all false last


def build_truth_table(formulas: list[Formula]) -> TruthTable:
    """
    Builds a table with one column per formula.

    Raises ValueError if the formulas use more than MAX_ATOMS atoms.
    """
    raise NotImplementedError("build_truth_table")
