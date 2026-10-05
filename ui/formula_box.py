"""
Everything to do with typing a formula: reading what was typed, showing a
mistake with a pointer to where it is, and the row of on-screen keys.
"""

import streamlit as st

from engine import Formula, ParseError, parse

# The keys to type are written between backquotes. Without them Streamlit
# would turn "->" into an arrow, and the help would read "→ for →".
SYNTAX_HELP = "Type `~` for ¬, `&` for ∧, `|` for ∨, `->` for →, `<->` for ↔. Brackets are allowed."

CONNECTIVE_KEYS = ["¬", "∧", "∨", "→", "↔", "(", ")"]


# ------------------------------------------------------- reading what was typed


def show_parse_error(text: str, error: ParseError) -> None:
    """Shows the parser's message, then the text with a ^ under the place it points at."""
    st.error(str(error))
    pointer = " " * error.position + "^"
    st.code(text + "\n" + pointer, language=None)


def read_formula(text: str, label: str) -> Formula | None:
    """
    Parses one typed formula.
    If it is malformed, shows the mistake and returns None.
    """
    try:
        return parse(text)
    except ParseError as error:
        st.markdown(f"**{label}** could not be read:")
        show_parse_error(text, error)
        return None


def read_formulas(text: str, label: str) -> list[Formula] | None:
    """
    Parses a box of formulas, one per line; blank lines are skipped.
    If any line is malformed, shows the first mistake and returns None.
    """
    formulas = []
    number = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        number += 1
        formula = read_formula(line, f"{label} {number}")
        if formula is None:
            return None
        formulas.append(formula)
    return formulas


# ------------------------------------------------------------ on-screen keys


def type_key(box: str, text: str) -> None:
    """Runs when an on-screen key is pressed: adds its text to the end of the box."""
    st.session_state[box] = st.session_state.get(box, "") + text


def erase_key(box: str) -> None:
    """Runs when ⌫ is pressed: removes the last character from the box."""
    st.session_state[box] = st.session_state.get(box, "")[:-1]


def show_keyboard(box: str, letters: list[str], prefix: str) -> None:
    """
    A row of keys that type into a text box: the connectives, the given
    letters, and ⌫.

    box     the key of the text box the keys type into
    prefix  put in front of each key's own name, so that two keyboards on one
            screen do not clash
    """
    keys = CONNECTIVE_KEYS + letters
    with st.container(horizontal=True, key=f"keys_{prefix}"):
        for number, text in enumerate(keys):
            st.button(text, key=f"{prefix}_key_{number}", on_click=type_key, args=(box, text))
        st.button("⌫", key=f"{prefix}_key_erase", on_click=erase_key, args=(box,))
