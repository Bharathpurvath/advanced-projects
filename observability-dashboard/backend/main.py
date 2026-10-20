from fastapi import FastAPI, Request
from time import perf_counter
from collections import defaultdict
from uuid import uuid4
app=FastAPI(title="Observability Dashboard API",version="0.1.0")
metrics=defaultdict(int);latencies=[];traces=[]
@app.middleware("http")
async def observe(request:Request,call_next):
    start=perf_counter(); trace=str(uuid4())
    try: response=await call_next(request);metrics[f"http_{response.status_code}"]+=1;return response
    finally:
        ms=(perf_counter()-start)*1000;latencies.append(ms);traces.append({"trace_id":trace,"path":request.url.path,"latency_ms":round(ms,2)})
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/metrics")
def get_metrics(): return {"requests":sum(metrics.values()),"status_counts":dict(metrics),"latency_ms":{"count":len(latencies),"avg":round(sum(latencies)/len(latencies),2) if latencies else 0,"max":round(max(latencies),2) if latencies else 0}}
@app.get("/traces")
def get_traces(): return traces[-50:]

