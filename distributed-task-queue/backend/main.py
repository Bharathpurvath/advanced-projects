from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3, uuid, json
app=FastAPI(title="Distributed Task Queue API",version="0.1.0")
db=sqlite3.connect("queue.db",check_same_thread=False)
db.execute("create table if not exists jobs(id text primary key,payload text,status text,attempts int default 0)")
db.commit()
class JobIn(BaseModel): payload:dict
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/jobs")
def enqueue(j:JobIn):
    i=str(uuid.uuid4());db.execute("insert into jobs(id,payload,status) values(?,?,?)",(i,json.dumps(j.payload),"queued"));db.commit();return {"id":i,"status":"queued"}
@app.get("/jobs")
def list_jobs(): return [{"id":r[0],"payload":json.loads(r[1]),"status":r[2],"attempts":r[3]} for r in db.execute("select id,payload,status,attempts from jobs order by rowid desc")]
@app.post("/jobs/{job_id}/claim")
def claim(job_id:str):
    cur=db.execute("update jobs set status='processing',attempts=attempts+1 where id=? and status='queued'",(job_id,));db.commit()
    if not cur.rowcount: raise HTTPException(409,"Job unavailable")
    return {"id":job_id,"status":"processing"}
@app.post("/jobs/{job_id}/complete")
def complete(job_id:str):
    cur=db.execute("update jobs set status='complete' where id=? and status='processing'",(job_id,));db.commit()
    if not cur.rowcount: raise HTTPException(409,"Job not claimed")
    return {"id":job_id,"status":"complete"}

