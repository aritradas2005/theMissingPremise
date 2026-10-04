"""
Reading case files from data/cases/.

A case is a dictionary with these keys (see data/cases/case-01.json):
    id, title, difficulty, briefing
    atoms        atom name → what it means in English
    statements   what the witnesses say: a list of {speaker, text, formula}
    clues        facts found at the scene: a list of {id, location, text, formula};
                 some close the gap, some are distractions
    conclusion   what the detective must prove: {text, formula}
    rules        ids from engine.RULES that the player may use in this case
"""

import json
from pathlib import Path

CASES_DIR = Path(__file__).parent.parent / "data" / "cases"


def load_case_index() -> list[dict]:
    """Returns the id, title and difficulty of every case, in play order."""
    return _read_json(CASES_DIR / "index.json")


def load_case(case_id: str) -> dict:
    """
    Returns one case.

    Raises FileNotFoundError if there is no case with this id.
    """
    return _read_json(CASES_DIR / f"{case_id}.json")


def _read_json(path: Path):
    # The case files contain symbols such as ¬, so the encoding must be stated:
    # on Windows, open() does not default to UTF-8.
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def validate_case(case: dict) -> list[str]:
    """
    Checks a case before it is played, whether it came from a file or from the
    custom case screen: every formula parses, every atom used is listed in atoms,
    clue ids are unique, every rule id exists.

    Returns one message per problem; an empty list means the case is playable.
    """
    raise NotImplementedError("validate_case")
