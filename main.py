from fastapi import FastAPI
from api.endpoints import transcription

app = FastAPI(title="Speech-to-Text API")

# Include routers
app.include_router(transcription.router, prefix="/api/v1", tags=["transcription"])