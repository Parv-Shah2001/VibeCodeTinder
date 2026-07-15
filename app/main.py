"""
VibeCodeTinder - Modular Monolithic Tinder Replica
Production-ready FastAPI app targeting:
- 50M users
- 1M DAU
- 500k new profiles/day
- 1B matches/day (design)
- 200M messages/day
- 10M media uploads/day

Modular Monolith Architecture:
Each module has its own domain (models, schemas, service, repository, router) and communicates via events.
Deployment: Single binary, but modules can be extracted to microservices later with minimal coupling.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.logger import setup_logging
from app.core.middleware import LoggingMiddleware, RateLimitMiddleware
from app.core.database import init_db
from app.core import events as events_module  # ensure subscriptions
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Ensure all event subscribers are imported
import app.modules.notifications.service  # noqa
import app.modules.analytics.service  # noqa
import app.modules.users.service  # noqa

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print(f"🚀 {settings.APP_NAME} starting in {settings.ENV} mode")
    print(f"📦 DATABASE: {'SQLite (local)' if settings.is_sqlite else 'PostgreSQL'}")
    print(f"⚡ REDIS: {settings.REDIS_URL}")
    print(f"📸 S3: {settings.S3_ENDPOINT_URL or 'local filesystem fallback'}")
    yield
    print("👋 Shutting down")

app = FastAPI(
    title="VibeCodeTinder API",
    description="""
    ## Tinder Replica - Production Modular Monolith

    ### Scale Targets
    - **50M users**, **1M DAU**
    - **500k new profiles/day**
    - **1B matches/day** (architected)
    - **200M messages/day**
    - **10M media uploads/day**

    ### Modules
    - Auth, Users, Media (S3), Discovery (Recommendation Engine), Swipes, Matches, Messaging (WebSocket), Subscriptions, Moderation, Notifications, Analytics, Admin

    ### Architecture Notes
    - Modular monolith with event bus for decoupling (Redis Streams ready)
    - Redis for caching, rate limiting, pub/sub, bloom filter swipes
    - S3 for media storage with CDN + local fallback
    - Geo-indexing + Elo recommendation + newbie boost
    - WebSocket real-time messaging with horizontal scale via Redis PubSub
    - Production patterns: rate limiting, pagination, observability, Prometheus metrics, structured logging

    ### Quick Start
    1. Register -> get token
    2. Create profile
    3. Upload photos
    4. GET /api/v1/discovery/feed
    5. POST /api/v1/swipes
    6. On match -> conversation auto-created
    7. Messaging via REST + WS /api/v1/messaging/ws?token=...

    See /docs for interactive API.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=300)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"] if settings.ENV != "production" else settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.media.router import router as media_router
from app.modules.discovery.router import router as discovery_router
from app.modules.swipes.router import router as swipes_router
from app.modules.matches.router import router as matches_router
from app.modules.messaging.router import router as messaging_router
from app.modules.notifications.router import router as notif_router
from app.modules.subscriptions.router import router as subs_router
from app.modules.moderation.router import router as mod_router
from app.modules.analytics.router import router as analytics_router
from app.modules.admin.router import router as admin_router

v1_prefix = settings.API_V1_PREFIX

app.include_router(auth_router, prefix=v1_prefix)
app.include_router(users_router, prefix=v1_prefix)
app.include_router(media_router, prefix=v1_prefix)
app.include_router(discovery_router, prefix=v1_prefix)
app.include_router(swipes_router, prefix=v1_prefix)
app.include_router(matches_router, prefix=v1_prefix)
app.include_router(messaging_router, prefix=v1_prefix)
app.include_router(notif_router, prefix=v1_prefix)
app.include_router(subs_router, prefix=v1_prefix)
app.include_router(mod_router, prefix=v1_prefix)
app.include_router(analytics_router, prefix=v1_prefix)
app.include_router(admin_router, prefix=v1_prefix)

# Health - detailed for k8s liveness/readiness
@app.get("/health", tags=["health"])
def health():
    # Check DB, Redis, S3
    checks = {"api": "ok"}
    # DB
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"fail: {str(e)}"
    # Redis
    try:
        from app.core.redis import redis_client
        redis_client.get("healthcheck")
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"fail: {str(e)}"
    # S3/storage
    try:
        from app.core.s3 import get_storage
        storage = get_storage()
        checks["storage"] = "s3" if storage.use_s3 else "local"
    except Exception as e:
        checks["storage"] = f"fail: {str(e)}"

    return {"status": "ok" if all(v in ("ok","s3","local") for v in checks.values()) else "degraded", "env": settings.ENV, "app": settings.APP_NAME, "checks": checks}

@app.get("/ready", tags=["health"])
def ready():
    return {"status": "ready"}

@app.get("/", tags=["health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "api": v1_prefix,
        "metrics": "/metrics",
    }

# Static for local media fallback
storage_path = "./storage"
os.makedirs(storage_path, exist_ok=True)
if os.path.exists(storage_path):
    app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

# Metrics endpoint Prometheus
@app.get("/metrics", tags=["health"])
def metrics():
    try:
        from app.core.metrics import get_metrics
        from prometheus_client import CONTENT_TYPE_LATEST
        data = get_metrics()
        return PlainTextResponse(content=data.decode("utf-8") if isinstance(data, bytes) else data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        return JSONResponse({"status": "metrics error", "error": str(e)})
