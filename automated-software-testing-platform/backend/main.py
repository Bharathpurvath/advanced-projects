from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid
app=FastAPI(title="Automated Testing Platform API",version="0.1.0")
runs=[]
class Suite(BaseModel): name:str="smoke"; environment:str="local"
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/runs")
def list_runs(): return runs
@app.post("/runs")
def run_suite(suite:Suite):
    # Safe demo: report predeclared checks; this endpoint does not execute uploaded code.
    checks=[{"name":"health endpoint","status":"passed"},{"name":"authentication boundary","status":"passed"},{"name":"invalid payload","status":"passed"},{"name":"retry behavior","status":"flaky"},{"name":"accessibility snapshot","status":"passed"},{"name":"response budget","status":"passed"}]
    r={"id":str(uuid.uuid4()),"suite":suite.name,"environment":suite.environment,"started_at":datetime.now(timezone.utc).isoformat(),"checks":checks,"passed":5,"failed":0,"flaky":1}
    runs.insert(0,r)
    return r

