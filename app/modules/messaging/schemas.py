from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    content: Optional[str] = None
    media_asset_id: Optional[int] = None
    message_type: str = "text"
    reply_to_message_id: Optional[int] = None

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: Optional[str]
    media_asset_id: Optional[int] = None
    media_url: Optional[str] = None
    message_type: str
    is_read: bool
    created_at: datetime
    reply_to_message_id: Optional[int] = None

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    other_user: Optional[dict] = None
    last_message_at: Optional[datetime]
    last_message_text: Optional[str]
    unread_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
