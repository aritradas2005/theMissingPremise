"""
Case files screen. It shows one of two things:
    - the cabinet: a folder for each case, locked until the one before it is solved;
    - one case, once the player has opened its folder.

Which case is open is remembered in st.session_state["open_case"].
The last lines of this file decide which of the two to draw.
"""

from html import escape

import streamlit as st

from game.case_loader import load_case, load_case_index, validate_case
from game.scoring import stars_for
from ui.board import play
from ui.board_pieces import stamp_html, stars_html
from ui.detective import detective_says, show_sidekick
from ui.look import kicker, set_scene, show_html
from ui.session import best_scores


def open_case(case_id: str) -> None:
    """Runs when a folder's button is pressed."""
    st.session_state["open_case"] = case_id


def close_case() -> None:
    """Runs when "Case cabinet" is pressed."""
    st.session_state.pop("open_case", None)


# --------------------------------------------------------------- the cabinet


def is_unlocked(position: int, cases: list[dict]) -> bool:
    """The first case is always open; every other opens once the one before it is solved."""
    if position == 0:
        return True
    if st.session_state.get("unlock_all"):
        return True
    previous_case = cases[position - 1]
    return previous_case["id"] in best_scores()


def show_cabinet() -> None:
    """The folders, three to a row."""
    kicker("Detective bureau · case cabinet")
    st.title("Case files")
    detective_says("Pick a case file. Solve it, and the next one opens.")
    show_sidekick()

    cases = load_case_index()
    columns = st.columns(3)
    for position, case in enumerate(cases):
        column = columns[position % 3]      # 0, 1, 2, then back to 0 for the next row
        with column:
            show_folder(position, case, is_unlocked(position, cases))

    st.toggle("Chief's override: unlock every case", key="unlock_all")


def folder_status_html(case_id: str, unlocked: bool) -> str:
    """What the folder says about the case: its stars and points, or an OPEN or LOCKED stamp."""
    scores = best_scores()
    if case_id in scores:
        best = scores[case_id]
        return stars_html(stars_for(best)) + f'<span class="mp-points">{best} pts</span>'
    if unlocked:
        return stamp_html("Open", "green")
    return stamp_html("Locked", "grey")


def show_folder(position: int, case: dict, unlocked: bool) -> None:
    """One case folder: its number, title, difficulty, status, and the button to open it."""
    number = position + 1
    difficulty = "◆" * case["difficulty"]

    with st.container(key=f"folder_{case['id']}", border=True):
        show_html(
            f'<div class="mp-kicker">Case #{number:02d}</div>'
            f'<div class="mp-folder-title">{escape(case["title"])}</div>'
            f'<div class="mp-difficulty">Difficulty {difficulty}</div>'
            f'<div class="mp-folder-status">{folder_status_html(case["id"], unlocked)}</div>'
        )
        if unlocked:
            st.button("Open case file", key=case["id"], on_click=open_case, args=(case["id"],))
        else:
            st.button("🔒 Locked", key=case["id"], disabled=True)


# ------------------------------------------------------------------ one case


def show_case(case_id: str) -> None:
    """The opened case: its story, the testimony, and then the deduction board."""
    st.button("← Case cabinet", key="back", on_click=close_case)

    case = load_case(case_id)
    problems = validate_case(case)
    if problems:
        st.error("This case file cannot be played:")
        for problem in problems:
            st.markdown(f"- {problem}")
        return

    case_ids = [entry["id"] for entry in load_case_index()]
    number = case_ids.index(case_id) + 1
    difficulty = "◆" * case["difficulty"]

    kicker(f"Case #{number:02d} · difficulty {difficulty}")
    st.title(case["title"])
    show_html(f'<div class="mp-briefing">{escape(case["briefing"])}</div>')

    if "tip" in case:
        st.info(f"**Detective's note.** {case['tip']}", icon="🗒️")

    show_testimony(case)

    state = play(case, key=case_id)
    show_sidekick(happy=state.solved)

    if state.solved:
        show_next_case_button(number, case_ids)


def show_testimony(case: dict) -> None:
    """What each witness said, as a speech bubble with a small picture of the speaker."""
    kicker("Testimony")
    for statement in case["statements"]:
        picture = statement.get("avatar", "🗣️")
        with st.chat_message(statement["speaker"], avatar=picture):
            st.markdown(f"**{statement['speaker']}:** {statement['text']}")


def show_next_case_button(number: int, case_ids: list[str]) -> None:
    """After a solved case: a button to the next one, or a note that this was the last."""
    if number == len(case_ids):
        st.info("That was the last case. Build a case of your own next.")
        return

    next_case_id = case_ids[number]     # the list starts at 0, so entry `number` is the next case
    # The button gets a row of its own so that it can sit at the right, under the board.
    with st.container(key="next_row", horizontal=True, horizontal_alignment="right"):
        st.button(
            "Next case →", key="next_case", type="primary",
            on_click=open_case, args=(next_case_id,),
        )


# --------------------------------------------- what this screen draws

set_scene("office")

open_case_id = st.session_state.get("open_case")
if open_case_id is None:
    show_cabinet()
else:
    show_case(open_case_id)
