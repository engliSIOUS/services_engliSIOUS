from pymongo import MongoClient, DESCENDING
from datetime import datetime
from services.gemini.config import MONGODB_URI,DB_NAME,CONVERSATION_COLLECTION
from typing import List, Dict
from bson import ObjectId
from services.transcription.transcription_service import nlp

def tokenize_text(data: str) -> list:
    doc = nlp(data)
    return [str(token) for token in doc if not token.is_punct]
 
class ConversationRepository:
    def __init__(self, uri: str = MONGODB_URI):
        self.client = MongoClient(uri)
        self.db = self.client[DB_NAME]
        self.collection = self.db[CONVERSATION_COLLECTION]

    def save_conversation(self, conversation_id: ObjectId, title: str, user_id: str, history: list[dict], follow_up_questions : list[str] = None,
                          vocabulary : list[dict[str, str]] = None, error_message: str = None):
        doc = {
            "conversation_id": conversation_id,
            "title": title,
            "user_id": user_id,  
            "history": history,
            "follow_up_questions" : follow_up_questions,
            "vocabulary" : vocabulary,
            "error_message": error_message,
            "created_at": datetime.now().isoformat()
        }
        self.collection.insert_one(
            document=doc
        )

    def get_conversation(self, conversation_id: ObjectId) -> Dict:
        documents = self.collection.find_one(
            {"conversation_id": conversation_id}, 
            sort =[('created_at', DESCENDING)]
        )
        if documents:
            return {"title" : documents["title"], "history" : documents["history"]}
        return {}
    
    def get_paginated_conversations(self, user_id: str, page: int, limit: int = 8) -> Dict:
        if not user_id:
            return {
            "current_page": 1,
            "conversations": [],
            "total_conversations": 0,
            "total_pages": 1
        }

        skip = (page - 1) * limit
        collection = self.collection.find({"user_id": user_id})
        total_conversations = collection.count()

        # Fetch conversations
        documents = collection.sort('created_at', DESCENDING).skip(skip).limit(limit)
        conversations = []

        for doc in documents:
            history_with_tokenized = []
            for item in doc["history"]:
                item_copy = item.copy()
                item_copy["text_tokenized"] = tokenize_text(item_copy["text"]) if "text" in item_copy else []
                history_with_tokenized.append(item_copy)

            conversations.append({
                "conversation_id" : str(doc["conversation_id"]),
                "title" : doc["title"],
                "history" : history_with_tokenized,
                "created_at" : doc["created_at"]                 
            })

        total_pages = (total_conversations - 1 + limit) // limit 
        
        return {
            "current_page": page,
            "conversations": conversations,
            "total_conversations": total_conversations,
            "total_pages": total_pages
        }