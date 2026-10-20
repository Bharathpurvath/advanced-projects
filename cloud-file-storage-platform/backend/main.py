from fastapi import FastAPI, HTTPException, UploadFile, File
from pathlib import Path
import uuid, hashlib, hmac, os, time
app=FastAPI(title="Cloud File Storage API",version="0.1.0")
ROOT=Path("storage").resolve(); ROOT.mkdir(exist_ok=True)
KEY=os.getenv("SIGNING_KEY","development-only-change-me").encode()
metadata={}
@app.get("/health")
def health(): return {"status":"ok","files":len(metadata)}
@app.post("/files")
async def upload(file:UploadFile=File(...), user_id:str="demo"):
    raw=await file.read(10_000_001)
    if len(raw)>10_000_000: raise HTTPException(413,"Demo limit is 10 MB")
    file_id=str(uuid.uuid4()); target=(ROOT/file_id).resolve()
    if ROOT not in target.parents: raise HTTPException(400,"Invalid path")
    target.write_bytes(raw)
    row={"id":file_id,"name":Path(file.filename or "upload").name,"size":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"owner":user_id}
    metadata[file_id]=row
    return row
@app.post("/files/{file_id}/signed-url")
def signed_url(file_id:str, user_id:str="demo"):
    row=metadata.get(file_id)
    if not row or row["owner"]!=user_id: raise HTTPException(404,"File not found")
    expiry=int(time.time())+300
    token=hmac.new(KEY,f"{file_id}:{user_id}:{expiry}".encode(),hashlib.sha256).hexdigest()
    return {"url":f"/files/{file_id}/download?user_id={user_id}&expires={expiry}&signature={token}","expires_at":expiry}
@app.get("/files/{file_id}/download")
def download(file_id:str,user_id:str,expires:int,signature:str):
    expected=hmac.new(KEY,f"{file_id}:{user_id}:{expires}".encode(),hashlib.sha256).hexdigest()
    if expires<int(time.time()) or not hmac.compare_digest(expected,signature): raise HTTPException(403,"Invalid or expired URL")
    row=metadata.get(file_id); path=ROOT/file_id
    if not row or row["owner"]!=user_id or not path.exists(): raise HTTPException(404,"File not found")
    return {"file":row,"note":"Serve bytes with FileResponse in a production deployment"}

