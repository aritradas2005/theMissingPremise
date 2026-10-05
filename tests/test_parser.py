import pytest

from engine import (
    MAX_NESTING,
    MAX_TOKENS,
    And,
    Atom,
    Iff,
    Implies,
    Not,
    Or,
    ParseError,
    format_formula,
    parse,
    tokenize,
)

P = Atom("P")
Q = Atom("Q")
R = Atom("R")


# ------------------------------------------------------------------ parsing


def test_single_atom():
    assert parse("P") == P


def test_atom_names_may_be_words():
    assert parse("Butler_Lied2") == Atom("Butler_Lied2")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("¬P", Not(P)),
        ("~P", Not(P)),
        ("!P", Not(P)),
        ("P ∧ Q", And(P, Q)),
        ("P & Q", And(P, Q)),
        ("P ^ Q", And(P, Q)),
        ("P ∨ Q", Or(P, Q)),
        ("P | Q", Or(P, Q)),
        ("P → Q", Implies(P, Q)),
        ("P -> Q", Implies(P, Q)),
        ("P => Q", Implies(P, Q)),
        ("P ↔ Q", Iff(P, Q)),
        ("P <-> Q", Iff(P, Q)),
        ("P <=> Q", Iff(P, Q)),
    ],
)
def test_aliases(text, expected):
    assert parse(text) == expected


def test_precedence():
    """¬ binds tighter than ∧, ∧ than ∨, ∨ than →, → than ↔."""
    assert parse("~P & Q") == And(Not(P), Q)
    assert parse("P | Q & R") == Or(P, And(Q, R))
    assert parse("P & Q | R") == Or(And(P, Q), R)
    assert parse("P -> Q | R") == Implies(P, Or(Q, R))
    assert parse("P <-> Q -> R") == Iff(P, Implies(Q, R))


def test_implies_groups_to_the_right():
    assert parse("P -> Q -> R") == Implies(P, Implies(Q, R))


def test_and_or_and_iff_group_to_the_left():
    assert parse("P & Q & R") == And(And(P, Q), R)
    assert parse("P | Q | R") == Or(Or(P, Q), R)
    assert parse("P <-> Q <-> R") == Iff(Iff(P, Q), R)


def test_brackets_override_precedence():
    assert parse("(P | Q) & R") == And(Or(P, Q), R)
    assert parse("(P -> Q) -> R") == Implies(Implies(P, Q), R)
    assert parse("~(P & Q)") == Not(And(P, Q))
    assert parse("((P))") == P


def test_double_negation():
    assert parse("~~P") == Not(Not(P))


def test_spaces_are_ignored():
    assert parse("  P->Q  ") == parse("P -> Q")


def test_tokens_record_where_they_start():
    tokens = tokenize("P -> (Q)")
    assert [(token.kind, token.text, token.position) for token in tokens] == [
        ("atom", "P", 0),
        ("implies", "->", 2),
        ("(", "(", 5),
        ("atom", "Q", 6),
        (")", ")", 7),
    ]


# ------------------------------------------------------------------- errors


@pytest.mark.parametrize(
    "text, position",
    [
        ("", 0),          # empty
        ("   ", 0),       # only spaces
        ("P ->", 4),      # missing right operand: points just past the end
        ("& P", 0),       # missing left operand
        ("P & | Q", 4),   # two connectives in a row
        ("~", 1),         # ¬ with nothing after it
        ("(P & Q", 0),    # bracket never closed: points at the bracket
        ("P & Q)", 5),    # closing bracket with no opening one
        ("()", 1),        # empty brackets
        ("P Q", 2),       # two atoms with no connective
        ("(P Q)", 3),     # the same, inside brackets
        ("P ~Q", 2),      # ¬ where a two-sided connective is needed
        ("P # Q", 2),     # a character that is not part of any formula
        ("P - Q", 2),     # half of ->
        ("2P", 0),        # atom names cannot start with a digit
    ],
)
def test_malformed_input_is_rejected_with_the_position(text, position):
    with pytest.raises(ParseError) as error:
        parse(text)
    assert error.value.position == position


