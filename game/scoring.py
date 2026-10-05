"""
Points, stars and rank.

A solved case is worth 100 points. Points are taken off for each rejected
step, each hint, and each clue the player pinned to the board that the
argument did not need. Stars and rank are worked out from the points.
"""

from dataclasses import dataclass

from engine import check_argument, parse
from game.game_state import GameState, goal

SOLVED_POINTS = 100
MISTAKE_PENALTY = 10
HINT_PENALTY = 15
UNNEEDED_CLUE_PENALTY = 10

# The detective's rank: the points needed, and the title earned.
RANKS = [
    (0, "Rookie"),
    (100, "Constable"),
    (200, "Detective"),
    (300, "Inspector"),
    (400, "Chief Inspector"),
    (500, "Master of Logic"),
]


@dataclass
class Score:
    total: int
    # Each entry is (label, points), e.g. ("Case solved", 100) or ("Rejected steps: 2", -20).
    breakdown: list[tuple[str, int]]


def rank_for(points: int) -> str:
    """Returns the highest rank whose points have been reached."""
    title = "Rookie"
    for points_needed, name in RANKS:
        if points >= points_needed:
            title = name
    return title


def stars_for(total: int) -> int:
    """Stars for a solved case: three for 90 points or more, two for 60 or more, otherwise one."""
    if total >= 90:
        return 3
    if total >= 60:
        return 2
    return 1


def unneeded_clues(state: GameState) -> list[str]:
    """
    The ids of the collected clues that the argument did not need.

    A clue was not needed if, with that one clue taken away, the statements
    and the other collected clues still entail the conclusion.
    """
    statements = [parse(statement["formula"]) for statement in state.case["statements"]]

    collected = []
    for clue in state.case["clues"]:
        if clue["id"] in state.collected_clues:
            collected.append(clue)

    unneeded = []
    for clue in collected:
        others = []
        for other in collected:
            if other["id"] != clue["id"]:
                others.append(parse(other["formula"]))
        if check_argument(statements + others, goal(state)).valid:
            unneeded.append(clue["id"])
    return unneeded


def score_case(state: GameState) -> Score:
    """Rewards solving the case and takes points off for mistakes, hints and unneeded clues."""
    breakdown = []

    if state.solved:
        breakdown.append(("Case solved", SOLVED_POINTS))
    if state.mistakes > 0:
        breakdown.append((f"Rejected steps: {state.mistakes}", -MISTAKE_PENALTY * state.mistakes))
    if state.hints_used > 0:
        breakdown.append((f"Hints used: {state.hints_used}", -HINT_PENALTY * state.hints_used))
    for clue_id in unneeded_clues(state):
        breakdown.append((f"Clue not needed: {clue_id}", -UNNEEDED_CLUE_PENALTY))

    total = 0
    for label, points in breakdown:
        total += points
    if total < 0:
        total = 0          # the score never goes below zero
    return Score(total=total, breakdown=breakdown)
