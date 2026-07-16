"""
Notification service: push, in-app, email.
For scale: outbox pattern + worker pool.
"""
import structlog
from app.core.events import event_bus, Events
from app.core.redis import redis_client
import json

logger = structlog.get_logger(__name__)

def send_push_notification(user_id: int, title: str, body: str, data: dict | None = None):
    # Placeholder: would integrate FCM/APNS
    logger.info("push_notification", user_id=user_id, title=title, body=body)
    try:
        redis_client.publish(f"notifications:{user_id}", json.dumps({"title": title, "body": body, "data": data}))
    except Exception:
        pass
    return True

# Event handlers
def on_match_created(payload: dict):
    user1 = payload.get("user1_id")
    user2 = payload.get("user2_id")
    send_push_notification(user1, "It's a Match! 🎉", f"You matched with user {user2}", {"type": "match", "match_id": payload.get("match_id")})
    send_push_notification(user2, "It's a Match! 🎉", f"You matched with user {user1}", {"type": "match", "match_id": payload.get("match_id")})

def on_message_sent(payload: dict):
    # Could send push if recipient offline
    pass

event_bus.subscribe(Events.MATCH_CREATED, on_match_created)
event_bus.subscribe(Events.MESSAGE_SENT, on_message_sent)
