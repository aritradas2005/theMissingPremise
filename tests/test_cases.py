import pytest

from engine import RULES
from game.case_loader import load_case, load_case_index

todo = pytest.mark.skip(reason="not written yet")

INDEX = load_case_index()


def test_the_index_lists_at_least_one_case():
    assert len(INDEX) > 0


@pytest.mark.parametrize("entry", INDEX, ids=lambda entry: entry["id"])
def test_case_has_every_field_the_game_reads(entry):
    case = load_case(entry["id"])

    assert case["id"] == entry["id"]
    assert case["title"] == entry["title"]
    assert case["difficulty"] == entry["difficulty"]
    assert isinstance(case["briefing"], str)
    assert isinstance(case["atoms"], dict)
    assert len(case["statements"]) > 0
    for statement in case["statements"]:
        assert set(statement) == {"speaker", "text", "formula"}
    for clue in case["clues"]:
        assert set(clue) == {"id", "location", "text", "formula"}
    assert set(case["conclusion"]) == {"text", "formula"}
    assert set(case["rules"]) <= {rule.id for rule in RULES}


@todo
def test_every_formula_in_every_case_parses():
    pass


@todo
def test_every_case_is_unsolved_without_its_clues_and_solvable_with_them():
    pass
