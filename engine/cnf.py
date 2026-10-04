"""
Conjunctive normal form: rewriting a formula as an AND of ORs of literals,
recording each rewrite so it can be shown step by step.
"""

from dataclasses import dataclass

from engine.formula import And, Atom, Formula, Iff, Implies, Not, Or

# One OR of literals. A literal is an atom name, or "¬" followed by an atom name.
# A frozenset is a set that cannot change, which lets clauses be stored inside other sets.
# The empty clause frozenset() stands for a contradiction.
Clause = frozenset[str]


@dataclass
class CnfStep:
    rule: str         # what was done, e.g. "Eliminate →" or "De Morgan"
    formula: Formula  # the whole formula after this step


@dataclass
class CnfConversion:
    steps: list[CnfStep]
    result: Formula


def _eliminate_iff(f: Formula) -> tuple[Formula, bool]:
    if isinstance(f, Atom):
        return f, False
    if isinstance(f, Not):
        op, changed = _eliminate_iff(f.operand)
        return Not(op), changed
    if isinstance(f, Iff):
        left, _ = _eliminate_iff(f.left)
        right, _ = _eliminate_iff(f.right)
        return And(Implies(left, right), Implies(right, left)), True
    left, ch1 = _eliminate_iff(f.left)
    right, ch2 = _eliminate_iff(f.right)
    return type(f)(left, right), ch1 or ch2


def _eliminate_implies(f: Formula) -> tuple[Formula, bool]:
    if isinstance(f, Atom):
        return f, False
    if isinstance(f, Not):
        op, changed = _eliminate_implies(f.operand)
        return Not(op), changed
    if isinstance(f, Implies):
        left, _ = _eliminate_implies(f.left)
        right, _ = _eliminate_implies(f.right)
        return Or(Not(left), right), True
    left, ch1 = _eliminate_implies(f.left)
    right, ch2 = _eliminate_implies(f.right)
    return type(f)(left, right), ch1 or ch2


def _apply_double_negation(f: Formula) -> tuple[Formula, bool]:
    if isinstance(f, Atom):
        return f, False
    if isinstance(f, Not):
        if isinstance(f.operand, Not):
            res, _ = _apply_double_negation(f.operand.operand)
            return res, True
        op, changed = _apply_double_negation(f.operand)
        return Not(op), changed
    left, ch1 = _apply_double_negation(f.left)
    right, ch2 = _apply_double_negation(f.right)
    return type(f)(left, right), ch1 or ch2


def _apply_de_morgan(f: Formula) -> tuple[Formula, bool]:
    if isinstance(f, Atom):
        return f, False
    if isinstance(f, Not):
        if isinstance(f.operand, And):
            a, b = f.operand.left, f.operand.right
            return Or(Not(a), Not(b)), True
        if isinstance(f.operand, Or):
            a, b = f.operand.left, f.operand.right
            return And(Not(a), Not(b)), True
        op, changed = _apply_de_morgan(f.operand)
        return Not(op), changed
    left, ch1 = _apply_de_morgan(f.left)
    right, ch2 = _apply_de_morgan(f.right)
    return type(f)(left, right), ch1 or ch2


def _distribute_once(f: Formula) -> tuple[Formula, bool]:
    if isinstance(f, Atom):
        return f, False
    if isinstance(f, Not):
        op, ch = _distribute_once(f.operand)
        return Not(op), ch
    if isinstance(f, Or):
        if isinstance(f.right, And):
            a = f.left
            b = f.right.left
            c = f.right.right
            return And(Or(a, b), Or(a, c)), True
        if isinstance(f.left, And):
            a = f.left.left
            b = f.left.right
            c = f.right
            return And(Or(a, c), Or(b, c)), True
        left, ch1 = _distribute_once(f.left)
        if ch1:
            return Or(left, f.right), True
        right, ch2 = _distribute_once(f.right)
        if ch2:
            return Or(f.left, right), True
        return f, False
    if isinstance(f, And):
        left, ch1 = _distribute_once(f.left)
        if ch1:
            return And(left, f.right), True
        right, ch2 = _distribute_once(f.right)
        if ch2:
            return And(f.left, right), True
        return f, False
    return f, False


def to_cnf(formula: Formula) -> CnfConversion:
    """
    Converts in this order: eliminate ↔, eliminate →, push ¬ inwards
    (De Morgan, double negation), distribute ∨ over ∧.
    Steps that change nothing are left out.
    """
    steps: list[CnfStep] = []
    current = formula

    # 1. Eliminate ↔
    f, changed = _eliminate_iff(current)
    if changed:
        current = f
        steps.append(CnfStep("Eliminate ↔", current))

    # 2. Eliminate →
    f, changed = _eliminate_implies(current)
    if changed:
        current = f
        steps.append(CnfStep("Eliminate →", current))

    # 3. Push ¬ inwards (De Morgan, double negation)
    while True:
        f, changed = _apply_double_negation(current)
        if changed:
            current = f
            steps.append(CnfStep("Double negation", current))
            continue
        f, changed = _apply_de_morgan(current)
        if changed:
            current = f
            steps.append(CnfStep("De Morgan", current))
            continue
        break

    # 4. Distribute ∨ over ∧
    while True:
        f, changed = _distribute_once(current)
        if changed:
            current = f
            steps.append(CnfStep("Distribute ∨ over ∧", current))
        else:
            break

    return CnfConversion(steps=steps, result=current)


def to_clauses(cnf_formula: Formula) -> list[Clause]:
    """
    Reads the clauses off a formula that is already in CNF.
    Clauses containing both X and ¬X are always true and are dropped.
    """
    def get_conjuncts(f: Formula) -> list[Formula]:
        if isinstance(f, And):
            return get_conjuncts(f.left) + get_conjuncts(f.right)
        return [f]

    def get_disjuncts(f: Formula) -> list[str]:
        if isinstance(f, Or):
            return get_disjuncts(f.left) + get_disjuncts(f.right)
        if isinstance(f, Atom):
            return [f.name]
        if isinstance(f, Not) and isinstance(f.operand, Atom):
            return [f"¬{f.operand.name}"]
        raise ValueError(f"Formula is not in CNF: {f}")

    clauses: list[Clause] = []
    seen: set[Clause] = set()
    for conj in get_conjuncts(cnf_formula):
        lits = get_disjuncts(conj)
        clause = frozenset(lits)
        # Drop tautological clauses containing X and ¬X
        has_tautology = any(
            f"¬{lit}" in clause for lit in clause if not lit.startswith("¬")
        )
        if not has_tautology and clause not in seen:
            clauses.append(clause)
            seen.add(clause)
    return clauses
