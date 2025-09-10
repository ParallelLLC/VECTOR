from typing import Dict, List, Any
import yaml
import pandas as pd
from collections import defaultdict

def load_taxonomy(path: str) -> Dict[str, List[str]]:
    with open(path, "r") as f:
        y = yaml.safe_load(f)
    issues = y.get("issues", {})
    return {issue: [kw.lower() for kw in kws] for issue, kws in issues.items()}

def tag_posts_by_issue(posts: pd.DataFrame, taxonomy: Dict[str, List[str]]) -> Dict[str, List[str]]:
    idx_to_issues = {}
    for _, row in posts.iterrows():
        text = str(row["text"]).lower()
        matched = []
        for issue, kws in taxonomy.items():
            if any(kw in text for kw in kws):
                matched.append(issue)
        idx_to_issues[str(row["post_id"])] = matched
    return idx_to_issues

def compute_user_issue_stats(posts: pd.DataFrame, post_issue_map: Dict[str, List[str]]) -> Dict[str, Dict[str, Dict[str, float]]]:
    per_user: Dict[str, Dict[str, Dict[str, float]]] = {}
    for _, row in posts.iterrows():
        uid = str(row["user_id"])
        pid = str(row["post_id"])
        issues = post_issue_map.get(pid, [])
        eng = float(row.get("likes",0) + row.get("shares",0) + row.get("comments",0))
        
        if uid not in per_user:
            per_user[uid] = {}
            
        for issue in issues:
            if issue not in per_user[uid]:
                per_user[uid][issue] = {"count": 0.0, "eng_sum": 0.0}
            per_user[uid][issue]["count"] += 1.0
            per_user[uid][issue]["eng_sum"] += eng
    
    return per_user
