from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
app=FastAPI(title="Multi Vendor Marketplace API",version="0.1.0")
products=[{"id":"desk","name":"Studio Desk","price":249.0,"seller":"North Studio","stock":8},{"id":"camera","name":"Field Camera","price":489.0,"seller":"Peak Goods","stock":5}]
orders=[]
class OrderIn(BaseModel): product_id:str; quantity:int=1
@app.get("/health")
def health(): return {"status":"ok","orders":len(orders)}
@app.get("/products")
def list_products(): return products
@app.post("/orders")
def place_order(data:OrderIn):
    p=next((x for x in products if x["id"]==data.product_id),None)
    if not p: raise HTTPException(404,"Product not found")
    if data.quantity<1 or p["stock"]<data.quantity: raise HTTPException(409,"Insufficient stock")
    p["stock"]-=data.quantity
    order={"id":str(uuid.uuid4()),"product":p["name"],"quantity":data.quantity,"total":p["price"]*data.quantity,"payment_status":"demo_pending"}
    orders.append(order)
    return order

