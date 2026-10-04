"""
Entry point. Start the game with:  python -m streamlit run app.py

This file only sets up the page and the menu; each screen lives in ui/.
"""

import streamlit as st

st.set_page_config(page_title="The Missing Premise", page_icon="🔎", layout="wide")

screens = [
    st.Page("ui/home.py", title="Home", default=True),
    st.Page("ui/case_files.py", title="Case files"),
    st.Page("ui/custom_case.py", title="Custom case"),
    st.Page("ui/truth_table_lab.py", title="Truth table lab"),
]

st.navigation(screens).run()
