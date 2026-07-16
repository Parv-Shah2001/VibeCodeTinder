"""
Analytics service tracking scale metrics: 500k new profiles/day, 1B matches/day etc.

In production this would push to ClickHouse / BigQuery via Kafka.
For monolith we store in Postgres + async batch.

Use cases:
- DAU tracking
- Funnel: register -> profile -> swipe -> match -> message
- Retention cohorts
- Recommendation A/B testing
"""
from sqlalchemy.orm import Session
from .models import AnalyticsEvent, DailyMetrics
from datetime import datetime, date
from app.core.events import event_bus, Events
import structlog

logger = structlog.get_logger(__name__)

def track_event(db: Session, user_id: int | None, event_type: str, properties: dict | None = None, session_id: str | None = None, ip: str | None = None, ua: str | None = None):
    try:
        ev = AnalyticsEvent(
            user_id=user_id,
            event_type=event_type,
            properties=properties or {},
            session_id=session_id,
            ip_address=ip,
            user_agent=ua,
        )
        db.add(ev)
        db.commit()
        logger.info("analytics_tracked", event_type=event_type, user_id=user_id)
    except Exception as e:
        logger.error("analytics_failed", error=str(e))
        db.rollback()

def track_event_async(user_id: int | None, event_type: str, properties: dict | None = None):
    # For use in event bus handlers without DB session – open new session
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        track_event(db, user_id, event_type, properties)
    finally:
        db.close()

# Event handlers for auto-tracking scale metrics
def on_user_registered(payload: dict):
    track_event_async(payload.get("user_id"), "user_registered", {"email": payload.get("email")})
    # Increment daily metrics
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        today = date.today().isoformat()
        dm = db.query(DailyMetrics).filter(DailyMetrics.date == today).first()
        if not dm:
            dm = DailyMetrics(date=today, new_users=1, dau=1)
            db.add(dm)
        else:
            dm.new_users += 1
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

def on_swipe_created(payload: dict):
    track_event_async(payload.get("swiper_id"), "swipe", {"swiped_id": payload.get("swiped_id"), "type": payload.get("swipe_type")})

def on_match_created(payload: dict):
    track_event_async(payload.get("user1_id"), "match", {"matched_with": payload.get("user2_id"), "match_id": payload.get("match_id")})
    track_event_async(payload.get("user2_id"), "match", {"matched_with": payload.get("user1_id"), "match_id": payload.get("match_id")})

def on_message_sent(payload: dict):
    track_event_async(payload.get("sender_id"), "message_sent", {"conversation_id": payload.get("conversation_id")})

def on_media_uploaded(payload: dict):
    track_event_async(payload.get("user_id"), "media_uploaded", {"media_id": payload.get("media_id")})

# Subscribe
event_bus.subscribe(Events.USER_REGISTERED, on_user_registered)
event_bus.subscribe(Events.SWIPE_CREATED, on_swipe_created)
event_bus.subscribe(Events.MATCH_CREATED, on_match_created)
event_bus.subscribe(Events.MESSAGE_SENT, on_message_sent)
event_bus.subscribe(Events.MEDIA_UPLOADED, on_media_uploaded)

def get_daily_metrics(db: Session, days: int = 30):
    return db.query(DailyMetrics).order_by(DailyMetrics.date.desc()).limit(days).all()

def get_user_funnel(db: Session, user_id: int):
    events = db.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == user_id).order_by(AnalyticsEvent.created_at).all()
    return [{"type": e.event_type, "at": e.created_at, "props": e.properties} for e in events]
