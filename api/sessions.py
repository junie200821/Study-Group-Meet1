from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
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
sessions_collection = db.sessions

# Pydantic models
class CreateSessionRequest(BaseModel):
    title: str
    description: str
    date_time: Optional[str] = None
    tags: List[str] = []

class JoinSessionRequest(BaseModel):
    session_id: str

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def session_to_dict(session_doc):
    """Convert MongoDB document to dict, handling ObjectId"""
    if session_doc:
        doc_copy = dict(session_doc)
        if '_id' in doc_copy:
            doc_copy['_id'] = str(doc_copy['_id'])
        return doc_copy
    return None

@app.get("/")
async def get_sessions():
    """Get all active sessions, newest first"""
    current_time = datetime.now(timezone.utc)
    sessions_collection.update_many(
        {"date_time": {"$lt": current_time}, "date_time": {"$ne": None}},
        {"$set": {"is_expired": True}}
    )
    
    sessions_cursor = sessions_collection.find({"is_expired": {"$ne": True}}).sort("created_at", -1)
    sessions = []
    
    for session_doc in sessions_cursor:
        session_data = session_to_dict(session_doc)
        sessions.append(session_data)
    
    return {"sessions": sessions}

@app.post("/")
async def create_session(request: CreateSessionRequest):
    """Create a new study session"""
    creator_username = "anonymous"
    creator_id = str(uuid.uuid4())
    
    session_data = {
        "id": str(uuid.uuid4()),
        "title": request.title,
        "description": request.description,
        "creator_username": creator_username,
        "creator_id": creator_id,
        "date_time": datetime.fromisoformat(request.date_time.replace('Z', '+00:00')) if request.date_time else None,
        "tags": request.tags,
        "participants": [],
        "participant_usernames": [],
        "created_at": datetime.now(timezone.utc),
        "is_expired": False
    }
    
    sessions_collection.insert_one(session_data)
    
    if '_id' in session_data:
        del session_data['_id']
    
    return {"message": "Session created successfully", "session": session_data}

@app.get("/trending")
async def get_trending_sessions():
    """Get sessions with the most participants"""
    sessions_cursor = sessions_collection.find({"is_expired": {"$ne": True}})
    sessions = []
    
    for session_doc in sessions_cursor:
        session_data = session_to_dict(session_doc)
        session_data['participant_count'] = len(session_data.get('participant_usernames', []))
        sessions.append(session_data)
    
    sessions.sort(key=lambda x: (x['participant_count'], x['created_at']), reverse=True)
    
    return {"trending_sessions": sessions[:10]}

@app.post("/{session_id}/join")
async def join_session(session_id: str, username: str = "anonymous"):
    """Join a study session"""
    session_doc = sessions_collection.find_one({"id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if username in session_doc.get("participant_usernames", []):
        return {"message": "Already joined this session", "session": session_to_dict(session_doc)}
    
    sessions_collection.update_one(
        {"id": session_id},
        {
            "$push": {
                "participants": str(uuid.uuid4()),
                "participant_usernames": username
            }
        }
    )
    
    updated_session = sessions_collection.find_one({"id": session_id})
    return {"message": "Successfully joined session", "session": session_to_dict(updated_session)}

@app.post("/{session_id}/leave")
async def leave_session(session_id: str, username: str = "anonymous"):
    """Leave a study session"""
    session_doc = sessions_collection.find_one({"id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_collection.update_one(
        {"id": session_id},
        {"$pull": {"participant_usernames": username}}
    )
    
    updated_session = sessions_collection.find_one({"id": session_id})
    return {"message": "Successfully left session", "session": session_to_dict(updated_session)}

@app.delete("/{session_id}")
async def delete_session(session_id: str, creator_username: str = "anonymous"):
    """Delete a session"""
    session_doc = sessions_collection.find_one({"id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_collection.delete_one({"id": session_id})
    return {"message": "Session deleted successfully"}

# Vercel serverless handler
def handler(request):
    return app(request)