"""
Text to formula and back.

parse() turns what the player typed into a Formula;
format_formula() turns a Formula back into text.
"""

from dataclasses import dataclass

from engine.formula import And, Formula, Iff, Implies, Not, Or

# What the player may type for each connective. The first entry is the display symbol.
ALIASES = {
    Not: ["¬", "~", "!"],
    And: ["∧", "&", "^"],
    Or: ["∨", "|"],
    Implies: ["→", "->", "=>"],
    Iff: ["↔", "<->", "<=>"],
}

# Binding strength, loosest first: ↔, →, ∨, ∧, ¬.
# ∧ and ∨ group to the left; → groups to the right, so P → Q → R means P → (Q → R).
PRECEDENCE = {Iff: 1, Implies: 2, Or: 3, And: 4, Not: 5}


class ParseError(ValueError):
    """Raised for input that is not a well-formed formula."""

    def __init__(self, message: str, position: int):
        """
        message   plain-English explanation shown to the player
        position  0-based index in the input where the problem was found
        """
        super().__init__(message)
        self.position = position


@dataclass(frozen=True)
class Token:
    kind: str      # "atom", "not", "and", "or", "implies", "iff", "(" or ")"
    text: str      # the characters as typed
    position: int  # 0-based index in the input


def tokenize(text: str) -> list[Token]:
    """
    Splits the input into tokens, skipping spaces.
    Atom names start with a letter and may continue with letters, digits or underscores.

    Raises ParseError on a character that belongs to no token.
    """
    raise NotImplementedError("tokenize")


def parse(text: str) -> Formula:
    """
    Reads a formula such as "(P -> Q) & ~R".

    Raises ParseError on empty input, unbalanced brackets, a missing operand or leftover text.
    """
    raise NotImplementedError("parse")


def format_formula(formula: Formula) -> str:
    """
    Writes a formula with display symbols and only the brackets it needs,
    for example "(P → Q) ∧ ¬R", so that parse(format_formula(f)) == f.
    """
    raise NotImplementedError("format_formula")
