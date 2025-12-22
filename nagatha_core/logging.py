"""
Unified structured logging configuration for nagatha_core.

DEPRECATED: This module is maintained for backwards compatibility.
New code should import from nagatha_core.observability.logging instead.
"""

# Import from new location for backwards compatibility
from nagatha_core.observability.logging import (
    get_logger,
    configure_logging,
    StructuredLogger,
    LoggerFactory,
)

__all__ = [
    "get_logger",
    "configure_logging",
    "StructuredLogger",
    "LoggerFactory",
]
