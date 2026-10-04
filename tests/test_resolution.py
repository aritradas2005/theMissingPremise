import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_proves_modus_ponens():
    """P → Q, P ∴ Q."""


@todo
def test_proves_a_chain():
    """W → G, G → B, ¬B ∴ ¬W."""


@todo
def test_does_not_prove_an_invalid_argument():
    """P → Q, Q ∴ P."""


@todo
def test_every_resolvent_names_its_two_parents_and_the_atom():
    pass


@todo
def test_stops_when_no_new_clause_can_be_made():
    pass


@todo
def test_agrees_with_check_argument_on_a_batch_of_arguments():
    pass
