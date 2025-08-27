from typing import Dict, Any, Union
import json, os, logging
import pandas as pd
from .ingestion.adapters import load_users, load_edges, load_posts
from .nlp.topics import load_taxonomy, compute_user_issue_stats
from .compliance.policies import assert_non_political, ComplianceError
from .config import AppConfig
from .plugins import load_class
from .logging import configure_logging

log = logging.getLogger("vector.pipeline")

def run_pipeline(users_path: str, edges_path: str, posts_path: str, taxonomy_path: str, out_dir: str, cfg: Union[Dict[str, Any], None]):
    configure_logging("INFO")
    os.makedirs(out_dir, exist_ok=True)

    appcfg = AppConfig(**(cfg or {}))

    users = load_users(users_path)
    edges = load_edges(edges_path)
    posts = load_posts(posts_path)
    taxonomy = load_taxonomy(taxonomy_path)

    if appcfg.compliance.disallow_political_persuasion:
        deny = appcfg.compliance.deny_keywords
        try:
            assert_non_political(list(taxonomy.keys()), deny)
        except ComplianceError as e:
            raise RuntimeError("Compliance check failed for taxonomy/issues. " + str(e))

    # Plugins
    TaggerCls = load_class(appcfg.plugins.tagger)
    CentralityCls = load_class(appcfg.plugins.centrality)
    ScorerCls = load_class(appcfg.plugins.scorer)

    tagger = TaggerCls()
    central = CentralityCls()
    scorer = ScorerCls(weights=appcfg.weights.model_dump(), min_samples_for_eng=appcfg.scoring.min_samples_for_engagement, epsilon=appcfg.scoring.epsilon)

    post_issue_map = tagger.tag_posts_by_issue(posts, taxonomy)
    user_issue_stats = compute_user_issue_stats(posts, post_issue_map)

    pr = central.compute(users, edges)
    comms = central.communities(users, edges)

    scores = scorer.score(users, pr, comms, user_issue_stats)
    scores_path = os.path.join(out_dir, "issue_scores.csv")
    scores.to_csv(scores_path, index=False)

    state = {
        "issues": list(taxonomy.keys()),
        "pagerank": pr,
        "communities": comms,
        "user_meta": users.set_index("user_id").to_dict(orient="index"),
        "post_issue_map": post_issue_map,
        "user_issue_stats": user_issue_stats,
        "config": appcfg.model_dump(),
    }
    state_path = os.path.join(out_dir, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f)

    log.info("pipeline_complete")
    return {"scores_csv": scores_path, "state_json": state_path}

def load_state(state_path: str):
    with open(state_path, "r") as f:
        return json.load(f)

def rank_issue(state: Dict[str, Any], issue: str, top_k: int = 25, diverse: bool = True):
    from .plugins import load_class
    from .plugins.selector import RoundRobinSelector  # default fallback
    from .config import AppConfig

    users = pd.DataFrame([{"user_id": k, **v} for k, v in state["user_meta"].items()])
    pr = state["pagerank"]
    comms = state["communities"]
    user_issue_stats = state["user_issue_stats"]
    cfg = AppConfig(**state.get("config", {}))

    ScorerCls = load_class(cfg.plugins.scorer)
    scorer = ScorerCls(weights=cfg.weights.model_dump(), min_samples_for_eng=cfg.scoring.min_samples_for_engagement, epsilon=cfg.scoring.epsilon)
    scores_df = scorer.score(users, pr, comms, user_issue_stats)

    SelectorCls = load_class(cfg.plugins.selector) if cfg.plugins.selector else RoundRobinSelector
    selector = SelectorCls()
    seeds = selector.select(scores_df, issue=issue, k=top_k, diverse=diverse if cfg.selection.enforce_diversity else False)
    return seeds

def export_audience(seeds_df: pd.DataFrame, edges_path: str):
    from .ingestion.adapters import load_edges
    from .audience.build import build_audience
    edges = load_edges(edges_path)
    return build_audience(seeds_df, edges)
