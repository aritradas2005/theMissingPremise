"""
Custom case screen ("Build a case"). The player types premises, a conclusion
and, if they like, some evidence, and gets:

    1. the verdict: is the argument valid?
    2. the truth table, with counterexample rows marked
    3. a test of each piece of evidence as the missing premise
    4. an automatic resolution proof
    5. the same argument as a case to play on the deduction board

The functions come first. The part that draws the screen is at the bottom and
reads from top to bottom. st.stop() ends the drawing early when there is
nothing more to show, for example when a formula is malformed.
"""

import streamlit as st

from engine import check_argument, find_liars, format_formula, try_candidates
from game.case_loader import build_custom_case, validate_case
from ui.board import play
from ui.detective import detective_says, show_sidekick
from ui.formula_box import SYNTAX_HELP, read_formula, read_formulas
from ui.look import kicker, set_scene, show_html
from ui.resolution_view import show_resolution_proof
from ui.session import has_game, restart, start_game
from ui.tables import html_table, show_truth_table


def typed_lines(text: str) -> list[str]:
    """The non-empty lines of a text box."""
    lines = []
    for line in text.splitlines():
        if line.strip():
            lines.append(line.strip())
    return lines


def argument_text(premises, conclusion) -> str:
    """The argument on one line, for example  P → Q, P  ∴  Q. With no premises it starts with ∅."""
    if premises:
        left = ", ".join(format_formula(premise) for premise in premises)
    else:
        left = "∅"
    return f"{left}  ∴  {format_formula(conclusion)}"


def show_verdict(premises, result) -> None:
    """Says whether the argument is valid, and points out the special cases."""
    critical = len(result.critical_rows)
    counterexamples = len(result.counterexamples)

    if not result.valid:
        st.error(
            f"Invalid. In {counterexamples} of the {critical} rows where every premise is true, "
            "the conclusion is false. A premise is missing."
        )
    elif not premises:
        st.success("Valid with no premises: the conclusion is a tautology.")
    elif critical == 0:
        st.warning(
            "Valid, but only vacuously: the premises contradict each other, so no row "
            "makes them all true and anything follows from them."
        )
        show_liars(premises)
    else:
        st.success(
            f"Valid. In all {critical} rows where every premise is true, the conclusion is true."
        )


def show_liars(premises) -> None:
    """For contradictory premises: which single premise could be removed to make the rest agree."""
    liars = find_liars(premises)
    if not liars:
        return
    names = ", ".join(f"premise {position + 1}" for position in liars)
    st.caption(f"Removing any one of these alone would make the rest consistent: {names}.")


def candidate_rows(premises, conclusion, clues) -> list[list[str]]:
    """Tests each typed clue as the missing premise: one row of [clue, verdict] per clue."""
    rows = []
    results = try_candidates(premises, conclusion, clues)
    for clue, result in zip(clues, results):
        if result.closes_gap and result.consistent:
            verdict = "Missing premise: with it, the conclusion follows"
        elif result.closes_gap:
            verdict = "Contradicts the premises, so it proves nothing"
        else:
            verdict = "Does not close the gap"
        rows.append([format_formula(clue), verdict])
    return rows


def start_custom_game(case: dict, typed: tuple) -> None:
    """Runs when "Play this case" is pressed."""
    st.session_state["custom_started_with"] = typed
    start_game(case, "custom")


# --------------------------------------------- what this screen draws

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

# Read everything that was typed. A malformed formula has already been
# reported by read_formula(), so there is nothing more to draw.
premises = read_formulas(premises_text, "Premise")
conclusion = read_formula(conclusion_text, "Conclusion")
clues = read_formulas(clues_text, "Clue")
if premises is None or conclusion is None or clues is None:
    st.stop()

try:
    result = check_argument(premises, conclusion)
except ValueError as error:      # more atoms than a truth table can hold
    st.error(str(error))
    st.stop()

st.subheader("Verdict")
st.code(argument_text(premises, conclusion), language=None)
show_verdict(premises, result)

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

# A game belongs to the formulas it was started with. If they have been
# edited since, the game is thrown away.
typed = (premises_text, conclusion_text, clues_text)
if has_game("custom") and st.session_state.get("custom_started_with") != typed:
    restart("custom")

if problems:
    for problem in problems:
        st.error(problem)
elif has_game("custom"):
    play(case, key="custom")
else:
    st.write("Prove the conclusion yourself on the deduction board, with every rule available.")
    st.button(
        "▶ Play this case", key="custom_play", type="primary",
        on_click=start_custom_game, args=(case, typed),
    )
