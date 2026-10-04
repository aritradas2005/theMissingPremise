import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_a_new_game_starts_with_the_witness_statements_as_proof_lines():
    pass


@todo
def test_collecting_a_clue_adds_it_as_a_premise_line_once():
    pass


@todo
def test_a_valid_step_adds_a_line_justified_by_the_rule_and_line_numbers():
    pass


@todo
def test_an_invalid_step_adds_nothing_and_counts_as_a_mistake():
    pass


@todo
def test_a_conclusion_that_does_not_parse_is_rejected_with_the_parser_message():
    pass


@todo
def test_the_game_is_solved_when_the_conclusion_is_on_the_board():
    pass


@todo
def test_assume_opposite_adds_the_negated_conclusion_once():
    pass


@todo
def test_by_contradiction_is_solved_by_a_formula_and_its_negation():
    """Having the conclusion on the board is not needed in this mode."""


@todo
def test_validate_case_reports_each_kind_of_problem():
    """An unparseable formula, an undeclared atom, a repeated clue id and an unknown rule."""


@todo
def test_score_rewards_solving_and_takes_points_off_for_mistakes_and_hints():
    pass
