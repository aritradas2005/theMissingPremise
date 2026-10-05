"""
The deduction board: one case in play. Used by the case files screen for the
written cases and by the custom case screen for typed ones.

The game itself lives in a GameState object kept in st.session_state, so it
survives Streamlit re-running the screen after every click. Each show_...
function draws one part of the screen from that state.

Every button names a function to run when it is pressed (on_click). Streamlit
runs that function first, which changes the game, and then redraws the screen.
"""

from html import escape

import streamlit as st

from engine import RULES, format_formula, parse
from game.game_state import (
    GameState,
    assume_opposite,
    attempt_step,
    board_premises,
    collect_clue,
    create_game,
    current_argument,
    goal,
)
from game.hints import use_hint
from game.scoring import score_case, stars_for
from ui.components import (
    SYNTAX_HELP,
    detective_says,
    goal_html,
    kicker,
    proof_html,
    score_html,
    show_html,
    show_keyboard,
    show_resolution_proof,
    show_truth_table,
    stamp_html,
    stars_html,
    stepper_html,
)

RULES_BY_ID = {rule.id: rule for rule in RULES}

# What the detective says at each stage of a case.
OBJECTIVES = {
    1: "The testimony alone does not prove it. A premise is missing: pin the evidence "
       "that rules out the red rows of the truth table.",
    2: "Now we have enough. Choose a rule, choose the lines it uses, and write the line that follows.",
    3: "Case closed. The logic holds.",
}


def play(case: dict, key: str) -> GameState:
    """
    Draws the case and returns its state.
    key names this game in st.session_state and keeps its widgets apart from other cases.
    """
    games = st.session_state.setdefault("games", {})
    if key not in games:
        games[key] = create_game(case)
    state = games[key]

    current = stage(state)
    show_html(stepper_html(current))
    detective_says(OBJECTIVES[current], smiling=state.solved)

    locker, board = st.columns([2, 3], gap="large")
    with locker:
        show_evidence(state, key)
    with board:
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


def record_score(key: str) -> None:
    """
    Once a game is solved, keeps its score as the best for that case.
    This is called by the buttons that can finish a case, before the screen is
    redrawn, so that the top bar already shows the new points and rank.
    """
    state = st.session_state["games"][key]
    if state.solved:
        scores = st.session_state.setdefault("scores", {})
        scores[key] = max(score_case(state).total, scores.get(key, 0))


def pin_evidence(key: str, clue_id: str) -> None:
    """Runs when "Pin to the board" is pressed."""
    collect_clue(st.session_state["games"][key], clue_id)
    record_score(key)


def restart(key: str) -> None:
    """Throws the game away; play() starts a fresh one on the next run."""
    st.session_state["games"].pop(key, None)
    # Also forget the last message, the celebration, and whatever was half-filled
    # in the step builder, so that nothing from the old game is left selected.
    for name in ("message", "celebrated", "step_rule", "step_lines", "step_new_line"):
        st.session_state.pop(f"{key}_{name}", None)


# ----------------------------------------------------------------- evidence


def show_letter_key(case: dict) -> None:
    """
    What each letter stands for. The rows are statements to reason about, not
    facts, so each meaning is shown in quotes with a note saying so.
    """
    rows = "".join(
        f'<div class="mp-legend-row"><span class="mp-formula">{escape(name)}</span>'
        '<span class="mp-legend-means">stands for</span>'
        f'<span class="mp-legend-meaning">“{escape(meaning)}”</span></div>'
        for name, meaning in case["atoms"].items()
        if meaning
    )
    if not rows:
        return

    kicker("Key to the letters")
    show_html(f'<div class="mp-legend">{rows}</div>')
    st.caption(
        "A letter only names a statement; it does not say the statement is true. "
        "¬ in front of a letter says it is false."
    )


def show_evidence(state: GameState, key: str) -> None:
    case = state.case
    show_letter_key(case)
    kicker("Evidence locker")

    if not case["clues"]:
        st.caption("There is no evidence to collect in this case.")
        return

    for position, clue in enumerate(case["clues"]):
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


# -------------------------------------------------------------------- board


