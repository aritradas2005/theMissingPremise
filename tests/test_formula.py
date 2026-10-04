from dataclasses import FrozenInstanceError

import pytest

from engine import And, Atom, Iff, Implies, Not, Or

P = Atom("P")
Q = Atom("Q")


def test_formulas_written_the_same_way_are_equal():
    assert Iff(And(P, Q), Not(P)) == Iff(And(P, Q), Not(P))


def test_different_atoms_connectives_and_operand_order_are_not_equal():
    assert P != Q
    assert And(P, Q) != Or(P, Q)
    assert And(P, Q) != And(Q, P)
    assert Not(P) != P


def test_formulas_can_be_stored_in_a_set():
    assert len({Implies(P, Q), Implies(P, Q), Implies(Q, P)}) == 2


def test_a_formula_cannot_be_changed_once_made():
    with pytest.raises(FrozenInstanceError):
        P.name = "Q"
