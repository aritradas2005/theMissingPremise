"""
Turning a finished case into a score.
"""

from dataclasses import dataclass

from engine import check_argument, parse
from game.game_state import GameState, goal

SOLVED_POINTS = 100
MISTAKE_PENALTY = 10
HINT_PENALTY = 15
UNNEEDED_CLUE_PENALTY = 10


# The detective's rank, by total points across the written cases.
RANKS = [
    (0, "Rookie"),
    (100, "Constable"),
    (200, "Detective"),
    (300, "Inspector"),
    (400, "Chief Inspector"),
    (500, "Master of Logic"),
]


def rank_for(points: int) -> str:
    """Returns the highest rank whose threshold the points have reached."""
    title = RANKS[0][1]
    for threshold, name in RANKS:
        if points >= threshold:
            title = name
    return title


def stars_for(total: int) -> int:
    """Stars for a solved case: three for 90 points or more, two for 60 or more, otherwise one."""
    if total >= 90:
        return 3
    if total >= 60:
        return 2
    return 1


@dataclass
class Score:
    total: int
    # Each entry is (label, points), e.g. ("Case solved", 100) or ("Rejected steps: 2", -20).
    breakdown: list[tuple[str, int]]


def unneeded_clues(state: GameState) -> list[str]:
    """
    The collected clues the argument did not need: with that clue taken away,
    the remaining premises still entail the conclusion.
    """
    statements = [parse(statement["formula"]) for statement in state.case["statements"]]
    collected = [clue for clue in state.case["clues"] if clue["id"] in state.collected_clues]

    unneeded = []
    for clue in collected:
        others = [parse(other["formula"]) for other in collected if other is not clue]
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

    total = sum(points for label, points in breakdown)
    return Score(total=max(0, total), breakdown=breakdown)
