"""Middleware for CORS and rate limiting"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import get_settings
from ..core.exceptions import RateLimitError

settings = get_settings()

# Rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    enabled=settings.rate_limit_enabled,
)


def configure_cors(app) -> None:
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests with timing information"""

    async def dispatch(self, request: Request, call_next):
        import time
        import uuid
        from ..core.logging import get_logger

        logger = get_logger(__name__)

        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "ip_address": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        response: Response = await call_next(request)

        # Log request completion
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "ip_address": request.client.host if request.client else "unknown",
                "duration_ms": duration_ms,
                "status_code": response.status_code,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
