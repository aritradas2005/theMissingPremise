"""
Conjunctive normal form (CNF): rewriting a formula as an AND of ORs of literals,
for example (¬P ∨ Q) ∧ (P ∨ R). Every rewrite is recorded so it can be shown
step by step.

The conversion makes four kinds of change, always in this order:
    1. remove ↔      A ↔ B      becomes  (A → B) ∧ (B → A)
    2. remove →      A → B      becomes  ¬A ∨ B
    3. push ¬ in     ¬¬A        becomes  A
                     ¬(A ∧ B)   becomes  ¬A ∨ ¬B        (De Morgan)
                     ¬(A ∨ B)   becomes  ¬A ∧ ¬B        (De Morgan)
    4. distribute    A ∨ (B ∧ C) becomes (A ∨ B) ∧ (A ∨ C)

Each function below makes one kind of change and returns the new formula.
It returns a formula equal to the one it was given when there was nothing to
change, which is how to_cnf() knows when to stop.
"""

from dataclasses import dataclass

from engine.formula import And, Atom, Formula, Iff, Implies, Not, Or

# One OR of literals. A literal is an atom name, or "¬" followed by an atom name.
# A frozenset is a set that cannot change, which lets clauses be stored inside other sets.
# The empty clause frozenset() stands for a contradiction.
Clause = frozenset[str]

# Distributing ∨ over ∧ can double the size of a formula at every step, so a
# formula with several ↔ inside one another can need thousands of steps and
# minutes of time. The conversion stops with an error at this many steps.
MAX_CNF_STEPS = 1000


@dataclass
class CnfStep:
    rule: str         # what was done, e.g. "Eliminate →" or "De Morgan"
    formula: Formula  # the whole formula after this step


@dataclass
class CnfConversion:
    steps: list[CnfStep]
    result: Formula


def same_connective(formula: Formula, left: Formula, right: Formula) -> Formula:
    """A formula with the same connective as the one given, but with new sides."""
    connective = type(formula)
    return connective(left, right)


# ------------------------------------------------------ the kinds of change


def remove_iff(formula: Formula) -> Formula:
    """Replaces every A ↔ B by (A → B) ∧ (B → A)."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(remove_iff(formula.operand))

    left = remove_iff(formula.left)
    right = remove_iff(formula.right)
    if isinstance(formula, Iff):
        return And(Implies(left, right), Implies(right, left))
    return same_connective(formula, left, right)


def remove_implies(formula: Formula) -> Formula:
    """Replaces every A → B by ¬A ∨ B."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(remove_implies(formula.operand))

    left = remove_implies(formula.left)
    right = remove_implies(formula.right)
    if isinstance(formula, Implies):
        return Or(Not(left), right)
    return same_connective(formula, left, right)


def remove_double_negations(formula: Formula) -> Formula:
    """Replaces every ¬¬A by A."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        inside = formula.operand
        if isinstance(inside, Not):
            return remove_double_negations(inside.operand)
        return Not(remove_double_negations(inside))

    left = remove_double_negations(formula.left)
    right = remove_double_negations(formula.right)
    return same_connective(formula, left, right)


def apply_de_morgan(formula: Formula) -> Formula:
    """Replaces ¬(A ∧ B) by ¬A ∨ ¬B, and ¬(A ∨ B) by ¬A ∧ ¬B."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        inside = formula.operand
        if isinstance(inside, And):
            return Or(Not(inside.left), Not(inside.right))
        if isinstance(inside, Or):
            return And(Not(inside.left), Not(inside.right))
        return Not(apply_de_morgan(inside))

    left = apply_de_morgan(formula.left)
    right = apply_de_morgan(formula.right)
    return same_connective(formula, left, right)


