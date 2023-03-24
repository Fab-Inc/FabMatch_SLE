import streamlit as st
st.experimental_set_query_params(embed="true")

from app_utils.results import (
    gen_download,
    resplot,
    gen_map,
    gen_schlteach_after,
)
from app_utils.session import validate_page

validate_page()

st.title("Match Results")
############################################

outs = st.session_state["outs"]
if outs is None:
    st.write("Results will appear here after you run match")
else:
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
            vars = ["qual", "gender", "years"]
            resplot(outt, vars)
        if outs is not None:
            # school characteristics of result
            st.write("School characteristics of result:\n")
            vars = ["district", "type"]
            resplot(outs, vars)
    with befaft:
        if outs is not None:
            newschl, newteach, oldschl, oldteach, newgper, oldgper = gen_schlteach_after()
            st.metric("GPE R Squared", newgper.round(3), (newgper - oldgper).round(3))
            vars = ["qual", "gender", "years"]
            resplot(newteach, vars, True, compare=oldteach)
            vars = ["district$teachtot", "type$teachtot"]
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
                        useouts, size=name, color=name, size_max=8, colormap="Plasma"
                    )
