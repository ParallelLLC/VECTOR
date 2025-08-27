import json, os, yaml
import typer
import pandas as pd
from . import pipeline as pl

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
    cfg = {}
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

if __name__ == "__main__":
    app()
