from sqlalchemy.orm import Session
from fastapi import HTTPException
from .repository import (
    get_conversation_between, get_or_create_conversation, get_conversation_by_id,
    create_message, list_messages, list_conversations_for_user, mark_messages_read, count_unread
)
from app.core.events import event_bus, Events
from .websocket import manager
import asyncio

def ensure_conversation_access(db: Session, conversation_id: int, user_id: int):
    conv = get_conversation_by_id(db, conversation_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    if user_id not in (conv.user1_id, conv.user2_id):
        raise HTTPException(403, "Not a participant")
    return conv

def send_message_service(db: Session, sender_id: int, conversation_id: int, content: str | None, media_asset_id: int | None = None, message_type: str = "text", reply_to: int | None = None):
    conv = ensure_conversation_access(db, conversation_id, sender_id)

    # Rate limit check via redis
    from app.core.redis import redis_client
    from app.core.config import settings
    import time
    key = f"ratelimit:msg:{sender_id}:{int(time.time()//60)}"
    try:
        cnt = redis_client.incr(key)
        if cnt == 1:
            redis_client.expire(key, 60)
        if cnt > settings.MESSAGE_RATE_LIMIT_PER_MINUTE:
            raise HTTPException(429, "Message rate limit exceeded")
    except HTTPException:
        raise
    except Exception:
        pass

    if not content and not media_asset_id:
        raise HTTPException(400, "Message must have content or media")

    msg = create_message(db, conversation_id, sender_id, content, media_asset_id, message_type, reply_to)

    # Build payload for realtime
    payload = {
        "type": "new_message",
        "conversation_id": conversation_id,
        "message": {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "media_asset_id": msg.media_asset_id,
            "message_type": msg.message_type,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
    }

    # Async broadcast - schedule
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast_to_conversation(conversation_id, conv.user1_id, conv.user2_id, payload))
        else:
            # fallback sync if no loop
            pass
    except RuntimeError:
        pass

    event_bus.publish(Events.MESSAGE_SENT, {
        "conversation_id": conversation_id,
        "message_id": msg.id,
        "sender_id": sender_id,
    })

    return msg

def get_conversations_enriched(db: Session, user_id: int, limit: int = 50, offset: int = 0):
    convs = list_conversations_for_user(db, user_id, limit, offset)
    from app.modules.users.repository import get_profile_by_user_id
    from app.modules.media.repository import get_media_by_user_id
    from app.modules.messaging.repository import count_unread

    result = []
    for c in convs:
        other_id = c.user2_id if c.user1_id == user_id else c.user1_id
        profile = get_profile_by_user_id(db, other_id)
        media = get_media_by_user_id(db, other_id)
        unread = count_unread(db, c.id, user_id)
        result.append({
            "id": c.id,
            "user1_id": c.user1_id,
            "user2_id": c.user2_id,
            "other_user": {
                "user_id": other_id,
                "display_name": profile.display_name if profile else f"User{other_id}",
                "photo": media[0].public_url if media else None,
            },
            "last_message_at": c.last_message_at,
            "last_message_text": c.last_message_text,
            "unread_count": unread,
            "created_at": c.created_at,
        })
    return result

def get_messages_service(db: Session, user_id: int, conversation_id: int, limit: int = 50, before_id: int | None = None):
    ensure_conversation_access(db, conversation_id, user_id)
    msgs = list_messages(db, conversation_id, limit, before_id)
    # Enrich with media url
    from app.modules.media.repository import get_media_by_id
    enriched = []
    for m in reversed(msgs):  # chronological
        media_url = None
        if m.media_asset_id:
            asset = get_media_by_id(db, m.media_asset_id)
            media_url = asset.public_url if asset else None
        enriched.append({
            "id": m.id,
            "conversation_id": m.conversation_id,
            "sender_id": m.sender_id,
            "content": m.content,
            "media_asset_id": m.media_asset_id,
            "media_url": media_url,
            "message_type": m.message_type,
            "is_read": m.is_read,
            "created_at": m.created_at,
            "reply_to_message_id": m.reply_to_message_id,
        })
    # Mark as read
    mark_messages_read(db, conversation_id, user_id)
    return enriched

def start_conversation_service(db: Session, user_id: int, other_user_id: int):
    if user_id == other_user_id:
        raise HTTPException(400, "Cannot message yourself")
    # Must have matched first
    from app.modules.matches.repository import get_match_between
    match = get_match_between(db, user_id, other_user_id)
    if not match or not match.is_active:
        raise HTTPException(403, "You can only message your matches")
    conv = get_or_create_conversation(db, user_id, other_user_id)
    return conv
