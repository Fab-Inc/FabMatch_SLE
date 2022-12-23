import streamlit as st
import yaml

from app_utils.settings import rpt_tabs
from app_utils.home import gen_rptdict
from app_utils.common import show_filters, displaykey
from app_utils.importer import set_intercols

########################
########################
st.set_page_config(page_title="Fab Matcher")
enable_scroll = """
<style>
.main {
    overflow: auto;
}
</style>
"""
st.markdown(enable_scroll, unsafe_allow_html=True)

stdata = st.session_state["stdata"]
intercols = st.session_state["intercols"]
stdatalayout = st.session_state["stdatalayout"]
matcher = st.session_state["matcher"]
vpnames = st.session_state["vpnames"]
srdict = st.session_state["rptdict"]["Schools"]["Rule"]
########################
st.title("Settings")

if not any(val is None for val in stdata.values()):
    for rkey, pkey, ukey in zip(
        ["district", "type"], ["schldistrictp", "schltypep"], ["usedistrictp", "usetypep"]
    ): 
        if rkey not in srdict:
            st.session_state[pkey] = {
                k: 1/len(st.session_state[pkey])
                for k in st.session_state[pkey] 
            }
            st.session_state[ukey] = False
    dk = {
        **displaykey("Schools", invert=True),
        **displaykey("Teachers", invert=True),
    }
    schl, teach = stdata.values()
    home, *schlteach, vp = st.tabs(["Overview", *stdatalayout, "Valid Pairs"])
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

    if st.sidebar.button("Reset Settings"):
        set_intercols(*st.session_state["stdata"].values())
        st.session_state["rptdict"] = gen_rptdict()
        st.session_state["proj"]["rptdict"] = st.session_state["rptdict"]
        st.session_state["usedistrictp"] = False
        st.session_state["usetypep"] = False
        st.experimental_rerun()

    ########################
    tc = home.number_input("Total Cap", min_value=0)
    if home.button("Set cap"):
        st.session_state["rptdict"]["Total Cap"] = tc

    ########################
    with home:
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
    
    st.session_state["proj"]["rptdict"] = st.session_state["rptdict"]

else:
    st.write("Please import data before attempting to set match settings")
