import copy

import streamlit as st

from .common import (
    dataselector,
    proportional_sliderset,
    dynamic_checkbox,
    update_proportions,
    displaykey,
    show_filters,
    show_ordered_list
)
from .home import gen_rptdict, cache_proj
from .importer import set_intercols

################################################
################################################
def settings_advanced():
    stdatalayout = st.session_state["stdatalayout"]
    vpnames = st.session_state["vpnames"]
    stdata = st.session_state["stdata"]
    intercols = st.session_state["intercols"]
    dk = {
        **displaykey("Schools", invert=True),
        **displaykey("Teachers", invert=True),
    }
    #######################
    home, *schlteach, vp = st.tabs(["Overview", *stdatalayout, "Valid Pairs"])
    with home:
        home_tab()
    for tab, (name, datadict) in zip(schlteach, stdatalayout.items()):
        with tab:
            rpt_tabs(name, datadict, stdata)
    with vp:
        col1, col2 = st.columns(2)
        with col1:
            option = st.selectbox("Rule", vpnames)
        with col2:
            if option == "Match Key":
                option2 = [dk[o] for o in st.multiselect("Key", intercols)]
            elif option == "Radius":
                option2 = st.number_input("Radius (km)", min_value=0.0, step=0.1)
        if st.button("Add pairing rule", disabled=(not option2)):
            st.session_state["rptdict"]["Valid Pairs"][option] = option2

################################################
################################################
def settings_simple():
    set_cap(st.session_state["simple_rptdict"])
    dk = {
        **displaykey("Schools"),
        **displaykey("Teachers"),
    }
    schl, teach = st.session_state["stdata"].values()
    if st.session_state["simple_quallist"] is None:
        st.session_state["simple_quallist"] = sorted(teach[dk["qual"]].unique())
    if st.session_state["simple_genderlist"] is None:
        st.session_state["simple_genderlist"] = sorted(teach[dk["gender"]].unique())
    rptdict = st.session_state["simple_rptdict"]
    rptdict["Teachers"]["Tiebreak"] = {}
    rptdict["Valid Pairs"] = {}
    #############
    st.markdown("---")
    dynamic_checkbox(
        "simple_WBrule_district",
        label="Distribute assignments between districts based on their relative need",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_WBrule_district"]
    )
    dynamic_checkbox(
        "simple_WBrule_type",
        label="Distribute assignments between school types based on their relative pupil counts",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_WBrule_type"]
    )
    if st.session_state["simple_WBrule_district"] and st.session_state["simple_WBrule_type"]:
        rptdict["Schools"]["Rule"]["usefunc"] = "WB_rules.ruleschl"
    elif st.session_state["simple_WBrule_district"]:
        rptdict["Schools"]["Rule"]["usefunc"] = "WB_rules.ruleschldistr"
    elif st.session_state["simple_WBrule_type"]:
        rptdict["Schools"]["Rule"]["usefunc"] = "WB_rules.ruleschltype"
    #############
    st.markdown("---")
    dynamic_checkbox(
        "simple_limit",
        label="Limit possible matches based on teacher's current school",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_limit"]
    )
    if st.session_state["simple_limit"]:
        _, col = st.columns([1,8])
        with col:
            dynamic_checkbox(
                "simple_limit_sameschl",
                label="Teacher must already work at same school",
                rerun_internal=True,
                matched_checkboxes=["simple_limit_radius"],
                help=st.session_state["tt"]["simple_limit_radius"]
            )
            if st.session_state["simple_limit_sameschl"]:
                rptdict["Valid Pairs"]["Match Key"] = "schoolid"
            dynamic_checkbox(
                "simple_limit_radius",
                label="Teacher can work at a different school of the same type within radius of school",
                rerun_internal=True,
                matched_checkboxes=["simple_limit_sameschl"],
                help=st.session_state["tt"]["simple_limit_radius"]
            )
            if st.session_state["simple_limit_radius"]:
                rad = st.number_input("Radius (km)", value=5.0, min_value=0.0, step=0.1)
                rptdict["Valid Pairs"]["Radius"] = rad
                rptdict["Valid Pairs"]["Match Key"] = "type"
    #############
    st.markdown("---")
    dynamic_checkbox(
        "simple_salsrc",
        label="Only consider teachers not currently on government salary",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_salsrc"]
    )
    if st.session_state["simple_salsrc"]:
        rptdict["Teachers"]["Rule"]["salsrc"] = [["Government", 0]]
    else:
        rptdict["Teachers"]["Rule"].pop("salsrc", None)
    #############
    dynamic_checkbox(
        "simple_qual",
        label="Prefer teachers by qualification",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_qual"]
    )
    if st.session_state["simple_qual"]:
        show_ordered_list("simple_quallist", indent=2)
        rptdict["Schools"]["Pref"]["qual"] = st.session_state["simple_quallist"]
    #############
    dynamic_checkbox(
        "simple_gender",
        label="Tiebreak teachers by gender",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_gender"]
    )
    if st.session_state["simple_gender"]:
        show_ordered_list("simple_genderlist", indent=2)
        rptdict["Teachers"]["Tiebreak"]["gender"] = st.session_state["simple_genderlist"]
    #############
    dynamic_checkbox(
        "simple_years",
        label="Tiebreak teachers by experience",
        rerun_internal=True,
        help=st.session_state["tt"]["simple_years"]
    )
    if st.session_state["simple_years"]:
        rptdict["Teachers"]["Tiebreak"]["years"] = None
        
    

