"""
The formula tree shared by every engine module.

A formula is built from six small classes:
    Atom("P")              a proposition letter
    Not(operand)           ¬operand
    And(left, right)       left ∧ right
    Or(left, right)        left ∨ right
    Implies(left, right)   left → right
    Iff(left, right)       left ↔ right

Example: P → ¬Q is Implies(Atom("P"), Not(Atom("Q"))).

Each class is a frozen dataclass: like a C struct whose fields cannot be changed
once it is made. Python writes the constructor and == for us, so two formulas are
equal when they are written the same way, and formulas can be stored in sets.
Equal does not mean logically equivalent: And(P, Q) != And(Q, P).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Not:
    operand: "Formula"


@dataclass(frozen=True)
class And:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True)
class Or:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True)
class Implies:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True)
class Iff:
    left: "Formula"
    right: "Formula"


Formula = Atom | Not | And | Or | Implies | Iff

# The connectives that take two operands, for isinstance(formula, BINARY).
BINARY = (And, Or, Implies, Iff)

# The symbol shown on screen for each connective.
SYMBOLS = {Not: "¬", And: "∧", Or: "∨", Implies: "→", Iff: "↔"}
