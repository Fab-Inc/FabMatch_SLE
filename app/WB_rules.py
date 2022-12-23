import pandas as pd
import numpy as np

from WB_utils import CAN_SPATIAL

#################################################################
def ruleschl(schl):
    schl, schl_cap = _common(schl)
    ##########
    type_dist = (
        schl.groupby("type")
        .apply(lambda x: x["puptot"].sum() / schl["puptot"].sum())
    )
    ##########
    treq = (
        pd.concat((schl, schl_cap), axis=1)
        .groupby(["type", "district"])[0]
        .sum()
    ) * type_dist
    ##########
    dquot = treq / treq.sum()
    ##########
    rules = []
    for (t, d), quot in dquot.items():
        filt = (schl["type"] == t) & (schl["district"] == d)
        rules.append((filt.to_numpy(), quot))
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