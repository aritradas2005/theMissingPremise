"""
Runs the engine on every entry in the test_data/ folder and compares the
answer with the one written in the file.

    test_data/arguments.json        arguments, and whether each is valid
    test_data/formulas.json         formulas, and what kind each is
    test_data/malformed_input.json  bad input, and the message it should get
"""

import json
from pathlib import Path

import pytest

from engine import (
    ParseError,
    build_truth_table,
    check_argument,
    classify,
    parse,
    prove_by_resolution,
)

TEST_DATA = Path(__file__).parent.parent / "test_data"


def read(name: str) -> list[dict]:
    with open(TEST_DATA / name, encoding="utf-8") as file:
        return json.load(file)


def name_of(entry: dict) -> str:
    """The label pytest shows for one entry of a file."""
    return entry.get("name") or entry.get("formula") or repr(entry["input"])


ARGUMENTS = read("arguments.json")
FORMULAS = read("formulas.json")
MALFORMED = read("malformed_input.json")


@pytest.mark.parametrize("entry", ARGUMENTS, ids=name_of)
def test_argument_gets_the_expected_verdict(entry):
    premises = [parse(text) for text in entry["premises"]]
    conclusion = parse(entry["conclusion"])

    result = check_argument(premises, conclusion)

    assert result.valid == entry["valid"]
    if not entry["valid"]:
        counterexamples = [result.table.rows[row].assignment for row in result.counterexamples]
        assert entry["counterexample"] in counterexamples


@pytest.mark.parametrize("entry", ARGUMENTS, ids=name_of)
def test_resolution_agrees_with_the_truth_table(entry):
    premises = [parse(text) for text in entry["premises"]]
    conclusion = parse(entry["conclusion"])

    assert prove_by_resolution(premises, conclusion).proved == entry["valid"]


@pytest.mark.parametrize("entry", FORMULAS, ids=name_of)
def test_formula_is_of_the_expected_kind(entry):
    formula = parse(entry["formula"])
    table = build_truth_table([formula])
    true_rows = [row for row in table.rows if row.values[0]]

    assert classify(formula) == entry["kind"]
    assert len(table.rows) == entry["rows"]
    assert len(true_rows) == entry["true_rows"]


@pytest.mark.parametrize("entry", MALFORMED, ids=name_of)
def test_malformed_input_gets_the_expected_message(entry):
    with pytest.raises(ParseError) as error:
        parse(entry["input"])

    assert str(error.value) == entry["message"]
    assert error.value.position == entry["position"]