def test_error_message_names_the_bad_character():
    with pytest.raises(ParseError, match="'#' cannot be used in a formula"):
        parse("P # Q")


# --------------------------------------------------------------- formatting


def test_format_uses_display_symbols():
    assert format_formula(parse("~P & Q | R -> P <-> Q")) == "¬P ∧ Q ∨ R → P ↔ Q"


@pytest.mark.parametrize(
    "formula, text",
    [
        (And(Or(P, Q), R), "(P ∨ Q) ∧ R"),
        (Or(And(P, Q), R), "P ∧ Q ∨ R"),
        (Not(And(P, Q)), "¬(P ∧ Q)"),
        (Not(Not(P)), "¬¬P"),
        (Implies(P, Implies(Q, R)), "P → Q → R"),
        (Implies(Implies(P, Q), R), "(P → Q) → R"),
        (And(And(P, Q), R), "P ∧ Q ∧ R"),
        (And(P, And(Q, R)), "P ∧ (Q ∧ R)"),
        (Iff(P, Iff(Q, R)), "P ↔ (Q ↔ R)"),
    ],
)
def test_format_writes_only_the_brackets_needed(formula, text):
    assert format_formula(formula) == text


@pytest.mark.parametrize(
    "text",
    [
        "P",
        "~~P",
        "~(P & Q) | R",
        "(P -> Q) -> R",
        "P -> Q -> R",
        "P & (Q & R)",
        "(P <-> Q) & ~(R | P)",
        "P <-> (Q <-> R)",
        "(P -> Q) & (Q -> R) -> (P -> R)",
    ],
)
def test_parse_undoes_format(text):
    formula = parse(text)
    assert parse(format_formula(formula)) == formula


# ------------------------------------------------------- very large formulas


def test_nesting_up_to_the_limit_is_accepted():
    assert parse("(" * MAX_NESTING + "P" + ")" * MAX_NESTING) == P
    assert parse("~" * MAX_NESTING + "P") == parse("~" * MAX_NESTING + "P")


def test_nesting_past_the_limit_is_refused_at_the_bracket_that_goes_too_deep():
    with pytest.raises(ParseError, match="nested too deeply") as error:
        parse("(" * (MAX_NESTING + 1) + "P" + ")" * (MAX_NESTING + 1))
    assert error.value.position == MAX_NESTING


def test_brackets_and_negations_count_towards_the_same_limit():
    half = MAX_NESTING // 2
    parse("(" * half + "~" * half + "P" + ")" * half)                 # exactly at the limit
    with pytest.raises(ParseError, match="nested too deeply"):
        parse("(" * half + "~" * (half + 1) + "P" + ")" * half)


def test_closed_brackets_do_not_count_as_nesting():
    """Sixty bracketed atoms side by side are only one level deep."""
    parse(" & ".join(["(P)"] * 40))


@pytest.mark.parametrize(
    "text",
    [
        "(" * 200 + "P" + ")" * 200,        # used to crash with a RecursionError
        "~" * 3000 + "P",                   # so did this
        " & ".join(["P"] * 2000),
        "(" * 100_000,
    ],
    # Short names, because pytest would otherwise use the whole formula as the test's name.
    ids=["200 brackets", "3000 negations", "2000 atoms", "100000 brackets"],
)
def test_an_enormous_formula_is_refused_with_a_message_not_a_crash(text):
    with pytest.raises(ParseError, match="too long"):
        parse(text)


def test_the_longest_accepted_formula_can_be_formatted_and_parsed_again():
    atoms = (MAX_TOKENS + 1) // 2           # n atoms joined by n - 1 connectives
    formula = parse(" -> ".join(["P"] * atoms))
    assert parse(format_formula(formula)) == formula
