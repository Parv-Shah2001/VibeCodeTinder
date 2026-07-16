from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import get_user_subscription, subscribe

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/me")
def my_sub(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_subscription(db, current_user.id)

@router.post("/subscribe")
def subscribe_route(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tier = payload.get("tier")
    try:
        sub = subscribe(db, current_user.id, tier, auto_renew=payload.get("auto_renew", False))
        return sub
    except ValueError as e:
        raise HTTPException(400, str(e))
