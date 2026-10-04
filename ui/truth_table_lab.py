"""
Truth table lab: type any formula and see its truth table, column by column.
"""

import streamlit as st

from ui.components import placeholder

st.title("Truth table lab")

placeholder("Formula", "A text box with buttons for ¬ ∧ ∨ → ↔.")
placeholder(
    "Truth table",
    "One column per sub-formula, and whether the formula is a tautology, a contradiction or a contingency.",
)
