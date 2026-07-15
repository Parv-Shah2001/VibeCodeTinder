from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool, QueuePool
from typing import Generator

from .config import settings

# Engine config tuned for scale: 50M users, 1M DAU
# For Postgres we use QueuePool with pre_ping.
# For SQLite (local dev) we use NullPool.
if settings.is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        echo=False,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
        pool_recycle=3600,
        poolclass=QueuePool,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models to register them with Base – 18 modules for full production
    from app.modules.auth.models import User  # noqa: F401
    from app.modules.users.models import Profile, UserPreference  # noqa: F401
    from app.modules.media.models import MediaAsset  # noqa: F401
    from app.modules.swipes.models import Swipe  # noqa: F401
    from app.modules.matches.models import Match  # noqa: F401
    from app.modules.messaging.models import Conversation, Message  # noqa: F401
    from app.modules.subscriptions.models import Subscription  # noqa: F401
    from app.modules.moderation.models import Report, Block  # noqa: F401
    from app.modules.analytics.models import AnalyticsEvent, DailyMetrics  # noqa: F401
    from app.modules.payments.models import Payment, Invoice  # noqa: F401
    from app.modules.verification.models import VerificationRequest  # noqa: F401
    Base.metadata.create_all(bind=engine)