def show_proof(state: GameState) -> None:
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

    if not result.critical_rows:
        st.error(
            "The premises on the board contradict each other: no row of the truth "
            "table makes them all true."
        )
    elif result.valid:
        st.success("The premises on the board are enough. Now derive the conclusion step by step.")
    else:
        count = len(result.counterexamples)
        rows = "row" if count == 1 else "rows"
        st.warning(
            f"A premise is missing. In {count} {rows} of the truth table every premise on "
            f"the board is true and the conclusion is false. Find the evidence that rules "
            f"{'it' if count == 1 else 'them'} out."
        )

    with st.expander("🔍 Examine the truth table"):
        show_truth_table(result.table, result.critical_rows, result.counterexamples)


def show_step_builder(state: GameState, key: str) -> None:
    """Three choices make one deduction: a rule, the lines it uses, and the new line."""
    rule_key = f"{key}_step_rule"
    lines_key = f"{key}_step_lines"
    new_line_key = f"{key}_step_new_line"

    rules = state.case["rules"]
    line_ids = [line.id for line in state.lines]
    formulas = {line.id: format_formula(line.formula) for line in state.lines}

    # A rule is always selected, so its pattern can be shown.
    if st.session_state.get(rule_key) not in rules:
        st.session_state[rule_key] = rules[0]

    with st.container(key=f"builder_{key}", border=True):
        kicker("Make a deduction")

        st.pills(
            "1 · Rule of inference",
            rules,
            format_func=lambda rule_id: RULES_BY_ID[rule_id].name,
            key=rule_key,
        )
        rule = RULES_BY_ID[st.session_state[rule_key]]
        show_html(
            '<div class="mp-rule">'
            f'<span class="mp-formula">{" ,  ".join(rule.premises)}</span>'
            '<span class="mp-turnstile">⊢</span>'
            f'<span class="mp-formula">{rule.conclusion}</span></div>'
        )

        st.pills(
            "2 · Lines it uses",
            line_ids,
            selection_mode="multi",
            format_func=lambda line_id: f"{line_id} ·  {formulas[line_id]}",
            key=lines_key,
        )

        st.text_input(
            "3 · The line that follows",
            key=new_line_key,
            placeholder="press the keys below, or type the formula",
            help=SYNTAX_HELP,
        )
        show_keyboard(new_line_key, list(state.case["atoms"]), prefix=key)

        st.button(
            "Check this step", key=f"{key}_check", type="primary",
            on_click=submit_step, args=(key,),
        )

    show_message(key)


def submit_step(key: str) -> None:
    """Runs when "Check this step" is pressed: hands the three choices to the game."""
    state = st.session_state["games"][key]
    result = attempt_step(
        state,
        st.session_state[f"{key}_step_rule"],
        list(st.session_state.get(f"{key}_step_lines", [])),
        st.session_state.get(f"{key}_step_new_line", ""),
    )
    st.session_state[f"{key}_message"] = ("success" if result.valid else "error", result.reason)

    # An accepted step empties the builder, ready for the next one.
    if result.valid:
        st.session_state[f"{key}_step_lines"] = []
        st.session_state[f"{key}_step_new_line"] = ""
        record_score(key)


def show_message(key: str) -> None:
    """Shows the result of the last step or hint."""
    message = st.session_state.get(f"{key}_message")
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
    with st.container(horizontal=True, key=f"actions_{key}"):
        st.button(
            "⇄ Assume the opposite", key=f"{key}_assume", disabled=state.by_contradiction,
            help="Switch to proof by contradiction.", on_click=start_contradiction, args=(key,),
        )
        st.button("💡 Hint", key=f"{key}_hint", help="Costs 15 points.", on_click=give_hint, args=(key,))
        st.button("↺ Start again", key=f"{key}_restart", on_click=restart, args=(key,))

    st.caption(f"Rejected steps: {state.mistakes}  ·  Hints used: {state.hints_used}")


def start_contradiction(key: str) -> None:
    assume_opposite(st.session_state["games"][key])
    st.session_state.pop(f"{key}_message", None)
    record_score(key)


def give_hint(key: str) -> None:
    st.session_state[f"{key}_message"] = ("info", use_hint(st.session_state["games"][key]))


# ------------------------------------------------------------------ verdict


def show_verdict(state: GameState, key: str) -> None:
    score = score_case(state)

    # Balloons once, not on every redraw of the solved case.
    if not st.session_state.get(f"{key}_celebrated"):
        st.balloons()
        st.session_state[f"{key}_celebrated"] = True

    technique = "proof by contradiction" if state.by_contradiction else "direct proof"
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
