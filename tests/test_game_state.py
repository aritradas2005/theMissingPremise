import pytest

from engine import format_formula, parse
from game.case_loader import build_custom_case, load_case, load_case_index, validate_case
from game.game_state import (
    assume_opposite,
    attempt_step,
    collect_clue,
    create_game,
    current_argument,
    opposite,
)
from game.hints import use_hint
from game.scoring import rank_for, score_case, stars_for


def new_game(case_id="case-01"):
    return create_game(load_case(case_id))


def board(state):
    """The formulas on the board, as text."""
    return [format_formula(line.formula) for line in state.lines]


# ---------------------------------------------------------------- game state


def test_a_new_game_starts_with_the_witness_statements_as_proof_lines():
    state = new_game()

    assert board(state) == ["W → G", "G → B"]
    assert [line.id for line in state.lines] == [1, 2]
    assert state.lines[0].justification == "Statement (Gardener)"
    assert not state.solved


def test_collecting_a_clue_adds_it_as_a_premise_line_once():
    state = new_game()

    collect_clue(state, "neighbour")
    collect_clue(state, "neighbour")

    assert board(state) == ["W → G", "G → B", "¬B"]
    assert state.lines[2].justification == "Clue (neighbour)"
    assert state.collected_clues == ["neighbour"]


def test_collecting_an_unknown_clue_raises_value_error():
    with pytest.raises(ValueError):
        collect_clue(new_game(), "no such clue")


def test_a_premise_is_missing_until_the_right_clue_is_collected():
    state = new_game()
    assert not current_argument(state).valid

    collect_clue(state, "mud")  # the distraction
    assert not current_argument(state).valid

    collect_clue(state, "neighbour")
    assert current_argument(state).valid


def test_a_valid_step_adds_a_line_justified_by_the_rule_and_line_numbers():
    state = new_game()
    collect_clue(state, "neighbour")

    result = attempt_step(state, "modus_tollens", [3, 2], "~G")

    assert result.valid
    assert board(state)[-1] == "¬G"
    assert state.lines[-1].justification == "Modus Tollens 2, 3"
    assert state.mistakes == 0


def test_an_invalid_step_adds_nothing_and_counts_as_a_mistake():
    state = new_game()
    collect_clue(state, "neighbour")

    result = attempt_step(state, "modus_tollens", [1, 3], "~W")

    assert not result.valid
    assert len(state.lines) == 3
    assert state.mistakes == 1


def test_a_conclusion_that_does_not_parse_is_rejected_with_the_parser_message():
    state = new_game()

    result = attempt_step(state, "modus_tollens", [1, 2], "~(G")

    assert not result.valid
    assert "This bracket is never closed." in result.reason
    assert state.mistakes == 0


def test_a_line_already_on_the_board_is_not_added_again():
    state = new_game()

    result = attempt_step(state, "hypothetical_syllogism", [1, 2], "W -> G")

    assert not result.valid
    assert "line 1" in result.reason
    assert len(state.lines) == 2
    assert state.mistakes == 0


def test_a_rule_the_case_does_not_allow_is_rejected():
    state = new_game()
    result = attempt_step(state, "addition", [1], "(W -> G) | B")

    assert not result.valid
    assert len(state.lines) == 2


def test_a_line_number_that_is_not_on_the_board_is_rejected():
    result = attempt_step(new_game(), "hypothetical_syllogism", [1, 9], "W -> B")
    assert not result.valid
    assert "no line 9" in result.reason


def test_the_game_is_solved_when_the_conclusion_is_on_the_board():
    state = new_game()
    collect_clue(state, "neighbour")
    attempt_step(state, "modus_tollens", [2, 3], "~G")
    assert not state.solved

    attempt_step(state, "modus_tollens", [1, 4], "~W")
    assert state.solved

    # Nothing more can be added once the case is closed.
    assert not attempt_step(state, "modus_tollens", [1, 4], "~W").valid


def test_opposite_removes_a_negation_instead_of_adding_a_second_one():
    assert opposite(parse("P")) == parse("~P")
    assert opposite(parse("~P")) == parse("P")
    assert opposite(parse("P & Q")) == parse("~(P & Q)")


def test_assume_opposite_adds_the_opposite_of_the_conclusion_once():
    state = new_game()

    assume_opposite(state)
    assume_opposite(state)

    assert state.by_contradiction
    assert board(state) == ["W → G", "G → B", "W"]
    assert state.lines[2].justification == "Assumption (for contradiction)"


def test_by_contradiction_is_solved_by_a_formula_and_its_negation():
    """Having the conclusion on the board is not needed in this mode."""
    state = new_game("case-04")
    collect_clue(state, "passport")
    assume_opposite(state)                                       # 4. ¬L
    attempt_step(state, "disjunctive_syllogism", [1, 4], "N")    # 5. N
    assert not state.solved

    attempt_step(state, "modus_ponens", [2, 5], "T")             # 6. T, against 3. ¬T
    assert state.solved
    assert "L" not in board(state)


