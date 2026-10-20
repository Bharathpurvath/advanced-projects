from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI(title="Recommendation Engine API",version="0.1.0")
items=[{"id":"1","name":"Grid notebook","tags":["Design","Travel"]},{"id":"2","name":"Trail camera","tags":["Outdoors","Technology"]},{"id":"3","name":"Design system handbook","tags":["Design","Technology"]},{"id":"4","name":"Packing cubes","tags":["Travel","Outdoors"]}]
class Preferences(BaseModel): interests:list[str]; exclude_ids:list[str]=[]
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/recommend")
def recommend(p:Preferences):
    ranked=[]
    for item in items:
        if item["id"] in p.exclude_ids:continue
        score=len(set(item["tags"])&set(p.interests))
        ranked.append({**item,"score":score})
    return sorted(ranked,key=lambda x:x["score"],reverse=True)

