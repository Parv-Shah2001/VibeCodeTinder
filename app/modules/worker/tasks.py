"""
Async tasks for scale: media processing, email push, recommendation cache refresh, daily metrics.
"""
from .celery_app import celery_app
import structlog

logger = structlog.get_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_media_task(self, media_asset_id: int):
    try:
        from app.core.database import SessionLocal
        from app.modules.media.models import MediaAsset
        from app.modules.media.processor import process_image
        from app.core.s3 import get_storage
        import io

        db = SessionLocal()
        asset = db.query(MediaAsset).filter(MediaAsset.id == media_asset_id).first()
        if not asset:
            return {"status": "not_found"}

        # In real flow, fetch raw from incoming bucket, process, re-upload
        # For MVP we already processed sync, so just mark ready
        asset.status = "ready"
        db.commit()
        logger.info("media_processed_async", asset_id=media_asset_id)
        return {"status": "processed", "asset_id": media_asset_id}
    except Exception as e:
        logger.error("media_process_failed", asset_id=media_asset_id, error=str(e))
        raise self.retry(exc=e, countdown=60)

@celery_app.task
def send_push_notification_task(user_id: int, title: str, body: str, data: dict | None = None):
    from app.modules.notifications.service import send_push_notification
    send_push_notification(user_id, title, body, data)
    return {"status": "sent"}

@celery_app.task
def send_email_task(to: str, subject: str, body: str):
    logger.info("email_task_queued", to=to, subject=subject)
    # In prod: ses.send_email
    return {"status": "queued"}

@celery_app.task
def refresh_recommendation_cache_task(user_id: int):
    from app.core.database import SessionLocal
    from app.modules.discovery.engine import get_recommendations
    db = SessionLocal()
    try:
        recs = get_recommendations(db, user_id, limit=20)
        logger.info("rec_cache_refreshed", user_id=user_id, count=len(recs))
        return {"count": len(recs)}
    finally:
        db.close()

@celery_app.task
def compute_daily_metrics_task(date_str: str):
    from app.core.database import SessionLocal
    from app.modules.analytics.models import DailyMetrics
    from datetime import datetime
    db = SessionLocal()
    try:
        # In prod aggregation query from analytics_events
        dm = db.query(DailyMetrics).filter(DailyMetrics.date == date_str).first()
        if not dm:
            dm = DailyMetrics(date=date_str)
            db.add(dm)
            db.commit()
        logger.info("daily_metrics_computed", date=date_str)
        return {"date": date_str}
    finally:
        db.close()

@celery_app.task
def cleanup_old_data_task(days: int = 90):
    """
    Cleanup old swipes, messages archived to S3, etc.
    For 50M users scale we need TTL.
    """
    from app.core.database import SessionLocal
    from datetime import datetime, timedelta
    from app.modules.swipes.models import Swipe
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(Swipe).filter(Swipe.created_at < cutoff).delete()
        db.commit()
        logger.info("cleanup_old_swipes", deleted=deleted, cutoff=str(cutoff))
        return {"deleted_swipes": deleted}
    finally:
        db.close()
