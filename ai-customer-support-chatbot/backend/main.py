from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI(title="AI Customer Support API",version="0.1.0")
faq=[("password","Use the password reset link on sign-in; a reset link is sent to your verified email."),("invoice","Invoices are available from Workspace > Billing > Invoices."),("cancel","Manage or cancel a plan from Workspace > Billing."),("export","Use Settings > Data > Export to download workspace data.")]
history=[]
class Message(BaseModel): conversation_id:str="demo"; text:str
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/chat")
def chat(m:Message):
    q=m.text.lower(); match=next(((k,a) for k,a in faq if k in q),None)
    answer=match[1] if match else "I could not find a verified answer. Please contact a human support agent."
    row={"conversation_id":m.conversation_id,"question":m.text,"answer":answer,"confidence":0.82 if match else 0.0}
    history.append(row)
    return row
@app.get("/conversations/{conversation_id}")
def conversation(conversation_id:str): return [x for x in history if x["conversation_id"]==conversation_id]

