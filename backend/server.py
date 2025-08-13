from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os
from pymongo import MongoClient
import uuid
from bson import ObjectId

# Load environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# Initialize FastAPI app
app = FastAPI(title="Study Group Sessions API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(',') if CORS_ORIGINS != '*' else ['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db.users
sessions_collection = db.sessions

# Pydantic models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    creator_username: str
    creator_id: str
    date_time: Optional[datetime] = None
    tags: List[str] = []
    participants: List[str] = []  # List of user IDs
    participant_usernames: List[str] = []  # List of usernames for easy display
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_expired: bool = False

class CreateSessionRequest(BaseModel):
    title: str
    description: str
    date_time: Optional[str] = None
    tags: List[str] = []

class JoinSessionRequest(BaseModel):
    session_id: str

class LoginRequest(BaseModel):
    username: str

# Helper functions
def session_to_dict(session_doc):
    """Convert MongoDB document to dict, handling ObjectId"""
    if session_doc:
        # Create a copy to avoid modifying the original
        doc_copy = dict(session_doc)
        if '_id' in doc_copy:
            doc_copy['_id'] = str(doc_copy['_id'])
        return doc_copy
    return None

def user_to_dict(user_doc):
    """Convert MongoDB document to dict, handling ObjectId"""
    if user_doc:
        # Create a copy to avoid modifying the original
        doc_copy = dict(user_doc)
        if '_id' in doc_copy:
            doc_copy['_id'] = str(doc_copy['_id'])
        return doc_copy
    return None

# Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/auth/login")
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
        user = User(username=username)
        user_dict = user.dict()
        users_collection.insert_one(user_dict)
        return {"message": "User created and logged in", "user": user_dict}

@app.get("/api/sessions")
async def get_sessions():
    """Get all active sessions, newest first"""
    # Remove expired sessions first
    current_time = datetime.now(timezone.utc)
    sessions_collection.update_many(
        {"date_time": {"$lt": current_time}, "date_time": {"$ne": None}},
        {"$set": {"is_expired": True}}
    )
    
    # Get active sessions
    sessions_cursor = sessions_collection.find({"is_expired": {"$ne": True}}).sort("created_at", -1)
    sessions = []
    
    for session_doc in sessions_cursor:
        session_data = session_to_dict(session_doc)
        sessions.append(session_data)
    
    return {"sessions": sessions}

@app.post("/api/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new study session"""
    # For now, we'll use a simple approach - in real app, we'd get this from auth
    # Let's assume the first part of title indicates the creator
    creator_username = "anonymous"  # This should come from authentication
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
    session_data['_id'] = str(session_data['_id']) if '_id' in session_data else None
    
    return {"message": "Session created successfully", "session": session_data}

@app.post("/api/sessions/{session_id}/join")
async def join_session(session_id: str, username: str = "anonymous"):
    """Join a study session"""
    session_doc = sessions_collection.find_one({"id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user already joined
    if username in session_doc.get("participant_usernames", []):
        return {"message": "Already joined this session", "session": session_to_dict(session_doc)}
    
    # Add user to participants
    sessions_collection.update_one(
        {"id": session_id},
        {
            "$push": {
                "participants": str(uuid.uuid4()),  # Generate a participant ID
                "participant_usernames": username
            }
        }
    )
    
    updated_session = sessions_collection.find_one({"id": session_id})
    return {"message": "Successfully joined session", "session": session_to_dict(updated_session)}

@app.post("/api/sessions/{session_id}/leave")
async def leave_session(session_id: str, username: str = "anonymous"):
    """Leave a study session"""
    session_doc = sessions_collection.find_one({"id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Remove user from participants
    sessions_collection.update_one(
        {"id": session_id},
        {
            "$pull": {
                "participant_usernames": username
            }
        }
    )
    
    updated_session = sessions_collection.find_one({"id": session_id})
    return {"message": "Successfully left session", "session": session_to_dict(updated_session)}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, creator_username: str = "anonymous"):
    """Delete a session (only by creator)"""
    session_doc = sessions_collection.find_one({"id": session_id})
    
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # In a real app, check if user is the creator
    # For now, allow anyone to delete
    sessions_collection.delete_one({"id": session_id})
    
    return {"message": "Session deleted successfully"}

@app.get("/api/sessions/trending")
async def get_trending_sessions():
    """Get sessions with the most participants"""
    sessions_cursor = sessions_collection.find({"is_expired": {"$ne": True}})
    sessions = []
    
    for session_doc in sessions_cursor:
        session_data = session_to_dict(session_doc)
        session_data['participant_count'] = len(session_data.get('participant_usernames', []))
        sessions.append(session_data)
    
    # Sort by participant count, then by creation date
    sessions.sort(key=lambda x: (x['participant_count'], x['created_at']), reverse=True)
    
    return {"trending_sessions": sessions[:10]}  # Top 10 trending

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)