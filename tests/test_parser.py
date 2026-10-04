import pytest

todo = pytest.mark.skip(reason="not written yet")


@todo
def test_single_atom():
    """parse("P") is Atom("P")."""


@todo
def test_aliases():
    """~ ! for ¬, & ^ for ∧, | for ∨, -> => for →, <-> <=> for ↔."""


@todo
def test_precedence():
    """¬ binds tighter than ∧, ∧ than ∨, ∨ than →, → than ↔."""


@todo
def test_implies_groups_to_the_right():
    """P -> Q -> R is P -> (Q -> R)."""


@todo
def test_and_groups_to_the_left():
    """P & Q & R is (P & Q) & R."""


@todo
def test_brackets_override_precedence():
    pass


@todo
def test_spaces_are_ignored():
    pass


@todo
def test_empty_input_is_rejected():
    pass


@todo
def test_unbalanced_brackets_are_rejected_with_the_position():
    pass


@todo
def test_missing_operand_is_rejected():
    """As in "P ->"."""


@todo
def test_unknown_character_is_rejected():
    """As in "P # Q"."""


@todo
def test_format_uses_display_symbols_and_only_the_brackets_needed():
    pass


@todo
def test_parse_undoes_format():
    """parse(format_formula(f)) == f."""
