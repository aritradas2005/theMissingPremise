"""
Custom case screen: anyone can type their own premises and conclusion and get
a verdict, a truth table and a step-by-step proof.
"""

import streamlit as st

from ui.components import placeholder

st.title("Custom case")

placeholder(
    "Premises and conclusion",
    "One formula per line, with a message for anything malformed.",
)
placeholder(
    "Verdict",
    "Valid or invalid, the truth table with counterexample rows marked, and a resolution proof.",
)
