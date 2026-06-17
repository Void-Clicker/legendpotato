import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.db import supabase
from backend.auth import hash_password, verify_password

app = FastAPI()

# Allow frontend to call backend (important for Render + local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    return {"message": "Social App Backend - Day 2 Ready"}

@app.post("/register")
def register(user: User):
    try:
        hashed = hash_password(user.password)
        
        response = supabase.table("users").insert({
            "username": user.username,
            "password": hashed
        }).execute()
        
        return {"message": "User registered successfully!", "user_id": response.data[0]["id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: User):
    try:
        response = supabase.table("users").select("*").eq("username", user.username).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")
        
        db_user = response.data[0]
        
        if not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Wrong password")
        
        return {
            "message": "Login successful",
            "user": {
                "id": db_user["id"],
                "username": db_user["username"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# For Render deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
