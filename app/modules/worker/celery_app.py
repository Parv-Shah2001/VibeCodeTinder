"""
Celery worker for async jobs at scale: media processing, email, push, analytics batch, recommendation precompute.

For 10M media uploads/day we cannot process sync in API – need worker pool.
"""
try:
    from celery import Celery
    _celery_available = True
except ImportError:
    _celery_available = False

from app.core.config import settings

if _celery_available:
    celery_app = Celery(
        "vibe_worker",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["app.modules.worker.tasks"],
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        worker_max_tasks_per_child=1000,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )
else:
    # Mock for dev without celery
    class MockCelery:
        def task(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
    celery_app = MockCelery()
