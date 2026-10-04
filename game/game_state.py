"""
The state of one case being played: the proof so far, the clues found and the mistakes made.
"""

from dataclasses import dataclass

from engine import Formula, StepResult


@dataclass
class ProofLine:
    id: int             # line number, starting at 1
    formula: Formula
    justification: str  # e.g. "Statement (Gardener)", "Clue (neighbour)" or "Modus Tollens 2, 3"


@dataclass
class GameState:
    case: dict
    lines: list[ProofLine]      # the proof so far; starts with the witness statements
    collected_clues: list[str]  # ids of the clues added to the proof
    mistakes: int = 0           # rejected steps
    hints_used: int = 0
    solved: bool = False        # the conclusion is on the board


def create_game(case: dict) -> GameState:
    """Starts a case: the witness statements become the first proof lines."""
    raise NotImplementedError("create_game")


def collect_clue(state: GameState, clue_id: str) -> None:
    """Adds a clue to the proof as a new premise line. Collecting it twice does nothing."""
    raise NotImplementedError("collect_clue")


def attempt_step(
    state: GameState, rule_id: str, line_ids: list[int], conclusion_text: str
) -> StepResult:
    """
    Tries one deduction.

    line_ids         the proof lines used as premises
    conclusion_text  what the player typed

    A valid step is added as a new line; an invalid one counts as a mistake.
    Text that does not parse is rejected with the parser's message.
    """
    raise NotImplementedError("attempt_step")
