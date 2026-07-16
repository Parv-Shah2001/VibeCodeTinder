from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .repository import get_user_by_email, create_user, update_last_login
from .schemas import UserCreate
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.events import event_bus, Events

def register_user(db: Session, payload: UserCreate):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(payload.password)
    user = create_user(db, email=payload.email, hashed_password=hashed, phone=payload.phone)

    # Event for profile creation etc.
    event_bus.publish(Events.USER_REGISTERED, {"user_id": user.id, "email": user.email, "name": payload.name})

    access = create_access_token({"sub": str(user.id), "email": user.email})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    update_last_login(db, user)
    access = create_access_token({"sub": str(user.id), "email": user.email})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }

def refresh_access_token(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    from .repository import get_user_by_id
    user = get_user_by_id(db, int(user_id)) if user_id else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token({"sub": str(user.id), "email": user.email})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }
