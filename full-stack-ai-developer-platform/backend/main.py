from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
app=FastAPI(title="AI Developer Platform API",version="0.1.0")
agents={}
allowed={"search_local_docs","summarize_demo_status","create_checklist"}
class AgentIn(BaseModel): name:str; tools:list[str]=["create_checklist"]
class TaskIn(BaseModel): task:str
@app.get("/health")
def health():return {"status":"ok","agents":len(agents)}
@app.post("/agents")
def create(a:AgentIn):
    invalid=set(a.tools)-allowed
    if invalid:raise HTTPException(400,"Tool is not in the safe allowlist")
    i=str(uuid.uuid4());agents[i]=a.model_dump();return {"id":i,**agents[i]}
@app.post("/agents/{agent_id}/run")
def run(agent_id:str,t:TaskIn):
    a=agents.get(agent_id)
    if not a:raise HTTPException(404,"Agent not found")
    return {"agent":a["name"],"task":t.task,"tool_plan":[x for x in a["tools"]],"result":"Demo task accepted. Configure a reviewed model provider to add LLM reasoning.","execution":"safe_simulation"}

