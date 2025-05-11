from .config import genai, MODEL, API_KEY, CONTEXT, GENERATION_CONFIG, SAFETY_SETTINGS
from typing import List, Dict, Optional
import json
from pydantic import BaseModel
from repositories.conversation_repository import ConversationRepository
from bson import ObjectId

class Vocabulary(BaseModel):
    word: str
    definition: str

class FollowUpQuestion(BaseModel):
    question: str

class Response(BaseModel):
    title: str
    response: str
    follow_up_questions: List[FollowUpQuestion]
    vocabulary: List[Vocabulary]

class GeminiClient:
    def __init__(self, conversation_id: str = None, user_id: str = "anonymous", title: str = "Untitled", 
                 db: ConversationRepository = None):
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=CONTEXT,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        self.db = db
        self.conversation_id = ObjectId(conversation_id) if conversation_id else ObjectId()
        self.user_id = user_id
        self.title = title
        self.conversation_history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        if self.db:
            conversation = self.db.get_conversation(self.conversation_id)
            if conversation:
                self.title = conversation.get("title", "Untitled")
            return conversation.get("history", [])
        return []

    
    def generate_response(self, user_input: str):
        prompt = f"{CONTEXT}\nConversation history:\n"
        for msg in self.conversation_history:
            prompt += f"{msg['role'].capitalize()}: {msg['text']}\n"
        prompt += f"\nCurrent user input: '{user_input}'"

        try:
            response = self.model.generate_content(contents=prompt)
            parsed_response = Response(**json.loads(response.text))

            # Generate title
            if self.title == "Untitled":
                self.title = parsed_response.title

            # Update conversation history
            self.conversation_history.append({"role": "user", "text": user_input})
            self.conversation_history.append({"role": "model", "text": parsed_response.response})
        
            # Save to database
            if self.db:
                self.db.save_conversation(
                    conversation_id=self.conversation_id,
                    title=self.title,
                    user_id=self.user_id,
                    history=self.conversation_history,
                    follow_up_questions=[q.model_dump() for q in parsed_response.follow_up_questions],
                    vocabulary=[v.model_dump() for v in parsed_response.vocabulary],
                    error_message=None
                )

            return parsed_response

        except Exception as e:
            if self.db:
                self.db.save_conversation(
                    conversation_id=self.conversation_id,
                    title=self.title,
                    user_id=self.user_id,
                    history=self.conversation_history + [{"role": "user", "text": user_input}],
                    follow_up_questions=[],
                    vocabulary=[],
                    error_message=str(e)
                )
            return None
    
    def get_conversation_id(self) -> str:
        return str(self.conversation_id)