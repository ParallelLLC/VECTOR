import json, os, yaml
import typer
import pandas as pd
from datetime import date
from typing import Dict, Any, Optional
from . import pipeline as pl
from .ingestion.gdelt import download_gdelt_data, load_gdelt_data
from .ingestion.reddit import create_reddit_downloader, fetch_reddit_data, RedditProcessor, create_mock_reddit_data

app = typer.Typer(pretty_exceptions_show_locals=False, add_completion=False)

@app.command()
def run_pipeline(
    users: str = typer.Option(..., help="Path to users.csv"),
    edges: str = typer.Option(..., help="Path to edges.csv"),
    posts: str = typer.Option(..., help="Path to posts.csv"),
    taxonomy: str = typer.Option(..., help="Path to taxonomy.yaml"),
    out: str = typer.Option("./out", help="Output directory"),
    config: str = typer.Option(None, help="Path to config YAML")
):
    cfg: Dict[str, Any] = {}
    if config and os.path.exists(config):
        with open(config, "r") as f:
            cfg = yaml.safe_load(f) or {}
    res = pl.run_pipeline(users, edges, posts, taxonomy, out, cfg)
    typer.echo(json.dumps(res, indent=2))

@app.command()
def rank_issue(
    issue: str = typer.Option(..., help="Issue key found in taxonomy"),
    stateful: str = typer.Option(..., help="Path to state.json from run-pipeline"),
    top_k: int = typer.Option(25, help="Number of seeds"),
    diverse: bool = typer.Option(True, help="Community-diverse selection"),
    out: str = typer.Option(None, help="Optional CSV output path")
):
    state = pl.load_state(stateful)
    seeds = pl.rank_issue(state, issue, top_k, diverse)
    if out:
        seeds.to_csv(out, index=False)
        typer.echo(f"Wrote seeds to {out}")
    else:
        typer.echo(seeds.to_csv(index=False))

@app.command()
def export_audience(
    issue: str = typer.Option(..., help="Issue (for logging only)"),
    stateful: str = typer.Option(..., help="Path to state.json"),
    seeds: str = typer.Option(..., help="CSV of seeds from rank-issue"),
    edges: str = typer.Option(..., help="Path to edges.csv"),
    out: str = typer.Option(None, help="Optional CSV output path")
):
    state = pl.load_state(stateful)  # not used now but kept for parity
    seeds_df = pd.read_csv(seeds)
    audience = pl.export_audience(seeds_df, edges)
    if out:
        audience.to_csv(out, index=False)
        typer.echo(f"Wrote audience to {out}")
    else:
        typer.echo(audience.to_csv(index=False))

@app.command()
def download_gdelt(
    date_str: str = typer.Option(..., help="Date in YYYYMMDD format (e.g., 20250101)"),
    data_types: str = typer.Option("gkg,events", help="Comma-separated data types: gkg,events"),
    download_dir: str = typer.Option("./gdelt_data", help="Directory to store downloaded files"),
    extract: bool = typer.Option(True, help="Extract zip files after download")
):
    """Download GDELT data for a specific date."""
    data_types_list = [dt.strip() for dt in data_types.split(',')]
    
    try:
        # Parse date to validate format
        date_obj = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
        
        typer.echo(f"Downloading GDELT data for {date_str}...")
        filepaths = download_gdelt_data(date_obj, data_types_list, download_dir, extract)
        
        typer.echo("Download completed successfully!")
        for data_type, filepath in filepaths.items():
            typer.echo(f"  {data_type.upper()}: {filepath}")
            
    except ValueError as e:
        typer.echo(f"Error: Invalid date format. Use YYYYMMDD format. {e}", err=True)
    except Exception as e:
        typer.echo(f"Error downloading data: {e}", err=True)

@app.command()
def load_gdelt(
    gkg_file: str = typer.Option(None, help="Path to GKG CSV file"),
    events_file: str = typer.Option(None, help="Path to Events CSV file"),
    sample_size: int = typer.Option(None, help="Number of rows to sample (for testing)"),
    out: str = typer.Option(None, help="Output directory for processed data")
):
    """Load and process GDELT data files."""
    filepaths = {}
    if gkg_file:
        filepaths['gkg'] = gkg_file
    if events_file:
        filepaths['events'] = events_file
    
    if not filepaths:
        typer.echo("Error: Please specify at least one file (--gkg-file or --events-file)", err=True)
        return
    
    try:
        typer.echo("Loading GDELT data...")
        data = load_gdelt_data(filepaths, sample_size)
        
        for data_type, df in data.items():
            typer.echo(f"{data_type.upper()} data: {df.shape[0]} rows, {df.shape[1]} columns")
            
            if out:
                output_file = f"{out}/{data_type}_processed.csv"
                df.to_csv(output_file, index=False)
                typer.echo(f"  Saved to: {output_file}")
        
        # Show sample data
        if 'gkg' in data:
            typer.echo("\nGKG sample:")
            typer.echo(data['gkg'][['DATE', 'SourceCommonName', 'Themes']].head().to_string())
        
        if 'events' in data:
            typer.echo("\nEvents sample:")
            typer.echo(data['events'][['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode']].head().to_string())
            
    except Exception as e:
        typer.echo(f"Error loading data: {e}", err=True)

