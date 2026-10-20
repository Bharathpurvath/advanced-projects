from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
from time import time
app=FastAPI(title="API Gateway and Rate Limiter",version="0.1.0")
hits=defaultdict(deque); cache={}
@app.middleware("http")
async def limit(request:Request,call_next):
    if request.url.path.startswith("/health"): return await call_next(request)
    key=request.client.host if request.client else "unknown"; now=time(); q=hits[key]
    while q and now-q[0]>60:q.popleft()
    if len(q)>=30:return JSONResponse(status_code=429,content={"detail":"Rate limit exceeded","retry_after":60-int(now-q[0])})
    q.append(now);return await call_next(request)
@app.get("/health")
def health(): return {"status":"ok","clients":len(hits)}
@app.get("/proxy/catalog")
def catalog():
    if "catalog" not in cache: cache["catalog"]={"items":["docs","reports","projects"],"cached_at":time()}
    return cache["catalog"]
@app.post("/cache/invalidate")
def invalidate(): cache.clear();return {"status":"cleared"}

