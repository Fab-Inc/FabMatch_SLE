import time
import os
from pathlib import Path

import streamlit as st
from PIL import Image

from app_utils.home import (
    cache_proj, cache_stdataholder, gen_globvars, get_default_cfg
)
from app_utils.importer import apply_proj

home = Path(__file__).parents[1]
logo = Image.open(home / "logo.png")

def validate_page():
    st.set_page_config(page_title="Fab Matcher", layout="wide")
    enable_scroll = """
    <style>
    .main {
        overflow: auto;
    }
    </style>
    """
    st.markdown(enable_scroll, unsafe_allow_html=True)    
    with st.sidebar:
        st.image(logo)
    if "exit" in st.session_state:
        if st.session_state["exit"]:
            st.header("Program closed. Please close browser tab")
            cache_proj.clear()
            cache_stdataholder.clear()
            time.sleep(0.1)
            os._exit(0)
    else:
        cfg = get_default_cfg()
        gen_globvars.clear()
        gen_globvars(cfg)
        proj = cache_proj(st.session_state)
        stdataholder = cache_stdataholder(st.session_state)
        apply_proj(proj, stdataholder)
        