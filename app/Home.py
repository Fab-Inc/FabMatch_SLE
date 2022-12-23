import streamlit as st
st.experimental_set_query_params(embed="true")

import yaml
import pandas as pd
import h5py
from io import StringIO
import os
import time

from st_utils import st_stdout, parse_stdout
from app_utils.home import (
    get_default_cfg,
    init_matcher,
    gen_globvars,
    prepare_match,
    gen_download,
    resplot,
    gen_map,
    gen_schlteach_after,
    gen_proj
)
from app_utils.common import displaykey
from app_utils.importer import set_stdata

st.set_page_config(page_title="Fab Matcher")
enable_scroll = """
<style>
.main {
    overflow: auto;
}
</style>
"""
st.markdown(enable_scroll, unsafe_allow_html=True)


cfg = get_default_cfg()
gen_globvars(cfg)
if st.session_state["exit"]:
    st.header("Program closed. Please close browser tab")
    time.sleep(0.1)
    os._exit(0)

schlteach = list(st.session_state["stdata"].values())
if not any(val is None for val in schlteach):
    schl, teach = schlteach
    schl = schl.rename(columns=displaykey("Schools", invert=True))
    teach = teach.rename(columns=displaykey("Teachers", invert=True))
    st.session_state["matcher"] = init_matcher(schl, teach)
rptdict = st.session_state["rptdict"]

st.title("Home")

##########
with st.sidebar:
    c1 = st.container()
    c2 = st.container()
    c3 = st.container()
    with c3.expander("Load project"):
        file = st.file_uploader("Choose file", type=["h5"])
        if st.button("Load", disabled=(file is None)):
            with st.spinner("Loading project"):
                with h5py.File(file, "r") as f:
                    proj = yaml.safe_load(f["proj"].asstr()[()])
                    for name in proj["importoptions"]:
                        file = StringIO(f[name].asstr()[()])
                        st.session_state["stdataholder"][name] = pd.read_csv(
                            file, low_memory=False
                        )
                st.session_state["rptdict"] = proj["rptdict"]
                st.session_state["importoptions"] = proj["importoptions"]
                st.session_state["proj"] = proj
                for name in proj["importoptions"]:
                    set_stdata(name, True)
            st.experimental_rerun()
    with c3.expander("Save project"):
        if st.button("Generate project data"):
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
    if c3.button("Exit"):
        st.session_state["exit"] = True
        print(st.session_state["exit"])
        st.experimental_rerun()
    if c2.button("Reset match"):
        init_matcher.clear()
        st.session_state["outt"] = None
        st.session_state["outs"] = None
        st.session_state["matcher"] = None
        st.experimental_rerun()
    if c1.button(
        "Run match",
        disabled=(
            st.session_state["matcher"] is None
            or "Total Cap" not in st.session_state["rptdict"]
            or st.session_state["rptdict"]["Total Cap"] is None
        )
    ):
        with st.spinner("Preparing match"):
            time.sleep(0.1)
            prepare_match(st.session_state["matcher"], rptdict)
        with st.spinner("Matching"):
            time.sleep(0.1)
            with st_stdout("progress", parse_stdout(rptdict["Total Cap"])):
                outs, outt = st.session_state["matcher"].match(-1)
            st.session_state["outs"] = outs
            st.session_state["outt"] = outt

##########################
outs = st.session_state["outs"]
if outs is not None:
    outsneed = st.session_state["matcher"].caps["asker_cap"][outs["index"]]
outt = st.session_state["outt"]
results, graphs, befaft, maps = st.tabs(["Results", "Graphs", "Before / After", "Maps"])
with results:
    stnames = ["Schools", "Teachers"]
    school, teach = st.tabs(stnames)
    for tab, df, name in zip([school, teach], [outs, outt], stnames):
        with tab:
            if df is not None:
                df = df.drop(columns="index")
                st.dataframe(df)
            file = st.download_button(
                f"Export {name} results",
                gen_download(df),
                disabled=(df is None),
                mime="text/csv",
            )
with graphs:
    if outt is not None:
        # teacher characteristics of result
        st.write("Teacher characteristics of result:\n")
        vars = ["qual", "gender", "years", "type"]
        resplot(outt, vars)
    if outs is not None:
        # school characteristics of result
        st.write("School characteristics of result:\n")
        vars = ["district"]
        resplot(outs, vars)
with befaft:
    if outs is not None:
        newschl, newteach, oldschl, oldteach, newgper, oldgper = gen_schlteach_after()
        st.metric("GPE R Squared", newgper.round(3), (newgper - oldgper).round(3))
        vars = ["qual", "gender", "years", "type"]
        resplot(newteach, vars, True, compare=oldteach)
        vars = ["district$teachtot"]
        resplot(newschl, vars, True, compare=oldschl)
with maps:
    if outs is not None:
        useouts = outs.copy()
        # school characteristics of result
        outsassigned = outs.groupby("schoolid")["schoolid"].transform(len)
        st.write(f"Average need of assigned: {outsneed.mean()}")
        useouts["Need"] = outsneed
        useouts["Received"] = outsassigned
        tnames = ["Need", "Received"]
        for tab, name in zip(st.tabs(tnames), tnames):
            with tab:
                gen_map(
                    useouts, sizekey=name, colorkey=name, scale=50, colormap="plasma"
                )
