"""
Text to formula and back.

parse() turns what the player typed into a Formula;
format_formula() turns a Formula back into text.

Parsing happens in two passes:
  1. tokenize() cuts the text into tokens: atoms, connectives and brackets.
  2. A recursive descent parser reads the tokens using this grammar,
     one function per line, loosest connective first:

         iff      :=  implies ( ↔ implies )*
         implies  :=  or ( → implies )?
         or       :=  and ( ∨ and )*
         and      :=  unary ( ∧ unary )*
         unary    :=  ¬ unary  |  atom  |  ( iff )

     Each level only calls the level below it, which is what makes ¬ bind
     tighter than ∧, ∧ tighter than ∨, and so on.
"""

from dataclasses import dataclass

from engine.formula import BINARY, SYMBOLS, And, Atom, Formula, Iff, Implies, Not, Or

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

# The token kind for each connective.
KIND = {Not: "not", And: "and", Or: "or", Implies: "implies", Iff: "iff"}


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


# ---------------------------------------------------------------- tokenizer


def tokenize(text: str) -> list[Token]:
    """
    Splits the input into tokens, skipping spaces.
    Atom names start with a letter and may continue with letters, digits or underscores.

    Raises ParseError on a character that belongs to no token.
    """
    tokens = []
    position = 0

    while position < len(text):
        char = text[position]

        if char.isspace():
            position += 1

        elif char in "()":
            tokens.append(Token(char, char, position))
            position += 1

        elif _is_letter(char):
            end = position + 1
            while end < len(text) and _is_name_char(text[end]):
                end += 1
            tokens.append(Token("atom", text[position:end], position))
            position = end

        else:
            token = _read_connective(text, position)
            if token is None:
                raise ParseError(f"'{char}' cannot be used in a formula.", position)
            tokens.append(token)
            position += len(token.text)

    return tokens


def _is_letter(char: str) -> bool:
    return char.isascii() and char.isalpha()


def _is_name_char(char: str) -> bool:
    return char.isascii() and (char.isalnum() or char == "_")


def _read_connective(text: str, position: int) -> Token | None:
    """Returns the connective spelled at this position, or None if there is none."""
    for connective, spellings in ALIASES.items():
        for spelling in spellings:
            if text.startswith(spelling, position):
                return Token(KIND[connective], spelling, position)
    return None


# ------------------------------------------------------------------- parser


class _Parser:
    """Reads a list of tokens from left to right, one grammar rule per method."""

    def __init__(self, tokens: list[Token], end_position: int):
        self.tokens = tokens
        self.index = 0                    # the next token to read
        self.end_position = end_position  # where to point if the formula stops too early

    def peek(self) -> Token | None:
        """Returns the next token without consuming it, or None at the end."""
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def next_is(self, kind: str) -> bool:
        token = self.peek()
        return token is not None and token.kind == kind

    def take(self) -> Token:
        """Consumes the next token and returns it."""
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse_iff(self) -> Formula:
        left = self.parse_implies()
        while self.next_is("iff"):
            self.take()
            left = Iff(left, self.parse_implies())
        return left

    def parse_implies(self) -> Formula:
        left = self.parse_or()
        if self.next_is("implies"):
            self.take()
            # Calling parse_implies again for the right side is what makes
            # → group to the right: P → Q → R becomes P → (Q → R).
            return Implies(left, self.parse_implies())
        return left

    def parse_or(self) -> Formula:
        left = self.parse_and()
        while self.next_is("or"):
            self.take()
            left = Or(left, self.parse_and())
        return left

    def parse_and(self) -> Formula:
        left = self.parse_unary()
        # The loop folds each new operand into the left side,
        # so P ∧ Q ∧ R becomes (P ∧ Q) ∧ R.
        while self.next_is("and"):
            self.take()
            left = And(left, self.parse_unary())
        return left

    def parse_unary(self) -> Formula:
        token = self.peek()

        if token is None:
            raise ParseError(
                "The formula stops too early: an atom, ¬ or ( is expected here.",
                self.end_position,
            )

        if token.kind == "not":
            self.take()
            return Not(self.parse_unary())

        if token.kind == "atom":
            self.take()
            return Atom(token.text)

        if token.kind == "(":
            self.take()
            inside = self.parse_iff()
            closing = self.peek()
            if closing is None:
                raise ParseError("This bracket is never closed.", token.position)
            if closing.kind != ")":
                raise ParseError(
                    f"A connective or ) is expected here, not '{closing.text}'.",
                    closing.position,
                )
            self.take()
            return inside

        raise ParseError(
            f"An atom, ¬ or ( is expected here, not '{token.text}'.", token.position
        )


def parse(text: str) -> Formula:
    """
    Reads a formula such as "(P -> Q) & ~R".

    Raises ParseError on empty input, unbalanced brackets, a missing operand or leftover text.
    """
    tokens = tokenize(text)
    if not tokens:
        raise ParseError("Type a formula first.", 0)

    parser = _Parser(tokens, end_position=len(text))
    formula = parser.parse_iff()

    # A complete formula has been read. Anything still unread is a mistake.
    leftover = parser.peek()
    if leftover is not None:
        if leftover.kind == ")":
            raise ParseError(
                "This closing bracket has no matching opening bracket.", leftover.position
            )
        raise ParseError(
            f"One of ∧ ∨ → ↔ is expected here, not '{leftover.text}'.", leftover.position
        )

    return formula


# ---------------------------------------------------------------- formatter


def format_formula(formula: Formula) -> str:
    """
    Writes a formula with display symbols and only the brackets it needs,
    for example "(P → Q) ∧ ¬R", so that parse(format_formula(f)) == f.
    """
    if isinstance(formula, Atom):
        return formula.name

    if isinstance(formula, Not):
        inner = format_formula(formula.operand)
        if isinstance(formula.operand, BINARY):
            inner = f"({inner})"
        return SYMBOLS[Not] + inner

    connective = type(formula)
    left = format_formula(formula.left)
    right = format_formula(formula.right)

    # A side needs brackets when the parser would otherwise group it differently:
    # when it binds more loosely than this connective, or equally loosely on the
    # side this connective does not group towards.
    groups_to_the_right = connective is Implies
    if _binds_looser(formula.left, connective, or_equal=groups_to_the_right):
        left = f"({left})"
    if _binds_looser(formula.right, connective, or_equal=not groups_to_the_right):
        right = f"({right})"

    return f"{left} {SYMBOLS[connective]} {right}"


def _binds_looser(part: Formula, connective: type, or_equal: bool) -> bool:
    """Is this part of a formula held together more loosely than the connective around it?"""
    if isinstance(part, Atom):
        return False
    if or_equal:
        return PRECEDENCE[type(part)] <= PRECEDENCE[connective]
    return PRECEDENCE[type(part)] < PRECEDENCE[connective]
