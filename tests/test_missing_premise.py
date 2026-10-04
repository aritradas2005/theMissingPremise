import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_consistent_premises():
    """P, P → Q."""


@todo
def test_inconsistent_premises():
    """P, ¬P."""


@todo
def test_an_empty_list_is_consistent():
    pass


@todo
def test_case_01_missing_premise():
    """¬B closes the gap and M does not."""


@todo
def test_a_candidate_that_contradicts_the_premises_is_not_consistent():
    """It closes the gap, but only because nothing can make all the premises true."""


@todo
def test_find_liars():
    """P, P → Q, ¬Q returns all three."""


@todo
def test_find_liars_on_a_consistent_list_returns_nothing():
    pass
