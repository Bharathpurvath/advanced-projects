from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
app=FastAPI(title="Workflow Automation API",version="0.1.0")
flows={};history=[]
class Workflow(BaseModel): name:str; trigger:str; action:str
@app.get("/health")
def health(): return {"status":"ok","workflows":len(flows)}
@app.post("/workflows")
def create(w:Workflow):
    if w.action not in {"create_notification","open_triage_task","write_demo_log"}: raise HTTPException(400,"Action is not in the safe allowlist")
    i=str(uuid.uuid4());flows[i]=w.model_dump();return {"id":i,**flows[i]}
@app.post("/workflows/{flow_id}/trigger")
def trigger(flow_id:str,event:str):
    w=flows.get(flow_id)
    if not w: raise HTTPException(404,"Workflow not found")
    if w["trigger"]!=event: return {"matched":False}
    result={"id":str(uuid.uuid4()),"workflow":flow_id,"action":w["action"],"event":event,"status":"demo_completed"}
    history.append(result);return {"matched":True,"result":result}
@app.get("/runs")
def runs(): return history