def distribute_once(formula: Formula) -> Formula:
    """
    Replaces A ∨ (B ∧ C) by (A ∨ B) ∧ (A ∨ C) at the first place it fits.
    Only one place is changed per call, so each call is one visible step.

    When nothing fits, the very same formula is handed back. to_cnf() checks
    for that with "is", which asks "is this the same object?" and is instant.
    """
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        inside = distribute_once(formula.operand)
        if inside is formula.operand:
            return formula
        return Not(inside)

    left = formula.left
    right = formula.right

    if isinstance(formula, Or) and isinstance(right, And):
        return And(Or(left, right.left), Or(left, right.right))
    if isinstance(formula, Or) and isinstance(left, And):
        return And(Or(left.left, right), Or(left.right, right))

    # Nothing to do at this level: look inside the left side, then the right.
    new_left = distribute_once(left)
    if new_left is not left:
        return same_connective(formula, new_left, right)
    new_right = distribute_once(right)
    if new_right is not right:
        return same_connective(formula, left, new_right)
    return formula


# ------------------------------------------------------------ the conversion


def record(steps: list[CnfStep], rule: str, formula: Formula) -> None:
    """Adds one step to the list, and gives up once the conversion has taken too many."""
    if len(steps) >= MAX_CNF_STEPS:
        raise ValueError(
            f"This formula is too large to convert to CNF: it needs more than {MAX_CNF_STEPS} "
            "rewriting steps. Formulas with several ↔ inside one another grow very quickly."
        )
    steps.append(CnfStep(rule, formula))


def to_cnf(formula: Formula) -> CnfConversion:
    """
    Converts a formula to CNF and returns every step taken and the result.
    Steps that change nothing are left out.

    Raises ValueError if the conversion needs more than MAX_CNF_STEPS steps.
    """
    steps = []
    current = formula

    # 1. Remove ↔.
    changed = remove_iff(current)
    if changed != current:
        current = changed
        record(steps, "Eliminate ↔", current)

    # 2. Remove →.
    changed = remove_implies(current)
    if changed != current:
        current = changed
        record(steps, "Eliminate →", current)

    # 3. Push ¬ inwards. Double negations are cleared first; when there are
    #    none, De Morgan is applied. Repeat until neither changes anything.
    while True:
        changed = remove_double_negations(current)
        rule = "Double negation"
        if changed == current:
            changed = apply_de_morgan(current)
            rule = "De Morgan"
        if changed == current:
            break
        current = changed
        record(steps, rule, current)

    # 4. Distribute ∨ over ∧, one place at a time, until no place is left.
    while True:
        changed = distribute_once(current)
        if changed is current:
            break
        current = changed
        record(steps, "Distribute ∨ over ∧", current)

    return CnfConversion(steps=steps, result=current)


# ------------------------------------------------------------------ clauses


def split_on_and(formula: Formula) -> list[Formula]:
    """The pieces of a formula that are joined by ∧: for (A ∨ B) ∧ C these are A ∨ B and C."""
    if isinstance(formula, And):
        return split_on_and(formula.left) + split_on_and(formula.right)
    return [formula]


def literals_of(formula: Formula) -> list[str]:
    """The literals joined by ∨ in one piece: for A ∨ ¬B these are "A" and "¬B"."""
    if isinstance(formula, Or):
        return literals_of(formula.left) + literals_of(formula.right)
    if isinstance(formula, Atom):
        return [formula.name]
    if isinstance(formula, Not) and isinstance(formula.operand, Atom):
        return ["¬" + formula.operand.name]
    raise ValueError(f"Formula is not in CNF: {formula}")


def is_always_true(clause: Clause) -> bool:
    """True when the clause holds both an atom and its negation, such as P ∨ ¬P."""
    for literal in clause:
        if "¬" + literal in clause:
            return True
    return False


def to_clauses(cnf_formula: Formula) -> list[Clause]:
    """
    Reads the clauses off a formula that is already in CNF.
    Clauses containing both X and ¬X are always true and are dropped,
    and a clause that appears twice is kept once.
    """
    clauses = []
    for piece in split_on_and(cnf_formula):
        clause = frozenset(literals_of(piece))
        if not is_always_true(clause) and clause not in clauses:
            clauses.append(clause)
    return clauses
