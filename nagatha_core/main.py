"""
Main FastAPI application and Celery worker entrypoint.

Serves the HTTP API for task invocation, module discovery, and status tracking.
"""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import get_config
from .registry import initialize_registry
from .logging import get_logger, configure_logging
from .api.schemas import (
    ErrorResponse,
    ModuleInfo,
    PingResponse,
    StandardResponse,
    TaskRunRequest,
    TaskRunResponse,
    TaskStatusResponse,
    TaskSummary,
)
from .api.utils import apply_legacy_headers
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


@app.get(
    "/ping",
    response_model=StandardResponse[PingResponse],
    status_code=status.HTTP_200_OK,
    deprecated=True,
    tags=["system"],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
)
async def legacy_ping(request: Request, response: Response) -> StandardResponse[PingResponse]:
    """Legacy health check endpoint (deprecated)."""
    apply_legacy_headers(response, "/api/v1/ping")
    return await v1_routes.ping(request)


@app.get(
    "/modules",
    response_model=StandardResponse[dict[str, ModuleInfo]],
    status_code=status.HTTP_200_OK,
    deprecated=True,
    tags=["modules"],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
)
async def legacy_list_modules(request: Request, response: Response) -> StandardResponse[dict[str, ModuleInfo]]:
    """Legacy modules listing (deprecated)."""
    apply_legacy_headers(response, "/api/v1/modules")
    return await v1_routes.list_modules(request)


@app.get(
    "/tasks",
    response_model=StandardResponse[list[TaskSummary]],
    status_code=status.HTTP_200_OK,
    deprecated=True,
    tags=["tasks"],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
)
async def legacy_list_tasks(request: Request, response: Response) -> StandardResponse[list[TaskSummary]]:
    """Legacy task listing (deprecated)."""
    apply_legacy_headers(response, "/api/v1/tasks")
    return await v1_routes.list_tasks(request)


@app.post(
    "/tasks/run",
    response_model=StandardResponse[TaskRunResponse],
    status_code=status.HTTP_202_ACCEPTED,
    deprecated=True,
    tags=["tasks"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def legacy_run_task(
    request: Request,
    payload: TaskRunRequest,
    background_tasks: BackgroundTasks,
    response: Response,
) -> StandardResponse[TaskRunResponse]:
    """Legacy task execution endpoint (deprecated)."""
    apply_legacy_headers(response, "/api/v1/tasks/run")
    return await v1_routes.run_task(request, payload, background_tasks, response)


@app.get(
    "/tasks/{task_id}",
    response_model=StandardResponse[TaskStatusResponse],
    status_code=status.HTTP_200_OK,
    deprecated=True,
    tags=["tasks"],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
)
async def legacy_get_task_status(
    request: Request,
    response: Response,
    task_id: str,
) -> StandardResponse[TaskStatusResponse]:
    """Legacy task status endpoint (deprecated)."""
    apply_legacy_headers(response, f"/api/v1/tasks/{task_id}")
    return await v1_routes.get_task_status(request, task_id)


@app.get(
    "/status/{task_id}",
    response_model=StandardResponse[TaskStatusResponse],
    status_code=status.HTTP_200_OK,
    deprecated=True,
    tags=["tasks"],
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
)
async def legacy_get_status(
    request: Request,
    response: Response,
    task_id: str,
) -> StandardResponse[TaskStatusResponse]:
    """Legacy alias for task status (deprecated)."""
    apply_legacy_headers(response, f"/api/v1/tasks/{task_id}")
    return await v1_routes.get_task_status(request, task_id)


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
