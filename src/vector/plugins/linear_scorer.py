from typing import Dict, Union
import pandas as pd
import numpy as np
from ..utils import minmax_scale

class LinearScorer:
    def __init__(self, weights: Union[Dict[str, float], None] = None, min_samples_for_eng: int = 3, epsilon: float = 1e-9):
        self.weights = weights or {"reach":0.35,"engagement":0.25,"centrality":0.25,"salience":0.15}
        self.min_samples_for_eng = min_samples_for_eng
        self.epsilon = epsilon

    def score(self, users: pd.DataFrame, pagerank: Dict[str,float], communities: Dict[str,int], user_issue_stats: Dict[str, Dict[str, Dict[str, float]]]) -> pd.DataFrame:
        uid_list = [str(u) for u in users["user_id"].tolist()]
        handle_map = {str(r["user_id"]): r["handle"] for _, r in users.iterrows()}
        followers_map = {str(r["user_id"]): int(r.get("followers",0)) for _, r in users.iterrows()}

        reach_vec = np.array([followers_map.get(uid, 0) for uid in uid_list], dtype=float)
        centrality_vec = np.array([pagerank.get(uid, 0.0) for uid in uid_list], dtype=float)
        reach_norm = minmax_scale(reach_vec)
        centrality_norm = minmax_scale(centrality_vec)

        issues = sorted({iss for uid in user_issue_stats for iss in user_issue_stats[uid].keys()})
        results = []
        for issue in issues:
            eng_rate, salience = [], []
            for uid in uid_list:
                stats = user_issue_stats.get(uid, {}).get(issue, {"count":0.0, "eng_sum":0.0})
                cnt = stats["count"]
                eng_sum = stats["eng_sum"]
                followers = max(1.0, float(followers_map.get(uid, 1)))
                if cnt >= self.min_samples_for_eng:
                    eng_rate.append( (eng_sum / cnt) / followers )
                else:
                    eng_rate.append( 0.0 )
                total_issue_mentions = sum(v.get("count",0.0) for v in user_issue_stats.get(uid, {}).values())
                sal = (cnt / (total_issue_mentions + self.epsilon)) if total_issue_mentions > 0 else 0.0
                salience.append(sal)

            eng_norm = minmax_scale(eng_rate)
            sal_norm = minmax_scale(salience)

            w = self.weights
            score = w["reach"]*reach_norm + w["engagement"]*eng_norm + w["centrality"]*centrality_norm + w["salience"]*sal_norm

            for i, uid in enumerate(uid_list):
                results.append({
                    "user_id": uid,
                    "handle": handle_map.get(uid, ""),
                    "issue": issue,
                    "reach": float(reach_norm[i]),
                    "engagement": float(eng_norm[i]),
                    "centrality": float(centrality_norm[i]),
                    "salience": float(sal_norm[i]),
                    "score": float(score[i]),
                    "community": int(communities.get(uid, -1)) if uid in communities else None
                })
        return pd.DataFrame(results)
