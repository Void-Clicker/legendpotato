import os
import hashlib
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = "https://gzcbnuxuraoavywfouhg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6Y2JudXh1cmFvYXZ5d2ZvdWhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3MTA0NTUsImV4cCI6MjA5NzI4NjQ1NX0.kkg9kL7jq4EzIap4i0OFkLdqQPG-geyObe_Evd-cFVk"   # ← YOUR FULL ANON KEY HERE

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

active_connections: Dict[str, WebSocket] = {}

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    return {"message": "Social App Backend Running"}

# Register
@app.post("/register")
def register(user: User):
    try:
        hashed = hashlib.sha256(user.password.encode()).hexdigest()
        supabase.table("users").insert({
            "username": user.username, 
            "password": hashed
        }).execute()
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Login
@app.post("/login")
def login(user: User):
    try:
        hashed = hashlib.sha256(user.password.encode()).hexdigest()
        res = supabase.table("users").select("*").eq("username", user.username).execute()
        if not res.data:
            raise HTTPException(status_code=401, detail="User not found")
        if res.data[0]["password"] != hashed:
            raise HTTPException(status_code=401, detail="Wrong password")
        return {"message": "Login successful!", "username": user.username}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Global Chat WebSocket
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            message = f"[{username}]: {data}"
            for user, conn in list(active_connections.items()):
                try:
                    await conn.send_text(message)
                except:
                    active_connections.pop(user, None)
    except WebSocketDisconnect:
        active_connections.pop(username, None)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
