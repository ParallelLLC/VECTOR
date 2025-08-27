from typing import Optional, Dict, Any
import pandas as pd

def estimate_uplift(df: pd.DataFrame, treatment_col: str, outcome_col: str, feature_cols: Optional[list] = None) -> Dict[str, Any]:
    treated = df[df[treatment_col]==1]
    control = df[df[treatment_col]==0]
    uplift = treated[outcome_col].mean() - control[outcome_col].mean()
    return {"method": "diff_in_means", "uplift": float(uplift)}
