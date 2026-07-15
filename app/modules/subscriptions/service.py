from sqlalchemy.orm import Session
from .models import Subscription
from datetime import datetime, timedelta, timezone

def get_user_subscription(db: Session, user_id: int) -> Subscription:
    sub = db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.is_active == True).first()
    if not sub:
        sub = Subscription(user_id=user_id, tier="free", is_active=True)
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub

def subscribe(db: Session, user_id: int, tier: str, auto_renew: bool = False) -> Subscription:
    if tier not in ("plus", "gold", "platinum"):
        raise ValueError("Invalid tier")
    # deactivate old
    db.query(Subscription).filter(Subscription.user_id == user_id).update({"is_active": False})
    sub = Subscription(
        user_id=user_id,
        tier=tier,
        is_active=True,
        auto_renew=auto_renew,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub
