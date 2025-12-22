"""
nagatha_core - Modular AI Orchestration Framework

A Python 3.13+ framework for managing autonomous AI-driven submodules
via a central orchestration system using RabbitMQ and Celery.

Package Structure:
- contracts: Types, protocols, and interfaces
- runtime: Settings, Celery, and Redis factories
- events: Event envelopes and event bus implementations
- agent: Agent base classes and runner infrastructure
- observability: Logging and tracing utilities
"""

__version__ = "0.1.0"
__author__ = "Nagatha Team"

# Legacy imports (backwards compatibility)
from .config import get_config, load_config, FrameworkConfig
from .broker import get_celery_app, register_task
from .registry import get_registry, initialize_registry, TaskRegistry
from .logging import get_logger, configure_logging
from .types import TaskStatus, TaskResult, ModuleMetadata

# New package exports
from . import contracts
from . import runtime
from . import events
from . import agent
from . import observability

__all__ = [
    # Legacy exports
    "get_config",
    "load_config",
    "FrameworkConfig",
    "get_celery_app",
    "register_task",
    "get_registry",
    "initialize_registry",
    "TaskRegistry",
    "get_logger",
    "configure_logging",
    "TaskStatus",
    "TaskResult",
    "ModuleMetadata",
    # New packages
    "contracts",
    "runtime",
    "events",
    "agent",
    "observability",
]
