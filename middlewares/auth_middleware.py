from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from pymongo import MongoClient
from repositories.user_repository import UserRepository
import os
from configs.api_config import API_PREFIX
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.user_repository = UserRepository(MongoClient(os.getenv("MONGODB_URI")))
        self.public_paths = ["/auth","/audio", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        if not any(request.url.path.startswith(path) for path in self.public_paths):
            auth_token = request.headers.get("Authorization")
            if not auth_token or not self.user_repository.get_session(auth_token):
                raise HTTPException(status_code=401, detail="Unauthorized")
        
        response = await call_next(request)
        return response

    def validate_token(self, token: str) -> bool:
        # Extract session ID from the token (assuming token is the session ID for simplicity)
        session = self.user_repository.get_session(token)
        if not session:
            return False
        return True