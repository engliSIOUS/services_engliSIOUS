from fastapi import FastAPI
from api.endpoints import transcription, gemini, auth
from middlewares.auth_middleware import AuthMiddleware
from configs.api_config import API_PREFIX
app = FastAPI(title="Englisious API", version="1.0.0")

# Define a constant for the API prefix


# Include routers

# app.add_middleware(AuthMiddleware,allow_origins=["http://localhost:8000", "http://localhost:3000"],  # Thêm domain của Swagger/frontend
#     allow_credentials=True,  # Cho phép gửi cookie
#     allow_methods=["*"],
#     allow_headers=["*"],
#     )
app.include_router(transcription.router, prefix=API_PREFIX, tags=["transcription"])
app.include_router(gemini.router, prefix=API_PREFIX, tags=["chat_box"])
app.include_router(auth.router, prefix='/auth', tags=["auth"])