from itertools import product

import pandas as pd
import numpy as np

from WB_utils import CAN_SPATIAL

#################################################################
def ruleschldistr(schl):
    return ruleschl(schl, "district")
def ruleschltype(schl):
    return ruleschl(schl, "type")

def ruleschl(schl, variant="both"):
    schl, schl_cap = _common(schl)
    ##########
    if variant in ["type", "both"]:
        treq = (
            schl.groupby("type")
            .apply(lambda x: x["puptot"].sum() / schl["puptot"].sum())
        )
    ##########
    if variant in ["district", "both"]:
        dreq = (
            pd.concat((schl, schl_cap), axis=1)
            .groupby(["type", "district"])[0]
            .sum()
        )
    rules = []
    if variant == "both":
        dquot = dreq * treq
        dquot = dquot / dquot.sum()
        for (t, d), dq in dquot.items():
            filt = (schl["type"] == t) & (schl["district"] == d)
            rules.append((filt.to_numpy(), dq))
    elif variant == "type":
        tquot = treq / treq.sum()
        for t, tq in tquot.items():
            filt = schl["type"] == t
            rules.append((filt.to_numpy(), tq))
    elif variant == "district":
        dquot = dreq / dreq.sum()
        for (t, d), dq in dquot.items():
            filt = (schl["type"] == t) & (schl["district"] == d)
            rules.append((filt.to_numpy(), dq))
        
    return rules, True, np.ceil(schl_cap).to_numpy().astype(int)

def simpleschl(schl):
    schl, schl_cap = _common(schl)
    return [], True, np.ceil(schl_cap).to_numpy().astype(int)


######################################################
def _common(schl):
    if CAN_SPATIAL:
        schl = schl.to_df()
    ########
    ptr_national = (
        schl.groupby("type")["puptot"].sum() 
        / schl.groupby("type")["teachtot"].sum()
    )
    ptr_target = ptr_national[schl["type"]].reset_index(drop=True)
    schl_cap = np.maximum(
        (schl["puptot"] / ptr_target) - schl["teachtot"], 0
    )
    return schl, schl_cap    