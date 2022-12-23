import pandas as pd

try:
    import fabgis
    CAN_SPATIAL = True
except:
    CAN_SPATIAL = False
if CAN_SPATIAL:
    from fabgis import ResourceDataFrame as ReDF
from ogutils import ContextMap, dirdict

def standardise_columns(df, coldict):
    return (
        df.rename(columns={
            val: key for key, val in coldict.items()
            if val is not None
        })
        [[key for key, val in coldict.items() if val is not None]]
    )
    

def load_data(cfg):
    paths = dirdict(cfg["paths"])
    def load_df(fname, cfg):        
        if CAN_SPATIAL:
            df = ReDF.read_file(fname, **cfg["load_kwargs"])
        else:
            lkw = {
                key: val for key, val in cfg["load_kwargs"].items()
                if key not in ["lonlab", "latlab"]
            }
            df = pd.read_csv(fname, **lkw)    
        #########
        df = standardise_columns(df, cfg["columns"]).reset_index(drop=True)
        ##
        if cfg["query"] is not None:
            df = df.query(cfg["query"]).reset_index(drop=True)
        return df
    schl = load_df(paths["schlfile"], cfg["schl"])
    teach = load_df(paths["teachfile"], cfg["teach"])
    ######
    if cfg["schl"]["recalc_ttot"]:
        ttot = (
            teach
            .groupby("schoolid")[["schoolid"]]
            .agg(len)
            .rename(columns={"schoolid": "teachtot"})
        ).reset_index()
        schl["teachtot"] = (
            schl[["schoolid"]]
            .merge(how="left", right=ttot, on="schoolid")["teachtot"]
            .fillna(0)
        )
    ######
    return schl, teach