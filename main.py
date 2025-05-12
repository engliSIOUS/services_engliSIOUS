from fastapi import FastAPI
from api.endpoints import transcription, gemini, auth

app = FastAPI(title="Englisious API", version="1.0.0")

# Define a constant for the API prefix
API_PREFIX = "/api/v1"

# Include routers
app.include_router(transcription.router, prefix=API_PREFIX, tags=["transcription"])
app.include_router(gemini.router, prefix=API_PREFIX, tags=["large_language_model"])
app.include_router(auth.router, prefix=API_PREFIX, tags=["auth"])