"""
Drawing the automatic resolution proof: first each formula's conversion to
CNF, then the numbered list of clauses, then the verdict.
"""

import streamlit as st

from engine import Formula, Not, format_formula, prove_by_resolution, to_cnf
from ui.look import show_html
from ui.tables import html_table

# A conversion to CNF can run to hundreds of steps; only this many are listed.
MAX_CNF_STEPS_SHOWN = 25


def atom_name(literal: str) -> str:
    """The atom inside a literal: "P" for both "P" and "¬P"."""
    return literal.lstrip("¬")


def clause_text(clause) -> str:
    """Writes a clause such as {¬P, Q} as "¬P ∨ Q"; the empty clause is written □."""
    if not clause:
        return "□ (empty clause: a contradiction)"
    in_order = sorted(clause, key=atom_name)     # alphabetical by atom, so ¬P comes before Q
    return " ∨ ".join(in_order)


def show_conversion(label: str, formula: Formula, conversion) -> None:
    """One formula's conversion to CNF, step by step. A very long one is shortened."""
    st.markdown(f"**{label}:** `{format_formula(formula)}`")
    if not conversion.steps:
        st.caption("Already in CNF.")
        return

    shown = conversion.steps[:MAX_CNF_STEPS_SHOWN]
    listing = ""
    for step in shown:
        listing += f"- {step.rule}: `{format_formula(step.formula)}`\n"
    st.markdown(listing)

    hidden = len(conversion.steps) - len(shown)
    if hidden > 0:
        st.caption(f"… and {hidden} more steps, ending in:")
        st.code(format_formula(conversion.result), language=None)


def proof_rows(proof) -> list[list[str]]:
    """The resolution proof as rows of text: line number, clause, where it came from."""
    rows = []
    for line in proof.lines:
        if line.source == "resolvent":
            first, second = line.parents
            came_from = f"Resolve {first}, {second} on {line.on}"
        else:
            came_from = line.source.capitalize()
        rows.append([str(line.id), clause_text(line.clause), came_from])
    return rows


def show_resolution_proof(premises: list[Formula], conclusion: Formula) -> None:
    """
    Draws the automatic proof by contradiction: the premises and the negated
    conclusion as clauses, then each resolution step, numbered.
    """
    labelled = []
    for number, formula in enumerate(premises, start=1):
        labelled.append((f"Premise {number}", formula))
    labelled.append(("Negated conclusion", Not(conclusion)))

    # All the work is done before anything is drawn. The engine refuses an
    # argument that would take too long, and that is reported as a message.
    try:
        conversions = []
        for label, formula in labelled:
            conversions.append(to_cnf(formula))
        proof = prove_by_resolution(premises, conclusion)
    except ValueError as error:
        st.info(f"The resolution proof is not shown. {error}")
        return

    with st.expander("Step 1: convert each premise and the negated conclusion to CNF"):
        for (label, formula), conversion in zip(labelled, conversions):
            show_conversion(label, formula, conversion)

    st.markdown("**Step 2: resolve pairs of clauses**")
    show_html(html_table(["#", "Clause", "From"], proof_rows(proof)))

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
