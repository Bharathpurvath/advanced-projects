from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
app=FastAPI(title="Financial Analytics API",version="0.1.0")
rows=[]
class Transaction(BaseModel): label:str; amount:float; type:str="Expense"; day:date=date.today()
@app.get("/health")
def health(): return {"status":"ok","transactions":len(rows)}
@app.post("/transactions")
def add(t:Transaction):
    row=t.model_dump();row["day"]=str(row["day"]);rows.append(row);return row
@app.get("/analytics")
def analytics():
    income=sum(x["amount"] for x in rows if x["type"].lower()=="income")
    expense=sum(x["amount"] for x in rows if x["type"].lower()=="expense")
    return {"income":income,"expense":expense,"net":income-expense,"count":len(rows)}

