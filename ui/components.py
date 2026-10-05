"""
Pieces shared by more than one screen.

Streamlit's own widgets are used for everything the player presses or types in.
What is only displayed (proof lines, truth tables, stamps, stars) is written as a
small piece of HTML, so that ui/style.css can make it look like part of a game.
Every function ending in _html returns a string and has no other effect, which
keeps them easy to test; show_html() puts such a string on the screen.

Text that comes from a case file or from the player always goes through
escape(), which turns characters such as < into harmless text.
"""

import base64
from html import escape
from pathlib import Path

import streamlit as st

from engine import (
    Formula,
    Iff,
    Not,
    ParseError,
    TruthTable,
    format_formula,
    get_subformulas,
    parse,
    prove_by_resolution,
    to_cnf,
)

SYNTAX_HELP = "Type ~ for ¬, & for ∧, | for ∨, -> for →, <-> for ↔. Brackets are allowed."

CONNECTIVE_KEYS = ["¬", "∧", "∨", "→", "↔", "(", ")"]

# Converting a formula with many ↔ to CNF takes exponentially many steps,
# so the resolution proof is skipped beyond this many in one formula.
MAX_IFFS_FOR_RESOLUTION = 5

STAGES = ["Evidence", "Deduction", "Verdict"]

ART_DIR = Path(__file__).parent / "art"

DETECTIVE_NAME = "Inspector Modus"


# -------------------------------------------------------------------- basics


def art_variables() -> str:
    """
    Makes every picture in ui/art available to style.css as a CSS variable:
    city.svg becomes --mp-art-city, and so on.

    The picture is written into the variable itself, encoded as text (base64),
    so the browser does not have to fetch a separate file.
    """
    variables = ""
    for path in sorted(ART_DIR.glob("*.svg")):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        variables += f'--mp-art-{path.stem}: url("data:image/svg+xml;base64,{encoded}");'
    return ":root {" + variables + "}"


def load_style() -> None:
    """Adds ui/style.css and the pictures to the page. Called once, from app.py."""
    css = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
    st.html(f"<style>{css}{art_variables()}</style>")


def set_scene(name: str) -> None:
    """Chooses the background picture of the current screen: "city", "office" or "lab"."""
    st.html(f"<style>:root {{ --mp-scene: var(--mp-art-{name}); }}</style>")


def show_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def detective_html(text: str, smiling: bool = False) -> str:
    """The detective's portrait beside a speech bubble."""
    mood = " smile" if smiling else ""
    return (
        '<div class="mp-detective">'
        f'<div class="mp-portrait{mood}"></div>'
        '<div class="mp-bubble">'
        f'<div class="mp-speaker">{DETECTIVE_NAME}</div>'
        f"<div>{escape(text)}</div>"
        "</div></div>"
    )


def detective_says(text: str, smiling: bool = False) -> None:
    show_html(detective_html(text, smiling))


def sidekick_html(happy: bool = False) -> str:
    """
    The detective standing at the left edge of the screen. style.css pins him
    there and shows him only when the window is wide enough to have room.
    """
    mood = " happy" if happy else ""
    return f'<div class="mp-sidekick{mood}"></div>'


def show_sidekick(happy: bool = False) -> None:
    show_html(sidekick_html(happy))


def kicker(text: str) -> None:
    """The small label above a title, like the tab on a case folder."""
    show_html(f'<div class="mp-kicker">{escape(text)}</div>')


