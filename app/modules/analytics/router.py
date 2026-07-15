from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import get_daily_metrics, get_user_funnel, track_event
from .models import AnalyticsEvent

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/track")
def track(event_type: str, properties: dict = {}, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    track_event(db, current_user.id, event_type, properties)
    return {"status": "tracked"}

@router.get("/daily")
def daily_metrics(days: int = 30, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # In production check superuser
    return get_daily_metrics(db, days)

@router.get("/funnel/{user_id}")
def funnel(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_superuser:
        from fastapi import HTTPException
        raise HTTPException(403, "Forbidden")
    return get_user_funnel(db, user_id)

@router.get("/me/events")
def my_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = db.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == current_user.id).order_by(AnalyticsEvent.created_at.desc()).limit(100).all()
    return events
