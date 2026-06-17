import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client

app = FastAPI()

# Enable CORS so frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SUPABASE CONFIG ===
SUPABASE_URL = "https://gzcbnuxuraoavywfouhg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6Y2JudXh1cmFvYXZ5d2ZvdWhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3MTA0NTUsImV4cCI6MjA5NzI4NjQ1NX0.kkg9kL7jq4EzIap4i0OFkLdqQPG-geyObe_Evd-cFVk"   # ← PASTE YOUR FULL ANON KEY HERE

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    return {"message": "Social App Backend - Working"}

@app.post("/register")
def register(user: User):
    try:
        import hashlib
        hashed = hashlib.sha256(user.password.encode()).hexdigest()
        
        response = supabase.table("users").insert({
            "username": user.username,
            "password": hashed
        }).execute()
        
        return {"message": "User registered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: User):
    try:
        import hashlib
        hashed = hashlib.sha256(user.password.encode()).hexdigest()
        
        response = supabase.table("users").select("*").eq("username", user.username).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")
        
        db_user = response.data[0]
        
        if db_user["password"] != hashed:
            raise HTTPException(status_code=401, detail="Wrong password")
        
        return {"message": "Login successful!", "username": db_user["username"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# For Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
