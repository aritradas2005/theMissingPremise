"""
Truth tables: every assignment of the atoms, with each formula evaluated on it.
"""

from dataclasses import dataclass
from itertools import product

from engine.evaluator import Assignment, evaluate, get_atoms
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
    names = set()
    for formula in formulas:
        names.update(get_atoms(formula))
    atoms = sorted(names)

    if len(atoms) > MAX_ATOMS:
        raise ValueError(
            f"These formulas use {len(atoms)} atoms, which would need {2 ** len(atoms)} rows. "
            f"The limit is {MAX_ATOMS} atoms."
        )

    rows = []
    # product([True, False], repeat=n) yields every n-tuple of truth values:
    # (T, T, T), (T, T, F), (T, F, T), ... (F, F, F). The last atom changes fastest.
    for truth_values in product([True, False], repeat=len(atoms)):
        assignment = dict(zip(atoms, truth_values))
        values = [evaluate(formula, assignment) for formula in formulas]
        rows.append(TruthTableRow(assignment, values))

    return TruthTable(atoms, list(formulas), rows)
