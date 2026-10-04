"""
Turning a finished case into a score.
"""

from dataclasses import dataclass

from game.game_state import GameState


@dataclass
class Score:
    total: int
    # Each entry is (label, points), e.g. ("Case solved", 100) or ("2 invalid steps", -20).
    breakdown: list[tuple[str, int]]


def score_case(state: GameState) -> Score:
    """Rewards solving the case and takes points off for mistakes and hints."""
    raise NotImplementedError("score_case")
