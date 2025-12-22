"""
Contracts package - Types, protocols, and ABCs for nagatha_core.

Defines the interfaces and data structures that all components
must adhere to for proper integration.
"""

from .types import TaskStatus, TaskResult, ModuleMetadata, TaskRequest
from .protocols import (
    EventBus,
    ShortTermStore,
    LongTermStore,
    EventStore,
    ModulePlugin,
    Agent,
)

__all__ = [
    # Types
    "TaskStatus",
    "TaskResult",
    "ModuleMetadata",
    "TaskRequest",
    # Protocols
    "EventBus",
    "ShortTermStore",
    "LongTermStore",
    "EventStore",
    "ModulePlugin",
    "Agent",
]
