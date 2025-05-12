from fastapi import APIRouter, Depends, Response
from dependencies.dependencies import get_user_service
from schemas.user_schema import UserCreate, UserLogin, UserResponse, SessionResponse
from services.auth.user_service import UserService

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, service: UserService = Depends(get_user_service)):
    user_id = service.signup(user.email, user.password)
    return UserResponse(id=user_id, email=user.email)

@router.post("/login", response_model=SessionResponse)
def login(user: UserLogin, service: UserService = Depends(get_user_service), response: Response = None):
    session = service.login(user.email, user.password)
    if session:
        response.set_cookie(key="session_id", value=session.session_id, httponly=True,max_age=3600,secure=False)
    return session
     

@router.post("/logout")
def logout(session_id: str, service: UserService = Depends(get_user_service)):
    service.logout(session_id)
    return {"message": "Logged out successfully"}