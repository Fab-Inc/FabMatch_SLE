import streamlit as st
import pandas as pd

from fabmatch import CAN_SPATIAL

if CAN_SPATIAL:
    from fabgis import ResourceDataFrame as ReDF

from .common import displaykey, dataselector, show_filters
from .home import init_matcher

########################
@st.cache
def load_data(file):
    return pd.read_csv(file)


def schlteach(name):
    stdataholder = st.session_state["stdataholder"]
    stdata = st.session_state["stdata"]
    file = st.file_uploader(f"Choose {name} file", type=["csv"])
    if st.button("Read columns", disabled=(file is None), key=f"i{name}"):
        stdataholder[name] = pd.read_csv(file, low_memory=False)
    if stdataholder[name] is not None:
        chooser, options = st.tabs(["Choose Columns", "Extra Options"])
        with chooser:
            if column_chooser(name, stdataholder):
                set_stdata(name)
                rerun()
        if stdata[name] is not None:
            with options:
                option_chooser(name, stdata)
                if st.button("Apply Options", key=f"b6{name}"):
                    set_stdata(name, filter=True)
                    rerun()
            st.write("Current data")
            st.dataframe(stdata[name])
            if st.button("Reset data", key=f"reset{name}"):
                stdata[name] = None
                rerun()


#################################
def column_chooser(name, data):
    impopt = st.session_state["importoptions"][name]
    datacols = data[name].columns
    for key, val in displaykey(name).items():
        optlist = ["", *datacols]
        if key in impopt["usecols"]:
            idx = optlist.index(impopt["usecols"][key])
        else:
            idx = 0
        impopt["usecols"][key] = st.selectbox(val, optlist, idx)
    submitted = st.button(
        "Import",
        disabled=any(not uc for uc in impopt["usecols"].values()),
        key=f"colchoose{name}",
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
    if st.button("Add filter", disabled=(value is None), key=f"b3{key}"):
        impopt["filters"][option] = value
        rerun()


def set_intercols(schl, teach):
    if not any(val is None for val in (schl, teach)):
        st.session_state["intercols"] = set(schl.columns).intersection(
            set(teach.columns)
        )
        districts = schl["District"].unique()
        types = schl["School type"].unique()
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
    st.experimental_rerun()