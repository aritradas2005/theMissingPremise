import pytest

from engine import MAX_ATOMS, build_truth_table, parse


@pytest.mark.parametrize("text, rows", [("P", 2), ("P & Q", 4), ("P & Q | R", 8), ("A & B & C & D", 16)])
def test_n_atoms_give_two_to_the_n_rows(text, rows):
    assert len(build_truth_table([parse(text)]).rows) == rows


def test_rows_run_from_all_true_to_all_false():
    table = build_truth_table([parse("P & Q")])
    assert [row.assignment for row in table.rows] == [
        {"P": True, "Q": True},
        {"P": True, "Q": False},
        {"P": False, "Q": True},
        {"P": False, "Q": False},
    ]


def test_atoms_are_collected_across_all_columns():
    table = build_truth_table([parse("Q -> R"), parse("P")])
    assert table.atoms == ["P", "Q", "R"]
    assert len(table.rows) == 8


def test_values_line_up_with_columns():
    columns = [parse("P & Q"), parse("P | Q"), parse("P -> Q")]
    table = build_truth_table(columns)

    assert table.columns == columns
    assert [row.values for row in table.rows] == [
        [True, True, True],
        [False, True, False],
        [False, True, True],
        [False, False, True],
    ]


def test_a_repeated_atom_is_one_column_of_the_assignment():
    table = build_truth_table([parse("P & ~P")])
    assert table.atoms == ["P"]
    assert [row.values for row in table.rows] == [[False], [False]]


def test_the_limit_itself_is_allowed():
    atoms = [f"A{number}" for number in range(MAX_ATOMS)]
    table = build_truth_table([parse(" & ".join(atoms))])
    assert len(table.rows) == 2 ** MAX_ATOMS


def test_more_than_max_atoms_raises_value_error():
    atoms = [f"A{number}" for number in range(MAX_ATOMS + 1)]
    with pytest.raises(ValueError, match="limit is 8 atoms"):
        build_truth_table([parse(" & ".join(atoms))])
