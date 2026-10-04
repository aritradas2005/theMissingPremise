"""
Questions answered by reading a truth table: what kind of formula is this,
are two formulas equivalent, and does a conclusion follow from the premises.
"""

from dataclasses import dataclass

from engine.formula import Formula
from engine.truth_table import TruthTable, build_truth_table


def classify(formula: Formula) -> str:
    """
    Returns "tautology" (true on every row), "contradiction" (false on every row)
    or "contingency" (a mix).
    """
    table = build_truth_table([formula])
    results = [row.values[0] for row in table.rows]

    if all(results):
        return "tautology"
    if not any(results):
        return "contradiction"
    return "contingency"


def are_equivalent(a: Formula, b: Formula) -> bool:
    """
    Logical equivalence: the two formulas agree on every row.
    The table is built over the atoms of both, so P and P ∧ (Q ∨ ¬Q) are equivalent.
    """
    table = build_truth_table([a, b])
    return all(row.values[0] == row.values[1] for row in table.rows)


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
    table = build_truth_table(premises + [conclusion])

    critical_rows = []
    counterexamples = []
    for index, row in enumerate(table.rows):
        premise_values = row.values[:-1]
        conclusion_value = row.values[-1]

        # all([]) is True, which is what makes every row critical when there are no premises.
        if all(premise_values):
            critical_rows.append(index)
            if not conclusion_value:
                counterexamples.append(index)

    return ArgumentResult(
        valid=len(counterexamples) == 0,
        table=table,
        critical_rows=critical_rows,
        counterexamples=counterexamples,
    )
