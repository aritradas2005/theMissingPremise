import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_get_atoms_is_alphabetical_without_duplicates():
    pass


@todo
def test_evaluate_follows_the_truth_table_of_each_connective():
    pass


@todo
def test_implies_is_false_only_for_true_then_false():
    pass


@todo
def test_evaluate_raises_key_error_for_a_missing_atom():
    pass


@todo
def test_get_subformulas_smallest_first_whole_formula_last_no_duplicates():
    pass
