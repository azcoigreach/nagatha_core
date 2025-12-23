"""
Versioned API routes for v1.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response, status

from nagatha_core.api.schemas import (
    ErrorResponse,
    ModuleInfo,
    PingResponse,
    StandardResponse,
    TaskRunRequest,
    TaskRunResponse,
    TaskStatusResponse,
    TaskSummary,
)
from nagatha_core.api.utils import build_standard_response
from nagatha_core.logging import get_logger
from nagatha_core.registry import get_registry
from nagatha_core.types import TaskStatus

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1")


@router.get(
    "/ping",
    response_model=StandardResponse[PingResponse],
    status_code=status.HTTP_200_OK,
    tags=["system"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def ping(request: Request) -> StandardResponse[PingResponse]:
    """Health check endpoint."""
    payload = PingResponse(status="healthy", version="0.1.0")
    return build_standard_response(request.state.request_id, payload)


@router.get(
    "/modules",
    response_model=StandardResponse[Dict[str, ModuleInfo]],
    status_code=status.HTTP_200_OK,
    tags=["modules"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def list_modules(request: Request) -> StandardResponse[Dict[str, ModuleInfo]]:
    """List all registered modules and their tasks."""
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

    return build_standard_response(request.state.request_id, result)


@router.get(
    "/tasks",
    response_model=StandardResponse[List[TaskSummary]],
    status_code=status.HTTP_200_OK,
    tags=["tasks"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def list_tasks(request: Request) -> StandardResponse[List[TaskSummary]]:
    """List available tasks and their schemas."""
    registry = get_registry()
    tasks = registry.list_task_summaries()
    return build_standard_response(request.state.request_id, tasks)


@router.post(
    "/tasks/run",
    response_model=StandardResponse[TaskRunResponse],
    status_code=status.HTTP_202_ACCEPTED,
    tags=["tasks"],
    responses={
        status.HTTP_200_OK: {"model": StandardResponse[TaskRunResponse]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def run_task(
    request: Request,
    payload: TaskRunRequest,
    background_tasks: BackgroundTasks,
    response: Response,
) -> StandardResponse[TaskRunResponse]:
    """Queue or run a task for execution."""
    registry = get_registry()

    task = registry.get_task(payload.task_name)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {payload.task_name}",
        )

    validation_error = registry.validate_task_kwargs(payload.task_name, payload.kwargs)
    if validation_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation_error,
        )

    try:
        if payload.mode == "sync":
            result = registry.run_task_sync(
                payload.task_name,
                timeout_s=payload.timeout_s,
                queue=payload.queue,
                **payload.kwargs,
            )
            response.status_code = status.HTTP_200_OK
            response_payload = TaskRunResponse(
                accepted=True,
                task_name=payload.task_name,
                status=TaskStatus.SUCCESS.value,
                celery_task_id=result.get("task_id"),
                result=result.get("result"),
                error=None,
            )
            return build_standard_response(request.state.request_id, response_payload)

        task_id = registry.run_task(
            payload.task_name,
            queue=payload.queue,
            **payload.kwargs,
        )
        response_payload = TaskRunResponse(
            accepted=True,
            task_name=payload.task_name,
            status=TaskStatus.PENDING.value,
            celery_task_id=task_id,
            result=None,
            error=None,
        )
        return build_standard_response(request.state.request_id, response_payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error running task: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/tasks/{task_id}",
    response_model=StandardResponse[TaskStatusResponse],
    status_code=status.HTTP_200_OK,
    tags=["tasks"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def get_task_status(
    request: Request,
    task_id: str,
) -> StandardResponse[TaskStatusResponse]:
    """Get the status of a running task."""
    registry = get_registry()
    task_result = registry.get_task_status(task_id)
    return build_standard_response(
        request.state.request_id,
        TaskStatusResponse(**task_result.to_dict()),
    )
