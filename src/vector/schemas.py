from pydantic import BaseModel
from typing import List, Dict, Optional

class User(BaseModel):
    user_id: str
    handle: str
    followers: int = 0
    following: int = 0
    geo: Optional[str] = None
    lang: Optional[str] = None
    profession: Optional[str] = None

class Edge(BaseModel):
    src_user_id: str
    dst_user_id: str

class Post(BaseModel):
    post_id: str
    user_id: str
    text: str
    likes: int = 0
    shares: int = 0
    comments: int = 0
    ts: Optional[str] = None

class IssueScore(BaseModel):
    user_id: str
    handle: str
    issue: str
    reach: float
    engagement: float
    centrality: float
    salience: float
    score: float
    community: Optional[int] = None

class PipelineState(BaseModel):
    issues: List[str]
    pagerank: Dict[str, float]
    communities: Dict[str, int]
    user_meta: Dict[str, Dict]
    post_issue_map: Dict[str, List[str]]
    user_issue_stats: Dict[str, Dict[str, Dict[str, float]]]
