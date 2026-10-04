import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_a_correct_use_of_each_rule_is_accepted():
    pass


@todo
def test_premises_are_accepted_in_either_order():
    pass


@todo
def test_letters_in_a_rule_may_stand_for_whole_formulas():
    """(A ∧ B) → C, A ∧ B gives C by Modus Ponens."""


@todo
def test_affirming_the_consequent_is_rejected():
    """P → Q, Q does not give P."""


@todo
def test_denying_the_antecedent_is_rejected():
    """P → Q, ¬P does not give ¬Q."""


@todo
def test_wrong_number_of_premises_is_rejected_with_a_reason():
    pass


@todo
def test_simplification_gives_either_side():
    pass


@todo
def test_contraposition_swaps_and_negates_both_sides():
    """P → Q gives ¬Q → ¬P, and does not give Q → P."""


@todo
def test_unknown_rule_id_raises_value_error():
    pass
