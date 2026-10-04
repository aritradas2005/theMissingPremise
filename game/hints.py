"""
Hints. While a premise is missing, the hint points at the clue that closes the gap.
Once the premises are enough, it points at a rule and lines that give a new step.
"""

from itertools import combinations

from engine import (
    RULES,
    Formula,
    Implies,
    Not,
    Or,
    check_step,
    get_subformulas,
    parse,
    try_candidates,
)
from game.game_state import GameState, board_premises, current_argument, goal, opposite


def use_hint(state: GameState) -> str:
    """Returns a hint for the player and counts it against the score."""
    if state.solved:
        return "The case is already solved."

    state.hints_used += 1
    if not current_argument(state).valid:
        return _clue_hint(state)
    return _step_hint(state)


def _clue_hint(state: GameState) -> str:
    """Tries each clue not yet on the board as the missing premise."""
    unused = [clue for clue in state.case["clues"] if clue["id"] not in state.collected_clues]
    if not unused:
        return "Every clue is on the board and the conclusion still does not follow."

    formulas = [parse(clue["formula"]) for clue in unused]
    results = try_candidates(board_premises(state), goal(state), formulas)
    for clue, result in zip(unused, results):
        if result.closes_gap and result.consistent:
            return f"A premise is missing. Look again at: {clue['location']}."

    return "No single clue closes the gap. This case needs more than one clue on the board."


def _step_hint(state: GameState) -> str:
    """
    Searches for a step the rule checker accepts: every allowed rule, on every
    choice of lines, against a list of likely conclusions.
    """
    on_board = [line.formula for line in state.lines]
    rules = [rule for rule in RULES if rule.id in state.case["rules"]]

    for conclusion in _likely_conclusions(state):
        if conclusion in on_board:
            continue
        for rule in rules:
            for lines in combinations(state.lines, len(rule.premises)):
                premises = [line.formula for line in lines]
                if check_step(rule.id, premises, conclusion).valid:
                    numbers = " and ".join(str(line.id) for line in lines)
                    word = "line" if len(lines) == 1 else "lines"
                    return f"Try {rule.name} on {word} {numbers}."

    if not state.by_contradiction:
        return "No direct step was found with these rules. Try assuming the opposite of the conclusion."
    return "No single step was found. Look for a rule whose pattern matches two lines on the board."


def _likely_conclusions(state: GameState) -> list[Formula]:
    """
    Formulas worth testing as the next line, most useful first: the goal, then
    whatever would contradict a line already on the board, then every part of
    every line, then the new formulas that some rules build.
    """
    on_board = [line.formula for line in state.lines]

    candidates = [goal(state)]
    if state.by_contradiction:
        candidates += [opposite(formula) for formula in on_board]

    for formula in on_board + [goal(state)]:
        for part in get_subformulas(formula):
            candidates.append(part)
            candidates.append(opposite(part))

    # Hypothetical Syllogism and Contraposition build implications that are
    # not part of any existing line.
    implications = [formula for formula in on_board if isinstance(formula, Implies)]
    for first in implications:
        candidates.append(Implies(Not(first.right), Not(first.left)))
        for second in implications:
            candidates.append(Implies(first.left, second.right))

    # Resolution builds a disjunction out of one side of each of two lines.
    disjunctions = [formula for formula in on_board if isinstance(formula, Or)]
    for first in disjunctions:
        for second in disjunctions:
            for left in (first.left, first.right):
                for right in (second.left, second.right):
                    candidates.append(Or(left, right))

    return candidates
