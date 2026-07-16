from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user
from app.core.security import decode_token
from app.modules.auth.models import User
from .schemas import MessageCreate
from .service import send_message_service, get_conversations_enriched, get_messages_service, start_conversation_service, ensure_conversation_access
from .websocket import manager
from .repository import get_conversation_between

router = APIRouter(prefix="/messaging", tags=["messaging"])

@router.get("/conversations")
def list_conversations(limit: int = 50, offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_conversations_enriched(db, current_user.id, limit, offset)

@router.post("/conversations/with/{other_user_id}")
def start_conversation(other_user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv = start_conversation_service(db, current_user.id, other_user_id)
    return {"id": conv.id, "user1_id": conv.user1_id, "user2_id": conv.user2_id, "created_at": conv.created_at}

@router.get("/conversations/{conversation_id}/messages")
def list_msgs(conversation_id: int, limit: int = 50, before_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_messages_service(db, current_user.id, conversation_id, limit, before_id)

@router.post("/conversations/{conversation_id}/messages")
def send_msg(conversation_id: int, payload: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = send_message_service(db, current_user.id, conversation_id, payload.content, payload.media_asset_id, payload.message_type, payload.reply_to_message_id)
    return {
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "sender_id": msg.sender_id,
        "content": msg.content,
        "media_asset_id": msg.media_asset_id,
        "message_type": msg.message_type,
        "created_at": msg.created_at,
    }

@router.post("/conversations/{conversation_id}/typing")
async def typing_indicator(conversation_id: int, is_typing: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv = ensure_conversation_access(db, conversation_id, current_user.id)
    other_id = conv.user2_id if conv.user1_id == current_user.id else conv.user1_id
    await manager.send_typing_indicator(conversation_id, current_user.id, other_id, is_typing)
    return {"status": "ok"}

# WebSocket endpoint for realtime
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Auth via query token
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Could handle ping/pong, typing etc from client
            # For now just keep alive
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
