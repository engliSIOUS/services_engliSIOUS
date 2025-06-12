from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from bson.objectid import ObjectId, InvalidId
from services.gemini.conversation_manager import ConversationManager
from repositories.conversation_repository import ConversationRepository
from services.gemini.vocabulary_extractor import VocabularyExtractor
from fastapi import APIRouter

router = APIRouter()
# Request model for converse
class ConverseRequest(BaseModel):
    user_id: str = "anonymous"
    conversation_id: Optional[str] = None
    user_input: str

# Response model for converse
class ConverseResponse(BaseModel):
    conversation_id: str
    title: str
    response: str
    follow_up_questions: List[dict]
    vocabulary: List[dict]

# Response model for conversations
class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    history: List[dict]
    created_at: str

class PaginatedConversationsResponse(BaseModel):
    current_page: int
    conversations: List[ConversationSummary]
    total_conversations: int
    total_pages: int

# Response model for dictionary lookup
class DictionaryDefinition(BaseModel):
    definition: str
    example: str

class DictionaryMeaning(BaseModel):
    partOfSpeech: str
    definitions: List[DictionaryDefinition]

class DictionaryResponse(BaseModel):
    word: str
    phonetic: str
    meanings: List[DictionaryMeaning]

# Response model for word translation
class WordTranslationResponse(BaseModel):
    word: str
    definition: str

@router.post("/converse", response_model=ConverseResponse, status_code=status.HTTP_200_OK)
async def converse(request: ConverseRequest):
    """Handle conversation requests."""
    # Validate conversation_id
    if request.conversation_id:
        try:
            ObjectId(request.conversation_id)
        except InvalidId:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID")

    # Initialize database and manager
    db = ConversationRepository()
    manager = ConversationManager(
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        db=db
    )

    # Process input
    result = manager.process_input(request.user_input)
    if "Error" in result["response"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["response"])

    return ConverseResponse(
        conversation_id=manager.get_conversation_id(),
        title=manager.gemini_client.title,
        response=result["response"],
        follow_up_questions=result["follow_up_questions"],
        vocabulary=result["vocabulary"]
    )

@router.get("/conversations", response_model=PaginatedConversationsResponse, status_code=status.HTTP_200_OK)
async def get_conversations(user_id : str = None, page: int = 1):
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page number must be positive")

    db = ConversationRepository()
    result = db.get_paginated_conversations(user_id=user_id, page=page, limit=8)

    if page > result["total_pages"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page exceeds total pages available")

    return PaginatedConversationsResponse(
        conversations=result["conversations"],
        total_conversations=result["total_conversations"],
        total_pages=result["total_pages"],
        current_page=result["current_page"]
    )

@router.get("/dictionary/{word}", response_model=DictionaryResponse, status_code=status.HTTP_200_OK)
async def lookup_word(word: str):
    extractor = VocabularyExtractor()
    try:
        result = extractor.lookup_word(word)
        return DictionaryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/quick_definition/{word}", response_model=WordTranslationResponse, status_code=status.HTTP_200_OK)
async def quick_definition(word: str, user_id: str = "anonymous"):
    """Handle quick word translation requests using Gemini AI."""
    db = ConversationRepository()
    manager = ConversationManager(user_id=user_id, db=db)
    
    result = manager.quick_definition(word)
    if "Error" in result["response"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["response"])
    
    return WordTranslationResponse(
        word=result["vocabulary"][0]["word"],
        definition=result["vocabulary"][0]["definition"]
    )
