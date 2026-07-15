from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from .schemas import UserCreate, UserLogin, TokenResponse, TokenRefresh, UserResponse
from .service import register_user, authenticate_user, refresh_access_token
from .models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, payload)

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, payload.email, payload.password)

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)):
    return refresh_access_token(db, payload.refresh_token)

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
