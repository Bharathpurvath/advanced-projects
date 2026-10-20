from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, os, json, urllib.request
app=FastAPI(title="CI/CD Deployment Dashboard API",version="0.1.0")
runs=[]
class PipelineIn(BaseModel): name:str="demo"; branch:str="main"
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/pipelines")
def start(p:PipelineIn):
    r={"id":str(uuid.uuid4()),"name":p.name,"branch":p.branch,"state":"queued","stages":["build","test","package","deploy"],"created_at":datetime.now(timezone.utc).isoformat()}
    runs.insert(0,r); return r
@app.get("/pipelines")
def list_runs(): return runs
@app.get("/github/{owner}/{repo}/runs")
def github_runs(owner:str,repo:str):
    token=os.getenv("GITHUB_TOKEN")
    if not token: raise HTTPException(501,"Set GITHUB_TOKEN to read GitHub Actions. This demo never writes to repositories.")
    req=urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=10",headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req,timeout=10) as r: return json.load(r)
    except Exception as e: raise HTTPException(502,"GitHub API request failed") from e

