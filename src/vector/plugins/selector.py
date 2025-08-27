import pandas as pd
from ..utils import round_robin_by_group

class RoundRobinSelector:
    def select(self, scores_df: pd.DataFrame, issue: str, k: int, diverse: bool) -> pd.DataFrame:
        df = scores_df[scores_df["issue"] == issue].sort_values("score", ascending=False).copy()
        if not diverse:
            return df.head(k).reset_index(drop=True)
        rows = df.to_dict("records")
        picked = round_robin_by_group(rows, group_fn=lambda r: r.get("community",-1), k=k)
        return pd.DataFrame(picked)
