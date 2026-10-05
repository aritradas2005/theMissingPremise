"""
Reading case files from data/cases/, checking them, and building a case from
formulas typed on the custom case screen.

A case is a dictionary with these keys (see data/cases/case-01.json):
    id, title, difficulty, briefing
    atoms        atom name → what it means in English
    statements   what the witnesses say: a list of {speaker, text, formula}
    clues        facts found at the scene: a list of {id, location, text, formula};
                 some close the gap, some are distractions
    conclusion   what the detective must prove: {text, formula}
    rules        ids from engine.RULES that the player may use in this case

A case file never says which clue is the missing premise. The engine works
that out, so a typed case plays in exactly the same way as a written one.
"""

import json
from pathlib import Path

from engine import MAX_ATOMS, RULES, ParseError, get_atoms, parse

CASES_DIR = Path(__file__).parent.parent / "data" / "cases"


# ---------------------------------------------------------- reading the files


def load_case_index() -> list[dict]:
    """Returns the id, title and difficulty of every case, in play order."""
    return read_json(CASES_DIR / "index.json")


def load_case(case_id: str) -> dict:
    """
    Returns one case.

    Raises FileNotFoundError if there is no case with this id.
    """
    return read_json(CASES_DIR / f"{case_id}.json")


def read_json(path: Path):
    """Reads one JSON file and returns what is in it."""
    # The case files contain symbols such as ¬, so the encoding must be stated:
    # on Windows, open() does not default to UTF-8.
    with open(path, encoding="utf-8") as file:
        return json.load(file)


# ------------------------------------------------------------ checking a case


def formulas_in(case: dict) -> list[tuple[str, str]]:
    """Every formula in a case as (where it came from, its text)."""
    formulas = []
    for statement in case["statements"]:
        formulas.append((f"Statement by {statement['speaker']}", statement["formula"]))
    for clue in case["clues"]:
        formulas.append((f"Clue '{clue['id']}'", clue["formula"]))
    formulas.append(("Conclusion", case["conclusion"]["formula"]))
    return formulas


def validate_case(case: dict) -> list[str]:
    """
    Checks a case before it is played, whether it came from a file or from the
    custom case screen: every formula parses, every atom used is listed in atoms,
    clue ids are unique, every rule id exists, and the case fits in a truth table.

    Returns one message per problem; an empty list means the case is playable.
    """
    problems = []

    # 1. Every formula must parse. Collect the atoms they use on the way.
    used_atoms = set()
    for label, text in formulas_in(case):
        try:
            formula = parse(text)
        except ParseError as error:
            problems.append(f"{label}: {error}")
            continue
        used_atoms.update(get_atoms(formula))

    # 2. Every atom used must be explained in the case, and there must not be too many.
    for name in sorted(used_atoms):
        if name not in case["atoms"]:
            problems.append(f"Atom {name} is used but not listed in atoms.")
    if len(used_atoms) > MAX_ATOMS:
        problems.append(f"The case uses {len(used_atoms)} atoms; the limit is {MAX_ATOMS}.")

    # 3. No two clues may share an id.
    seen_ids = []
    for clue in case["clues"]:
        if clue["id"] in seen_ids:
            problems.append(f"Clue id '{clue['id']}' is used more than once.")
        seen_ids.append(clue["id"])

    # 4. Every rule the case allows must exist.
    known_rules = [rule.id for rule in RULES]
    for rule_id in case["rules"]:
        if rule_id not in known_rules:
            problems.append(f"Unknown rule '{rule_id}'.")

    return problems


# ------------------------------------------------------------- a typed case


def build_custom_case(premises: list[str], clues: list[str], conclusion: str) -> dict:
    """
    Turns formulas typed by the player into a case with every rule allowed.
    The premises go straight onto the board; the clues can be added during play.

    A formula that does not parse is left for validate_case() to report.
    """
    atoms = set()
    for text in premises + clues + [conclusion]:
        try:
            atoms.update(get_atoms(parse(text)))
        except ParseError:
            pass

    statements = []
    for number, text in enumerate(premises, start=1):
        statements.append({"speaker": f"Premise {number}", "text": "", "formula": text})

    clue_entries = []
    for number, text in enumerate(clues, start=1):
        clue_entries.append(
            {"id": f"clue {number}", "location": f"Clue {number}", "text": "", "formula": text}
        )

    # A typed case has no story, so the atoms have no meanings to show.
    meanings = {}
    for name in sorted(atoms):
        meanings[name] = ""

    return {
        "id": "custom",
        "title": "Custom case",
        "difficulty": 0,
        "briefing": "",
        "atoms": meanings,
        "statements": statements,
        "clues": clue_entries,
        "conclusion": {"text": "", "formula": conclusion},
        "rules": [rule.id for rule in RULES],
    }
