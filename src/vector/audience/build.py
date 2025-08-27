import pandas as pd
from ..utils import round_robin_by_group

def select_seeds(scores_df: pd.DataFrame, issue: str, k: int, diverse: bool = True) -> pd.DataFrame:
    df = scores_df[scores_df["issue"] == issue].sort_values("score", ascending=False).copy()
    if not diverse:
        return df.head(k).reset_index(drop=True)
    rows = df.to_dict("records")
    picked = round_robin_by_group(rows, group_fn=lambda r: r.get("community",-1), k=k)
    return pd.DataFrame(picked)

def build_audience(seeds: pd.DataFrame, edges: pd.DataFrame) -> pd.DataFrame:
    seed_ids = set(seeds["user_id"].astype(str).tolist())
    aud_edges = edges[edges["dst_user_id"].astype(str).isin(seed_ids)]
    audience_user_ids = aud_edges["src_user_id"].astype(str).unique().tolist()
    return pd.DataFrame({"audience_user_id": audience_user_ids})
