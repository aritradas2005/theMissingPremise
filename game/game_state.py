"""
The state of one case being played: the proof so far, the clues found and the
mistakes made.

A GameState is a small record of where the player is. The functions below
change it: the screens call them when the player presses a button, and then
redraw the board from the state.

How a case is solved:
    - Direct proof: the conclusion appears as a line on the board.
    - Proof by contradiction: after assuming the opposite of the conclusion,
      some formula and its negation both appear on the board.
"""

from dataclasses import dataclass

from engine import (
    ArgumentResult,
    Formula,
    Not,
    ParseError,
    StepResult,
    check_argument,
    check_step,
    find_rule,
    parse,
)


@dataclass
class ProofLine:
    id: int             # line number, starting at 1
    formula: Formula
    # Where the line came from, for example "Statement (Gardener)",
    # "Clue (neighbour)", "Modus Tollens 2, 3" or "Assumption (for contradiction)".
    justification: str


@dataclass
class GameState:
    case: dict
    lines: list[ProofLine]      # the proof so far; starts with the witness statements
    collected_clues: list[str]  # ids of the clues added to the proof
    mistakes: int = 0           # rejected steps
    hints_used: int = 0
    by_contradiction: bool = False   # True once the player has assumed the opposite
    solved: bool = False


# ------------------------------------------------------------ starting a case


def create_game(case: dict) -> GameState:
    """Starts a case: the witness statements become the first proof lines."""
    state = GameState(case=case, lines=[], collected_clues=[])
    for statement in case["statements"]:
        formula = parse(statement["formula"])
        add_line(state, formula, f"Statement ({statement['speaker']})")
    update_solved(state)
    return state


def goal(state: GameState) -> Formula:
    """The conclusion the player has to prove."""
    return parse(state.case["conclusion"]["formula"])


def opposite(formula: Formula) -> Formula:
    """The opposite of ¬X is X; the opposite of anything else is its negation."""
    if isinstance(formula, Not):
        return formula.operand
    return Not(formula)


# -------------------------------------------------------------------- clues


def collect_clue(state: GameState, clue_id: str) -> None:
    """
    Adds a clue to the proof as a new premise line. Collecting it twice does nothing.

    Raises ValueError if the case has no clue with this id.
    """
    if clue_id in state.collected_clues:
        return

    for clue in state.case["clues"]:
        if clue["id"] == clue_id:
            add_line(state, parse(clue["formula"]), f"Clue ({clue_id})")
            state.collected_clues.append(clue_id)
            update_solved(state)
            return

    raise ValueError(f"This case has no clue '{clue_id}'.")


def board_premises(state: GameState) -> list[Formula]:
    """The witness statements and the collected clues: what the player may rely on."""
    premises = []
    for statement in state.case["statements"]:
        premises.append(parse(statement["formula"]))
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


# ------------------------------------------------------------- making steps


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
    add_line(state, opposite(goal(state)), "Assumption (for contradiction)")
    update_solved(state)


def attempt_step(
    state: GameState, rule_id: str, line_ids: list[int], conclusion_text: str
) -> StepResult:
    """
    Tries one deduction.

    line_ids         the proof lines used as premises
    conclusion_text  what the player typed

    A valid step is added as a new line; an invalid one counts as a mistake.
    A request that cannot even be checked (text that does not parse, a line
    that is already on the board, and so on) is refused without counting.
    """
    if state.solved:
        return StepResult(False, "The case is already solved.")

    if rule_id not in state.case["rules"]:
        return StepResult(False, "That rule is not available in this case.")

    premises = []
    for line_id in line_ids:
        line = find_line(state, line_id)
        if line is None:
            return StepResult(False, f"There is no line {line_id} on the board.")
        premises.append(line.formula)

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

    numbers = ", ".join(str(line_id) for line_id in sorted(line_ids))
    add_line(state, conclusion, f"{find_rule(rule_id).name} {numbers}")
    update_solved(state)
    return result


# ------------------------------------------------------------------ helpers


def find_line(state: GameState, line_id: int) -> ProofLine | None:
    """The proof line with this number, or None if there is no such line."""
    for line in state.lines:
        if line.id == line_id:
            return line
    return None


def add_line(state: GameState, formula: Formula, justification: str) -> None:
    """Adds a line to the end of the proof with the next line number."""
    next_number = len(state.lines) + 1
    state.lines.append(ProofLine(next_number, formula, justification))


def update_solved(state: GameState) -> None:
    """Works out whether the case is solved, after anything has been added to the board."""
    on_board = [line.formula for line in state.lines]

    if state.by_contradiction:
        # Solved when some formula and its negation are both on the board.
        state.solved = False
        for formula in on_board:
            if Not(formula) in on_board:
                state.solved = True
    else:
        state.solved = goal(state) in on_board
