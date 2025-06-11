from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import Optional
from schemas.user_schema import  SessionResponse
from os import getenv
class UserRepository:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client[getenv("DB_NAME")]
        self.users = self.db[getenv("USER_COLLECTION")]
        self.sessions = self.db[getenv("SESSION_COLLECTION")]

    def create_user(self, email: str, hashed_password: str) -> str:
        user = {
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        result = self.users.insert_one(user)
        return str(result.inserted_id)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        return self.users.find_one({"email": email})

    def create_session(self, user_id: str) -> SessionResponse:
        session = {
            "user_id": ObjectId(user_id),
            "created_at": datetime.now().isoformat(), 
        }
        result = self.sessions.insert_one(session)
        return SessionResponse(
            session_id=str(result.inserted_id),
            user_id=user_id,
            created_at=session["created_at"]
        )

    def get_session(self, session_id: str) -> Optional[dict]:
        session_info = self.sessions.find_one({"_id": ObjectId(session_id)})
        session_info.put("session_id", str(session_info["_id"]))
        return session_info

    def delete_session(self, session_id: str):
        self.sessions.delete_one({"_id": ObjectId(session_id)})