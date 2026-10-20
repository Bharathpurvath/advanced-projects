from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import Counter
import re, uuid

app = FastAPI(title="AI Document Assistant API", version="0.1.0")
docs = {}
class Document(BaseModel):
    title: str
    text: str
class Query(BaseModel):
    query: str
@app.get("/health")
def health(): return {"status":"ok","documents":len(docs)}
@app.get("/documents")
def list_documents(): return list(docs.values())
@app.post("/documents")
def add_document(doc: Document):
    if not doc.text.strip(): raise HTTPException(400,"Document text is required")
    item={"id":str(uuid.uuid4()),"title":doc.title,"text":doc.text}
    docs[item["id"]]=item
    return item
@app.post("/query")
def query(q: Query):
    terms=set(re.findall(r"\w+",q.query.lower()))
    ranked=[]
    for d in docs.values():
        words=re.findall(r"\w+",d["text"].lower())
        score=sum(1 for w in words if w in terms)
        if score: ranked.append({"document_id":d["id"],"title":d["title"],"score":score,"excerpt":d["text"][:320]})
    return {"results":sorted(ranked,key=lambda x:x["score"],reverse=True)[:5],"method":"transparent lexical baseline; replace with embeddings + vector store for RAG"}