################################################
################################################
def home_tab():
    set_cap(st.session_state["rptdict"])
    st.markdown("---")
    st.header("Current settings")
    c1 = st.container()
    c2 = st.container()
    for key, sdict in st.session_state["rptdict"].items():
        if isinstance(sdict, dict):
            with c2.expander(key):
                if sdict:
                    for key_, sdict_ in sdict.items():
                        if isinstance(sdict_, dict):
                            st.write(f"##### {key_}")
                            show_filters(sdict_, f"{key} {key_}")
                        else:
                            show_filters(sdict, f"{key} {key_}")
                            break
                else:
                    st.write(sdict)
        else:
            with c1.expander("General"):
                show_filters({key: sdict}, key, st.session_state["rptdict"])

################################################
################################################
def rpt_tabs(parentname, datadict, data):
    if parentname == "Schools":
        sdp = st.session_state["schldistrictp"]
        stp = st.session_state["schltypep"]
        srdict = st.session_state["rptdict"]["Schools"]["Rule"]
        usedata = data[datadict["Rule"]]
        districts = sorted(usedata["District"].unique())
        types = sorted(usedata["School type"].unique())
        with st.expander("District constraints", expanded=True):
            val, rr = dynamic_checkbox(
                "usedistrictp",
                label="Use district constraints",
                help=st.session_state["tt"]["use_district_constraints"]
            )
            if val:
                if st.button(
                    "Normalize",
                    key="normalize_d",
                    help=st.session_state["tt"]["normalize"]
                ):
                    update_proportions(sdp)
                proportional_sliderset(districts, sdp, "districts", dynamic_update=False)
                srdict["district"] = [[k, v] for k, v in sdp.items()]
            else: 
                srdict.pop("district", None)
            if rr:
                st.experimental_rerun()
        with st.expander("School type constraints", expanded=True):
            val, rr = dynamic_checkbox(
                "usetypep",
                label="Use school type constraints",
                help=st.session_state["tt"]["use_school_type_constraints"]
            )
            if val:
                if st.button(
                    "Normalize",
                    key="normalize_d",
                    help=st.session_state["tt"]["normalize"]
                ):
                    update_proportions(stp)
                proportional_sliderset(types, stp, "types", dynamic_update=False)
                srdict["type"] = [[k, v] for k, v in stp.items()]
            else:
                srdict.pop("type", None)
            if rr:
                st.experimental_rerun()
    ######################    
    rpt_tab = st.tabs(datadict)
    for tab, (name, key) in zip(rpt_tab, datadict.items()):
        with tab:
            rpt_advanced(parentname, name, data, key)

