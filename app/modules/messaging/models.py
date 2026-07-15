from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean, Index, Text
from app.core.database import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conv_user1_user2", "user1_id", "user2_id", unique=True),
        Index("ix_conv_last_message", "last_message_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_message_text = Column(Text, nullable=True)

    # For 200M messages/day, conversations table is small, but messages need partitioning
    # In PG we would do RANGE partitioning by created_at per month + hash partitioning by conversation_id

class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_message_conversation_created", "conversation_id", "created_at"),
        Index("ix_message_sender", "sender_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=True)
    media_asset_id = Column(Integer, ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True)
    message_type = Column(String(20), default="text")  # text, image, video, system
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    # For edit/delete
    is_deleted = Column(Boolean, default=False)
    # Reply
    reply_to_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
