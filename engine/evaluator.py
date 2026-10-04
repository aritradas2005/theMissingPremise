"""
Working out the truth value of a formula under one assignment of its atoms.

All three functions walk the formula tree recursively: handle the node in hand,
and call the same function on its parts.
"""

from engine.formula import And, Atom, Formula, Iff, Implies, Not, Or

# Atom name → truth value, for example {"P": True, "Q": False}.
Assignment = dict[str, bool]


def get_atoms(formula: Formula) -> list[str]:
    """Returns the atom names used, in alphabetical order, without duplicates."""
    names = set()
    _collect_atoms(formula, names)
    return sorted(names)


def _collect_atoms(formula: Formula, names: set[str]) -> None:
    if isinstance(formula, Atom):
        names.add(formula.name)
    elif isinstance(formula, Not):
        _collect_atoms(formula.operand, names)
    else:
        _collect_atoms(formula.left, names)
        _collect_atoms(formula.right, names)


def evaluate(formula: Formula, assignment: Assignment) -> bool:
    """
    Returns the truth value of the formula.

    Raises KeyError if the formula uses an atom the assignment does not mention.
    """
    if isinstance(formula, Atom):
        return assignment[formula.name]

    if isinstance(formula, Not):
        return not evaluate(formula.operand, assignment)

    left = evaluate(formula.left, assignment)
    right = evaluate(formula.right, assignment)

    if isinstance(formula, And):
        return left and right
    if isinstance(formula, Or):
        return left or right
    if isinstance(formula, Implies):
        # False only when a true statement leads to a false one.
        return (not left) or right
    if isinstance(formula, Iff):
        return left == right

    raise TypeError(f"Not a formula: {formula!r}")


def get_subformulas(formula: Formula) -> list[Formula]:
    """
    Returns every part of a formula, smallest first, ending with the formula itself,
    without duplicates. Used to show the intermediate columns of a truth table.

    For (P → Q) ∧ ¬R the result is: P, Q, R, P → Q, ¬R, (P → Q) ∧ ¬R.
    """
    parts = []
    _collect_subformulas(formula, parts)
    # sorted() keeps parts of the same size in the order they were found.
    return sorted(parts, key=_count_connectives)


def _collect_subformulas(formula: Formula, parts: list[Formula]) -> None:
    """Adds the parts of a formula before the formula itself, skipping repeats."""
    if isinstance(formula, Not):
        _collect_subformulas(formula.operand, parts)
    elif not isinstance(formula, Atom):
        _collect_subformulas(formula.left, parts)
        _collect_subformulas(formula.right, parts)

    if formula not in parts:
        parts.append(formula)


def _count_connectives(formula: Formula) -> int:
    if isinstance(formula, Atom):
        return 0
    if isinstance(formula, Not):
        return 1 + _count_connectives(formula.operand)
    return 1 + _count_connectives(formula.left) + _count_connectives(formula.right)
