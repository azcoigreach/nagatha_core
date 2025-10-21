"""
Shared data structures and typing for nagatha_core.

Defines common types, dataclasses, and type hints used across
the framework for consistency and IDE support.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    """Enum for task execution status."""
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


@dataclass
class TaskResult:
    """Represents the result of a Celery task execution."""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class ModuleMetadata:
    """Metadata about a registered module."""
    name: str
    description: str
    version: str
    tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    has_heartbeat: bool = False
    config_schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tasks": self.tasks,
            "has_heartbeat": self.has_heartbeat,
            "config_schema": self.config_schema,
        }


@dataclass
class TaskRequest:
    """Represents a task execution request."""
    task_name: str
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    retry: bool = True
    timeout: Optional[int] = None

    def validate(self) -> bool:
        """Validate the task request."""
        return bool(self.task_name) and isinstance(self.kwargs, dict)


class ModuleRegistration:
    """Callable type for module registration functions."""
    __call__: Callable[[], None]
