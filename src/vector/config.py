from __future__ import annotations
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel

class Weights(BaseModel):
    reach: float = 0.35
    engagement: float = 0.25
    centrality: float = 0.25
    salience: float = 0.15

class ScoringConfig(BaseModel):
    min_samples_for_engagement: int = 3
    epsilon: float = 1e-9

class SelectionConfig(BaseModel):
    enforce_diversity: bool = True
    top_k: int = 25

class ComplianceConfig(BaseModel):
    disallow_political_persuasion: bool = True
    deny_keywords: list[str] = ["vote for", "election", "ballot", "turnout", "register to vote"]
    allow_geos: list[str] = []

class PluginConfig(BaseModel):
    tagger: str = "vector.plugins.keyword:KeywordTagger"
    centrality: str = "vector.plugins.pagerank:PageRankCentrality"
    scorer: str = "vector.plugins.linear_scorer:LinearScorer"
    selector: str = "vector.plugins.selector:RoundRobinSelector"

class AppConfig(BaseModel):
    weights: Weights = Weights()
    scoring: ScoringConfig = ScoringConfig()
    selection: SelectionConfig = SelectionConfig()
    compliance: ComplianceConfig = ComplianceConfig()
    plugins: PluginConfig = PluginConfig()

    @staticmethod
    def from_yaml(path: Optional[str]) -> "AppConfig":
        if path is None:
            return AppConfig()
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return AppConfig(**data)
