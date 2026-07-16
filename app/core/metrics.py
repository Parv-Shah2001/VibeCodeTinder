"""
Prometheus metrics for production observability.
Tracks scale targets: swipes, matches, messages, media uploads.
"""
from prometheus_client import Counter, Histogram, Gauge
import time

# Counters
swipe_counter = Counter("vibe_swipes_total", "Total swipes", ["type"])
match_counter = Counter("vibe_matches_total", "Total matches created")
message_counter = Counter("vibe_messages_total", "Total messages sent", ["type"])
media_upload_counter = Counter("vibe_media_uploads_total", "Media uploads", ["type"])
user_registration_counter = Counter("vibe_registrations_total", "User registrations")

# Histograms
request_duration = Histogram("vibe_request_duration_seconds", "Request duration", ["method", "endpoint"])
swipe_duration = Histogram("vibe_swipe_duration_seconds", "Swipe processing time")
recommendation_duration = Histogram("vibe_recommendation_duration_seconds", "Recommendation generation time")
media_processing_duration = Histogram("vibe_media_processing_seconds", "Media processing time")
message_send_duration = Histogram("vibe_message_send_seconds", "Message send time")

# Gauges
active_websocket_connections = Gauge("vibe_ws_active_connections", "Active WS connections")
online_users = Gauge("vibe_online_users", "Online users")
discovery_cache_hit = Counter("vibe_discovery_cache_total", "Discovery cache hits/misses", ["result"])
db_pool_size = Gauge("vibe_db_pool_size", "DB connection pool size")

class MetricsMiddleware:
    """Middleware to collect request metrics"""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start = time.time()
        method = scope["method"]
        path = scope["path"]

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start
                request_duration.labels(method=method, endpoint=path).observe(duration)
            await send(message)

        await self.app(scope, receive, send_wrapper)

def get_metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest()
