from sqlalchemy.orm import Session
from .models import Report, Block
from fastapi import HTTPException

def report_user(db: Session, reporter_id: int, reported_id: int, reason: str, description: str | None = None):
    if reporter_id == reported_id:
        raise HTTPException(400, "Cannot report yourself")
    rep = Report(reporter_id=reporter_id, reported_user_id=reported_id, reason=reason, description=description)
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep

def block_user(db: Session, blocker_id: int, blocked_id: int):
    if blocker_id == blocked_id:
        raise HTTPException(400, "Cannot block yourself")
    existing = db.query(Block).filter(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id).first()
    if existing:
        return existing
    b = Block(blocker_id=blocker_id, blocked_id=blocked_id)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

def unblock_user(db: Session, blocker_id: int, blocked_id: int):
    db.query(Block).filter(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id).delete()
    db.commit()

def get_blocked_ids(db: Session, user_id: int):
    rows = db.query(Block.blocked_id).filter(Block.blocker_id == user_id).all()
    return [r[0] for r in rows]

def is_blocked(db: Session, user1: int, user2: int) -> bool:
    # check either direction
    return db.query(Block).filter(
        ((Block.blocker_id == user1) & (Block.blocked_id == user2)) |
        ((Block.blocker_id == user2) & (Block.blocked_id == user1))
    ).first() is not None
