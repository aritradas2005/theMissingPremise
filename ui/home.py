"""
Home screen: the title and a link to each of the other screens.
"""

import streamlit as st

st.title("The Missing Premise")
st.caption("Every case is an argument. Find what is missing, then prove it.")

left, middle, right = st.columns(3)

with left:
    st.page_link("ui/case_files.py", label="**Case files**")
    st.write("Solve the cases in order.")

with middle:
    st.page_link("ui/custom_case.py", label="**Custom case**")
    st.write("Type your own premises and conclusion.")

with right:
    st.page_link("ui/truth_table_lab.py", label="**Truth table lab**")
    st.write("Build the truth table of any formula.")
