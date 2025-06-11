from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from schemas.user_schema import UserSession
from os import getenv
class TranscriptionRepository:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client[getenv("DB_NAME")]
        self.collection = self.db[getenv("TRANSCRIPT_COLLECTION")]

    def save_transcription(self,user_id:str, filename: str, file_path: str, text: str, status: str, error_message: str = None) -> str:
        doc = {
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path,  
            "text": text,
            "status": status,
            "error_message": error_message,
            "created_at": datetime.now().isoformat()
        }
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_transcription(self, transcription_id: str, user_id: UserSession = None) -> dict:
        query = {"_id": ObjectId(transcription_id)}
        if user_id:
            query["user_id"] = user_id
        return self.collection.find_one(query)

def get_mongo_client() -> MongoClient:

    return MongoClient(getenv('MONGODB_URI'))