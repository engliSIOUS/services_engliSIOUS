from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.dependencies import get_user_service
from schemas.user_schema import UserCreate, UserLogin, UserResponse, SessionResponse
from services.auth.user_service import UserService

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, service: UserService = Depends(get_user_service)):
    user_id = service.signup(user.email, user.password)
    return UserResponse(id=user_id, email=user.email, created_at=None)

@router.post("/login", response_model=SessionResponse)
def login(user: UserLogin, service: UserService = Depends(get_user_service)):
    session_id = service.login(user.email, user.password)
    return SessionResponse(session_id=session_id, user_id=None, created_at=None)

@router.post("/logout")
def logout(session_id: str, service: UserService = Depends(get_user_service)):
    service.logout(session_id)
    return {"message": "Logged out successfully"}