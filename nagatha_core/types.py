"""
Shared data structures and typing for nagatha_core.

DEPRECATED: This module is maintained for backwards compatibility.
New code should import from nagatha_core.contracts.types instead.
"""

# Import from new location for backwards compatibility
from nagatha_core.contracts.types import (
    TaskStatus,
    TaskResult,
    ModuleMetadata,
    TaskRequest,
    ModuleRegistration,
)

__all__ = [
    "TaskStatus",
    "TaskResult",
    "ModuleMetadata",
    "TaskRequest",
    "ModuleRegistration",
]
