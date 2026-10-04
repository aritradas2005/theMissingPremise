"""
Reading case files from data/cases/, checking them, and building a case
from formulas typed on the custom case screen.

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

from engine import MAX_ATOMS, RULES, ParseError, get_atoms, parse

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
    clue ids are unique, every rule id exists, and the case fits in a truth table.

    Returns one message per problem; an empty list means the case is playable.
    """
    problems = []

    # Every formula in the case, with a label saying where it came from.
    labelled = [(f"Statement by {s['speaker']}", s["formula"]) for s in case["statements"]]
    labelled += [(f"Clue '{c['id']}'", c["formula"]) for c in case["clues"]]
    labelled.append(("Conclusion", case["conclusion"]["formula"]))

    used_atoms = set()
    for label, text in labelled:
        try:
            formula = parse(text)
        except ParseError as error:
            problems.append(f"{label}: {error}")
            continue
        used_atoms.update(get_atoms(formula))

    for name in sorted(used_atoms):
        if name not in case["atoms"]:
            problems.append(f"Atom {name} is used but not listed in atoms.")

    if len(used_atoms) > MAX_ATOMS:
        problems.append(f"The case uses {len(used_atoms)} atoms; the limit is {MAX_ATOMS}.")

    seen_ids = set()
    for clue in case["clues"]:
        if clue["id"] in seen_ids:
            problems.append(f"Clue id '{clue['id']}' is used more than once.")
        seen_ids.add(clue["id"])

    known_rules = {rule.id for rule in RULES}
    for rule_id in case["rules"]:
        if rule_id not in known_rules:
            problems.append(f"Unknown rule '{rule_id}'.")

    return problems


def build_custom_case(premises: list[str], clues: list[str], conclusion: str) -> dict:
    """
    Turns formulas typed by the player into a case with every rule allowed.
    The premises go straight onto the board; the clues can be added during play.

    The formulas must already parse (use validate_case on the result to be sure).
    """
    atoms = set()
    for text in premises + clues + [conclusion]:
        try:
            atoms.update(get_atoms(parse(text)))
        except ParseError:
            pass  # validate_case reports it

    return {
        "id": "custom",
        "title": "Custom case",
        "difficulty": 0,
        "briefing": "",
        "atoms": {name: "" for name in sorted(atoms)},
        "statements": [
            {"speaker": f"Premise {number}", "text": "", "formula": text}
            for number, text in enumerate(premises, start=1)
        ],
        "clues": [
            {"id": f"clue {number}", "location": f"Clue {number}", "text": "", "formula": text}
            for number, text in enumerate(clues, start=1)
        ],
        "conclusion": {"text": "", "formula": conclusion},
        "rules": [rule.id for rule in RULES],
    }
