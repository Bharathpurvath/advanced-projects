from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3,uuid,json
app=FastAPI(title="Production Job Processing API",version="0.1.0")
db=sqlite3.connect("jobs.db",check_same_thread=False)
db.execute("create table if not exists jobs(id text primary key,idem text unique,payload text,status text,attempts int default 0)")
db.commit()
class JobIn(BaseModel): idempotency_key:str; payload:dict
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/jobs")
def enqueue(j:JobIn):
    existing=db.execute("select id,status from jobs where idem=?",(j.idempotency_key,)).fetchone()
    if existing:return {"id":existing[0],"status":existing[1],"deduplicated":True}
    i=str(uuid.uuid4());db.execute("insert into jobs(id,idem,payload,status) values(?,?,?,'queued')",(i,j.idempotency_key,json.dumps(j.payload)));db.commit()
    return {"id":i,"status":"queued","deduplicated":False}
@app.post("/jobs/{job_id}/claim")
def claim(job_id:str):
    cur=db.execute("update jobs set status='processing',attempts=attempts+1 where id=? and status='queued'",(job_id,));db.commit()
    if not cur.rowcount:raise HTTPException(409,"Job is not queued")
    return {"id":job_id,"status":"processing"}
@app.get("/jobs")
def list_jobs():return [{"id":r[0],"key":r[1],"payload":json.loads(r[2]),"status":r[3],"attempts":r[4]} for r in db.execute("select id,idem,payload,status,attempts from jobs")]

