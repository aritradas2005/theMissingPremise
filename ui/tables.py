"""
Drawing tables: a general one, and the truth table with its coloured rows.

The functions ending in _html and _cells only build and return something;
show_truth_table() is the one that puts a table on the screen.
"""

from html import escape

import streamlit as st

from engine import TruthTable, format_formula
from ui.look import show_html


def html_table(headings: list[str], rows: list[list[str]], row_classes: list[str] | None = None) -> str:
    """
    A table as HTML.

    row_classes, if given, holds one CSS class name per row. style.css uses
    the names "critical" and "counter" to tint a row gold or red.
    """
    head = ""
    for heading in headings:
        head += f"<th>{escape(str(heading))}</th>"

    body = ""
    for number, row in enumerate(rows):
        css_class = row_classes[number] if row_classes else ""
        cells = ""
        for cell in row:
            cells += f"<td>{escape(str(cell))}</td>"
        body += f'<tr class="{css_class}">{cells}</tr>'

    return (
        '<div class="mp-table-wrap"><table class="mp-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def truth_value(value: bool) -> str:
    """Writes True as "T" and False as "F"."""
    if value:
        return "T"
    return "F"


def truth_table_cells(table: TruthTable) -> tuple[list[str], list[list[str]]]:
    """
    Turns a truth table into headings and rows of text, ready to be drawn.
    The first column is the row number, then the atoms, then the formulas.
    """
    headings = ["#"] + table.atoms

    # A formula that is a single atom, or that was given twice, already has
    # its column, so it is not shown a second time.
    shown_columns = []
    for position, formula in enumerate(table.columns):
        heading = format_formula(formula)
        if heading not in headings:
            headings.append(heading)
            shown_columns.append(position)

    rows = []
    for number, row in enumerate(table.rows, start=1):
        cells = [str(number)]
        for name in table.atoms:
            cells.append(truth_value(row.assignment[name]))
        for position in shown_columns:
            cells.append(truth_value(row.values[position]))
        rows.append(cells)

    return headings, rows


def truth_table_html(table: TruthTable, critical_rows=(), counterexamples=()) -> str:
    """A truth table as HTML, with critical rows tinted gold and counterexamples red."""
    headings, rows = truth_table_cells(table)

    row_classes = []
    for number in range(len(rows)):
        if number in counterexamples:
            row_classes.append("counter")
        elif number in critical_rows:
            row_classes.append("critical")
        else:
            row_classes.append("")

    return html_table(headings, rows, row_classes)


def show_truth_table(table: TruthTable, critical_rows=(), counterexamples=()) -> None:
    """Draws a truth table, with a note explaining the colours if any rows are tinted."""
    show_html(truth_table_html(table, critical_rows, counterexamples))
    if critical_rows or counterexamples:
        st.caption(
            "Gold rows: every premise is true (critical rows). "
            "Red rows: every premise is true and the conclusion is false (counterexamples)."
        )
