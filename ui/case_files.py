"""
Case files screen: the cabinet of case folders, or the case the player has opened.

Which case is open is remembered in st.session_state, a dictionary that
Streamlit keeps between reruns of this file.
"""

from html import escape

import streamlit as st

from game.case_loader import load_case, load_case_index, validate_case
from game.scoring import stars_for
from ui.board import play
from ui.components import (
    detective_says,
    kicker,
    set_scene,
    show_html,
    show_sidekick,
    stamp_html,
    stars_html,
)


def is_unlocked(position: int, index: list[dict]) -> bool:
    """A case opens once the one before it has been solved."""
    if position == 0 or st.session_state.get("unlock_all"):
        return True
    scores = st.session_state.get("scores", {})
    return index[position - 1]["id"] in scores


def open_case(case_id: str) -> None:
    st.session_state["open_case"] = case_id


def close_case() -> None:
    st.session_state.pop("open_case", None)


# --------------------------------------------------------------- the cabinet


def show_case_list() -> None:
    kicker("Detective bureau · case cabinet")
    st.title("Case files")
    detective_says("Pick a case file. Solve it, and the next one opens.")
    show_sidekick()

    index = load_case_index()
    columns = st.columns(3)
    for position, entry in enumerate(index):
        with columns[position % 3]:
            show_folder(position, entry, is_unlocked(position, index))

    st.toggle("Chief's override: unlock every case", key="unlock_all")


def show_folder(position: int, entry: dict, unlocked: bool) -> None:
    """One case folder: its number, title, difficulty and whether it is locked or solved."""
    best = st.session_state.get("scores", {}).get(entry["id"])

    if best is not None:
        status = stars_html(stars_for(best)) + f'<span class="mp-points">{best} pts</span>'
    elif unlocked:
        status = stamp_html("Open", "green")
    else:
        status = stamp_html("Locked", "grey")

    with st.container(key=f"folder_{entry['id']}", border=True):
        show_html(
            f'<div class="mp-kicker">Case #{position + 1:02d}</div>'
            f'<div class="mp-folder-title">{escape(entry["title"])}</div>'
            f'<div class="mp-difficulty">Difficulty {"◆" * entry["difficulty"]}</div>'
            f'<div class="mp-folder-status">{status}</div>'
        )
        st.button(
            "Open case file" if unlocked else "🔒 Locked",
            key=entry["id"],
            disabled=not unlocked,
            on_click=open_case,
            args=(entry["id"],),
        )


# ------------------------------------------------------------------ one case


def show_case(case_id: str) -> None:
    st.button("← Case cabinet", key="back", on_click=close_case)

    case = load_case(case_id)
    problems = validate_case(case)
    if problems:
        st.error("This case file cannot be played:")
        for problem in problems:
            st.markdown(f"- {problem}")
        return

    ids = [entry["id"] for entry in load_case_index()]
    kicker(f"Case #{ids.index(case_id) + 1:02d} · difficulty {'◆' * case['difficulty']}")
    st.title(case["title"])
    show_html(f'<div class="mp-briefing">{escape(case["briefing"])}</div>')

    if case.get("tip"):
        st.info(f"**Detective's note.** {case['tip']}", icon="🗒️")

    kicker("Testimony")
    for statement in case["statements"]:
        with st.chat_message(statement["speaker"], avatar=statement.get("avatar", "🗣️")):
            st.markdown(f"**{statement['speaker']}:** {statement['text']}")

    state = play(case, key=case_id)
    show_sidekick(happy=state.solved)

    if state.solved:
        show_next_case_button(case_id, ids)


def show_next_case_button(case_id: str, ids: list[str]) -> None:
    position = ids.index(case_id)
    if position + 1 < len(ids):
        # A row of its own, so the button can sit at the right under the board.
        with st.container(key="next_row", horizontal=True, horizontal_alignment="right"):
            st.button(
                "Next case →", key="next_case", type="primary",
                on_click=open_case, args=(ids[position + 1],),
            )
    else:
        st.info("That was the last case. Build a case of your own next.")


set_scene("office")

case_id = st.session_state.get("open_case")
if case_id is None:
    show_case_list()
else:
    show_case(case_id)
