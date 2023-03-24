from pathlib import Path
from inspect import getmembers, isfunction
from importlib import import_module
import copy
from io import BytesIO
import time

import streamlit as st
import h5py
import yaml

from ogutils import ContextMap

from fabmatch import Matcher, CAN_SPATIAL
from fabmatch.utils import format_settings
from WB_utils import load_data as load_data_
from WB_rules import simpleschl

from .common import gen_yaml

home = Path(__file__).resolve().parents[1]

stdatalayout = {
    "Schools": {
        "Rule": "Schools",
        "Pref": {"Pref": "Teachers", "Filt": "Schools"},
        "Tiebreak": "Schools",
    },
    "Teachers": {
        "Rule": "Teachers",
        "Pref": {"Pref": "Schools", "Filt": "Teachers"},
        "Tiebreak": "Teachers",
        "PrefFilt": "Teachers",
    },
}
vpnames = ["Match Key", "Radius"]
importoptions = {"usecols": {}, "extracols": [], "filters": {}}
rptdict = {"Rule": {}, "Pref": {}, "Tiebreak": {}}
proj = {"importoptions": None, "rptdict": None, "csv": {}}

################################################
################################################
def prepare_match(matcher, cfg):
    usecfg = format_settings(
        cfg, st.session_state["stdatalayout"], st.session_state["vpnames"]
    )
    # force district and type rules to sum to 1 if using the constraints interface
    for rulekey in ["district", "type"]:
        if rulekey in usecfg["rule_schl"] and st.session_state[f"use{rulekey}p"]:
            sumv = sum(v for _, v in usecfg["rule_schl"][rulekey])
            for kv in usecfg["rule_schl"][rulekey]:
                kv[1] = kv[1] / sumv
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
        **{"Valid Pairs": {}, "Total Cap": 0},
    }


@st.experimental_singleton
def gen_globvars(cfg):
    with open(home / "tooltips.yaml") as f:
        tt = yaml.safe_load(f)
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
        "simple_rptdict": gen_rptdict(),
        "matcher": None,
        "stdatalayout": stdatalayout,
        "stdata": {key: None for key in stdatalayout},
        "stdataholder": {key: None for key in stdatalayout},
        "importoptions": {key: copy.deepcopy(importoptions) for key in stdatalayout},
        # dynamic switches
        "usedistrictp": False,
        "usetypep": False,
        "sett_adv": False,
        "simple_qual": False,
        "simple_gender": False,
        "simple_years": False,
        "simple_salsrc": False,
        "simple_limit": False,
        "simple_limit_radius": True,
        "simple_limit_sameschl": False,
        "simple_WBrule_district": False,
        "simple_WBrule_type": False,
        #
        "simple_quallist": None,
        "simple_genderlist": None,
        #
        "tt": tt,
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
        "exit": False,
    }
    for gvn, gvv in globvars.items():
        if gvn not in st.session_state:
            st.session_state[gvn] = gvv
    st.session_state["proj"]["importoptions"] = st.session_state["importoptions"]
    st.session_state["proj"]["rptdict"] = st.session_state["rptdict"]
    time.sleep(0.1)


@st.experimental_memo(persist="disk")
def cache_proj(_session_state):
    proj = _session_state["proj"]
    return proj


@st.experimental_memo(persist="disk")
def cache_stdataholder(_session_state):
    stdataholder = _session_state["stdataholder"]
    return stdataholder


############################################
############################################


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
