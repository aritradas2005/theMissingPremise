import pytest

from engine import MAX_CNF_STEPS, are_equivalent, parse, to_clauses, to_cnf


def test_implication_is_eliminated():
    """P → Q becomes ¬P ∨ Q."""
    conv = to_cnf(parse("P -> Q"))
    assert conv.result == parse("~P | Q")


def test_biconditional_is_eliminated():
    """P ↔ Q becomes (¬P ∨ Q) ∧ (¬Q ∨ P)."""
    conv = to_cnf(parse("P <-> Q"))
    assert conv.result == parse("(~P | Q) & (~Q | P)")


def test_de_morgan():
    """¬(P ∧ Q) becomes ¬P ∨ ¬Q."""
    conv1 = to_cnf(parse("~(P & Q)"))
    assert conv1.result == parse("~P | ~Q")

    conv2 = to_cnf(parse("~(P | Q)"))
    assert conv2.result == parse("~P & ~Q")


def test_double_negation():
    """¬¬P becomes P."""
    conv = to_cnf(parse("~~P"))
    assert conv.result == parse("P")


def test_or_distributes_over_and():
    """P ∨ (Q ∧ R) becomes (P ∨ Q) ∧ (P ∨ R)."""
    conv = to_cnf(parse("P | (Q & R)"))
    assert conv.result == parse("(P | Q) & (P | R)")


def test_result_is_equivalent_to_the_input():
    cases = [
        "P -> Q",
        "P <-> Q",
        "~(P & (Q | ~R))",
        "(P | Q) -> (R & S)",
        "~~(A & B)",
        "(A & B) | (C & D)",
    ]
    for text in cases:
        f = parse(text)
        conv = to_cnf(f)
        assert are_equivalent(f, conv.result)


def test_a_formula_already_in_cnf_has_no_steps():
    f = parse("(P | ~Q) & (R | S)")
    conv = to_cnf(f)
    assert len(conv.steps) == 0
    assert conv.result == f


def test_to_clauses_drops_clauses_with_an_atom_and_its_negation():
    f = parse("(P | ~P) & (Q | ~R)")
    clauses = to_clauses(f)
    assert len(clauses) == 1
    assert clauses[0] == frozenset({"Q", "¬R"})


def test_a_formula_that_would_take_too_many_steps_is_refused():
    """Five ↔ inside one another used to take over a minute to convert."""
    formula = parse("A <-> (B <-> (C <-> (D <-> (E <-> F))))")
    with pytest.raises(ValueError, match="too large to convert to CNF"):
        to_cnf(formula)


def test_four_nested_biconditionals_are_still_converted():
    formula = parse("A <-> (B <-> (C <-> (D <-> E)))")
    conv = to_cnf(formula)
    assert 0 < len(conv.steps) <= MAX_CNF_STEPS
    assert are_equivalent(formula, conv.result)
