from io import StringIO

import streamlit as st
import pandas as pd

from fabmatch import CAN_SPATIAL

if CAN_SPATIAL:
    from fabgis import ResourceDataFrame as ReDF

from .common import displaykey, dataselector, show_filters
from .home import init_matcher, cache_proj, cache_stdataholder

########################
@st.cache
def load_data(file):
    return pd.read_csv(file)


def schlteach(name):
    stdataholder = st.session_state["stdataholder"]
    stdata = st.session_state["stdata"]
    file = st.file_uploader(f"Choose {name} file", type=["csv"])
    if st.button(
        "Read columns",
        disabled=(file is None),
        key=f"i{name}",
        help=st.session_state["tt"]["read_columns"]
    ):
        stdataholder[name] = pd.read_csv(file, low_memory=False)
        cache_stdataholder.clear()
        cache_stdataholder(st.session_state)
    if stdataholder[name] is not None:
        chooser, options = st.tabs(["Choose Columns", "Extra Options"])
        with chooser:
            if column_chooser(name, stdataholder):
                set_stdata(name)
                rerun()
        if stdata[name] is not None:
            with options:
                option_chooser(name, stdata)
                if st.button(
                    "Apply Options",
                    key=f"b6{name}",
                    help=st.session_state["tt"]["apply_options"]
                ):
                    set_stdata(name, filter=True)
                    rerun()
            st.write("Current data")
            st.dataframe(stdata[name])
            if st.button(
                "Reset data",
                key=f"reset{name}",
                help=st.session_state["tt"]["reset_data"]
            ):
                stdata[name] = None
                rerun()


#################################
def column_chooser(name, data):
    impopt = st.session_state["importoptions"][name]
    datacols = data[name].columns
    optlist = ["", *datacols]
    dk = displaykey(name, extracols=False)
    for key, val in dk.items():
        if key in impopt["usecols"]:
            idx = optlist.index(impopt["usecols"][key])
        else:
            idx = 0
        impopt["usecols"][key] = st.selectbox(
            val,
            optlist,
            idx,
            help=st.session_state["tt"].get("_".join(val.lower().split()), None)
        )
    st.markdown("---")
    
    validextraopt = [opt for opt in optlist if opt not in impopt["usecols"].values()]
    extracolscurr = [opt for opt in impopt.get("extracols", []) if opt in validextraopt]
    impopt["extracols"] = extracolscurr
    extracols = st.multiselect(
        "Additional columns to import",
        validextraopt,
        impopt["extracols"],
        help=st.session_state["tt"]["extracols"],
        key=f"Additional columns to import_{name}"
    )
    if impopt["extracols"] != extracols:
        impopt["extracols"] = extracols
        st.experimental_rerun()
    st.markdown("---")
    
    submitted = st.button(
        "Import",
        disabled=any(not uc for uc in impopt["usecols"].values()),
        key=f"colchoose{name}",
        help=st.session_state["tt"]["import"]
    )
    if submitted:
        return True
    else:
        return False


def option_chooser(key, data):
    impopt = st.session_state["importoptions"][key]
    st.write("Filters")
    show_filters(impopt["filters"], key)
    option, value = dataselector(data, key, f"{key}_")
    if st.button(
        "Add filter",
        disabled=(value is None), key=f"b3{key}",
        help=st.session_state["tt"]["add_filter"]
    ):
        impopt["filters"][option] = value
        rerun()


def set_intercols(schl, teach):
    if not any(val is None for val in (schl, teach)):
        st.session_state["intercols"] = set(schl.columns).intersection(
            set(teach.columns)
        )
        districts = sorted(schl["District"].unique())
        types = sorted(schl["School type"].unique())
        st.session_state["schldistrictp"] = {d: 1/len(districts) for d in districts}
        st.session_state["schltypep"] = {t: 1/len(types) for t in types}
    else:
        st.session_state["intercols"] = None
    init_matcher.clear()
    

#################################
def set_stdata(name, filter=False):
    stdataholder = st.session_state["stdataholder"]
    stdata = st.session_state["stdata"]
    importoptions = st.session_state["importoptions"]
    dk = displaykey(name)
    if stdataholder[name] is None or not importoptions[name]["usecols"]:
        return
    data = stdataholder[name].rename(
        columns={
            val: dk[key]
            for key, val in importoptions[name]["usecols"].items()
        }
    )[list(dk.values())]
    
    if filter:
        for filtn, filtv in importoptions[name]["filters"].items():
            query = "|".join(
                f"`{dk[filtn]}` == "
                + (f"'{fv}'" if isinstance(fv, str) else f"{fv}")
                for fv in filtv
            )
            data = data.query(query)        

    stdata[name] = (
        ReDF.from_df(data, latlab=dk["lat"], lonlab=dk["lon"])
        .dropna_latlon()
        .reset_index()
        .rename(columns={"index": "global_index"})
    )
    set_intercols(*stdata.values())
    
def rerun():
    st.session_state["proj"]["importoptions"] = st.session_state["importoptions"]
    cache_proj.clear()
    cache_proj(st.session_state)
    st.experimental_rerun()

def apply_proj(proj, stdataholder):
    st.session_state["stdataholder"] = stdataholder
    st.session_state["rptdict"] = proj["rptdict"]
    st.session_state["importoptions"] = proj["importoptions"]
    for name in proj["importoptions"]:
        set_stdata(name, True)
    for key, val in proj.items():
        if key.startswith("simple_"):
            st.session_state[key] = val
    st.session_state["proj"] = proj