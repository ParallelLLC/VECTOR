# Vector

**Issue-Conditioned Discovery & Ranking System**

A production-quality data science & engineering pipeline to discover, score, and export influencer audiences by issue. Designed as a clear, auditable baseline for commercial and research use.

**Parallel LLC** - Production-grade influencer discovery and audience analysis.

## What it does

- **Ingestion**: Loads user, graph edges, and posts from CSV/Parquet/JSON.
- **Issue Tagging**: Labels posts by issue using a keyword taxonomy (YAML) and lightweight TF-IDF fallback.
- **Graph & Signals**: Builds follower graph (NetworkX) and computes PageRank & communities.
- **Scoring (per issue)**: Combines normalized reach, engagement, centrality, and issue salience.
- **Diversity Constraint**: Optionally enforces community diversity via round-robin selection by detected communities.
- **Audience Export**: Exports top influencer seeds and their reachable audience (followers) as CSV.
- **Service/CLI**: Typer CLI and FastAPI service to run and query the pipeline.

## Quickstart

```bash
# 1) Create & activate a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2) Install Vector
pip install -e .

# 3) Run the pipeline with example data
make run-pipeline

# 4) Rank influencers for an issue
python -m vector.cli rank-issue \
  --issue cannabis_policy \
  --stateful outputs/state.json \
  --top-k 25 \
  --diverse true \
  --out outputs/cannabis_top25.csv

# 5) Export audience
python -m vector.cli export-audience \
  --issue cannabis_policy \
  --stateful outputs/state.json \
  --seeds outputs/cannabis_top25.csv \
  --edges data/external/edges.csv \
  --out outputs/cannabis_audience.csv

# 6) Start the web service
make run-service
```

## Development

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Clean build artifacts
make clean
```

## Data Integration

Vector supports multiple data sources:

- **CSV/Parquet/JSON**: Traditional data files
- **GDELT**: Global news and events data
- **Reddit**: Social media posts and comments
- **Custom APIs**: Extensible adapter system

### Data Contracts

- **users.csv**: `user_id,handle,followers,following,geo,lang,profession`
- **edges.csv** (directed follower graph): `src_user_id,dst_user_id` (edge means *src follows dst*)
- **posts.csv**: `post_id,user_id,text,likes,shares,comments,ts`
- **taxonomy.yaml**: Issues → list of keywords. Example in `data/external/`.

## Scoring formula (per issue)
```
score = w1·Reach + w2·EngagementRate(issue) + w3·PageRank + w4·IssueSalience(issue)
```
Weights configurable in `config/default.yaml`. All components are min-max scaled with ε-smoothing.

## Compliance & guardrails
- **No political persuasion**: The code and README explicitly restrict usage for targeting voters. See `compliance/policies.py`.
- **Brand-safety**: Basic keyword screens + allowlist/denylist hooks.
- **Diversity**: Community-aware selection to avoid echo chambers.

## Documentation

- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Complete directory layout and organization
- **[GDELT Integration](docs/guides/GDELT_USAGE.md)**: Global news data processing
- **[Reddit Integration](docs/guides/REDDIT_USAGE.md)**: Social media data processing
- **[Reddit Setup](docs/guides/REDDIT_SETUP.md)**: Reddit API configuration

## Dependencies

**Core**: `pandas, numpy, pydantic, pyyaml, typer, fastapi, uvicorn, scikit-learn, networkx`

**Data Sources**: `requests, python-dateutil, praw`

**Development**: `pytest, black, isort, flake8, mypy, pre-commit`

## License

Apache-2.0

---

**Parallel LLC** - Production-grade data analysis and influencer discovery solutions.