"""
The drawn pieces of a case: the stage tracker, the key to the letters, the
goal, the proof lines, stamps, stars and the score sheet.

Every function here takes plain values and returns a piece of HTML as text.
None of them changes anything, which makes them easy to test on their own.
The CSS classes they use (all starting with "mp-") are styled in ui/style.css.
"""

from html import escape

from engine import format_formula

STAGES = ["Evidence", "Deduction", "Verdict"]


def stepper_html(stage: int) -> str:
    """The three stages of a case in a row: earlier ones ticked off, the current one lit."""
    steps = ""
    for number, name in enumerate(STAGES, start=1):
        if number < stage:
            css_class = "done"
        elif number == stage:
            css_class = "active"
        else:
            css_class = ""
        steps += f'<div class="mp-step {css_class}"><span class="mp-step-num">{number}</span>{name}</div>'
    return f'<div class="mp-stepper">{steps}</div>'


def legend_html(atoms: dict) -> str:
    """
    The key to the letters. Each meaning is put in quotes, because a letter
    only names a statement and does not say that the statement is true.
    Returns "" when no letter has a meaning (a typed case has none).
    """
    rows = ""
    for name, meaning in atoms.items():
        if meaning:
            rows += (
                '<div class="mp-legend-row">'
                f'<span class="mp-formula">{escape(name)}</span>'
                '<span class="mp-legend-means">stands for</span>'
                f'<span class="mp-legend-meaning">“{escape(meaning)}”</span>'
                "</div>"
            )
    if rows == "":
        return ""
    return f'<div class="mp-legend">{rows}</div>'


def goal_html(formula_text: str, sentence: str) -> str:
    """The conclusion the player has to reach: its formula and its English sentence."""
    return (
        '<div class="mp-goal"><span class="mp-goal-label">To prove</span>'
        f'<span class="mp-formula">{escape(formula_text)}</span>'
        f"<span>{escape(sentence)}</span></div>"
    )


def line_kind(justification: str) -> str:
    """
    Which sort of proof line this is: "statement", "clue", "assumption" or "derived".
    style.css gives each sort a different coloured edge.
    """
    for kind in ["Statement", "Clue", "Assumption"]:
        if justification.startswith(kind):
            return kind.lower()
    return "derived"


def proof_html(lines) -> str:
    """The proof so far, one row per line: its number, its formula, and where it came from."""
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


def rule_pattern_html(premises, conclusion: str) -> str:
    """The pattern of a rule, for example  P → Q ,  ¬Q  ⊢  ¬P."""
    return (
        '<div class="mp-rule">'
        f'<span class="mp-formula">{" ,  ".join(premises)}</span>'
        '<span class="mp-turnstile">⊢</span>'
        f'<span class="mp-formula">{conclusion}</span></div>'
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
    """The score sheet: one row for each reason points were won or lost, then the total."""
    rows = ""
    for label, points in breakdown:
        # {points:+d} writes the number with its sign: +100 or -15.
        rows += f'<div class="mp-score-row"><span>{escape(label)}</span><span>{points:+d}</span></div>'
    return (
        f'<div class="mp-score">{rows}'
        f'<div class="mp-score-row total"><span>Score</span><span>{total}</span></div></div>'
    )
