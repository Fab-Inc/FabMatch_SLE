import streamlit as st
import yaml

from .common import dataselector, proportional_sliderset, dynamic_checkbox

################################################
################################################
def rpt_tabs(parentname, datadict, data):
    if parentname == "Schools":
        sdp = st.session_state["schldistrictp"]
        stp = st.session_state["schltypep"]
        srdict = st.session_state["rptdict"]["Schools"]["Rule"]
        usedata = data[datadict["Rule"]]
        districts = usedata["District"].unique()
        types = usedata["School type"].unique()
        with st.expander("District constraints"):
            val, rr = dynamic_checkbox("usedistrictp", label="Use district constraints")
            if val:
                proportional_sliderset(districts, sdp, "districts")
                srdict["district"] = [[k, v] for k, v in sdp.items()]
            else: 
                srdict.pop("district", None)
            if rr:
                st.experimental_rerun()
        with st.expander("School type constraints"):
            val, rr = dynamic_checkbox("usetypep", label="Use school type constraints")
            if val:
                proportional_sliderset(types, stp, "types")
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
    rptdict = st.session_state["rptdict"]
    fullname = f"{parentname}_{name}"
    ########################################
    usepreset = st.checkbox(
        "Use preset function", key=f"sbr{fullname}"
    )
    if usepreset:
        funcslist = st.session_state[f"{name}funcs"]
        funcname = st.selectbox(
            "Function name", funcslist, key=f"sb9{fullname}"
        )
        rpt = funcname
    else:
        option, rpt = dataselector(data, key, fullname)
    ########################################
    but = st.button(f"Add {fullname}", key=f"b{fullname}")
    if but and (rpt or rpt is None):
        if usepreset:
            rptdict[parentname][name]["usefunc"] = rpt
        elif name == "Rule" and option in rptdict[parentname][name]:
                rptdict[parentname][name][option].extend(rpt)
        else:
            rptdict[parentname][name][option] = rpt
        rpt = ""
    st.write(rpt)

