import pandas as pd
import networkx as nx
from typing import Dict

def build_graph(users: pd.DataFrame, edges: pd.DataFrame) -> nx.DiGraph:
    G = nx.DiGraph()
    for _, u in users.iterrows():
        G.add_node(str(u["user_id"]), handle=u["handle"], followers=int(u.get("followers",0)))
    for _, e in edges.iterrows():
        G.add_edge(str(e["src_user_id"]), str(e["dst_user_id"]))
    return G

def compute_pagerank(G: nx.DiGraph) -> Dict[str, float]:
    if len(G) == 0:
        return {}
    try:
        pr = nx.pagerank(G, alpha=0.85)
    except Exception:
        pr = {n: 1.0/len(G) for n in G.nodes()}
    return pr

def compute_communities(G: nx.DiGraph) -> Dict[str, int]:
    UG = G.to_undirected()
    if len(UG) == 0:
        return {}
    comms = list(nx.algorithms.community.greedy_modularity_communities(UG))
    node_to_comm = {}
    for i, cset in enumerate(comms):
        for n in cset:
            node_to_comm[str(n)] = i
    return node_to_comm
