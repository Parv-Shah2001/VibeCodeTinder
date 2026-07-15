from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text, Index
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (Index("ix_report_reported", "reported_user_id"),)

    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reported_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (Index("ix_block_blocker_blocked", "blocker_id", "blocked_id", unique=True),)

    id = Column(Integer, primary_key=True)
    blocker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
