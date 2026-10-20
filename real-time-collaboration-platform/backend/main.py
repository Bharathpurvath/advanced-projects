from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from collections import defaultdict
import uuid
app=FastAPI(title="Real Time Collaboration API",version="0.1.0")
rooms=defaultdict(set); snapshots={}
class Update(BaseModel): user:str; content:str; version:int
@app.get("/health")
def health(): return {"status":"ok","rooms":len(rooms)}
@app.websocket("/ws/{room_id}")
async def connect(ws:WebSocket,room_id:str):
    await ws.accept(); rooms[room_id].add(ws)
    try:
        await ws.send_json({"type":"snapshot","content":snapshots.get(room_id,""),"peers":len(rooms[room_id])})
        while True:
            msg=await ws.receive_json()
            snapshots[room_id]=msg.get("content","")
            dead=[]
            for peer in rooms[room_id]:
                if peer is ws: continue
                try: await peer.send_json({"type":"update","content":snapshots[room_id],"user":msg.get("user","guest"),"version":msg.get("version",0)})
                except Exception: dead.append(peer)
            for peer in dead: rooms[room_id].discard(peer)
    except WebSocketDisconnect:
        rooms[room_id].discard(ws)

