"""
The deduction board: one case in play.

It is used by the case files screen for the written cases, and by the custom
case screen for typed ones. play() draws everything; each show_... function
draws one part:

    stage tracker and the detective's instruction
    left column    key to the letters, and the evidence cards
    right column   the goal and the proof so far, then either
                   the step builder (while playing) or the verdict (once solved)
"""

import streamlit as st

from engine import format_formula, parse
from game.game_state import GameState, board_premises, collect_clue, current_argument, goal
from game.scoring import score_case, stars_for
from ui.board_pieces import (
    goal_html,
    legend_html,
    proof_html,
    score_html,
    stamp_html,
    stars_html,
    stepper_html,
)
from ui.detective import detective_says
from ui.look import kicker, show_html
from ui.resolution_view import show_resolution_proof
from ui.session import find_game, get_game, record_score, restart
from ui.step_builder import show_actions, show_step_builder
from ui.tables import show_truth_table

# What the detective says at each stage of a case.
INSTRUCTIONS = {
    1: "The testimony alone does not prove it. A premise is missing: pin the evidence "
       "that rules out the red rows of the truth table.",
    2: "Now we have enough. Choose a rule, choose the lines it uses, and write the line that follows.",
    3: "Case closed. The logic holds.",
}


def play(case: dict, key: str) -> GameState:
    """
    Draws the case and returns its state.

    key names this game (see ui/session.py) and is put in front of the name of
    every button, so that two cases never share a button.
    """
    state = get_game(case, key)

    current_stage = stage(state)
    show_html(stepper_html(current_stage))
    detective_says(INSTRUCTIONS[current_stage], smiling=state.solved)

    left, right = st.columns([2, 3], gap="large")
    with left:
        show_letter_key(case)
        show_evidence(state, key)
    with right:
        show_proof(state)
        if state.solved:
            show_verdict(state, key)
        else:
            show_gap(state)
            show_step_builder(state, key)
            show_actions(state, key)

    return state


def stage(state: GameState) -> int:
    """1 while a premise is missing, 2 while the proof is unfinished, 3 once solved."""
    if state.solved:
        return 3
    if current_argument(state).valid:
        return 2
    return 1


# ------------------------------------------------------------- left column


def show_letter_key(case: dict) -> None:
    """What each letter stands for. Nothing is drawn for a typed case, which has no meanings."""
    legend = legend_html(case["atoms"])
    if legend == "":
        return

    kicker("Key to the letters")
    show_html(legend)
    st.caption(
        "A letter only names a statement; it does not say the statement is true. "
        "¬ in front of a letter says it is false."
    )


def show_evidence(state: GameState, key: str) -> None:
    """One card per clue, with a button to pin it to the board."""
    kicker("Evidence locker")

    clues = state.case["clues"]
    if not clues:
        st.caption("There is no evidence to collect in this case.")
        return

    for position, clue in enumerate(clues):
        with st.container(key=f"evidence_{key}_{position}", border=True):
            st.caption(f"📍 {clue['location']}")
            if clue["text"]:
                st.write(clue["text"])
            st.code(format_formula(parse(clue["formula"])), language=None)

            if clue["id"] in state.collected_clues:
                show_html(stamp_html("On the board", "green"))
            elif not state.solved:
                st.button(
                    "📌 Pin to the board",
                    key=f"{key}_clue_{clue['id']}",
                    on_click=pin_evidence,
                    args=(key, clue["id"]),
                )


def pin_evidence(key: str, clue_id: str) -> None:
    """Runs when "Pin to the board" is pressed."""
    collect_clue(find_game(key), clue_id)
    record_score(key)


# ------------------------------------------------------------ right column


def show_proof(state: GameState) -> None:
    """The goal, the proof technique in use, and the proof lines so far."""
    kicker("Deduction board")

    conclusion = state.case["conclusion"]
    show_html(goal_html(format_formula(goal(state)), conclusion["text"]))

    if state.by_contradiction:
        st.caption(
            "Technique: proof by contradiction. "
            "Derive some formula and its negation from the assumption."
        )
    else:
        st.caption("Technique: direct proof. Derive the conclusion from the lines on the board.")

    show_html(proof_html(state.lines))


def show_gap(state: GameState) -> None:
    """Says whether the premises on the board are enough, with the truth table as evidence."""
    result = current_argument(state)
    counterexamples = len(result.counterexamples)

    if not result.critical_rows:
        st.error(
            "The premises on the board contradict each other: no row of the truth "
            "table makes them all true."
        )
    elif result.valid:
        st.success("The premises on the board are enough. Now derive the conclusion step by step.")
    elif counterexamples == 1:
        st.warning(
            "A premise is missing. In 1 row of the truth table every premise on the board "
            "is true and the conclusion is false. Find the evidence that rules it out."
        )
    else:
        st.warning(
            f"A premise is missing. In {counterexamples} rows of the truth table every premise "
            "on the board is true and the conclusion is false. Find the evidence that rules them out."
        )

    with st.expander("🔍 Examine the truth table"):
        show_truth_table(result.table, result.critical_rows, result.counterexamples)


def show_verdict(state: GameState, key: str) -> None:
    """The solved case: stamp, stars, score sheet, and two ways to check the result."""
    score = score_case(state)

    # Balloons once, not on every redraw of the solved case.
    if not st.session_state.get(f"{key}_celebrated"):
        st.balloons()
        st.session_state[f"{key}_celebrated"] = True

    if state.by_contradiction:
        technique = "proof by contradiction"
    else:
        technique = "direct proof"

    with st.container(key=f"verdict_{key}", border=True):
        show_html(stamp_html("Case closed") + stars_html(stars_for(score.total)))
        st.success(f"Case solved by {technique}.")
        show_html(score_html(score.breakdown, score.total))

    with st.expander("Check by truth table"):
        result = current_argument(state)
        show_truth_table(result.table, result.critical_rows, result.counterexamples)
        st.caption("No red rows: the conclusion is true wherever all the premises are true.")
    with st.expander("Check by resolution"):
        show_resolution_proof(board_premises(state), goal(state))

    st.button("↺ Play this case again", key=f"{key}_again", on_click=restart, args=(key,))
