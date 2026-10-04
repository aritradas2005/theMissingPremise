"""
Case files screen: the list of cases, or the case the player has opened.

Which case is open is remembered in st.session_state, a dictionary that
Streamlit keeps between reruns of this file.
"""

import streamlit as st

from game.case_loader import load_case, load_case_index
from ui.components import placeholder


def show_case_list() -> None:
    st.title("Case files")

    for entry in load_case_index():
        name, difficulty, button = st.columns([4, 2, 1])
        name.markdown(f"**{entry['title']}**")
        difficulty.caption(f"Difficulty {entry['difficulty']}")
        if button.button("Open", key=entry["id"]):
            st.session_state["open_case"] = entry["id"]
            st.rerun()


def show_case(case_id: str) -> None:
    """For now this only shows the case file as written; formulas appear as typed in the JSON."""
    if st.button("← All case files"):
        del st.session_state["open_case"]
        st.rerun()

    case = load_case(case_id)
    st.title(case["title"])
    st.write(case["briefing"])

    st.subheader("Witness statements")
    for statement in case["statements"]:
        show_entry(statement["speaker"], statement["text"], statement["formula"])

    st.subheader("Clues")
    for clue in case["clues"]:
        show_entry(clue["location"], clue["text"], clue["formula"])

    st.subheader("To prove")
    show_entry("Conclusion", case["conclusion"]["text"], case["conclusion"]["formula"])

    placeholder(
        "Deduction board",
        "Direct proof: pick lines and a rule of inference to add a new line. "
        "Proof by contradiction: assume the opposite of the conclusion and derive a formula and its negation.",
    )
    placeholder(
        "Truth table",
        "Counterexample rows: every premise is true and the conclusion is still false.",
    )


def show_entry(label: str, text: str, formula: str) -> None:
    label_column, text_column, formula_column = st.columns([2, 6, 2])
    label_column.caption(label)
    text_column.write(text)
    formula_column.code(formula, language=None)


open_case = st.session_state.get("open_case")
if open_case is None:
    show_case_list()
else:
    show_case(open_case)
