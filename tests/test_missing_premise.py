from engine import find_liars, is_consistent, parse, try_candidates


def test_consistent_premises():
    """P, P → Q."""
    assert is_consistent([parse("P"), parse("P -> Q")])


def test_inconsistent_premises():
    """P, ¬P."""
    assert not is_consistent([parse("P"), parse("~P")])


def test_an_empty_list_is_consistent():
    assert is_consistent([])


def test_case_01_missing_premise():
    """¬B closes the gap and M does not."""
    premises = [parse("W -> G"), parse("G -> B")]
    conclusion = parse("~W")
    candidates = [parse("~B"), parse("M")]

    results = try_candidates(premises, conclusion, candidates)
    assert len(results) == 2
    # ~B closes the gap and is consistent
    assert results[0].closes_gap
    assert results[0].consistent
    # M does not close the gap
    assert not results[1].closes_gap


def test_a_candidate_that_contradicts_the_premises_is_not_consistent():
    """It closes the gap, but only because nothing can make all the premises true."""
    premises = [parse("P")]
    conclusion = parse("Q")
    candidates = [parse("~P")]

    results = try_candidates(premises, conclusion, candidates)
    assert len(results) == 1
    assert results[0].closes_gap
    assert not results[0].consistent


def test_find_liars():
    """P, P → Q, ¬Q returns all three."""
    statements = [parse("P"), parse("P -> Q"), parse("~Q")]
    assert find_liars(statements) == [0, 1, 2]


def test_find_liars_on_a_consistent_list_returns_nothing():
    statements = [parse("P"), parse("P -> Q")]
    assert find_liars(statements) == []
