# Vector (Issue-Conditioned Discovery & Ranking)

A minimal, production-quality pipeline to **discover, score, and export influencer audiences by issue**.
Designed as a clear, auditable baseline for commercial and research use (not electioneering).

> ⚖️ **Use responsibly**: This template is for general marketing, research, and public-interest information campaigns.
> It **must not** be used to target or persuade voters or specific political demographics.

## What it does

- **Ingestion**: Loads user, graph edges, and posts from CSV/Parquet/JSON.
- **Issue Tagging**: Labels posts by issue using a keyword taxonomy (YAML) and lightweight TF-IDF fallback.
- **Graph & Signals**: Builds follower graph (NetworkX) and computes PageRank & communities.
- **Scoring (per issue)**: Combines normalized **reach**, **engagement**, **centrality**, and **issue salience**.
- **Diversity Constraint**: Optionally enforces community diversity via round-robin selection by detected communities.
- **Audience Export**: Exports top influencer **seeds** and their reachable **audience** (followers) as CSV.
- **Service/CLI**: Typer CLI and FastAPI service to run and query the pipeline.

## Quickstart

```bash
# 1) Create & activate a venv (recommended)
python -m venv .venv && source .venv/bin/activate

# 2) Install
pip install -e .

# 3) Run the pipeline on toy data
python -m vector.cli run-pipeline   --users examples/users.csv   --edges examples/edges.csv   --posts examples/posts.csv   --taxonomy examples/taxonomy.yaml   --out ./out

# 4) Rank influencers for an issue with diversity constraint
python -m vector.cli rank-issue   --issue cannabis_policy   --stateful ./out/state.json   --top-k 25   --diverse true   --out ./out/cannabis_top25.csv

# 5) Export audience (followers of the selected seeds)
python -m vector.cli export-audience   --issue cannabis_policy   --stateful ./out/state.json   --seeds ./out/cannabis_top25.csv   --edges examples/edges.csv   --out ./out/cannabis_audience.csv

# 6) (Optional) Serve an API
export VECTOR_STATE_FILE=./out/state.json
export VECTOR_EDGES_FILE=examples/edges.csv
uvicorn vector.service:app --reload
```

## Data contracts

- **users.csv**: `user_id,handle,followers,following,geo,lang,profession`
- **edges.csv** (directed follower graph): `src_user_id,dst_user_id` (edge means *src follows dst*)
- **posts.csv**: `post_id,user_id,text,likes,shares,comments,ts`
- **taxonomy.yaml**: Issues → list of keywords. Example in `examples/`.

## Scoring formula (per issue)
```
score = w1·Reach + w2·EngagementRate(issue) + w3·PageRank + w4·IssueSalience(issue)
```
Weights configurable in `config/default.yaml`. All components are min-max scaled with ε-smoothing.

## Compliance & guardrails
- **No political persuasion**: The code and README explicitly restrict usage for targeting voters. See `compliance/policies.py`.
- **Brand-safety**: Basic keyword screens + allowlist/denylist hooks.
- **Diversity**: Community-aware selection to avoid echo chambers.

## Dependencies
`pandas, numpy, pydantic, pyyaml, typer, fastapi, uvicorn, scikit-learn, networkx`

## License
Apache-2.0