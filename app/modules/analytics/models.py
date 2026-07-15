from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, JSON, Float, Index
from app.core.database import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    __table_args__ = (
        Index("ix_analytics_user_created", "user_id", "created_at"),
        Index("ix_analytics_event_type", "event_type"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # swipe, match, message, profile_view, app_open
    properties = Column(JSON, nullable=True)  # flexible properties
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class DailyMetrics(Base):
    __tablename__ = "daily_metrics"
    __table_args__ = (Index("ix_daily_metrics_date", "date", unique=True),)

    id = Column(Integer, primary_key=True)
    date = Column(String(20), unique=True, nullable=False)  # YYYY-MM-DD
    dau = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    swipes = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    matches = Column(Integer, default=0)
    messages = Column(Integer, default=0)
    media_uploads = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
