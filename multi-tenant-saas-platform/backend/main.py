from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uuid
app=FastAPI(title="Multi Tenant SaaS API",version="0.1.0")
rows={}
class Record(BaseModel): value:str
def key(tenant,record):return f"{tenant}:{record}"
@app.get("/health")
def health():return {"status":"ok","tenants":len({k.split(':',1)[0] for k in rows})}
@app.get("/records")
def list_records(x_tenant_id:str=Header(...)):
    return [{"id":k.split(':',1)[1],"value":v} for k,v in rows.items() if k.startswith(x_tenant_id+":")]
@app.post("/records")
def add_record(r:Record,x_tenant_id:str=Header(...),x_role:str=Header(default="viewer")):
    if x_role not in {"owner","admin","editor"}:raise HTTPException(403,"Tenant role cannot write")
    i=str(uuid.uuid4());rows[key(x_tenant_id,i)]=r.value;return {"id":i,"value":r.value}

