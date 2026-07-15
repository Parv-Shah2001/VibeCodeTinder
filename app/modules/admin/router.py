from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from app.modules.users.models import Profile
from app.modules.swipes.models import Swipe
from app.modules.matches.models import Match
from app.modules.messaging.models import Message
from app.modules.media.models import MediaAsset

router = APIRouter(prefix="/admin", tags=["admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(403, "Admin only")
    return current_user

@router.get("/stats")
def stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {
        "total_users": db.query(User).count(),
        "total_profiles": db.query(Profile).count(),
        "total_swipes": db.query(Swipe).count(),
        "total_matches": db.query(Match).count(),
        "total_messages": db.query(Message).count(),
        "total_media": db.query(MediaAsset).count(),
        "active_users_24h": db.query(User).filter(User.last_login_at != None).count(),
        "verified_users": db.query(User).filter(User.is_verified == True).count(),
    }

@router.get("/users")
def list_users(limit: int = 50, offset: int = 0, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).offset(offset).all()
    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

@router.get("/reports")
def reports(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    from app.modules.moderation.models import Report
    return db.query(Report).order_by(Report.created_at.desc()).limit(100).all()

@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Not found")
    user.is_active = False
    db.commit()
    return {"status": "banned"}
