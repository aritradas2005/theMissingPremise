"""
Conjunctive normal form: rewriting a formula as an AND of ORs of literals,
recording each rewrite so it can be shown step by step.
"""

from dataclasses import dataclass

from engine.formula import Formula

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


def to_cnf(formula: Formula) -> CnfConversion:
    """
    Converts in this order: eliminate ↔, eliminate →, push ¬ inwards
    (De Morgan, double negation), distribute ∨ over ∧.
    Steps that change nothing are left out.
    """
    raise NotImplementedError("to_cnf")


def to_clauses(cnf_formula: Formula) -> list[Clause]:
    """
    Reads the clauses off a formula that is already in CNF.
    Clauses containing both X and ¬X are always true and are dropped.
    """
    raise NotImplementedError("to_clauses")
