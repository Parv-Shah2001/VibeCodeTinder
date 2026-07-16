from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import boost_profile, super_boost_profile, rewind_last_swipe, get_superlike_balance

router = APIRouter(prefix="/boosts", tags=["boosts"])

@router.post("/boost")
def boost(duration_minutes: int = 30, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return boost_profile(db, current_user.id, duration_minutes)

@router.post("/super-boost")
def super_boost(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return super_boost_profile(db, current_user.id)

@router.post("/rewind")
def rewind(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return rewind_last_swipe(db, current_user.id)

@router.get("/superlike/balance")
def balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"balance": get_superlike_balance(db, current_user.id)}
