"""FastAPI application entry point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from . import __version__
from .api.middleware import RequestLoggingMiddleware, configure_cors, limiter
from .api.routes import router
from .core.config import get_settings
from .core.exceptions import AppException
from .core.logging import get_logger, setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger = get_logger(__name__)
    logger.info("Application startup", extra={"version": __version__, "env": settings.app_env})

    # Create storage directories if they don't exist
    import os
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    logger.info("Storage directories initialized")

    yield

    logger.info("Application shutdown")


# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title="GeminiWatermarkTool API",
    description="Web API for removing Gemini watermarks from images",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS
configure_cors(app)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.state.limiter = limiter


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger = get_logger(__name__)
    logger.warning(
        f"Application exception: {exc.message}",
        extra={
            "error": exc.__class__.__name__,
            "status_code": exc.status_code,
            "details": exc.details,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceptions"""
    logger = get_logger(__name__)
    logger.warning(
        "Rate limit exceeded",
        extra={
            "ip_address": request.client.host if request.client else "unknown",
        },
    )
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "RateLimitExceeded",
            "message": "Too many requests. Please try again later.",
            "details": {"limit": f"{settings.rate_limit_per_minute} requests per minute"},
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger = get_logger(__name__)
    logger.error(
        f"Unexpected exception: {str(exc)}",
        exc_info=True,
        extra={
            "error": exc.__class__.__name__,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )


# Register routes
app.include_router(router, tags=["health"])


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirect to docs"""
    return {
        "message": "GeminiWatermarkTool API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
