"""
The checks behind the game's title: which clue closes the gap in an argument,
and which witness has to be lying when the statements cannot all be true.
"""

from dataclasses import dataclass

from engine.formula import Formula


def is_consistent(formulas: list[Formula]) -> bool:
    """
    Returns True when some assignment makes all the formulas true.
    An empty list is consistent.
    """
    raise NotImplementedError("is_consistent")


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
    raise NotImplementedError("try_candidates")


def find_liars(statements: list[Formula]) -> list[int]:
    """
    For statements that cannot all be true: returns the index of each statement
    whose removal alone leaves the rest consistent.
    Returns an empty list if the statements are already consistent.
    """
    raise NotImplementedError("find_liars")
