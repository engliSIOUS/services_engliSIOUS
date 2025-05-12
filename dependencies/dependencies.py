from fastapi import Depends
from pymongo import MongoClient
from services.speech_to_text.azure import AzureSpeechToTextProvider
from services.transcription.transcription_service import TranscriptionService
from repositories.transcription_repository import TranscriptionRepository, get_mongo_client
from repositories.user_repository import UserRepository
from services.auth.user_service import UserService
import os

def get_speech_to_text_provider():
    # Thay thế bằng Azure credentials thực tế
    return AzureSpeechToTextProvider(subscription_key=os.getenv("AZURE_SUBSCRIPTION_KEY"), region=os.getenv("AZURE_REGION"))

def get_transcription_repository(mongo_client: MongoClient = Depends(get_mongo_client)):
    return TranscriptionRepository(mongo_client)

def get_transcription_service(
    speech_to_text_provider=Depends(get_speech_to_text_provider),
    transcription_repo=Depends(get_transcription_repository)
):
    return TranscriptionService(speech_to_text_provider, transcription_repo)

def get_user_repository(mongo_client: MongoClient = Depends(get_mongo_client)):
    return UserRepository(mongo_client)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)):
    return UserService(user_repo)