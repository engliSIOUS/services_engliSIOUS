from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

class TranscriptionRepository:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client["speech_to_text_db"]
        self.collection = self.db["transcriptions"]

    def save_transcription(self, filename: str, file_path: str, text: str, status: str, error_message: str = None) -> str:
        doc = {
            "filename": filename,
            "file_path": file_path,  # Lưu thêm file_path
            "text": text,
            "status": status,
            "error_message": error_message,
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def get_transcription(self, transcription_id: str) -> dict:
        return self.collection.find_one({"_id": ObjectId(transcription_id)})

def get_mongo_client() -> MongoClient:
    # Thay thế bằng connection string thực tế
    return MongoClient("mongodb://localhost:27017")