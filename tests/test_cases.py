import pytest

from engine import RULES, check_argument, get_atoms, parse
from game.case_loader import load_case, load_case_index

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
        # speaker, text and formula are required; avatar is optional
        assert {"speaker", "text", "formula"} <= set(statement) <= {"speaker", "text", "formula", "avatar"}
    for clue in case["clues"]:
        assert set(clue) == {"id", "location", "text", "formula"}
    assert set(case["conclusion"]) == {"text", "formula"}
    assert set(case["rules"]) <= {rule.id for rule in RULES}


@pytest.mark.parametrize("entry", INDEX, ids=lambda entry: entry["id"])
def test_every_formula_parses_and_uses_only_declared_atoms(entry):
    case = load_case(entry["id"])
    texts = [statement["formula"] for statement in case["statements"]]
    texts += [clue["formula"] for clue in case["clues"]]
    texts.append(case["conclusion"]["formula"])

    for text in texts:
        formula = parse(text)
        assert set(get_atoms(formula)) <= set(case["atoms"])


@pytest.mark.parametrize("entry", INDEX, ids=lambda entry: entry["id"])
def test_case_is_unsolved_without_its_clues_and_solvable_with_them(entry):
    case = load_case(entry["id"])
    statements = [parse(statement["formula"]) for statement in case["statements"]]
    clues = [parse(clue["formula"]) for clue in case["clues"]]
    conclusion = parse(case["conclusion"]["formula"])

    # The witness statements alone must leave a gap for the player to close.
    assert not check_argument(statements, conclusion).valid

    # With every clue the conclusion follows, and not just because the
    # premises contradict each other.
    with_clues = check_argument(statements + clues, conclusion)
    assert with_clues.valid
    assert len(with_clues.critical_rows) > 0
