"""
Pieces shared by more than one screen.
"""

import streamlit as st


def placeholder(title: str, description: str) -> None:
    """Draws a box marking a part of a screen that has not been built yet."""
    with st.container(border=True):
        st.markdown(f"**{title}** · not built yet")
        st.caption(description)
