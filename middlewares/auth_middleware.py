

from fastapi import Request,status,HTTPException
from pymongo import MongoClient
from starlette.responses import JSONResponse, Response

from repositories.user_repository import UserRepository
from starlette.middleware.base import BaseHTTPMiddleware
import os
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.user_repository = UserRepository(MongoClient(os.getenv("MONGODB_URI")))
        self.public_paths = ["/auth","/audio", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next) -> Response:
            if not any(request.url.path.startswith(path) for path in self.public_paths):
                auth_token = request.headers.get("Authorization")
                if auth_token and auth_token.startswith("Bearer "):
                    auth_token = auth_token[len("Bearer "):]
                else:
                    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Invalid or missing Authorization header")
                user_info = self.user_repository.get_session(auth_token)
                if not auth_token or not user_info:
                    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Unauthorized")

            response = await call_next(request)
            return response
