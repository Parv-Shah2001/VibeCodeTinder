"""
Global exception handling for production.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

logger = structlog.get_logger(__name__)

class AppException(HTTPException):
    """Base app exception"""
    def __init__(self, status_code: int, detail: str, code: str | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class RateLimitExceeded(AppException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail, code="RATE_LIMIT")

class ProfileNotFound(AppException):
    def __init__(self):
        super().__init__(status_code=404, detail="Profile not found", code="PROFILE_NOT_FOUND")

class MatchNotFound(AppException):
    def __init__(self):
        super().__init__(status_code=404, detail="Match not found", code="MATCH_NOT_FOUND")

class ConversationNotFound(AppException):
    def __init__(self):
        super().__init__(status_code=404, detail="Conversation not found", code="CONVERSATION_NOT_FOUND")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation_error", path=request.url.path, errors=exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors(), "code": "VALIDATION_ERROR"},
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": getattr(exc, "code", "HTTP_ERROR")},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=request.url.path, error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )
