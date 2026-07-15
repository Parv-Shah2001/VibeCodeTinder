"""
Boost + SuperLike + Rewind – Premium features.

- Boost: profile boosted 30min +200 score, shows 10x in feed
- Super Boost: 3 hours
- SuperLike: priority, recipient sees blue star + higher ranking
- Rewind: undo last swipe (Plus feature)
"""
from sqlalchemy.orm import Session
from app.modules.users.repository import get_profile_by_user_id
from app.modules.swipes.repository import get_swipe
from app.modules.swipes.models import Swipe
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

def boost_profile(db: Session, user_id: int, duration_minutes: int = 30):
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    profile.is_boosted = True
    profile.boosted_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
    db.commit()
    return {"status": "boosted", "until": profile.boosted_until, "duration": duration_minutes}

def super_boost_profile(db: Session, user_id: int):
    return boost_profile(db, user_id, duration_minutes=180)

def rewind_last_swipe(db: Session, user_id: int):
    last = db.query(Swipe).filter(Swipe.swiper_id == user_id).order_by(Swipe.created_at.desc()).first()
    if not last:
        raise HTTPException(404, "No swipes to rewind")
    # Check within 5 min window for free, else require Plus
    if datetime.utcnow() - last.created_at.replace(tzinfo=None) > timedelta(minutes=5):
        # In prod check subscription
        pass
    db.delete(last)
    db.commit()
    # Also delete match if existed? For simplicity keep match but could check
    return {"status": "rewound", "swiped_id": last.swiped_id, "type": last.swipe_type}

def get_superlike_balance(db: Session, user_id: int) -> int:
    # Would have table superlike_balance; for MVP give 1 per day free, unlimited for Plus
    from app.modules.subscriptions.service import get_user_subscription
    sub = get_user_subscription(db, user_id)
    if sub.tier in ("plus", "gold", "platinum"):
        return 999  # unlimited
    # Check daily usage
    today_count = db.query(Swipe).filter(Swipe.swiper_id == user_id, Swipe.swipe_type == "superlike", Swipe.created_at >= datetime.utcnow().date()).count()
    return max(0, 1 - today_count)
