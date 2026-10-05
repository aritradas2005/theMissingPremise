"""
The checks behind the game's title: which clue closes the gap in an argument,
and which witness has to be lying when the statements cannot all be true.

All three functions work by reading a truth table.
"""

from dataclasses import dataclass

from engine.formula import Formula
from engine.truth_table import build_truth_table
from engine.validity import check_argument


def is_consistent(formulas: list[Formula]) -> bool:
    """
    Returns True when some row of the truth table makes all the formulas true,
    which means they can all be true together. An empty list is consistent.
    """
    if not formulas:
        return True

    table = build_truth_table(formulas)
    for row in table.rows:
        if all(row.values):
            return True
    return False


@dataclass
class CandidateResult:
    index: int         # position in the candidates list
    closes_gap: bool   # premises plus this candidate entail the conclusion
    consistent: bool   # premises plus this candidate can all be true together


def try_candidates(
    premises: list[Formula], conclusion: Formula, candidates: list[Formula]
) -> list[CandidateResult]:
    """
    Tries each candidate as an extra premise and returns one result per candidate,
    in the same order. The candidates are usually the clues the player has not used yet.

    The missing premise is a candidate with closes_gap and consistent both True:
    a candidate that only closes the gap by contradicting the other premises proves nothing.
    """
    results = []
    for index, candidate in enumerate(candidates):
        with_candidate = premises + [candidate]
        closes_gap = check_argument(with_candidate, conclusion).valid
        consistent = is_consistent(with_candidate)
        results.append(CandidateResult(index, closes_gap, consistent))
    return results


def find_liars(statements: list[Formula]) -> list[int]:
    """
    For statements that cannot all be true: returns the position of each statement
    whose removal alone leaves the rest consistent.
    Returns an empty list if the statements are already consistent.
    """
    if is_consistent(statements):
        return []

    liars = []
    for index in range(len(statements)):
        all_but_this_one = statements[:index] + statements[index + 1:]
        if is_consistent(all_but_this_one):
            liars.append(index)
    return liars
