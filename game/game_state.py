"""
The state of one case being played: the proof so far, the clues found and the mistakes made.
"""

from dataclasses import dataclass

from engine import Formula, StepResult


@dataclass
class ProofLine:
    id: int             # line number, starting at 1
    formula: Formula
    # e.g. "Statement (Gardener)", "Clue (neighbour)", "Modus Tollens 2, 3"
    # or "Assumption (for contradiction)"
    justification: str


@dataclass
class GameState:
    case: dict
    lines: list[ProofLine]      # the proof so far; starts with the witness statements
    collected_clues: list[str]  # ids of the clues added to the proof
    mistakes: int = 0           # rejected steps
    hints_used: int = 0
    # False: direct proof, solved when the conclusion is on the board.
    # True: proof by contradiction, solved when the board holds some formula and its negation.
    by_contradiction: bool = False
    solved: bool = False


def create_game(case: dict) -> GameState:
    """Starts a case: the witness statements become the first proof lines."""
    raise NotImplementedError("create_game")


def collect_clue(state: GameState, clue_id: str) -> None:
    """Adds a clue to the proof as a new premise line. Collecting it twice does nothing."""
    raise NotImplementedError("collect_clue")


def assume_opposite(state: GameState) -> None:
    """
    Switches the case to proof by contradiction: adds the negation of the conclusion
    as a new line justified as "Assumption (for contradiction)".

    This is sound because if the premises together with ¬C lead to a contradiction,
    no row makes the premises true and C false, so the premises entail C.
    Calling it a second time does nothing.
    """
    raise NotImplementedError("assume_opposite")


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
