from fastapi import FastAPI
from pydantic import BaseModel
import re
app=FastAPI(title="AI Code Review Assistant API",version="0.1.0")
class ReviewIn(BaseModel): code:str
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/review")
def review(r:ReviewIn):
    rules=[(r"password\s*=\s*['\"][^'\"]+['\"]","high","Possible hard-coded credential"),(r"eval\s*\(","high","Dynamic eval call"),(r"except\s*:\s*pass","medium","Swallowed exception"),(r"TODO|FIXME","low","Unfinished marker")]
    findings=[]
    for pattern,severity,message in rules:
        for m in re.finditer(pattern,r.code,re.I): findings.append({"severity":severity,"message":message,"offset":m.start()})
    return {"findings":findings,"engine":"local rules","note":"Use a reviewed LLM integration for contextual suggestions"}

