from pathlib import Path
from inspect import getmembers, isfunction
from importlib import import_module
import copy
from io import BytesIO
import time

import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
import numpy as np
from scipy.stats import pearsonr
import h5py
import yaml

from ogutils import ContextMap

from fabmatch import Matcher, CAN_SPATIAL
from fabmatch.utils import format_settings
from WB_utils import load_data as load_data_
from WB_rules import simpleschl

from .common import displaykey, gen_yaml

home = Path(__file__).resolve().parents[1]

stdatalayout = {
    "Schools": {
        "Rule": "Schools", "Pref": "Teachers", "Tiebreak": "Schools"
    },
    "Teachers": {
        "Rule": "Teachers", "Pref": "Schools", "Tiebreak": "Teachers"
    }
}
vpnames = ["Match Key", "Radius"]
importoptions = {
    "usecols": {},
    "filters": {}
}
rptdict = {"Rule": {}, "Pref": {}, "Tiebreak": {}}
proj = {
    "importoptions": None,
    "rptdict": None
}

################################################
################################################
def prepare_match(matcher, cfg):
    usecfg = format_settings(
        cfg, st.session_state["stdatalayout"], st.session_state["vpnames"]
    )
    matcher.prepare_match(usecfg)
    if "usefunc" not in usecfg["rule_schl"]:
        _, _, schl_cap = simpleschl(matcher.asker)
        matcher.caps["asker_cap"] = schl_cap

############################################
############################################

@st.experimental_singleton
def get_default_cfg(context=""):
    return ContextMap(home / "cfg")[context]
    
@st.experimental_singleton
def load_data(cfg):
    schl, teach = load_data_(cfg)
    intercols = set(schl.columns).intersection(set(teach.columns))
    return schl, teach, intercols

@st.experimental_singleton
def init_matcher(_schl, _teach):
    return Matcher(_schl, _teach)    

def gen_rptdict():
    return {
        **{key: copy.deepcopy(rptdict) for key in stdatalayout},
        **{"Valid Pairs": {}, "Total Cap": None}
    }

@st.cache
def gen_globvars(cfg):
    modname = "WB_rules"
    rulefuncmod = import_module(modname)
    rulefuncs = [
        ".".join((modname, f[0]))
        for f in getmembers(rulefuncmod, isfunction)
        if not f[0].startswith("_")
    ]
    globvars = {
        "cfg": cfg,
        "rptdict": gen_rptdict(),
        "matcher": None,
        "stdatalayout": stdatalayout,
        "stdata": {key: None for key in stdatalayout},
        "stdataholder": {key: None for key in stdatalayout},
        "importoptions": {key: copy.deepcopy(importoptions) for key in stdatalayout},
        "intercols": None,
        "vpnames": vpnames,
        "outt": None,
        "outs": None,
        "Rulefuncs": rulefuncs,
        "Preffuncs": [None],
        "Tiebreakfuncs": [None],
        "proj": proj,
        "home_exstate": False,
        "schldistrictp": None,
        "schltypep": None,
        "usedistrictp": False,
        "usetypep": False,
        "exit": False
    }
    for gvn, gvv in globvars.items():
        if gvn not in st.session_state:
            st.session_state[gvn] = gvv
    st.session_state["proj"]["importoptions"] = st.session_state["importoptions"]
    st.session_state["proj"]["rptdict"] = st.session_state["rptdict"]
    time.sleep(0.1)


############################################
############################################

def resplot(df, vars, standardize=False, compare=None):
    dk = {**displaykey("Schools"), **displaykey("Teachers")}
    vars, aggvars = [*zip(*[(v+"$" if "$" not in v else v).split("$") for v in vars])]
    tabs = st.tabs([dk[v] for v in vars])
    for tab, var, avar in zip(tabs, vars, aggvars):
        with tab:
            vals = df[var]
            if vals.dtype == object:
                if avar:
                    out = df.groupby(var)[avar].agg(sum)
                    if standardize:
                        out /= df[avar].sum()
                        if compare is not None:
                            cout = compare.groupby(var)[avar].agg(sum)
                            out -= cout / compare[avar].sum()
                else:
                    out = df.groupby(var)[var].agg(len)
                    if standardize:
                        out /= len(df)
                        if compare is not None:
                            cout = compare.groupby(var)[var].agg(len)
                            out -= cout / len(compare)
                out.index.rename("index", inplace=True)
                out = out.replace(dk)
                st.bar_chart(out)
            else:
                fig, ax = plt.subplots()
                fig.patch.set_facecolor([0,0,0,0])
                ax.patch.set_facecolor([0,0,0,0])
                ax.tick_params(colors=[1,1,1,1])
                ax.hist(vals)
                st.pyplot(fig)

@st.cache
def gen_download(df):
    if df is None:
        return ""
    df = df.to_df() if CAN_SPATIAL else df
    return df.to_csv(index=False).encode("utf-8")

def gen_map(redf, **skwargs):
    fig, ax = plt.subplots(figsize=(10,10))
    fig.patch.set_facecolor("black")
    ax.patch.set_facecolor("black")
    redf.scatter(ax=ax, **skwargs)
    st.pyplot(fig)

def gen_schlteach_after():
    def gper(df):
        return pearsonr(df["puptot"], df["teachtot"]).statistic ** 2
    schl, teach = st.session_state["stdata"].values()
    outs = st.session_state["outs"].to_df()
    outt = st.session_state["outt"].to_df()
    #######
    oldschl = schl.to_df().rename(columns=displaykey("Schools", invert=True))
    newschl = oldschl.copy()
    nnew = pd.concat(
        (outs.groupby("schoolid")["schoolid"].transform(len), outs["index"]),
        axis=1
    ).drop_duplicates("index").set_index("index").sort_index()
    newschl.loc[nnew.index, "teachtot"] += nnew["schoolid"]
    # newschl = newschl.rename(columns=displaykey("Schools"))
    ######
    oldteach = teach.to_df().rename(columns=displaykey("Teachers", invert=True))
    newteach = oldteach.copy()
    bothkey = list(st.session_state["cfg"]["displaykey"]["both"])
    repteach = outs.copy()
    repteach["index"] = outt["index"]
    repteach = repteach.set_index("index")[bothkey]
    newteach.loc[repteach.index, bothkey] = repteach
    newteach.loc[repteach.index, "salsrc"] = "Government"
    ######
    newteach = newteach.query("salsrc == 'Government'")
    oldteach = oldteach.query("salsrc == 'Government'")
    # newteach = newteach.rename(columns=displaykey("Teachers"))
    newgper = gper(newschl)
    oldgper = gper(oldschl)
    return newschl, newteach, oldschl, oldteach, newgper, oldgper

def gen_proj():
    yamstr = gen_yaml(st.session_state["proj"])
    csvs = {
        name: df.to_csv() if df is not None else None
        for name, df in st.session_state["stdataholder"].items()
    }
    outf = BytesIO()
    with h5py.File(outf, "w") as f:
        f["proj"] = yamstr
        for name, val in csvs.items():
            f[name] = val
    outf.seek(0)
    return outf