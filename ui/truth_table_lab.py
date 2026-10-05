"""
Logic lab: type any formula and see its truth table, column by column.
"""

import streamlit as st

from engine import (
    Formula,
    ParseError,
    are_equivalent,
    build_truth_table,
    format_formula,
    get_subformulas,
    parse,
)
from ui.components import (
    SYNTAX_HELP,
    detective_says,
    kicker,
    read_formula,
    set_scene,
    show_keyboard,
    show_parse_error,
    show_sidekick,
    show_truth_table,
)


def show_formula(text: str) -> Formula | None:
    """
    Shows the verdict and the truth table for one formula and returns it.
    If the text is malformed, shows the error and returns None.
    """
    try:
        formula = parse(text)
        # One column for every part of the formula, smallest first, so the
        # table shows how the final column is worked out.
        table = build_truth_table(get_subformulas(formula))
    except ParseError as error:
        show_parse_error(text, error)
        return None
    except ValueError as error:  # more atoms than a table can hold
        st.error(str(error))
        return None

    st.subheader(format_formula(formula))

    # The formula itself is the last column of the table.
    true_rows = sum(1 for row in table.rows if row.values[-1])
    total = len(table.rows)
    if true_rows == total:
        st.success(f"Tautology: true in all {total} rows.")
    elif true_rows == 0:
        st.error(f"Contradiction: false in all {total} rows.")
    else:
        st.info(f"Contingency: true in {true_rows} of {total} rows.")

    show_truth_table(table)
    return formula


def show_comparison(first: Formula, second_text: str) -> None:
    """Says whether two formulas are logically equivalent, with the rows where they differ."""
    second = read_formula(second_text, "The second formula")
    if second is None:
        return

    try:
        table = build_truth_table([first, second])
    except ValueError as error:
        st.error(str(error))
        return

    differing = [index for index, row in enumerate(table.rows) if row.values[0] != row.values[1]]

    if are_equivalent(first, second):
        st.success(
            f"Equivalent: {format_formula(first)} ≡ {format_formula(second)}. "
            "They agree on every row."
        )
        show_truth_table(table)
    else:
        rows = ", ".join(str(index + 1) for index in differing)
        st.error(f"Not equivalent: they differ on row {rows}.")
        show_truth_table(table, counterexamples=differing)
        st.caption("Red rows: the two formulas have different truth values.")


set_scene("lab")
kicker("Forensics · logic lab")
st.title("Truth table lab")
detective_says("Put any formula under the lamp. I will work out every row, one column at a time.")
show_sidekick()

formula_text = st.text_input(
    "Formula", key="lab_formula", placeholder="(P -> Q) & ~R", help=SYNTAX_HELP
)
show_keyboard("lab_formula", ["P", "Q", "R"], prefix="lab")

if formula_text.strip():
    formula = show_formula(formula_text)

    st.divider()
    other_text = st.text_input(
        "Compare with another formula (optional)",
        key="lab_compare",
        placeholder="~P | Q",
        help="Checks logical equivalence.",
    )
    if formula is not None and other_text.strip():
        show_comparison(formula, other_text)
else:
    st.info(f"{SYNTAX_HELP} Try (P -> Q) & P -> Q.")
