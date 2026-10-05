"""
The step builder: where the player makes one deduction.

A deduction takes three choices:
    1. a rule of inference,
    2. the lines on the board that the rule is used on,
    3. the new line that follows.

About the buttons. Each button is told which function to run when it is
pressed (on_click) and what to pass to it (args). Streamlit runs that function
first, and then draws the whole screen again. So the functions below named
submit_step, start_contradiction and give_hint only change the game; they
never draw anything.
"""

import streamlit as st

from engine import find_rule, format_formula
from game.game_state import GameState, assume_opposite, attempt_step
from game.hints import use_hint
from ui.board_pieces import rule_pattern_html
from ui.formula_box import SYNTAX_HELP, show_keyboard
from ui.look import kicker, show_html
from ui.session import clear_message, find_game, get_message, record_score, restart, set_message


def rule_name(rule_id: str) -> str:
    """The name shown on a rule's chip, for example "Modus Tollens"."""
    return find_rule(rule_id).name


def show_step_builder(state: GameState, key: str) -> None:
    """Draws the three choices and the "Check this step" button."""
    rule_box = f"{key}_step_rule"
    lines_box = f"{key}_step_lines"
    new_line_box = f"{key}_step_new_line"

    allowed_rules = state.case["rules"]

    # A rule is always selected, so that its pattern can be shown.
    if st.session_state.get(rule_box) not in allowed_rules:
        st.session_state[rule_box] = allowed_rules[0]

    # What to write on each line's chip, for example "2 ·  G → B".
    line_labels = {}
    for line in state.lines:
        line_labels[line.id] = f"{line.id} ·  {format_formula(line.formula)}"

    with st.container(key=f"builder_{key}", border=True):
        kicker("Make a deduction")

        # format_func turns each option into the text shown on its chip.
        st.pills("1 · Rule of inference", allowed_rules, format_func=rule_name, key=rule_box)
        chosen_rule = find_rule(st.session_state[rule_box])
        show_html(rule_pattern_html(chosen_rule.premises, chosen_rule.conclusion))

        st.pills(
            "2 · Lines it uses",
            list(line_labels),
            selection_mode="multi",
            format_func=line_labels.get,
            key=lines_box,
        )

        st.text_input(
            "3 · The line that follows",
            key=new_line_box,
            placeholder="press the keys below, or type the formula",
            help=SYNTAX_HELP,
        )
        show_keyboard(new_line_box, list(state.case["atoms"]), prefix=key)

        st.button(
            "Check this step", key=f"{key}_check", type="primary",
            on_click=submit_step, args=(key,),
        )

    show_message(key)


def submit_step(key: str) -> None:
    """Runs when "Check this step" is pressed: hands the three choices to the game."""
    state = find_game(key)
    rule_id = st.session_state[f"{key}_step_rule"]
    line_ids = list(st.session_state.get(f"{key}_step_lines", []))
    new_line = st.session_state.get(f"{key}_step_new_line", "")

    result = attempt_step(state, rule_id, line_ids, new_line)

    if result.valid:
        set_message(key, "success", result.reason)
        # An accepted step empties the builder, ready for the next one.
        st.session_state[f"{key}_step_lines"] = []
        st.session_state[f"{key}_step_new_line"] = ""
        record_score(key)
    else:
        set_message(key, "error", result.reason)


def show_message(key: str) -> None:
    """Shows the result of the last step or hint, if there is one."""
    message = get_message(key)
    if message is None:
        return

    kind, text = message
    if kind == "success":
        st.success(text)
    elif kind == "error":
        st.error(text)
    else:
        st.info(text)


def show_actions(state: GameState, key: str) -> None:
    """The three buttons under the builder, and the count of mistakes and hints."""
    with st.container(horizontal=True, key=f"actions_{key}"):
        st.button(
            "⇄ Assume the opposite", key=f"{key}_assume", disabled=state.by_contradiction,
            help="Switch to proof by contradiction.", on_click=start_contradiction, args=(key,),
        )
        st.button("💡 Hint", key=f"{key}_hint", help="Costs 15 points.", on_click=give_hint, args=(key,))
        st.button("↺ Start again", key=f"{key}_restart", on_click=restart, args=(key,))

    st.caption(f"Rejected steps: {state.mistakes}  ·  Hints used: {state.hints_used}")


def start_contradiction(key: str) -> None:
    """Runs when "Assume the opposite" is pressed."""
    assume_opposite(find_game(key))
    clear_message(key)
    record_score(key)


def give_hint(key: str) -> None:
    """Runs when "Hint" is pressed: the hint becomes the message under the builder."""
    hint = use_hint(find_game(key))
    set_message(key, "info", hint)
