"""
nagatha_core - Modular AI Orchestration Framework

A Python 3.13+ framework for managing autonomous AI-driven submodules
via a central orchestration system using RabbitMQ and Celery.
"""

__version__ = "0.1.0"
__author__ = "Nagatha Team"

from .config import get_config, load_config, FrameworkConfig
from .broker import get_celery_app, register_task
from .registry import get_registry, initialize_registry, TaskRegistry
from .logging import get_logger, configure_logging
from .types import TaskStatus, TaskResult, ModuleMetadata

__all__ = [
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
]
