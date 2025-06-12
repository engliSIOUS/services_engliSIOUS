from typing import Dict
from .gemini_client import GeminiClient
from .response_formatter import ResponseFormatter
from repositories.conversation_repository import ConversationRepository

class ConversationManager:
    def __init__(self, conversation_id: str = None, user_id: str = "anonymous", 
                 title: str = "Untitled", db: ConversationRepository = None):
        self.gemini_client = GeminiClient(conversation_id=conversation_id, user_id=user_id, title=title, db=db)
        self.response_formatter = ResponseFormatter()

    def process_input(self, user_input: str) -> Dict:
        if not user_input.strip():
            error_response = self.response_formatter.format_error("Input cannot be empty.")
            if self.gemini_client.db:
                self.gemini_client.db.save_conversation(
                    conversation_id=self.gemini_client.conversation_id,
                    title=self.gemini_client.title,
                    user_id=self.gemini_client.user_id,
                    history=self.gemini_client.conversation_history,
                    follow_up_questions=[],
                    vocabulary=[],
                    error_message=error_response["response"]
                )
            return error_response

        # Generate conversational response
        parsed_response = self.gemini_client.generate_response(user_input)
        if not parsed_response:
            error_response = self.response_formatter.format_error("Failed to generate response.")
            return error_response

        # Format response
        return self.response_formatter.format_response(
            response=parsed_response.response,
            follow_up_questions=[q.model_dump() for q in parsed_response.follow_up_questions],
            vocabulary=[v.model_dump() for v in parsed_response.vocabulary]
        )
    
    def get_conversation_id(self) -> str:
        return self.gemini_client.get_conversation_id()
    
    def quick_definition(self, word: str) -> Dict:
        if not word.strip():
            return self.response_formatter.format_error("Word cannot be empty.")
        
        result = self.gemini_client.quick_translate(word)
        if not result:
            return self.response_formatter.format_error("Failed to generate word definition.")
        
        return self.response_formatter.format_response(
            response=result["definition"],
            follow_up_questions=[],
            vocabulary=[{"word": result["word"], "definition": result["definition"]}]
        )