"""
Title screen: the detective, the game's name, the three ways to play, and the handbook.
"""

import streamlit as st

from ui.components import DETECTIVE_NAME, set_scene, show_html

set_scene("city")

figure, words = st.columns([2, 3], vertical_alignment="center")

with figure:
    # The detective is a background picture of this box, set in style.css.
    show_html('<div class="mp-hero-figure"></div>')

with words:
    show_html('<div class="mp-hero mp-kicker">A discrete mathematics mystery</div>')
    st.title("The Missing Premise")
    show_html(
        '<div class="mp-tagline">Every case is an argument. '
        f"Find what is missing, then prove it. With {DETECTIVE_NAME} on the case.</div>"
    )

MENU = [
    ("ui/case_files.py", "▶  Investigate", "Five cases. Find the missing premise and prove who did it."),
    ("ui/custom_case.py", "✎  Build a case", "Type your own premises and conclusion, then play them."),
    ("ui/truth_table_lab.py", "⚗  Logic lab", "Work out the truth table of any formula."),
]

for column, (page, label, description) in zip(st.columns(3), MENU):
    with column.container(key=f"menu_{page.split('/')[1].split('.')[0]}", border=True):
        st.page_link(page, label=f"**{label}**")
        st.caption(description)

with st.expander("📖 Detective's handbook: how to play"):
    st.markdown(
        """
1. **Read the testimony.** The witness statements are your premises, already on the deduction board.
2. **Find the missing premise.** The statements alone never prove the conclusion. The truth table
   shows the rows where they are all true and the conclusion is false. Pin the evidence that rules
   those rows out.
3. **Prove it.** Pick a rule of inference, the lines it uses, and write the new line. Every step
   is checked. Derive the conclusion (direct proof), or assume its opposite and derive a formula
   together with its negation (proof by contradiction).
4. **Score.** A solved case is worth 100 points, less 10 for each rejected step, 15 for each hint
   and 10 for each piece of evidence the argument did not need. Points raise your rank.
"""
    )
