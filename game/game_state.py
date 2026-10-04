"""
The state of one case being played: the proof so far, the clues found and the mistakes made.

The functions below change the GameState they are given. The screens call them
when the player presses a button, then redraw the board from the state.
"""

from dataclasses import dataclass

from engine import (
    RULES,
    ArgumentResult,
    Formula,
    Not,
    ParseError,
    StepResult,
    check_argument,
    check_step,
    parse,
)


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
    state = GameState(case=case, lines=[], collected_clues=[])
    for statement in case["statements"]:
        _add_line(state, parse(statement["formula"]), f"Statement ({statement['speaker']})")
    _update_solved(state)
    return state


def goal(state: GameState) -> Formula:
    """The conclusion the player has to prove."""
    return parse(state.case["conclusion"]["formula"])


def opposite(formula: Formula) -> Formula:
    """The opposite of ¬X is X; the opposite of anything else is its negation."""
    if isinstance(formula, Not):
        return formula.operand
    return Not(formula)


def collect_clue(state: GameState, clue_id: str) -> None:
    """
    Adds a clue to the proof as a new premise line. Collecting it twice does nothing.

    Raises ValueError if the case has no clue with this id.
    """
    if clue_id in state.collected_clues:
        return

    for clue in state.case["clues"]:
        if clue["id"] == clue_id:
            _add_line(state, parse(clue["formula"]), f"Clue ({clue_id})")
            state.collected_clues.append(clue_id)
            _update_solved(state)
            return

    raise ValueError(f"This case has no clue '{clue_id}'.")


def board_premises(state: GameState) -> list[Formula]:
    """The witness statements and the collected clues: what the player may rely on."""
    premises = [parse(statement["formula"]) for statement in state.case["statements"]]
    for clue in state.case["clues"]:
        if clue["id"] in state.collected_clues:
            premises.append(parse(clue["formula"]))
    return premises


def current_argument(state: GameState) -> ArgumentResult:
    """
    Do the premises on the board already entail the conclusion?
    While the answer is no, a premise is missing and no proof can succeed.
    """
    return check_argument(board_premises(state), goal(state))


def assume_opposite(state: GameState) -> None:
    """
    Switches the case to proof by contradiction: adds the opposite of the conclusion
    as a new line justified as "Assumption (for contradiction)".

    This is sound because if the premises together with the opposite of C lead to a
    contradiction, no row makes the premises true and C false, so the premises entail C.
    Calling it a second time does nothing.
    """
    if state.by_contradiction:
        return

    state.by_contradiction = True
    _add_line(state, opposite(goal(state)), "Assumption (for contradiction)")
    _update_solved(state)


def attempt_step(
    state: GameState, rule_id: str, line_ids: list[int], conclusion_text: str
) -> StepResult:
    """
    Tries one deduction.

    line_ids         the proof lines used as premises
    conclusion_text  what the player typed

    A valid step is added as a new line; an invalid one counts as a mistake.
    Text that does not parse is rejected with the parser's message, and so is a
    line that is already on the board; neither counts as a mistake.
    """
    if state.solved:
        return StepResult(False, "The case is already solved.")

    if rule_id not in state.case["rules"]:
        return StepResult(False, "That rule is not available in this case.")

    lines_by_id = {line.id: line for line in state.lines}
    for line_id in line_ids:
        if line_id not in lines_by_id:
            return StepResult(False, f"There is no line {line_id} on the board.")
    premises = [lines_by_id[line_id].formula for line_id in line_ids]

    try:
        conclusion = parse(conclusion_text)
    except ParseError as error:
        return StepResult(False, f"The new line could not be read. {error}")

    for line in state.lines:
        if line.formula == conclusion:
            return StepResult(False, f"That is already on the board as line {line.id}.")

    result = check_step(rule_id, premises, conclusion)
    if not result.valid:
        state.mistakes += 1
        return result

    rule_name = next(rule.name for rule in RULES if rule.id == rule_id)
    used = ", ".join(str(line_id) for line_id in sorted(line_ids))
    _add_line(state, conclusion, f"{rule_name} {used}")
    _update_solved(state)
    return result


def _add_line(state: GameState, formula: Formula, justification: str) -> None:
    state.lines.append(ProofLine(len(state.lines) + 1, formula, justification))


def _update_solved(state: GameState) -> None:
    on_board = [line.formula for line in state.lines]
    if state.by_contradiction:
        state.solved = any(Not(formula) in on_board for formula in on_board)
    else:
        state.solved = goal(state) in on_board
