from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import Optional

class UserRepository:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client["auth_db"]
        self.users = self.db["users"]
        self.sessions = self.db["sessions"]

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

    def create_session(self, user_id: str) -> str:
        session = {
            "user_id": ObjectId(user_id),
            "created_at": datetime.now().isoformat()
        }
        result = self.sessions.insert_one(session)
        return str(result.inserted_id)

    def get_session(self, session_id: str) -> Optional[dict]:
        return self.sessions.find_one({"_id": ObjectId(session_id)})

    def delete_session(self, session_id: str):
        self.sessions.delete_one({"_id": ObjectId(session_id)})