from itertools import chain

import streamlit as st
import yaml

from app_utils.importer import column_chooser, option_chooser, set_intercols, schlteach
from app_utils.common import displaykey, gen_yaml

#################################################
#################################################
st.set_page_config(page_title="Fab Matcher")
enable_scroll = """
<style>
.main {
    overflow: auto;
}
</style>
"""
st.markdown(enable_scroll, unsafe_allow_html=True)

stdatalayout = st.session_state["stdatalayout"]

st.title("Import")

for tab, name in zip(st.tabs(stdatalayout), stdatalayout):
    with tab:
        schlteach(name)
