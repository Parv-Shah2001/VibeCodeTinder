from sqlalchemy.orm import Session
from .models import Conversation, Message
from typing import List, Optional
from datetime import datetime

def get_conversation_between(db: Session, user1: int, user2: int) -> Optional[Conversation]:
    u1, u2 = sorted([user1, user2])
    return db.query(Conversation).filter(Conversation.user1_id == u1, Conversation.user2_id == u2).first()

def get_or_create_conversation(db: Session, user1: int, user2: int) -> Conversation:
    conv = get_conversation_between(db, user1, user2)
    if conv:
        return conv
    u1, u2 = sorted([user1, user2])
    conv = Conversation(user1_id=u1, user2_id=u2)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def get_conversation_by_id(db: Session, conv_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conv_id).first()

def list_conversations_for_user(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Conversation]:
    return db.query(Conversation).filter(
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
    ).order_by(Conversation.last_message_at.desc().nullslast(), Conversation.created_at.desc()).limit(limit).offset(offset).all()

def create_message(db: Session, conversation_id: int, sender_id: int, content: Optional[str], media_asset_id: Optional[int] = None, message_type: str = "text", reply_to: Optional[int] = None) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        media_asset_id=media_asset_id,
        message_type=message_type,
        reply_to_message_id=reply_to,
    )
    db.add(msg)
    # Update conversation last message
    conv = get_conversation_by_id(db, conversation_id)
    if conv:
        conv.last_message_at = datetime.utcnow()
        conv.last_message_text = content or f"[{message_type}]"
        # Also update match last_message_at for ordering
        from app.modules.matches.repository import get_match_between
        other_id = conv.user2_id if conv.user1_id == sender_id else conv.user1_id if conv.user2_id == sender_id else None
        # Need to find other participant
        # conv stores sorted ids, so find counterpart
        if conv.user1_id == sender_id:
            other = conv.user2_id
        else:
            other = conv.user1_id
        match = get_match_between(db, sender_id, other)
        if match:
            match.last_message_at = conv.last_message_at
    db.commit()
    db.refresh(msg)
    return msg

def list_messages(db: Session, conversation_id: int, limit: int = 50, before_id: Optional[int] = None) -> List[Message]:
    q = db.query(Message).filter(Message.conversation_id == conversation_id, Message.is_deleted == False).order_by(Message.created_at.desc())
    if before_id:
        before_msg = db.query(Message).filter(Message.id == before_id).first()
        if before_msg:
            q = q.filter(Message.created_at < before_msg.created_at)
    return q.limit(limit).all()

def get_last_message_for_conversation(db: Session, conversation_id: int) -> Optional[Message]:
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).first()

def mark_messages_read(db: Session, conversation_id: int, reader_id: int):
    # Mark messages not sent by reader as read
    db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != reader_id,
        Message.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()

def count_unread(db: Session, conversation_id: int, user_id: int) -> int:
    return db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,
        Message.is_read == False,
        Message.is_deleted == False
    ).count()
