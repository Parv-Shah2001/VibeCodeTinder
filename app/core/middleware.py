import time
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            "request",
            path=request.url.path,
            method=request.method,
            status=response.status_code,
            duration_ms=round(duration * 1000, 2),
            client=request.client.host if request.client else "unknown",
        )
        # Prometheus metric hook could go here
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate-limit for global API, per-IP.
    Production would use Redis token bucket.
    """
    def __init__(self, app, requests_per_minute: int = 200):
        super().__init__(app)
        self.rpm = requests_per_minute
        self._hits: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        # skip websockets
        if request.url.path.startswith("/api/v1/realtime"):
            return await call_next(request)
        ip = request.client.host if request.client else "0.0.0.0"
        now = time.time()
        window = self._hits.get(ip, [])
        # keep last 60s
        window = [t for t in window if now - t < 60]
        if len(window) >= self.rpm:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        window.append(now)
        self._hits[ip] = window
        return await call_next(request)
