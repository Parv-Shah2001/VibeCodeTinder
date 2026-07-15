"""
Internal Event Bus for modular monolith decoupling.
Modules communicate via events rather than direct imports where possible.
In production scale, this could be backed by Redis Streams / Kafka, but for monolith we keep in-process pub/sub + optional redis publish.
"""
import asyncio
from typing import Callable, Dict, List, Any, DefaultDict
from collections import defaultdict
import structlog

logger = structlog.get_logger(__name__)

class EventBus:
    def __init__(self):
        self._handlers: DefaultDict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Callable):
        self._handlers[event_name].append(handler)
        logger.info("event_subscribed", event_name=event_name, handler_name=handler.__name__)

    def unsubscribe(self, event_name: str, handler: Callable):
        if handler in self._handlers[event_name]:
            self._handlers[event_name].remove(handler)

    async def publish_async(self, event_name: str, payload: Any):
        handlers = self._handlers.get(event_name, [])
        logger.info("event_published", event_name=event_name, handlers_count=len(handlers))
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                logger.error("event_handler_failed", event_name=event_name, error_msg=str(e))

    def publish(self, event_name: str, payload: Any):
        # Try to publish synchronously; if in async context, schedule
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.publish_async(event_name, payload))
            else:
                loop.run_until_complete(self.publish_async(event_name, payload))
        except RuntimeError:
            # No event loop, run handlers sync
            for handler in self._handlers.get(event_name, []):
                try:
                    handler(payload)
                except Exception as e:
                    logger.error("event_handler_failed_sync", event_name=event_name, error_msg=str(e))

        # Also publish to redis for horizontally scaled instances
        try:
            from app.core.redis import redis_client
            import json
            redis_client.publish(f"events:{event_name}", json.dumps(payload, default=str))
        except Exception:
            pass

# global singleton
event_bus = EventBus()

# Event names constants
class Events:
    USER_REGISTERED = "user.registered"
    PROFILE_CREATED = "profile.created"
    PROFILE_UPDATED = "profile.updated"
    MEDIA_UPLOADED = "media.uploaded"
    SWIPE_CREATED = "swipe.created"
    MATCH_CREATED = "match.created"
    MESSAGE_SENT = "message.sent"
    USER_ONLINE = "user.online"
    USER_OFFLINE = "user.offline"
