"""
Main FastAPI application and Celery worker entrypoint.

Serves the HTTP API for task invocation, module discovery, and status tracking.
"""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import get_config
from .registry import initialize_registry
from .logging import get_logger, configure_logging
from .api.schemas import ErrorResponse
from .api import v1 as v1_routes

logger = get_logger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app startup and shutdown.
    
    Startup: Initialize registry and discover modules
    Shutdown: Cleanup resources
    """
    # Startup
    logger.info("Starting nagatha_core")
    config = get_config()
    configure_logging(config.logging.level, config.logging.log_file)
    
    # Initialize module registry
    initialize_registry(config.module_paths)
    
    yield
    
    # Shutdown
    logger.info("Shutting down nagatha_core")


# Create FastAPI app
app = FastAPI(
    title="nagatha_core",
    description="Modular AI Orchestration Framework",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Attach a request ID to all responses."""
    request_id = request.headers.get("X-Request-ID", f"req_{uuid4().hex}")
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return consistent validation error responses."""
    request_id = getattr(request.state, "request_id", f"req_{uuid4().hex}")
    payload = ErrorResponse(
        code="validation_error",
        message="Request validation failed.",
        details=exc.errors(),
        request_id=request_id,
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return consistent HTTP error responses."""
    request_id = getattr(request.state, "request_id", f"req_{uuid4().hex}")
    details = exc.detail if not isinstance(exc.detail, str) else None
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    payload = ErrorResponse(
        code="http_error",
        message=message,
        details=details,
        request_id=request_id,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return consistent unexpected error responses."""
    request_id = getattr(request.state, "request_id", f"req_{uuid4().hex}")
    logger.error("Unhandled exception: %s", exc)
    payload = ErrorResponse(
        code="internal_error",
        message="Unexpected server error.",
        details=str(exc),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload.model_dump(),
    )


app.include_router(v1_routes.router)


if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        workers=config.api.workers,
    )
