from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.modules.auth.models import User
from .service import report_user, block_user, unblock_user, get_blocked_ids

router = APIRouter(prefix="/moderation", tags=["moderation"])

@router.post("/report/{reported_id}")
def report(reported_id: int, reason: str, description: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return report_user(db, current_user.id, reported_id, reason, description)

@router.post("/block/{blocked_id}")
def block(blocked_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return block_user(db, current_user.id, blocked_id)

@router.delete("/block/{blocked_id}")
def unblock(blocked_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    unblock_user(db, current_user.id, blocked_id)
    return {"status": "unblocked"}

@router.get("/blocks")
def list_blocks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_blocked_ids(db, current_user.id)
