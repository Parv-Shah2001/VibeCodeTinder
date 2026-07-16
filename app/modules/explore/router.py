from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import get_explore_feed, get_top_picks, get_likes_you

router = APIRouter(prefix="/explore", tags=["explore"])

@router.get("")
def explore(interest: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_explore_feed(db, current_user.id, interest)

@router.get("/top-picks")
def top_picks(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_top_picks(db, current_user.id, limit)

@router.get("/likes-you")
def likes_you(limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # In prod check subscription Gold
    return get_likes_you(db, current_user.id, limit)
