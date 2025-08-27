import os, json
import pandas as pd
from typing import Union
from fastapi import FastAPI, HTTPException, Query
from . import pipeline as pl

STATE_FILE = os.environ.get("VECTOR_STATE_FILE", "./out/state.json")
EDGES_FILE = os.environ.get("VECTOR_EDGES_FILE", "./examples/edges.csv")

app = FastAPI(title="Vector API", version="0.1.0")

def _load_state():
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError(f"State file not found: {STATE_FILE}")
    return pl.load_state(STATE_FILE)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/issues")
def issues():
    try:
        st = _load_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"issues": st.get("issues", [])}

@app.get("/rank/{issue}")
def rank(issue: str, top_k: int = Query(25, ge=1, le=500), diverse: bool = Query(True)):
    try:
        st = _load_state()
        if issue not in st.get("issues", []):
            raise HTTPException(status_code=404, detail=f"Issue '{issue}' not found in state.")
        seeds = pl.rank_issue(st, issue, top_k, diverse)
        return {"issue": issue, "top_k": top_k, "diverse": diverse, "seeds": seeds.to_dict(orient="records")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audience/{issue}")
def audience(issue: str, seeds: Union[list[dict], None] = None):
    try:
        if seeds is None:
            return {"error":"Provide seeds list in JSON body."}
        seeds_df = pd.DataFrame(seeds)
        aud = pl.export_audience(seeds_df, EDGES_FILE)
        return {"issue": issue, "audience_size": int(len(aud)), "audience": aud.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
