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
    ProviderRegisterRequest,
    ProviderInfoResponse,
    ProviderTaskSummary,
)
from nagatha_core.api.utils import build_standard_response
from nagatha_core.logging import get_logger
from nagatha_core.registry import get_registry
from nagatha_core.types import TaskStatus
from nagatha_core.providers import get_provider_registry
from nagatha_core.broker import get_celery_app

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
    provider_registry = get_provider_registry()

    # Try provider-based routing first
    provider_task = provider_registry.resolve_task(payload.task_name)
    if provider_task:
        try:
            celery_app = get_celery_app()
            queue = payload.queue or provider_task.queue
            result = celery_app.send_task(
                provider_task.celery_name,
                kwargs=payload.kwargs,
                queue=queue,
            )
            if payload.mode == "sync":
                output = result.get(timeout=payload.timeout_s)
                response.status_code = status.HTTP_200_OK
                response_payload = TaskRunResponse(
                    accepted=True,
                    task_name=payload.task_name,
                    status=TaskStatus.SUCCESS.value,
                    celery_task_id=result.id,
                    result=output,
                    error=None,
                )
                return build_standard_response(request.state.request_id, response_payload)
            response_payload = TaskRunResponse(
                accepted=True,
                task_name=payload.task_name,
                status=TaskStatus.PENDING.value,
                celery_task_id=result.id,
                result=None,
                error=None,
            )
            return build_standard_response(request.state.request_id, response_payload)
        except Exception as exc:
            logger.error("Error routing provider task: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            )

    # Fallback to local registry tasks for backward compatibility
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
    "/tasks/catalog",
    response_model=StandardResponse[List[ProviderTaskSummary]],
    status_code=status.HTTP_200_OK,
    tags=["tasks"],
)
async def task_catalog(request: Request) -> StandardResponse[List[ProviderTaskSummary]]:
    preg = get_provider_registry()
    catalog = preg.task_catalog()
    payload = [
        ProviderTaskSummary(
            name=it["name"],
            provider_id=it["provider_id"],
            version=it.get("version"),
            description=it.get("description"),
            input_schema=it.get("input_schema"),
            output_schema=it.get("output_schema"),
            queue=it.get("queue"),
            retries=it.get("retries"),
            timeout_s=it.get("timeout_s"),
        )
        for it in catalog
    ]
    return build_standard_response(request.state.request_id, payload)


# Provider endpoints

@router.post(
    "/providers/register",
    response_model=StandardResponse[ProviderInfoResponse],
    status_code=status.HTTP_201_CREATED,
    tags=["providers"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def register_provider(
    request: Request,
    payload: ProviderRegisterRequest,
) -> StandardResponse[ProviderInfoResponse]:
    """Register a provider by fetching its manifest and indexing tasks."""
    preg = get_provider_registry()
    try:
        info = await preg.register_provider(payload.provider_id, payload.base_url, payload.manifest_url)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    response_payload = ProviderInfoResponse(
        provider_id=info.provider_id,
        base_url=info.base_url,
        manifest_url=info.manifest_url,
        version=info.version,
        last_seen=info.last_seen.isoformat() if info.last_seen else None,
        tasks=[
            ProviderTaskSummary(
                name=t.name,
                provider_id=info.provider_id,
                version=t.version,
                description=t.description,
                input_schema=t.input_schema,
                output_schema=t.output_schema,
                queue=t.queue,
                retries=t.retries,
                timeout_s=t.timeout_s,
            )
            for t in info.tasks.values()
        ],
    )
    return build_standard_response(request.state.request_id, response_payload)


@router.post(
    "/providers/{provider_id}/refresh",
    response_model=StandardResponse[ProviderInfoResponse],
    status_code=status.HTTP_200_OK,
    tags=["providers"],
)
async def refresh_provider(request: Request, provider_id: str) -> StandardResponse[ProviderInfoResponse]:
    preg = get_provider_registry()
    try:
        info = await preg.refresh_provider(provider_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider not found: {provider_id}")
    response_payload = ProviderInfoResponse(
        provider_id=info.provider_id,
        base_url=info.base_url,
        manifest_url=info.manifest_url,
        version=info.version,
        last_seen=info.last_seen.isoformat() if info.last_seen else None,
        tasks=[
            ProviderTaskSummary(
                name=t.name,
                provider_id=info.provider_id,
                version=t.version,
                description=t.description,
                input_schema=t.input_schema,
                output_schema=t.output_schema,
                queue=t.queue,
                retries=t.retries,
                timeout_s=t.timeout_s,
            )
            for t in info.tasks.values()
        ],
    )
    return build_standard_response(request.state.request_id, response_payload)


@router.get(
    "/providers",
    response_model=StandardResponse[List[ProviderInfoResponse]],
    status_code=status.HTTP_200_OK,
    tags=["providers"],
)
async def list_providers(request: Request) -> StandardResponse[List[ProviderInfoResponse]]:
    preg = get_provider_registry()
    providers = preg.list_providers()
    payload = [
        ProviderInfoResponse(
            provider_id=p.provider_id,
            base_url=p.base_url,
            manifest_url=p.manifest_url,
            version=p.version,
            last_seen=p.last_seen.isoformat() if p.last_seen else None,
            tasks=[
                ProviderTaskSummary(
                    name=t.name,
                    provider_id=p.provider_id,
                    version=t.version,
                    description=t.description,
                    input_schema=t.input_schema,
                    output_schema=t.output_schema,
                    queue=t.queue,
                    retries=t.retries,
                    timeout_s=t.timeout_s,
                )
                for t in p.tasks.values()
            ],
        )
        for p in providers
    ]
    return build_standard_response(request.state.request_id, payload)


@router.get(
    "/providers/{provider_id}",
    response_model=StandardResponse[ProviderInfoResponse],
    status_code=status.HTTP_200_OK,
    tags=["providers"],
)
async def get_provider(request: Request, provider_id: str) -> StandardResponse[ProviderInfoResponse]:
    preg = get_provider_registry()
    p = preg.get_provider(provider_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider not found: {provider_id}")
    payload = ProviderInfoResponse(
        provider_id=p.provider_id,
        base_url=p.base_url,
        manifest_url=p.manifest_url,
        version=p.version,
        last_seen=p.last_seen.isoformat() if p.last_seen else None,
        tasks=[
            ProviderTaskSummary(
                name=t.name,
                provider_id=p.provider_id,
                version=t.version,
                description=t.description,
                input_schema=t.input_schema,
                output_schema=t.output_schema,
                queue=t.queue,
                retries=t.retries,
                timeout_s=t.timeout_s,
            )
            for t in p.tasks.values()
        ],
    )
    return build_standard_response(request.state.request_id, payload)


@router.post(
    "/providers/{provider_id}/heartbeat",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    tags=["providers"],
)
async def heartbeat_provider(request: Request, provider_id: str) -> StandardResponse[dict]:
    preg = get_provider_registry()
    try:
        preg.heartbeat(provider_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider not found: {provider_id}")
    return build_standard_response(request.state.request_id, {"status": "ok", "provider_id": provider_id})


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