##########################
def rpt_advanced(parentname, name, data, key):
    if isinstance(key, dict):
        filtkey = key["Filt"]
        key = key[name]
    rptdict = st.session_state["rptdict"]
    fullname = f"{parentname}_{name}"
    filtoption = None
    ########################################
    if name == "Rule": 
        usepreset = st.checkbox(
            "Use preset function",
            key=f"sbr{fullname}",
            help=st.session_state["tt"]["use_preset_function"]
        )
        if usepreset:
            funcslist = st.session_state[f"{name}funcs"]
            funcname = st.selectbox(
                "Function name", funcslist, key=f"sb9{fullname}"
            )
            rpt = funcname
        else:
            option, rpt = dataselector(data, key, fullname)
    else:
        usepreset = False
        option, rpt = dataselector(data, key, fullname)
        if name == "Pref" and st.checkbox(
            f"Filter {parentname} where preference should apply",
            key=f"fspref{fullname}",
            help=st.session_state["tt"]["filter_pref"]
        ):
            filtoption, filtrpt = dataselector(data, filtkey, f"{parentname}_Filt")
    ########################################
    but = st.button(f"Add {fullname}", key=f"b{fullname}")
    if but and (rpt or rpt is None):
        if usepreset:
            rptdict[parentname][name]["usefunc"] = rpt
        elif name == "Rule" and option in rptdict[parentname][name]:
            rptdict[parentname][name][option].extend(rpt)
        elif filtoption is not None:
            rptdict[parentname][name][f"{filtoption}::{option}"] = (filtrpt, rpt)
        else:
            rptdict[parentname][name][option] = rpt
        rpt = ""
        filtoption = None
        st.experimental_rerun()
    if filtoption is not None:
        st.write({f"{filtoption}::{option}": (filtrpt, rpt)})
    else:
        st.write(rpt)

##########################################################
def set_cap(rptdict):
    st.write(f'Total cap: {rptdict["Total Cap"]}')
    with st.expander("Set total cap"):
        tc = st.number_input(
            "New value",
            min_value=0,
            help=st.session_state["tt"]["total_cap"]
        )
        if st.button("Enter new cap"):
            rptdict["Total Cap"] = tc
            st.experimental_rerun()

##########################################################
def pre_settings():
    srdict = st.session_state["rptdict"]["Schools"]["Rule"]
    stdata = st.session_state["stdata"]
    for rkey, pkey, ukey in zip(
        ["district", "type"],
        ["schldistrictp", "schltypep"],
        ["usedistrictp", "usetypep"]
    ): 
        if rkey not in srdict:
            st.session_state[pkey] = {
                k: 1/len(st.session_state[pkey])
                for k in st.session_state[pkey] 
            }
            st.session_state[ukey] = False
    schl, teach = stdata.values()
    return schl, teach

###########
def post_settings():
    st.markdown("---")
    sett_adv, rr = dynamic_checkbox(
        "sett_adv",
        label="Use Advanced Settings",
        help=st.session_state["tt"]["use_advanced_settings"]
    )
    if rr:
        if sett_adv:
            st.session_state["rptdict"] = copy.deepcopy(
                st.session_state["simple_rptdict"]
            )
        st.experimental_rerun()
    ################################
    if st.sidebar.button("Reset Settings"):
        set_intercols(*st.session_state["stdata"].values())
        st.session_state["rptdict"] = gen_rptdict()
        st.session_state["simple_rptdict"] = gen_rptdict()
        st.session_state["proj"]["rptdict"] = st.session_state["rptdict"]
        st.session_state["usedistrictp"] = False
        st.session_state["usetypep"] = False
        # reset simple settings switches
        for key, val in st.session_state.items():
            if key.startswith("simple_") and isinstance(val, bool):
                st.session_state[key] = False
                st.session_state["proj"][key] = False
        st.session_state["proj"]["sett_adv"] = False
        cache_proj.clear()
        cache_proj(st.session_state)
        st.experimental_rerun()
        
    st.session_state["proj"]["rptdict"] = st.session_state["rptdict"]
    for key, val in st.session_state.items():
        if key.startswith("simple_"):
            st.session_state["proj"][key] = val
    st.session_state["proj"]["sett_adv"] = st.session_state["sett_adv"]
    cache_proj.clear()
    cache_proj(st.session_state)
