"""
The games in progress, and the scores.

Streamlit runs a screen's file again from the top after every click. Anything
that must be remembered between clicks is kept in st.session_state, which
works like a dictionary that lasts as long as the browser tab is open. This
file is the only place that knows how the games are stored there.

What is stored:
    "games"               case key → GameState     every game in progress
    "scores"              case key → best score    one entry per solved case
    "<key>_message"       the last message shown under the step builder
    "<key>_celebrated"    True once the balloons have been shown for this game
    "<key>_step_rule", "<key>_step_lines", "<key>_step_new_line"
                          the three choices in the step builder

The case key is the case id, such as "case-01", or "custom" for a typed case.
"""

import streamlit as st

from game.game_state import GameState, create_game
from game.scoring import score_case

# The names, after "<key>_", of everything remembered about one game besides the game itself.
REMEMBERED_ABOUT_A_GAME = ["message", "celebrated", "step_rule", "step_lines", "step_new_line"]


# -------------------------------------------------------------------- games


def all_games() -> dict:
    """Every game in progress, by case key. Created empty the first time it is asked for."""
    if "games" not in st.session_state:
        st.session_state["games"] = {}
    return st.session_state["games"]


def has_game(key: str) -> bool:
    """True when a game with this key is in progress."""
    return key in all_games()


def start_game(case: dict, key: str) -> GameState:
    """Starts a fresh game of this case and remembers it."""
    state = create_game(case)
    all_games()[key] = state
    return state


def get_game(case: dict, key: str) -> GameState:
    """The game in progress for this case; one is started if there is none yet."""
    if has_game(key):
        return all_games()[key]
    return start_game(case, key)


def find_game(key: str) -> GameState:
    """The game in progress with this key. Used by buttons, which are only shown during a game."""
    return all_games()[key]


def restart(key: str) -> None:
    """
    Throws a game away, together with everything remembered about it, so that
    nothing from the old game is left selected. A fresh one starts on the next draw.
    """
    all_games().pop(key, None)
    for name in REMEMBERED_ABOUT_A_GAME:
        st.session_state.pop(f"{key}_{name}", None)


# ------------------------------------------------------------------- scores


def best_scores() -> dict:
    """The best score of each solved case, by case key."""
    if "scores" not in st.session_state:
        st.session_state["scores"] = {}
    return st.session_state["scores"]


def record_score(key: str) -> None:
    """
    If the game is solved, keeps its score as the best for that case.

    The buttons that can finish a case call this before the screen is redrawn,
    so that the top bar already shows the new points and rank.
    """
    state = find_game(key)
    if not state.solved:
        return

    total = score_case(state).total
    scores = best_scores()
    if key not in scores or total > scores[key]:
        scores[key] = total


# ----------------------------------------------------------------- messages


def set_message(key: str, kind: str, text: str) -> None:
    """Remembers a message to show under the step builder. kind is "success", "error" or "info"."""
    st.session_state[f"{key}_message"] = (kind, text)


def clear_message(key: str) -> None:
    """Forgets the remembered message, so that nothing is shown under the step builder."""
    st.session_state.pop(f"{key}_message", None)


def get_message(key: str):
    """The remembered message as (kind, text), or None if there is none."""
    return st.session_state.get(f"{key}_message")