@app.command()
def fetch_reddit(
    data_type: str = typer.Option(..., help="Type of data to fetch: subreddit_posts, user_posts, user_comments, search_posts"),
    client_id: str = typer.Option("OYCu9XcRwIu75LCKpJUCeg", help="Reddit API client ID"),
    client_secret: str = typer.Option("GPRHBHuigrk3Q1fPctJUR4UTsT85ZQ", help="Reddit API client secret"),
    limit: int = typer.Option(100, help="Maximum number of items to fetch"),
    subreddit: str = typer.Option(None, help="Subreddit name (for subreddit_posts or search_posts)"),
    username: str = typer.Option(None, help="Username (for user_posts or user_comments)"),
    query: str = typer.Option(None, help="Search query (for search_posts)"),
    sort: str = typer.Option("hot", help="Sort method (hot, new, top, rising, relevance)"),
    time_filter: str = typer.Option("week", help="Time filter (all, day, hour, month, week, year)"),
    out: str = typer.Option(None, help="Output file path for CSV export")
):
    """Fetch Reddit data using the Reddit API."""
    try:
        # Create Reddit downloader
        typer.echo("Connecting to Reddit API...")
        downloader = create_reddit_downloader(client_id, client_secret)
        
        # Prepare arguments based on data type
        kwargs: Dict[str, Any] = {'limit': limit}
        
        if data_type == 'subreddit_posts':
            if not subreddit:
                typer.echo("Error: --subreddit is required for subreddit_posts", err=True)
                return
            kwargs['subreddit_name'] = subreddit
            kwargs['sort'] = sort
            kwargs['time_filter'] = time_filter
            
        elif data_type in ['user_posts', 'user_comments']:
            if not username:
                typer.echo(f"Error: --username is required for {data_type}", err=True)
                return
            kwargs['username'] = username
            
        elif data_type == 'search_posts':
            if not query:
                typer.echo("Error: --query is required for search_posts", err=True)
                return
            kwargs['query'] = query
            kwargs['subreddit'] = subreddit
            kwargs['sort'] = sort
            kwargs['time_filter'] = time_filter
        
        # Fetch data
        typer.echo(f"Fetching {data_type}...")
        df = fetch_reddit_data(downloader, data_type, **kwargs)
        
        typer.echo(f"Successfully fetched {len(df)} items")
        
        # Show sample data
        if not df.empty:
            typer.echo("\nSample data:")
            if 'title' in df.columns:
                sample_cols = ['title', 'author', 'score', 'created_utc']
            else:
                sample_cols = ['text', 'author', 'score', 'created_utc']
            
            available_cols = [col for col in sample_cols if col in df.columns]
            if available_cols:
                typer.echo(df[available_cols].head().to_string())
        
        # Save to file if requested
        if out:
            df.to_csv(out, index=False)
            typer.echo(f"\nData saved to: {out}")
            
    except Exception as e:
        typer.echo(f"Error fetching Reddit data: {e}", err=True)

@app.command()
def convert_reddit(
    input_file: str = typer.Option(..., help="Path to Reddit data CSV file"),
    data_type: str = typer.Option("posts", help="Type of data: posts, comments"),
    out: str = typer.Option(None, help="Output file path for Vector format CSV")
):
    """Convert Reddit data to Vector pipeline format."""
    try:
        typer.echo(f"Loading Reddit data from {input_file}...")
        df = pd.read_csv(input_file)
        
        processor = RedditProcessor()
        
        if data_type == "posts":
            vector_df = processor.convert_to_vector_format(df)
        elif data_type == "comments":
            vector_df = processor.convert_comments_to_posts(df)
        else:
            typer.echo(f"Error: Invalid data_type '{data_type}'. Use 'posts' or 'comments'", err=True)
            return
        
        typer.echo(f"Converted {len(df)} Reddit items to {len(vector_df)} Vector format items")
        
        # Show sample data
        if not vector_df.empty:
            typer.echo("\nSample Vector format data:")
            typer.echo(vector_df[['user_id', 'text', 'likes', 'comments']].head().to_string())
        
        # Save to file if requested
        if out:
            vector_df.to_csv(out, index=False)
            typer.echo(f"\nVector format data saved to: {out}")
            
    except Exception as e:
        typer.echo(f"Error converting Reddit data: {e}", err=True)

@app.command()
def create_mock_reddit(
    data_type: str = typer.Option(..., help="Type of mock data: posts, comments"),
    count: int = typer.Option(100, help="Number of mock records to create"),
    subreddit: str = typer.Option("test", help="Subreddit name for mock data"),
    out: str = typer.Option(None, help="Output file path for CSV export")
):
    """Create mock Reddit data for testing purposes."""
    try:
        typer.echo(f"Creating {count} mock {data_type} records...")
        
        mock_df = create_mock_reddit_data(data_type, count, subreddit)
        
        typer.echo(f"Successfully created {len(mock_df)} mock {data_type} records")
        
        # Show sample data
        if not mock_df.empty:
            typer.echo("\nSample mock data:")
            if data_type == "posts":
                sample_cols = ['title', 'author', 'score', 'created_utc']
            else:
                sample_cols = ['text', 'author', 'score', 'created_utc']
            
            available_cols = [col for col in sample_cols if col in mock_df.columns]
            if available_cols:
                typer.echo(mock_df[available_cols].head().to_string())
        
        # Save to file if requested
        if out:
            mock_df.to_csv(out, index=False)
            typer.echo(f"\nMock data saved to: {out}")
            
    except Exception as e:
        typer.echo(f"Error creating mock Reddit data: {e}", err=True)

if __name__ == "__main__":
    app()
