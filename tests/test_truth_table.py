import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_n_atoms_give_two_to_the_n_rows():
    pass


@todo
def test_rows_run_from_all_true_to_all_false():
    pass


@todo
def test_atoms_are_collected_across_all_columns():
    pass


@todo
def test_values_line_up_with_columns():
    pass


@todo
def test_one_atom_gives_two_rows():
    pass


@todo
def test_more_than_max_atoms_raises_value_error():
    pass
