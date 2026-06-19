import os
import hashlib
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
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
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6Y2JudXh1cmFvYXZ5d2ZvdWhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3MTA0NTUsImV4cCI6MjA5NzI4NjQ1NX0.kkg9kL7jq4EzIap4i0OFkLdqQPG-geyObe_Evd-cFVk"  # ← YOUR FULL ANON KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

active_connections: Dict[str, WebSocket] = {}

@app.get("/")
def home():
    return {"message": "Social App - Improved Chat + Profiles"}

class User(BaseModel):
    username: str
    password: str

# Auth
@app.post("/register")
def register(user: User):
    try:
        hashed = hashlib.sha256(user.password.encode()).hexdigest()
        supabase.table("users").insert({
            "username": user.username, 
            "password": hashed,
            "profile_pic": None
        }).execute()
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

# Upload Profile Picture
@app.post("/upload-pfp/{username}")
async def upload_pfp(username: str, file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_path = f"pfp/{username}.jpg"
        
        supabase.storage.from_("social-app").upload(file_path, content, {"content-type": "image/jpeg"})
        public_url = supabase.storage.from_("social-app").get_public_url(file_path)
        
        supabase.table("users").update({"profile_pic": public_url}).eq("username", username).execute()
        
        return {"message": "Profile picture updated!", "url": public_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get User Profile
@app.get("/profile/{username}")
def get_profile(username: str):
    res = supabase.table("users").select("*").eq("username", username).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    return res.data[0]

# === IMPROVED WEBSOCKET CHAT ===
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