# A full solution of every case: the clues to collect, whether to assume the
# opposite, and the steps as (rule, lines, new line).
SOLUTIONS = {
    "case-01": (["neighbour"], False, [
        ("hypothetical_syllogism", [1, 2], "W -> B"),
        ("modus_tollens", [4, 3], "~W"),
    ]),
    "case-02": (["maid"], False, [
        ("modus_tollens", [2, 3], "~C"),
        ("disjunctive_syllogism", [1, 4], "B"),
    ]),
    "case-03": (["porter"], False, [
        ("simplification", [3], "T"),
        ("hypothetical_syllogism", [1, 2], "T -> H"),
        ("modus_ponens", [5, 4], "H"),
    ]),
    "case-04": (["passport"], True, [
        ("disjunctive_syllogism", [1, 4], "N"),
        ("modus_ponens", [2, 5], "T"),
    ]),
    "case-05": (["door"], False, [
        ("resolution", [1, 2], "D | I"),
        ("disjunctive_syllogism", [4, 3], "I"),
    ]),
}


def test_there_is_a_solution_for_every_case():
    assert set(SOLUTIONS) == {entry["id"] for entry in load_case_index()}


@pytest.mark.parametrize("case_id", SOLUTIONS)
def test_every_case_can_be_solved_with_its_own_rules(case_id):
    clues, by_contradiction, steps = SOLUTIONS[case_id]
    state = new_game(case_id)

    for clue_id in clues:
        collect_clue(state, clue_id)
    if by_contradiction:
        assume_opposite(state)
    for rule_id, line_ids, conclusion in steps:
        result = attempt_step(state, rule_id, line_ids, conclusion)
        assert result.valid, result.reason

    assert state.solved
    assert state.mistakes == 0
    assert score_case(state).total == 100


# --------------------------------------------------------------- validation


@pytest.mark.parametrize("entry", load_case_index(), ids=lambda entry: entry["id"])
def test_the_written_cases_have_no_problems(entry):
    assert validate_case(load_case(entry["id"])) == []


def test_validate_case_reports_each_kind_of_problem():
    case = load_case("case-01")
    case["statements"][0]["formula"] = "W ->"           # does not parse
    case["clues"][1]["formula"] = "Z"                   # atom not listed
    case["clues"][1]["id"] = "neighbour"                # repeated clue id
    case["rules"].append("guesswork")                   # unknown rule

    problems = validate_case(case)

    assert len(problems) == 4
    assert any("Statement by Gardener" in problem for problem in problems)
    assert any("Atom Z" in problem for problem in problems)
    assert any("more than once" in problem for problem in problems)
    assert any("guesswork" in problem for problem in problems)


def test_validate_case_reports_too_many_atoms():
    atoms = " & ".join(f"A{number}" for number in range(9))
    case = build_custom_case([atoms], [], "A0")
    assert any("limit is 8" in problem for problem in validate_case(case))


def test_a_custom_case_is_playable_with_every_rule():
    case = build_custom_case(["P -> Q", "Q -> R"], ["P"], "R")
    assert validate_case(case) == []

    state = create_game(case)
    assert not current_argument(state).valid

    collect_clue(state, "clue 1")
    assert attempt_step(state, "modus_ponens", [1, 3], "Q").valid
    assert attempt_step(state, "modus_ponens", [2, 4], "R").valid
    assert state.solved


# ------------------------------------------------------------------ scoring


def test_score_rewards_solving_and_takes_points_off_for_mistakes_and_hints():
    state = new_game()
    collect_clue(state, "neighbour")
    attempt_step(state, "modus_tollens", [1, 3], "~W")   # rejected
    use_hint(state)
    attempt_step(state, "modus_tollens", [2, 3], "~G")
    attempt_step(state, "modus_tollens", [1, 4], "~W")

    score = score_case(state)

    assert score.breakdown == [("Case solved", 100), ("Rejected steps: 1", -10), ("Hints used: 1", -15)]
    assert score.total == 75


def test_a_clue_the_argument_did_not_need_costs_points():
    state = new_game()
    collect_clue(state, "mud")
    collect_clue(state, "neighbour")
    attempt_step(state, "modus_tollens", [2, 4], "~G")
    attempt_step(state, "modus_tollens", [1, 5], "~W")

    score = score_case(state)

    assert ("Clue not needed: mud", -10) in score.breakdown
    assert score.total == 90


def test_the_score_never_goes_below_zero():
    state = new_game()
    state.mistakes = 50
    assert score_case(state).total == 0


def test_stars_follow_the_score():
    assert [stars_for(total) for total in (100, 90, 89, 60, 59, 0)] == [3, 3, 2, 2, 1, 1]


def test_rank_rises_with_total_points():
    assert rank_for(0) == "Rookie"
    assert rank_for(99) == "Rookie"
    assert rank_for(100) == "Constable"
    assert rank_for(275) == "Detective"
    assert rank_for(500) == "Master of Logic"


# -------------------------------------------------------------------- hints


def test_hint_points_at_the_clue_that_closes_the_gap():
    state = new_game()

    hint = use_hint(state)

    assert "Next door" in hint
    assert state.hints_used == 1


def test_hint_suggests_a_step_the_rule_checker_accepts():
    state = new_game()
    collect_clue(state, "neighbour")

    hint = use_hint(state)

    assert hint.startswith("Try ")
    assert "Modus Tollens" in hint or "Hypothetical Syllogism" in hint


def test_hint_on_a_solved_case_is_free():
    state = new_game()
    collect_clue(state, "neighbour")
    attempt_step(state, "modus_tollens", [2, 3], "~G")
    attempt_step(state, "modus_tollens", [1, 4], "~W")

    assert use_hint(state) == "The case is already solved."
    assert state.hints_used == 0
