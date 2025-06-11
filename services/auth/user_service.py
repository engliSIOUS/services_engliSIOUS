from passlib.hash import bcrypt
from fastapi import HTTPException, status
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate, UserLogin, UserResponse, SessionResponse
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def signup(self, email: str, password: str) -> str:
        if self.user_repo.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        hashed_password = bcrypt.hash(password)
        return self.user_repo.create_user(email, hashed_password)

    def login(self, email: str, password: str) -> SessionResponse:
        user = self.user_repo.get_user_by_email(email)
        if not user or not bcrypt.verify(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        return self.user_repo.create_session(str(user["_id"]))

    def logout(self, session_id: str):
        session = self.user_repo.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        self.user_repo.delete_session(session_id)

    def get_session(self, token: str) -> SessionResponse:
        session = self.user_repo.get_session(token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        return SessionResponse(session_id=session["session_id"], user_id=str(session["user_id"]), email=session["email"])