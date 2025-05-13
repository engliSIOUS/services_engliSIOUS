from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime

class UserSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime