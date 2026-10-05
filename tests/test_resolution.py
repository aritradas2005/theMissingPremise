import pytest

from engine import MAX_RESOLUTION_LINES, check_argument, parse, prove_by_resolution


def test_proves_modus_ponens():
    """P → Q, P ∴ Q."""
    proof = prove_by_resolution([parse("P -> Q"), parse("P")], parse("Q"))
    assert proof.proved


def test_proves_a_chain():
    """W → G, G → B, ¬B ∴ ¬W."""
    premises = [parse("W -> G"), parse("G -> B"), parse("~B")]
    conclusion = parse("~W")
    proof = prove_by_resolution(premises, conclusion)
    assert proof.proved


def test_does_not_prove_an_invalid_argument():
    """P → Q, Q ∴ P."""
    proof = prove_by_resolution([parse("P -> Q"), parse("Q")], parse("P"))
    assert not proof.proved


def test_every_resolvent_names_its_two_parents_and_the_atom():
    proof = prove_by_resolution([parse("P -> Q"), parse("P")], parse("Q"))
    resolvents = [line for line in proof.lines if line.source == "resolvent"]
    assert len(resolvents) > 0
    for line in resolvents:
        assert line.parents is not None and len(line.parents) == 2
        assert line.on is not None and len(line.on) > 0


def test_stops_when_no_new_clause_can_be_made():
    proof = prove_by_resolution([parse("P | Q"), parse("R | S")], parse("T"))
    assert not proof.proved


def test_agrees_with_check_argument_on_a_batch_of_arguments():
    batch = [
        (["P -> Q", "P"], "Q"),
        (["P -> Q", "~Q"], "~P"),
        (["P -> Q", "Q -> R"], "P -> R"),
        (["P | Q", "~P"], "Q"),
        (["P -> Q", "Q"], "P"),
        (["P -> Q", "~P"], "~Q"),
        (["P | Q", "P"], "~Q"),
        ([], "P | ~P"),
        ([], "P"),
        (["P", "~P"], "Q"),
    ]
    for prem_texts, conc_text in batch:
        premises = [parse(t) for t in prem_texts]
        conclusion = parse(conc_text)
        res_proof = prove_by_resolution(premises, conclusion)
        arg_result = check_argument(premises, conclusion)
        assert (
            res_proof.proved == arg_result.valid
        ), f"Disagreement on {prem_texts} ∴ {conc_text}: resolution={res_proof.proved}, truth_table={arg_result.valid}"


def test_a_search_that_grows_too_large_is_stopped():
    """Eight premises over eight atoms make thousands of clauses before the search can finish."""
    premises = [
        parse(text)
        for text in [
            "A | B | C", "D | E | F", "~A | D | G", "~B | E | H",
            "~C | F | G", "~D | ~E | H", "A | ~F | ~H", "B | ~G | H",
        ]
    ]
    with pytest.raises(ValueError, match=f"stopped after {MAX_RESOLUTION_LINES} clauses"):
        prove_by_resolution(premises, parse("A & D"))


def test_a_formula_too_large_for_cnf_is_refused_by_the_prover_too():
    with pytest.raises(ValueError, match="too large to convert to CNF"):
        prove_by_resolution([parse("A <-> (B <-> (C <-> (D <-> (E <-> F))))")], parse("A"))
