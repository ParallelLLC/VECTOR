import pandas as pd

def load_users(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"user_id","handle"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"users missing columns: {missing}")
    for col, default in [("followers",0),("following",0),("geo",""),("lang",""),("profession","")]:
        if col not in df.columns:
            df[col] = default
    return df

def load_edges(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"src_user_id","dst_user_id"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"edges missing columns: {missing}")
    return df

def load_posts(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"post_id","user_id","text"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"posts missing columns: {missing}")
    for col in ["likes","shares","comments"]:
        if col not in df.columns:
            df[col] = 0
    if "ts" not in df.columns:
        df["ts"] = ""
    return df
