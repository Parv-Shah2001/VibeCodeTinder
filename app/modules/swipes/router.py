from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .schemas import SwipeCreate, SwipeResponse
from .service import swipe_user, get_swipe_history
from .repository import get_likes_received

router = APIRouter(prefix="/swipes", tags=["swipes"])

@router.post("", response_model=SwipeResponse)
def create_swipe(payload: SwipeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return swipe_user(db, current_user.id, payload.swiped_id, payload.swipe_type)

@router.get("/history")
def history(limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_swipe_history(db, current_user.id, limit)

@router.get("/likes/received")
def likes_received(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    likes = get_likes_received(db, current_user.id)
    return [{"swiper_id": l.swiper_id, "swipe_type": l.swipe_type, "created_at": l.created_at} for l in likes]