def html_table(headers: list[str], rows: list[list[str]], row_classes: list[str] | None = None) -> str:
    """A table as HTML. row_classes gives each row a CSS class, used to tint it."""
    head = "".join(f"<th>{escape(str(heading))}</th>" for heading in headers)

    body = ""
    for index, row in enumerate(rows):
        css = row_classes[index] if row_classes else ""
        cells = "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
        body += f'<tr class="{css}">{cells}</tr>'

    return (
        '<div class="mp-table-wrap"><table class="mp-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


# ------------------------------------------------------------ typed formulas


def show_parse_error(text: str, error: ParseError) -> None:
    """Shows the parser's message with a ^ under the place it points at."""
    st.error(str(error))
    st.code(f"{text}\n{' ' * error.position}^", language=None)


def read_formula(text: str, label: str) -> Formula | None:
    """Parses one typed formula. On malformed input, shows the error and returns None."""
    try:
        return parse(text)
    except ParseError as error:
        st.markdown(f"**{label}** could not be read:")
        show_parse_error(text, error)
        return None


def read_formulas(text: str, label: str) -> list[Formula] | None:
    """
    Parses one formula per line, skipping blank lines.
    On the first malformed line, shows the error and returns None.
    """
    formulas = []
    lines = [line for line in text.splitlines() if line.strip()]
    for number, line in enumerate(lines, start=1):
        formula = read_formula(line, f"{label} {number}")
        if formula is None:
            return None
        formulas.append(formula)
    return formulas


def type_key(target: str, text: str) -> None:
    """Runs when an on-screen key is pressed: adds its text to the box named target."""
    st.session_state[target] = st.session_state.get(target, "") + text


def erase_key(target: str) -> None:
    """Runs when ⌫ is pressed: removes the last character from the box named target."""
    st.session_state[target] = st.session_state.get(target, "")[:-1]


def show_keyboard(target: str, letters: list[str], prefix: str) -> None:
    """
    A row of on-screen keys that type into the text box whose key is target:
    the connectives, the case's atoms, and ⌫. prefix keeps the keys of
    different boxes apart.
    """
    with st.container(horizontal=True, key=f"keys_{prefix}"):
        for number, text in enumerate(CONNECTIVE_KEYS + letters):
            st.button(text, key=f"{prefix}_key_{number}", on_click=type_key, args=(target, text))
        st.button("⌫", key=f"{prefix}_key_erase", on_click=erase_key, args=(target,))


# -------------------------------------------------------------- truth tables


def truth_table_cells(table: TruthTable) -> tuple[list[str], list[list[str]]]:
    """Returns the headings and the rows of T and F for a truth table, row numbers first."""
    headings = ["#"] + table.atoms
    kept = []  # indices of the formula columns that get their own column
    for index, formula in enumerate(table.columns):
        heading = format_formula(formula)
        # A formula that is a single atom, or that was given twice, already has its column.
        if heading not in headings:
            headings.append(heading)
            kept.append(index)

    rows = []
    for number, row in enumerate(table.rows, start=1):
        cells = [str(number)]
        cells += ["T" if row.assignment[name] else "F" for name in table.atoms]
        cells += ["T" if row.values[index] else "F" for index in kept]
        rows.append(cells)

    return headings, rows


def truth_table_html(table: TruthTable, critical_rows=(), counterexamples=()) -> str:
    """A truth table as HTML, with critical rows tinted gold and counterexamples red."""
    headings, rows = truth_table_cells(table)

    row_classes = []
    for index in range(len(rows)):
        if index in counterexamples:
            row_classes.append("counter")
        elif index in critical_rows:
            row_classes.append("critical")
        else:
            row_classes.append("")

    return html_table(headings, rows, row_classes)


def show_truth_table(table: TruthTable, critical_rows=(), counterexamples=()) -> None:
    show_html(truth_table_html(table, critical_rows, counterexamples))
    if critical_rows or counterexamples:
        st.caption(
            "Gold rows: every premise is true (critical rows). "
            "Red rows: every premise is true and the conclusion is false (counterexamples)."
        )


# ---------------------------------------------------------------- game board


def stepper_html(stage: int) -> str:
    """The three stages of a case across the top, with the current one lit."""
    steps = ""
    for number, name in enumerate(STAGES, start=1):
        if number < stage:
            css = "done"
        elif number == stage:
            css = "active"
        else:
            css = ""
        steps += f'<div class="mp-step {css}"><span class="mp-step-num">{number}</span>{name}</div>'
    return f'<div class="mp-stepper">{steps}</div>'


def line_kind(justification: str) -> str:
    """Which sort of proof line this is, used to colour its edge."""
    for kind in ("Statement", "Clue", "Assumption"):
        if justification.startswith(kind):
            return kind.lower()
    return "derived"


def proof_html(lines) -> str:
    """The proof so far as numbered lines: number, formula, and where it came from."""
    rows = ""
    for line in lines:
        rows += (
            f'<div class="mp-line {line_kind(line.justification)}">'
            f'<span class="mp-num">{line.id}</span>'
            f'<span class="mp-formula">{escape(format_formula(line.formula))}</span>'
            f'<span class="mp-from">{escape(line.justification)}</span>'
            "</div>"
        )
    return f'<div class="mp-proof">{rows}</div>'


def goal_html(formula_text: str, sentence: str) -> str:
    return (
        '<div class="mp-goal"><span class="mp-goal-label">To prove</span>'
        f'<span class="mp-formula">{escape(formula_text)}</span>'
        f"<span>{escape(sentence)}</span></div>"
    )


def stamp_html(text: str, colour: str = "red") -> str:
    """A rubber stamp, such as CASE CLOSED. colour is "red", "green" or "grey"."""
    return f'<div class="mp-stamp {colour}">{escape(text)}</div>'


def stars_html(stars: int) -> str:
    """Three stars, the first `stars` of them lit."""
    lit = "★" * stars
    unlit = "★" * (3 - stars)
    return f'<span class="mp-stars">{lit}<span class="unlit">{unlit}</span></span>'


def score_html(breakdown: list[tuple[str, int]], total: int) -> str:
    rows = "".join(
        f'<div class="mp-score-row"><span>{escape(label)}</span><span>{points:+d}</span></div>'
        for label, points in breakdown
    )
    return (
        f'<div class="mp-score">{rows}'
        f'<div class="mp-score-row total"><span>Score</span><span>{total}</span></div></div>'
    )


# ---------------------------------------------------------------- resolution


def clause_text(clause) -> str:
    """Writes a clause such as {¬P, Q} as "¬P ∨ Q"; the empty clause is written □."""
    if not clause:
        return "□ (empty clause: a contradiction)"
    return " ∨ ".join(sorted(clause, key=lambda literal: literal.lstrip("¬")))


def count_iffs(formula: Formula) -> int:
    return sum(1 for part in get_subformulas(formula) if isinstance(part, Iff))


def show_resolution_proof(premises: list[Formula], conclusion: Formula) -> None:
    """
    Draws the automatic proof by contradiction: the premises and the negated
    conclusion as clauses, then each resolution step, numbered.
    """
    negated = Not(conclusion)
    if any(count_iffs(formula) > MAX_IFFS_FOR_RESOLUTION for formula in premises + [negated]):
        st.info(
            f"The resolution proof is not shown: a formula here has more than "
            f"{MAX_IFFS_FOR_RESOLUTION} ↔ connectives, and its normal form would be too large to read."
        )
        return

    with st.expander("Step 1: convert each premise and the negated conclusion to CNF"):
        labelled = [(f"Premise {number}", formula) for number, formula in enumerate(premises, start=1)]
        labelled.append(("Negated conclusion", negated))
        for label, formula in labelled:
            conversion = to_cnf(formula)
            st.markdown(f"**{label}:** `{format_formula(formula)}`")
            if not conversion.steps:
                st.caption("Already in CNF.")
            for step in conversion.steps:
                st.markdown(f"- {step.rule}: `{format_formula(step.formula)}`")

    proof = prove_by_resolution(premises, conclusion)

    rows = []
    for line in proof.lines:
        if line.source == "resolvent":
            first, second = line.parents
            source = f"Resolve {first}, {second} on {line.on}"
        else:
            source = line.source.capitalize()
        rows.append([str(line.id), clause_text(line.clause), source])

    st.markdown("**Step 2: resolve pairs of clauses**")
    show_html(html_table(["#", "Clause", "From"], rows))

    if proof.proved:
        st.success(
            "The empty clause was derived: the premises together with the negated "
            "conclusion are contradictory, so the conclusion follows."
        )
    else:
        st.error(
            "No new clause can be made and the empty clause never appeared: "
            "the conclusion does not follow from the premises."
        )
