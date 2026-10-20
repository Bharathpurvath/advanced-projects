from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uuid
app=FastAPI(title="SaaS Project Management API",version="0.1.0")
tasks={}
class TaskIn(BaseModel):
    title:str
    project_id:str="default"
    assignee:str|None=None
@app.get("/health")
def health(): return {"status":"ok","tasks":len(tasks)}
@app.get("/tasks")
def list_tasks(project_id:str="default",x_role:str=Header(default="viewer")):
    return [t for t in tasks.values() if t["project_id"]==project_id]
@app.post("/tasks")
def create_task(data:TaskIn,x_role:str=Header(default="viewer")):
    if x_role not in {"admin","editor"}: raise HTTPException(403,"Editors or admins may create tasks")
    task={"id":str(uuid.uuid4()),**data.model_dump(),"status":"planned"}
    tasks[task["id"]]=task
    return task
@app.patch("/tasks/{task_id}")
def update_task(task_id:str,status:str,x_role:str=Header(default="viewer")):
    if x_role not in {"admin","editor"}: raise HTTPException(403,"Editors or admins may update tasks")
    if task_id not in tasks: raise HTTPException(404,"Task not found")
    tasks[task_id]["status"]=status
    return tasks[task_id]

