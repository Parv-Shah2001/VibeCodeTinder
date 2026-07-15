from sqlalchemy.orm import Session
from .models import Swipe
from typing import Optional, List
from datetime import datetime, timedelta

def has_swiped(db: Session, swiper_id: int, swiped_id: int) -> bool:
    return db.query(Swipe).filter(Swipe.swiper_id == swiper_id, Swipe.swiped_id == swiped_id).first() is not None

def get_swipe(db: Session, swiper_id: int, swiped_id: int) -> Optional[Swipe]:
    return db.query(Swipe).filter(Swipe.swiper_id == swiper_id, Swipe.swiped_id == swiped_id).first()

def create_swipe(db: Session, swiper_id: int, swiped_id: int, swipe_type: str) -> Swipe:
    swipe = Swipe(swiper_id=swiper_id, swiped_id=swiped_id, swipe_type=swipe_type)
    db.add(swipe)
    db.commit()
    db.refresh(swipe)
    return swipe

def get_swiped_ids_by_user(db: Session, swiper_id: int, limit: int = 1000) -> List[int]:
    rows = db.query(Swipe.swiped_id).filter(Swipe.swiper_id == swiper_id).order_by(Swipe.created_at.desc()).limit(limit).all()
    return [r[0] for r in rows]

def get_recent_swipe_count(db: Session, user_id: int, minutes: int = 1) -> int:
    since = datetime.utcnow() - timedelta(minutes=minutes)
    return db.query(Swipe).filter(Swipe.swiper_id == user_id, Swipe.created_at >= since).count()

def get_likes_received(db: Session, user_id: int) -> List[Swipe]:
    return db.query(Swipe).filter(Swipe.swiped_id == user_id, Swipe.swipe_type.in_(["like", "superlike"])).order_by(Swipe.created_at.desc()).limit(100).all()
