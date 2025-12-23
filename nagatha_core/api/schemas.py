"""
Pydantic schemas for the public API.

Defines request/response contracts, error envelopes, and documented examples.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standard response envelope for successful API responses."""

    request_id: str = Field(..., description="Request correlation identifier.")
    data: T

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "request_id": "req_12345",
                    "data": {},
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response model."""

    code: str = Field(..., description="Machine-readable error code.")
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[Any] = Field(
        default=None,
        description="Optional structured details about the error.",
    )
    request_id: str = Field(..., description="Request correlation identifier.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": {"field": "task_name", "issue": "field required"},
                    "request_id": "req_12345",
                }
            ]
        }
    }


class PingResponse(BaseModel):
    """Health response payload."""

    status: str = Field(..., example="healthy")
    version: str = Field(..., example="0.1.0")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "0.1.0",
                }
            ]
        }
    }


class TaskRunRequest(BaseModel):
    """Request body for running a task."""

    task_name: str = Field(..., example="echo_bot.echo")
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    mode: Literal["async", "sync"] = Field(default="async")
    queue: Optional[str] = Field(default=None, example="default")
    timeout_s: Optional[int] = Field(default=None, ge=1, example=30)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_name": "echo_bot.echo",
                    "kwargs": {"message": "Hello world"},
                    "mode": "async",
                }
            ]
        }
    }


class TaskRunResponse(BaseModel):
    """Response data for a task run request."""

    accepted: bool
    task_name: str
    status: str
    celery_task_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "accepted": True,
                    "task_name": "echo_bot.echo",
                    "status": "pending",
                    "celery_task_id": "6dc18df9-5bf6-4bb6-9f96-d76d4e5b0c8b",
                    "result": None,
                    "error": None,
                }
            ]
        }
    }


class TaskStatusResponse(BaseModel):
    """Response data for task status lookups."""

    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_id": "6dc18df9-5bf6-4bb6-9f96-d76d4e5b0c8b",
                    "status": "pending",
                    "result": None,
                    "error": None,
                    "created_at": "2024-01-01T12:00:00Z",
                    "completed_at": None,
                }
            ]
        }
    }


class TaskSummary(BaseModel):
    """Summary of an available task."""

    name: str
    module: str
    description: str
    kwargs_schema: Optional[Dict[str, Any]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "echo_bot.echo",
                    "module": "echo_bot",
                    "description": "Echo a message back.",
                    "kwargs_schema": {
                        "title": "EchoKwargs",
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                        "required": ["message"],
                    },
                }
            ]
        }
    }


class ModuleInfo(BaseModel):
    """Response model for module information."""

    name: str
    description: str
    version: str
    tasks: Dict[str, Any] = Field(default_factory=dict)
    has_heartbeat: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "echo_bot",
                    "description": "echo_bot - A simple test module that echoes messages.",
                    "version": "0.1.0",
                    "tasks": {
                        "echo": {
                            "name": "echo_bot.echo",
                            "doc": "Echo a message back.",
                        }
                    },
                    "has_heartbeat": True,
                }
            ]
        }
    }


# Provider API Schemas

class ProviderRegisterRequest(BaseModel):
    """Request body to register a provider."""

    provider_id: str = Field(..., example="image_service")
    base_url: str = Field(..., example="http://image-service:8080")
    manifest_url: Optional[str] = Field(
        default=None, example="http://image-service:8080/.well-known/nagatha/manifest"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "provider_id": "echo_provider",
                    "base_url": "http://echo:8001",
                }
            ]
        }
    }


class ProviderTaskSummary(BaseModel):
    name: str
    provider_id: str
    version: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    queue: Optional[str] = None
    retries: Optional[int] = None
    timeout_s: Optional[int] = None


class ProviderInfoResponse(BaseModel):
    provider_id: str
    base_url: str
    manifest_url: str
    version: str
    last_seen: Optional[str] = None
    tasks: List[ProviderTaskSummary] = Field(default_factory=list)

