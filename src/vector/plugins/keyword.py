from typing import Dict, List
import pandas as pd

class KeywordTagger:
    def tag_posts_by_issue(self, posts: pd.DataFrame, taxonomy: Dict[str, List[str]]) -> Dict[str, List[str]]:
        idx_to_issues = {}
        for _, row in posts.iterrows():
            text = str(row["text"]).lower()
            matched = []
            for issue, kws in taxonomy.items():
                if any(kw in text for kw in kws):
                    matched.append(issue)
            idx_to_issues[str(row["post_id"])] = matched
        return idx_to_issues
