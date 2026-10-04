import pytest

from engine import evaluate, format_formula, get_atoms, get_subformulas, parse


def test_get_atoms_is_alphabetical_without_duplicates():
    assert get_atoms(parse("(Q -> P) & (R | Q) & ~P")) == ["P", "Q", "R"]


# Each row is: formula, then its value for (P, Q) = TT, TF, FT, FF.
CONNECTIVE_TABLES = [
    ("~P", [False, False, True, True]),
    ("P & Q", [True, False, False, False]),
    ("P | Q", [True, True, True, False]),
    ("P -> Q", [True, False, True, True]),
    ("P <-> Q", [True, False, False, True]),
]


@pytest.mark.parametrize("text, expected", CONNECTIVE_TABLES)
def test_evaluate_follows_the_truth_table_of_each_connective(text, expected):
    formula = parse(text)
    assignments = [
        {"P": True, "Q": True},
        {"P": True, "Q": False},
        {"P": False, "Q": True},
        {"P": False, "Q": False},
    ]
    assert [evaluate(formula, assignment) for assignment in assignments] == expected


def test_evaluate_a_nested_formula():
    formula = parse("(P -> Q) & ~R")
    assert evaluate(formula, {"P": False, "Q": False, "R": False}) is True
    assert evaluate(formula, {"P": True, "Q": False, "R": False}) is False
    assert evaluate(formula, {"P": True, "Q": True, "R": True}) is False


def test_evaluate_ignores_atoms_the_formula_does_not_use():
    assert evaluate(parse("P"), {"P": True, "Z": False}) is True


def test_evaluate_raises_key_error_for_a_missing_atom():
    with pytest.raises(KeyError):
        evaluate(parse("P & Q"), {"P": True})


def test_get_subformulas_smallest_first_whole_formula_last():
    parts = get_subformulas(parse("(P -> Q) & ~R"))
    assert [format_formula(part) for part in parts] == [
        "P", "Q", "R", "P → Q", "¬R", "(P → Q) ∧ ¬R",
    ]


def test_get_subformulas_has_no_duplicates():
    parts = get_subformulas(parse("(P & Q) | (P & Q)"))
    assert [format_formula(part) for part in parts] == ["P", "Q", "P ∧ Q", "P ∧ Q ∨ P ∧ Q"]


def test_get_subformulas_of_an_atom_is_just_the_atom():
    assert get_subformulas(parse("P")) == [parse("P")]
