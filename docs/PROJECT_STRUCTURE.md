# Vector Project Structure

This document outlines the professional-grade directory structure for the Vector project by Parallel LLC.

## Overview

Vector is an issue-conditioned discovery and ranking system designed for influencer audience identification and analysis.

## Directory Structure

```
vector/
├── .github/                    # GitHub workflows and templates
│   └── workflows/             # CI/CD pipelines
├── config/                    # Configuration files
│   └── default.yaml          # Default application configuration
├── data/                      # Data storage (gitignored)
│   ├── external/             # External reference data
│   │   ├── edges.csv         # Sample social graph edges
│   │   ├── posts.csv         # Sample posts data
│   │   ├── taxonomy.yaml     # Issue taxonomy definitions
│   │   └── users.csv         # Sample users data
│   ├── processed/            # Processed/cleaned data
│   └── raw/                  # Raw data files (GDELT, Reddit, etc.)
├── docs/                      # Documentation
│   ├── api/                  # API documentation
│   ├── examples/             # Code examples and tutorials
│   │   ├── gdelt_example.py  # GDELT data processing example
│   │   └── reddit_example.py # Reddit data processing example
│   └── guides/               # User guides and documentation
│       ├── GDELT_USAGE.md    # GDELT integration guide
│       ├── REDDIT_SETUP.md   # Reddit API setup guide
│       └── REDDIT_USAGE.md   # Reddit integration guide
├── outputs/                   # Generated outputs (gitignored)
│   ├── exports/              # Exported results
│   └── reports/              # Generated reports
├── scripts/                   # Utility scripts
├── src/                       # Source code
│   └── vector/               # Main package
│       ├── __init__.py       # Package initialization
│       ├── audience/         # Audience building and analysis
│       │   ├── __init__.py
│       │   └── build.py      # Audience construction logic
│       ├── cli.py            # Command-line interface
│       ├── compliance/       # Compliance and safety features
│       │   ├── __init__.py
│       │   └── policies.py   # Usage policies and guardrails
│       ├── config.py         # Configuration management
│       ├── graph/            # Graph analysis and processing
│       │   ├── __init__.py
│       │   └── build.py      # Graph construction and analysis
│       ├── ingestion/        # Data ingestion adapters
│       │   ├── __init__.py
│       │   ├── adapters.py   # Base data adapters
│       │   ├── gdelt.py      # GDELT data integration
│       │   └── reddit.py     # Reddit data integration
│       ├── measurement/      # Performance measurement
│       │   ├── __init__.py
│       │   └── uplift.py     # Uplift measurement
│       ├── nlp/              # Natural language processing
│       │   ├── __init__.py
│       │   └── topics.py     # Topic modeling and classification
│       ├── pipeline.py       # Main processing pipeline
│       ├── plugins/          # Extensible plugin system
│       │   ├── __init__.py
│       │   ├── base.py       # Base plugin interface
│       │   ├── keyword.py    # Keyword-based scoring
│       │   ├── linear_scorer.py # Linear scoring algorithms
│       │   ├── pagerank.py   # PageRank implementation
│       │   └── selector.py   # Selection algorithms
│       ├── schemas.py        # Data schemas and validation
│       ├── scoring/          # Scoring algorithms
│       │   ├── __init__.py
│       │   └── score.py      # Core scoring logic
│       ├── service.py        # FastAPI web service
│       ├── utils.py          # Utility functions
│       └── vector_logging.py # Logging configuration
├── tests/                     # Test suite
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
│       ├── test_plugins.py   # Plugin tests
│       └── test_smoke.py     # Smoke tests
├── .gitignore                # Git ignore rules
├── Dockerfile                # Docker container definition
├── LICENSE                   # Apache 2.0 license
├── Makefile                  # Build and development commands
├── pyproject.toml            # Python project configuration
└── README.md                 # Project overview and quickstart
```

## Key Directories

### `/src/vector/`
The main source code package containing all core functionality:
- **Pipeline**: Main processing pipeline orchestration
- **Ingestion**: Data source adapters (GDELT, Reddit, CSV)
- **NLP**: Natural language processing for issue classification
- **Graph**: Social graph analysis and PageRank computation
- **Scoring**: Multi-factor scoring algorithms
- **Audience**: Audience building and export functionality
- **Compliance**: Safety and policy enforcement

### `/data/`
Data storage organized by lifecycle stage:
- **`external/`**: Reference data and examples
- **`raw/`**: Unprocessed data from external sources
- **`processed/`**: Cleaned and transformed data

### `/docs/`
Comprehensive documentation:
- **`guides/`**: User guides and integration documentation
- **`examples/`**: Code examples and tutorials
- **`api/`**: API reference documentation

### `/tests/`
Test suite with clear separation:
- **`unit/`**: Individual component tests
- **`integration/`**: End-to-end workflow tests

### `/outputs/`
Generated results and reports (gitignored):
- **`exports/`**: CSV exports and data dumps
- **`reports/`**: Analysis reports and visualizations

## Data Flow

1. **Raw Data** → `/data/raw/` (GDELT, Reddit, CSV files)
2. **Processing** → Vector pipeline processes and transforms data
3. **Results** → `/outputs/exports/` (CSV files, reports)
4. **Documentation** → `/docs/` (guides, examples, API docs)

## Development Workflow

1. **Source Code**: All development in `/src/vector/`
2. **Testing**: Write tests in `/tests/unit/` and `/tests/integration/`
3. **Documentation**: Update guides in `/docs/guides/`
4. **Examples**: Add examples in `/docs/examples/`
5. **Configuration**: Modify settings in `/config/`

## Best Practices

- **Data**: Never commit raw data files (use `.gitignore`)
- **Secrets**: Store API keys in environment variables
- **Testing**: Maintain high test coverage
- **Documentation**: Keep docs updated with code changes
- **Configuration**: Use YAML configs for environment-specific settings
