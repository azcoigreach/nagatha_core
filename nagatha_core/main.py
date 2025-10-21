"""
Main FastAPI application and Celery worker entrypoint.

Serves the HTTP API for task invocation, module discovery, and status tracking.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from .config import get_config
from .registry import get_registry, initialize_registry
from .types import TaskRequest, TaskStatus
from .logging import get_logger, configure_logging
from .broker import get_celery_app

logger = get_logger(__name__)


# Pydantic models for API
class RunTaskRequest(BaseModel):
    """Request model for running a task."""
    task_name: str
    kwargs: Dict[str, Any] = {}


class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    task_id: str
    status: str
    result: Any = None
    error: str | None = None


class ModuleInfo(BaseModel):
    """Response model for module information."""
    name: str
    description: str
    version: str
    tasks: Dict[str, Any] = {}
    has_heartbeat: bool = False


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str


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


@app.get("/ping", response_model=HealthResponse)
async def ping():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
    }


@app.get("/modules", response_model=Dict[str, ModuleInfo])
async def list_modules():
    """
    List all registered modules and their tasks.
    
    Returns:
        Dictionary of module information
    """
    registry = get_registry()
    modules = registry.list_modules()
    
    result = {}
    for name, metadata in modules.items():
        result[name] = ModuleInfo(
            name=metadata.name,
            description=metadata.description,
            version=metadata.version,
            tasks=metadata.tasks,
            has_heartbeat=metadata.has_heartbeat,
        )
    
    return result


@app.get("/tasks")
async def list_tasks():
    """
    List all available tasks grouped by module.
    
    Returns:
        Dictionary mapping modules to their tasks
    """
    registry = get_registry()
    return registry.list_tasks()


@app.post("/tasks/run")
async def run_task(request: RunTaskRequest, background_tasks: BackgroundTasks):
    """
    Queue a task for execution.
    
    Args:
        request: Task request with name and kwargs
        background_tasks: Background tasks context
        
    Returns:
        Task ID and status
        
    Raises:
        HTTPException: If task not found
    """
    if not request.task_name:
        raise HTTPException(status_code=400, detail="task_name is required")
    
    registry = get_registry()
    task = registry.get_task(request.task_name)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task not found: {request.task_name}",
        )
    
    try:
        task_id = registry.run_task(request.task_name, **request.kwargs)
        return {
            "task_id": task_id,
            "status": TaskStatus.PENDING.value,
            "task_name": request.task_name,
        }
    except Exception as e:
        logger.error(f"Error running task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a running task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status and result
    """
    registry = get_registry()
    task_result = registry.get_task_status(task_id)
    
    return task_result.to_dict()


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """
    Alias for /tasks/{task_id}.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status and result
    """
    return await get_task_status(task_id)


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
