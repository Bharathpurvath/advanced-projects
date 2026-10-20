from fastapi import FastAPI
from pydantic import BaseModel
from collections import Counter
import re,uuid,math
app=FastAPI(title="Semantic Search Engine API",version="0.1.0")
docs={}
class Doc(BaseModel): title:str; text:str
class Query(BaseModel): q:str
@app.get("/health")
def health():return {"status":"ok","documents":len(docs)}
@app.post("/documents")
def index(d:Doc):
    i=str(uuid.uuid4());docs[i]=d.model_dump();return {"id":i}
@app.post("/search")
def search(q:Query):
    terms=Counter(re.findall(r"\w+",q.q.lower()));scores=[]
    for i,d in docs.items():
        words=Counter(re.findall(r"\w+",d["text"].lower())); dot=sum(n*words[w] for w,n in terms.items()); norm=math.sqrt(sum(x*x for x in words.values())) or 1
        if dot:scores.append({"id":i,"title":d["title"],"score":round(dot/norm,4),"text":d["text"][:250]})
    return {"results":sorted(scores,key=lambda x:x["score"],reverse=True)[:10],"note":"Lexical cosine baseline; swap in vector embeddings for semantic retrieval"}

