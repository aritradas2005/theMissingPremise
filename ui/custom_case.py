"""
Build a case: anyone can type their own premises and conclusion and get
a verdict, a truth table and a step-by-step proof, then play it as a case.
"""

import streamlit as st

from engine import check_argument, find_liars, format_formula, try_candidates
from game.case_loader import build_custom_case, validate_case
from game.game_state import create_game
from ui.board import play, restart
from ui.components import (
    SYNTAX_HELP,
    detective_says,
    html_table,
    kicker,
    read_formula,
    read_formulas,
    set_scene,
    show_html,
    show_resolution_proof,
    show_sidekick,
    show_truth_table,
)


def typed_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def show_verdict(premises, conclusion, result) -> None:
    critical = len(result.critical_rows)
    counter = len(result.counterexamples)

    if not result.valid:
        st.error(
            f"Invalid. In {counter} of the {critical} rows where every premise is true, "
            "the conclusion is false. A premise is missing."
        )
    elif not premises:
        st.success("Valid with no premises: the conclusion is a tautology.")
    elif critical == 0:
        st.warning(
            "Valid, but only vacuously: the premises contradict each other, so no row "
            "makes them all true and anything follows from them."
        )
        liars = find_liars(premises)
        if liars:
            names = ", ".join(f"premise {index + 1}" for index in liars)
            st.caption(f"Removing any one of these alone would make the rest consistent: {names}.")
    else:
        st.success(
            f"Valid. In all {critical} rows where every premise is true, the conclusion is true."
        )


def candidate_rows(premises, conclusion, clues) -> list[list[str]]:
    """Tests each typed clue as the missing premise: one row of [clue, verdict] per clue."""
    rows = []
    for clue, result in zip(clues, try_candidates(premises, conclusion, clues)):
        if result.closes_gap and result.consistent:
            verdict = "Missing premise: with it, the conclusion follows"
        elif result.closes_gap:
            verdict = "Contradicts the premises, so it proves nothing"
        else:
            verdict = "Does not close the gap"
        rows.append([format_formula(clue), verdict])
    return rows


set_scene("office")
kicker("Detective bureau · new case")
st.title("Custom case")
detective_says(
    "Give me any premises and a conclusion. I will tell you whether the argument "
    "holds, and show you the row where it breaks if it does not."
)
show_sidekick()
st.caption(SYNTAX_HELP)

with st.container(key="panel_custom", border=True):
    premises_text = st.text_area(
        "Premises, one per line", key="custom_premises", placeholder="P -> Q\nQ -> R"
    )
    conclusion_text = st.text_input("Conclusion", key="custom_conclusion", placeholder="R")
    clues_text = st.text_area(
        "Evidence to test as the missing premise, one per line (optional)",
        key="custom_clues",
        placeholder="P\n~Q",
    )

if not conclusion_text.strip():
    st.info("Type a conclusion to see the verdict.")
    st.stop()

premises = read_formulas(premises_text, "Premise")
conclusion = read_formula(conclusion_text, "Conclusion")
clues = read_formulas(clues_text, "Clue")
if premises is None or conclusion is None or clues is None:
    st.stop()

try:
    result = check_argument(premises, conclusion)
except ValueError as error:  # more atoms than a truth table can hold
    st.error(str(error))
    st.stop()

st.subheader("Verdict")
argument = ", ".join(format_formula(premise) for premise in premises) or "∅"
st.code(f"{argument}  ∴  {format_formula(conclusion)}", language=None)
show_verdict(premises, conclusion, result)

st.subheader("Truth table")
show_truth_table(result.table, result.critical_rows, result.counterexamples)

if clues:
    st.subheader("Which clue is the missing premise?")
    try:
        show_html(html_table(["Clue", "Verdict"], candidate_rows(premises, conclusion, clues)))
    except ValueError as error:
        st.error(str(error))

st.subheader("Resolution proof")
show_resolution_proof(premises, conclusion)

st.subheader("Play it")
case = build_custom_case(typed_lines(premises_text), typed_lines(clues_text), conclusion_text)
problems = validate_case(case)

# The game belongs to the formulas it was started with. If they have been
# edited since, it is thrown away.
typed = (premises_text, conclusion_text, clues_text)
games = st.session_state.setdefault("games", {})
if "custom" in games and st.session_state.get("custom_started_with") != typed:
    restart("custom")


def start_custom_game() -> None:
    st.session_state["custom_started_with"] = typed
    st.session_state["games"]["custom"] = create_game(case)


if problems:
    for problem in problems:
        st.error(problem)
elif "custom" in games:
    play(case, key="custom")
else:
    st.write("Prove the conclusion yourself on the deduction board, with every rule available.")
    st.button("▶ Play this case", key="custom_play", type="primary", on_click=start_custom_game)
