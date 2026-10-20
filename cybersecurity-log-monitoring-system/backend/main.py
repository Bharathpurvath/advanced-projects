from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
app=FastAPI(title="Cybersecurity Log Monitor API",version="0.1.0")
events=[]
class LogIn(BaseModel): source:str="demo"; severity:str="INFO"; message:str
@app.get("/health")
def health(): return {"status":"ok","events":len(events)}
@app.post("/logs")
def ingest(row:LogIn):
    e={**row.model_dump(),"at":datetime.now(timezone.utc).isoformat()}
    events.append(e)
    high=sum(1 for x in events[-20:] if x["severity"].upper() in {"ERROR","CRITICAL"})
    return {"event":e,"alert":high>=3,"high_severity_in_window":high}
@app.get("/logs")
def list_logs(): return events[-100:]

