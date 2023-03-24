from pathlib import Path
from inspect import getmembers, isfunction
from importlib import import_module
import pandas as pd
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import pearsonr
import plotly.express as px
import plotly.graph_objs as go

from fabmatch import CAN_SPATIAL

from .common import displaykey


def resplot(df, vars, standardize=False, compare=None):
    dk = {**displaykey("Schools"), **displaykey("Teachers")}
    vars, aggvars = [*zip(*[(v + "$" if "$" not in v else v).split("$") for v in vars])]
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
                st.plotly_chart(px.bar(out))
            else:
                fig = go.Figure()
                fig.add_trace(
                    go.Histogram(
                        x=vals,
                        name=f"After",
                        marker=dict(color="cornflowerblue"),
                        nbinsx=25,
                    )
                )
                if compare is not None:
                    cvals = compare[var]
                    fig.add_trace(
                        go.Histogram(
                            x=cvals,
                            name=f"Before",
                            marker=dict(color="indianred"),
                        )
                    )
                st.plotly_chart(fig)

@st.cache
def gen_download(df):
    if df is None:
        return ""
    df = df.to_df() if CAN_SPATIAL else df
    return df.to_csv(index=False).encode("utf-8")


def gen_map(redf, **skwargs):
    cm = skwargs.pop("colormap")
    ccs = getattr(px.colors.sequential, cm, None)
    if ccs is not None:
        skwargs["color_continuous_scale"] = ccs
    sk = skwargs.get("sizekey", None)
    df = redf.to_df()
    if sk is not None:
        df = df.sort_values(by=sk, ascending=True).reset_index(drop=True)
    fig = px.scatter(df, y="lat", x="lon", **skwargs)
    fig.update_layout(
        autosize=False,
        width=600,
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar_title_text='',
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig)


def gen_schlteach_after():
    def gper(df):
        return pearsonr(df["puptot"], df["teachtot"]).statistic ** 2

    schl, teach = st.session_state["stdata"].values()
    outs = st.session_state["outs"].to_df()
    outt = st.session_state["outt"].to_df()
    #######
    oldschl = schl.to_df().rename(columns=displaykey("Schools", invert=True))
    newschl = oldschl.copy()
    nnew = (
        pd.concat(
            (outs.groupby("schoolid")["schoolid"].transform(len), outs["index"]), axis=1
        )
        .drop_duplicates("index")
        .set_index("index")
        .sort_index()
    )
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
