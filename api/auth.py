from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import os
from pymongo import MongoClient
import uuid

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'studymeet_db')

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db.users

# Pydantic models
class LoginRequest(BaseModel):
    username: str

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def user_to_dict(user_doc):
    """Convert MongoDB document to dict, handling ObjectId"""
    if user_doc:
        doc_copy = dict(user_doc)
        if '_id' in doc_copy:
            doc_copy['_id'] = str(doc_copy['_id'])
        return doc_copy
    return None

@app.post("/login")
async def login(request: LoginRequest):
    """Simple username-based login"""
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    # Check if user exists
    existing_user = users_collection.find_one({"username": username})
    
    if existing_user:
        user_data = user_to_dict(existing_user)
        return {"message": "Login successful", "user": user_data}
    else:
        # Create new user
        user_dict = {
            "id": str(uuid.uuid4()),
            "username": username,
            "created_at": datetime.now(timezone.utc)
        }
        users_collection.insert_one(user_dict)
        
        # Remove MongoDB _id from response
        if '_id' in user_dict:
            del user_dict['_id']
            
        return {"message": "User created and logged in", "user": user_dict}

# Vercel serverless handler
def handler(request):
    return app(request)