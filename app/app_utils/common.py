from collections import defaultdict
from itertools import chain

import numpy as np
import streamlit as st
import yaml

def show_filters(fdict, key, remdict=None):
    dk = {**displaykey("Schools"), **displaykey("Teachers")}
    filts = fdict.copy()
    for filtn, filtv in filts.items():
        pname = dk[filtn] if filtn in dk else filtn
        if isinstance(filtv, str) and filtv in dk:
            filtv = dk[filtv]
        elif isinstance(filtv, list):
            filtv = [dk[fv] if isinstance(fv, str) and fv in dk else fv for fv in filtv]
        c1, c2 = st.columns(2)
        with c1:
            if not isinstance(filtv, dict):
                st.write({pname: filtv})
            else:
                st.write(rf"###### {pname}")
                st.write(filtv)
        with c2:
            if st.button("Remove", key=f"rem{key}{filtn}"):
                if remdict is None:
                    fdict.pop(filtn)
                else:
                    remdict[filtn] = None
                st.experimental_rerun()


def displaykey(name, invert=False):
    cfg = st.session_state["cfg"]
    return {
        key if not invert else val: val if not invert else key
        for key, val in chain(
            cfg["displaykey"][name].items(), cfg["displaykey"]["both"].items()
        )
    }


def dataselector(data, key, fullname=None):
    data_ = data[key].rename(columns=displaykey(key))
    rpt = None
    if fullname is not None:
        _, name = fullname.split("_")
    else:
        name = ""
    col1, col2 = st.columns(2)
    with col1:
        option = st.selectbox(
            f"{key} Attribute", ["", *data_.columns], key=f"o1{fullname}"
        )
    if option:
        column = data_[option]
        with col2:
            if column.dtype in [object, bool] or len(column.unique()) < 3:
                option2 = st.multiselect("Values", column.unique(), key=f"o2{fullname}")
            elif name in ["Rule", ""]:
                range = np.array([column.min(), column.max()]).tolist()
                option2 = [
                    st.slider("Minimum value", *range, range[0]),
                    st.slider("Maximum value", *range, range[1]),
                ]
            if name in ["Rule", ""]:
                invert = st.checkbox("Invert Selection", key=f"cb{fullname}")
            if name == "Rule":
                prop = st.slider("Proportional cap", 0.0, 1.0, 1.0, key=f"sl{fullname}")
                if column.dtype == object:
                    if invert:
                        rpt = [[o, prop] for o in column.unique() if o not in option2]
                    else:
                        rpt = [[o, prop] for o in option2]
                else:
                    if invert:
                        rpt = [
                            [[range[0], option2[0]], prop],
                            [[option2[1], range[1]], prop],
                        ]
                    else:
                        rpt = [option2, prop]
            elif name:
                if column.dtype == object:
                    scores = {
                        o: st.number_input(o, key=f"ni{fullname}_{o}") for o in option2
                    }
                    rpt = defaultdict(list)
                    for key_, score in scores.items():
                        rpt[score].append(key_)
                    rpt = dict(rpt)
            else:
                if invert:
                    rpt = [o for o in column.unique() if o not in option2]
                else:
                    rpt = option2
    option = displaykey(key, invert=True)[option] if option else option
    return option, rpt

def proportional_sliderset(labels, valdict, name):    
    for lab in labels:
        c1 = st.container()
        c2 = st.container()
        wkwargs = dict(
            label=f"{lab}",
            value=valdict[lab]*100,
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            key=f"sllabs{name}{lab}"
        )
        if c2.checkbox("Enter number", key=f"cbdist{name}{lab}"):
            val = c1.number_input(**wkwargs)
        else:
            val = c1.slider(**wkwargs)
        if val != valdict[lab]*100:
            valdict[lab] = val / 100
            update_proportions(valdict, lab)
            st.experimental_rerun()

def update_proportions(pdict, key):
    pval = pdict[key]
    sumrest = sum(v for k, v in pdict.items() if k != key)
    for k in pdict:
        if k != key:
            if sumrest > 1e-6:
                pdict[k] *= (1-pval) / sumrest
            elif pval < 1-1e-6:
                pdict[k] = (1-pval) / (len(pdict) - 1)
    sumall = sum(pdict.values())
    for k in pdict:
        pdict[k] = pdict[k] / sumall

def dynamic_checkbox(onkey, **kwargs):
    kwargs["value"] = st.session_state[onkey]
    val = st.checkbox(**kwargs)
    if val != st.session_state[onkey]:
        rr = True
        st.session_state[onkey] = val
    else:
        rr = False
    return val, rr

########################
def gen_yaml(outd):
    def check_vals(d):
        outd = d.copy()
        for k, v in d.items():
            if isinstance(v, dict):
                outd[k] = check_vals(v)
            elif isinstance(v, list):
                outd[k] = list(
                    check_vals({i: v for i, v in enumerate(v)}).values()
                )
            elif isinstance(v, np.int64):
                outd[k] = int(v)
            elif isinstance(v, np.float64):
                outd[k] = float(v)
            else:
                outd[k] = v
        return outd
    return yaml.safe_dump(
        {
            key: dict(d) if isinstance(d, dict) else d
            for key, d in check_vals(outd).items()}
    )