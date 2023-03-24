import streamlit as st

from app_utils.settings import (
    pre_settings,
    post_settings,
    settings_advanced,
    settings_simple
)
from app_utils.common import show_filters, dynamic_checkbox
from app_utils.session import validate_page

########################
########################
validate_page()

stdata = st.session_state["stdata"]
intercols = st.session_state["intercols"]
stdatalayout = st.session_state["stdatalayout"]
matcher = st.session_state["matcher"]
vpnames = st.session_state["vpnames"]
########################
st.title("Match Settings")

if not any(val is None for val in stdata.values()):
    schl, teach = pre_settings()
    if st.session_state["sett_adv"]:
        settings_advanced()
    else:
        settings_simple()
    post_settings()
else:
    st.write("Please import data before attempting to set match settings")
