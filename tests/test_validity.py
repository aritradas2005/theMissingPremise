import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_classify():
    """P ∨ ¬P is a tautology, P ∧ ¬P a contradiction, P → Q a contingency."""


@todo
def test_implication_is_equivalent_to_its_or_form():
    """P → Q and ¬P ∨ Q."""


@todo
def test_de_morgan_equivalence():
    """¬(P ∧ Q) and ¬P ∨ ¬Q."""


@todo
def test_equivalence_over_different_atoms():
    """P and P ∧ (Q ∨ ¬Q)."""


@todo
def test_modus_ponens_is_a_valid_argument():
    pass


@todo
def test_affirming_the_consequent_is_invalid_with_its_counterexample_row():
    """P → Q, Q ∴ P fails on the row P false, Q true."""


@todo
def test_no_premises_is_valid_only_for_a_tautology():
    pass


@todo
def test_contradictory_premises_have_no_critical_rows_and_are_valid():
    pass
