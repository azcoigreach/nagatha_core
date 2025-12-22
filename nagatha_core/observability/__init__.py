"""
Observability package - Logging and tracing utilities.

Provides structured logging, correlation ID tracking, and tracing
helpers for better observability across the framework.
"""

from .logging import (
    get_logger,
    configure_logging,
    StructuredLogger,
)
from .tracing import (
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    correlation_context,
)

__all__ = [
    # Logging
    "get_logger",
    "configure_logging",
    "StructuredLogger",
    # Tracing
    "generate_correlation_id",
    "get_correlation_id",
    "set_correlation_id",
    "clear_correlation_id",
    "correlation_context",
]
