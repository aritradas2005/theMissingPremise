"""
Entry point. Start the game with:  python -m streamlit run app.py

This file sets up the page, loads the styling, and draws the bar that stays at
the top of every screen. Each screen lives in ui/.
"""

import streamlit as st

from game.case_loader import load_case_index
from game.scoring import rank_for
from ui.components import load_style, show_html

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
    case_ids = [entry["id"] for entry in load_case_index()]
    scores = st.session_state.get("scores", {})
    solved = [case_id for case_id in case_ids if case_id in scores]
    points = sum(scores[case_id] for case_id in solved)

    with st.container(key="topbar", horizontal=True, vertical_alignment="center"):
        st.page_link("ui/home.py", label="**🔎 The Missing Premise**")
        st.page_link("ui/case_files.py", label="Case files")
        st.page_link("ui/custom_case.py", label="Build a case")
        st.page_link("ui/truth_table_lab.py", label="Logic lab")
        show_html(
            '<div class="mp-badge">'
            f'<span class="mp-rank">{rank_for(points)}</span>'
            f"<span>{points} pts</span>"
            f"<span>{len(solved)}/{len(case_ids)} cases</span>"
            "</div>"
        )


# position="hidden" removes Streamlit's own sidebar menu; the top bar replaces it.
current_screen = st.navigation(screens, position="hidden")
show_top_bar()
current_screen.run()
