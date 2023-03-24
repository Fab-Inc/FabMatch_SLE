import streamlit as st

from app_utils.importer import schlteach
from app_utils.session import validate_page

#################################################
#################################################
validate_page()

stdatalayout = st.session_state["stdatalayout"]

st.title("Import Data")

for tab, name in zip(st.tabs(stdatalayout), stdatalayout):
    with tab:
        schlteach(name)
