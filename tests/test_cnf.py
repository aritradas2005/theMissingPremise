import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_implication_is_eliminated():
    """P → Q becomes ¬P ∨ Q."""


@todo
def test_biconditional_is_eliminated():
    """P ↔ Q becomes (¬P ∨ Q) ∧ (¬Q ∨ P)."""


@todo
def test_de_morgan():
    """¬(P ∧ Q) becomes ¬P ∨ ¬Q."""


@todo
def test_double_negation():
    """¬¬P becomes P."""


@todo
def test_or_distributes_over_and():
    """P ∨ (Q ∧ R) becomes (P ∨ Q) ∧ (P ∨ R)."""


@todo
def test_result_is_equivalent_to_the_input():
    pass


@todo
def test_a_formula_already_in_cnf_has_no_steps():
    pass


@todo
def test_to_clauses_drops_clauses_with_an_atom_and_its_negation():
    pass
