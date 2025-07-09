# mini_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import time

app = FastAPI()

users: Dict[str, Dict] = {}
transfer_requests: Dict[str, Dict] = {}

class RegisterData(BaseModel):
    username: str
    ip: str
    port: int

class TransferRequest(BaseModel):
    sender: str
    receiver: str
    filename: str

class TransferAccept(BaseModel):
    receiver: str
    sender: str

@app.post("/register")
def register(data: RegisterData):
    users[data.username] = {
        "ip": data.ip,
        "port": data.port,
        "last_seen": time.time()
    }
    return {"message": f"{data.username} registered."}

@app.get("/users")
def get_users():
    return users

@app.delete("/disconnect/{username}")
def disconnect(username: str):
    if username in users:
        del users[username]
    if username in transfer_requests:
        del transfer_requests[username]
    return {"message": f"{username} disconnected."}

@app.post("/request_transfer")
def request_transfer(req: TransferRequest):
    if req.receiver not in users:
        raise HTTPException(status_code=404, detail="Receiver not found.")
    transfer_requests[req.receiver] = {
        "from": req.sender,
        "filename": req.filename
    }
    return {"message": f"Transfer request sent to {req.receiver}"}

@app.get("/check_transfer/{username}")
def check_transfer(username: str):
    if username in transfer_requests:
        return transfer_requests[username]
    return {"message": "No transfer requests."}

@app.post("/accept_transfer")
def accept_transfer(data: TransferAccept):
    if data.receiver not in transfer_requests:
        raise HTTPException(status_code=404, detail="No pending transfer.")
    if transfer_requests[data.receiver]["from"] != data.sender:
        raise HTTPException(status_code=403, detail="Unauthorized sender.")
    
    sender = data.sender
    if sender not in users:
        raise HTTPException(status_code=404, detail="Sender offline.")

    return {
        "sender_ip": users[sender]["ip"],
        "sender_port": users[sender]["port"]
    }
