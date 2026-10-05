"""
The starting point of the game. Run it with:

    python -m streamlit run app.py

This file does three things:
    1. sets up the page and loads the styling and pictures;
    2. lists the four screens, each of which is a file in ui/;
    3. draws the bar at the top of every screen, then the screen itself.
"""

import streamlit as st

from game.case_loader import load_case_index
from game.scoring import rank_for
from ui.look import load_style, show_html
from ui.session import best_scores

st.set_page_config(page_title="The Missing Premise", page_icon="🔎", layout="wide")
load_style()

screens = [
    st.Page("ui/home.py", title="Home", default=True),
    st.Page("ui/case_files.py", title="Case files"),
    st.Page("ui/custom_case.py", title="Custom case"),
    st.Page("ui/truth_table_lab.py", title="Truth table lab"),
]


def show_top_bar() -> None:
    """The links to each screen, and the detective's rank, points and solved cases."""
    scores = best_scores()
    cases = load_case_index()

    # Only the written cases count towards the rank, not a typed custom case.
    points = 0
    solved = 0
    for case in cases:
        if case["id"] in scores:
            points += scores[case["id"]]
            solved += 1

    with st.container(key="topbar", horizontal=True, vertical_alignment="center"):
        st.page_link("ui/home.py", label="**🔎 The Missing Premise**")
        st.page_link("ui/case_files.py", label="Case files")
        st.page_link("ui/custom_case.py", label="Build a case")
        st.page_link("ui/truth_table_lab.py", label="Logic lab")
        show_html(
            '<div class="mp-badge">'
            f'<span class="mp-rank">{rank_for(points)}</span>'
            f"<span>{points} pts</span>"
            f"<span>{solved}/{len(cases)} cases</span>"
            "</div>"
        )


# position="hidden" removes Streamlit's own sidebar menu; the top bar replaces it.
current_screen = st.navigation(screens, position="hidden")
show_top_bar()
current_screen.run()
