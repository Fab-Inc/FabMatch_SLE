from io import StringIO
from pathlib import Path

import streamlit as st
st.experimental_set_query_params(embed="true")

import yaml
import pandas as pd
import h5py
import time

from st_utils import st_stdout, parse_stdout
from app_utils.home import (
    init_matcher,
    prepare_match,
    gen_proj,
    cache_proj,
    cache_stdataholder
)
from app_utils.common import displaykey
from app_utils.importer import apply_proj
from app_utils.session import validate_page

here = Path(__file__).parent

validate_page()

schlteach = list(st.session_state["stdata"].values())
if not any(val is None for val in schlteach):
    schl, teach = schlteach
    schl = schl.rename(columns=displaykey("Schools", invert=True))
    teach = teach.rename(columns=displaykey("Teachers", invert=True))
    st.session_state["matcher"] = init_matcher(schl, teach)
if st.session_state["sett_adv"]:
    rptdict = st.session_state["rptdict"]
else:
    rptdict = st.session_state["simple_rptdict"]

st.title("Home")

##########
with st.sidebar:
    c1 = st.container()
    c2 = st.container()
    c3 = st.container()
    c4 = st.container()
    with c3.expander("Load project", expanded=False):
        file = st.file_uploader("Choose file", type=["h5"])
        if st.button("Load", disabled=(file is None)):
            with st.spinner("Loading project"):
                with h5py.File(file, "r") as f:
                    proj = yaml.safe_load(f["proj"].asstr()[()])
                    if "csv" not in proj:
                        proj["csv"] = {}
                    stdataholder = {
                        name: pd.read_csv(
                            StringIO(f[name].asstr()[()]), low_memory=False
                        )
                        for name in proj["importoptions"]
                    }
                apply_proj(proj, stdataholder)
                cache_proj.clear()
                cache_proj(st.session_state)
                cache_stdataholder.clear()
                cache_stdataholder(st.session_state)                
            st.experimental_rerun()
    with c3.expander("Save project", expanded=False):
        if st.button(
            "Generate project data",
            disabled=any(
                val is None for val in st.session_state["stdataholder"].values()
            ),
            help=st.session_state["tt"]["generate_project_data"]
        ):
            st.session_state["home_exstate"] = True
        else:
            st.session_state["home_exstate"] = False
        if st.session_state["home_exstate"]:
            with st.spinner("Generating project..."):
                clicked = st.download_button(
                    "Choose file",
                    gen_proj(),
                    mime="application/x-hdf5",
                )
    with c4:
        st.markdown("---")
        if st.button("Exit"):
            st.session_state["exit"] = True
            st.experimental_rerun()
    if c2.button("Reset match", help=st.session_state["tt"]["reset_match"]):
        init_matcher.clear()
        st.session_state["outt"] = None
        st.session_state["outs"] = None
        st.session_state["matcher"] = None
        st.experimental_rerun()
    if c1.button(
        "Run match",
        disabled=(
            st.session_state["matcher"] is None
            or "Total Cap" not in rptdict
            or rptdict["Total Cap"] is None
        ),
        help=st.session_state["tt"]["run_match"]
    ):
        st.markdown("---")
        with st.spinner("Preparing match"):
            time.sleep(0.1)
            prepare_match(st.session_state["matcher"], rptdict)
        with st.spinner("Matching"):
            time.sleep(0.1)
            with st_stdout("progress", parse_stdout(rptdict["Total Cap"])):
                outs, outt = st.session_state["matcher"].match(-1)
            st.session_state["outs"] = outs
            st.session_state["outt"] = outt

##########
tabnames = ["Overview", "Guide", "Glossary"]

for tab, name in zip(st.tabs(tabnames), tabnames):
    with open(here / f"{name.lower()}.md") as f:
        md = f.read()
    with tab:
        st.markdown(md)