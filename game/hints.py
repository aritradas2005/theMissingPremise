"""
Hints for a player who is stuck.

There are two kinds, and which one is given depends on where the player is:
    - While a premise is still missing, the hint names the place where the
      clue that closes the gap was found.
    - Once the premises are enough, the hint names a rule and the lines to
      use it on. It does not give away the new line itself.

Each hint costs points (see scoring.py).
"""

from itertools import combinations

from engine import check_step, find_rule, get_subformulas, parse, try_candidates
from game.game_state import GameState, board_premises, current_argument, goal, opposite


def use_hint(state: GameState) -> str:
    """Returns a hint for the player and counts it against the score."""
    if state.solved:
        return "The case is already solved."

    state.hints_used += 1
    if current_argument(state).valid:
        return step_hint(state)
    return clue_hint(state)


def clue_hint(state: GameState) -> str:
    """Tries each clue that is not yet on the board as the missing premise."""
    unused = []
    for clue in state.case["clues"]:
        if clue["id"] not in state.collected_clues:
            unused.append(clue)

    if not unused:
        return "Every clue is on the board and the conclusion still does not follow."

    formulas = [parse(clue["formula"]) for clue in unused]
    results = try_candidates(board_premises(state), goal(state), formulas)

    for clue, result in zip(unused, results):
        if result.closes_gap and result.consistent:
            return f"A premise is missing. Look again at: {clue['location']}."

    return "No single clue closes the gap. This case needs more than one clue on the board."


def step_hint(state: GameState) -> str:
    """
    Looks for a step the rule checker would accept.

    It simply tries everything: each likely new line, with each rule the case
    allows, on each choice of lines. The first combination that the rule
    checker accepts is the hint.
    """
    on_board = [line.formula for line in state.lines]

    for new_line in likely_new_lines(state):
        if new_line in on_board:
            continue
        for rule_id in state.case["rules"]:
            rule = find_rule(rule_id)
            lines_needed = len(rule.premises)
            # combinations(lines, 2) gives every pair of lines, each pair once.
            for lines in combinations(state.lines, lines_needed):
                premises = [line.formula for line in lines]
                if check_step(rule_id, premises, new_line).valid:
                    return describe_step(rule.name, lines)

    if not state.by_contradiction:
        return "No direct step was found with these rules. Try assuming the opposite of the conclusion."
    return "No single step was found. Look for a rule whose pattern matches two lines on the board."


def likely_new_lines(state: GameState) -> list:
    """
    The formulas worth trying as the next line, the most useful first:
    the conclusion itself, then every part of every line on the board,
    each one both as it is and with its opposite.

    For the line W → G this gives W → G, W, G and their opposites.
    """
    on_board = [line.formula for line in state.lines]

    candidates = [goal(state)]
    for formula in on_board + [goal(state)]:
        for part in get_subformulas(formula):
            candidates.append(part)
            candidates.append(opposite(part))
    return candidates


def describe_step(rule_name: str, lines) -> str:
    """Words the hint, for example "Try Modus Tollens on lines 2 and 3."."""
    numbers = [str(line.id) for line in lines]
    if len(numbers) == 1:
        return f"Try {rule_name} on line {numbers[0]}."
    return f"Try {rule_name} on lines {' and '.join(numbers)}."
