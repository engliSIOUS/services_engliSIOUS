from fastapi import FastAPI
from api.endpoints import transcription, gemini, auth
from middlewares.auth_middleware import AuthMiddleware
from fastapi.staticfiles import StaticFiles
from configs.api_config import API_PREFIX
app = FastAPI(title="Englisious API", version="1.0.0")

# Define a constant for the API prefix


# Include routers

app.add_middleware(AuthMiddleware)
app.include_router(transcription.router, prefix=API_PREFIX, tags=["transcription"])
app.include_router(gemini.router, prefix=API_PREFIX, tags=["chat_box"])
app.include_router(auth.router, prefix='/auth', tags=["auth"])

# Mount the 'audio' directory to serve static files
app.mount("/audio", StaticFiles(directory="audio"), name="audio")