import pytest

from engine import RULES, check_step, parse


def test_a_correct_use_of_each_rule_is_accepted():
    examples = {
        "modus_ponens": ([parse("P -> Q"), parse("P")], parse("Q")),
        "modus_tollens": ([parse("P -> Q"), parse("~Q")], parse("~P")),
        "hypothetical_syllogism": (
            [parse("P -> Q"), parse("Q -> R")],
            parse("P -> R"),
        ),
        "disjunctive_syllogism": ([parse("P | Q"), parse("~P")], parse("Q")),
        "addition": ([parse("P")], parse("P | Q")),
        "simplification": ([parse("P & Q")], parse("P")),
        "conjunction": ([parse("P"), parse("Q")], parse("P & Q")),
        "resolution": ([parse("P | Q"), parse("~P | R")], parse("Q | R")),
        "contraposition": ([parse("P -> Q")], parse("~Q -> ~P")),
    }

    for rule in RULES:
        premises, conclusion = examples[rule.id]
        res = check_step(rule.id, premises, conclusion)
        assert res.valid, f"Rule {rule.id} failed: {res.reason}"


def test_premises_are_accepted_in_either_order():
    res1 = check_step("modus_ponens", [parse("P"), parse("P -> Q")], parse("Q"))
    assert res1.valid
    res2 = check_step("modus_tollens", [parse("~Q"), parse("P -> Q")], parse("~P"))
    assert res2.valid
    res3 = check_step(
        "hypothetical_syllogism", [parse("Q -> R"), parse("P -> Q")], parse("P -> R")
    )
    assert res3.valid


def test_letters_in_a_rule_may_stand_for_whole_formulas():
    """(A ∧ B) → C, A ∧ B gives C by Modus Ponens."""
    prem1 = parse("(A & B) -> C")
    prem2 = parse("A & B")
    conc = parse("C")
    res = check_step("modus_ponens", [prem1, prem2], conc)
    assert res.valid


def test_affirming_the_consequent_is_rejected():
    """P → Q, Q does not give P."""
    res = check_step("modus_ponens", [parse("P -> Q"), parse("Q")], parse("P"))
    assert not res.valid
    assert "consequent" in res.reason.lower() or "not prove" in res.reason.lower()


def test_denying_the_antecedent_is_rejected():
    """P → Q, ¬P does not give ¬Q."""
    res = check_step("modus_ponens", [parse("P -> Q"), parse("~P")], parse("~Q"))
    assert not res.valid
    assert "antecedent" in res.reason.lower() or "not prove" in res.reason.lower()


def test_wrong_number_of_premises_is_rejected_with_a_reason():
    res1 = check_step("modus_ponens", [parse("P")], parse("Q"))
    assert not res1.valid
    assert "premises" in res1.reason.lower()

    res2 = check_step("addition", [parse("P"), parse("Q")], parse("P | Q"))
    assert not res2.valid
    assert "premise" in res2.reason.lower()


def test_simplification_gives_either_side():
    premise = [parse("P & Q")]
    assert check_step("simplification", premise, parse("P")).valid
    assert check_step("simplification", premise, parse("Q")).valid


def test_contraposition_swaps_and_negates_both_sides():
    """P → Q gives ¬Q → ¬P, and does not give Q → P."""
    premise = [parse("P -> Q")]
    assert check_step("contraposition", premise, parse("~Q -> ~P")).valid
    assert not check_step("contraposition", premise, parse("Q -> P")).valid


def test_unknown_rule_id_raises_value_error():
    with pytest.raises(ValueError):
        check_step("non_existent_rule", [parse("P")], parse("P"))
