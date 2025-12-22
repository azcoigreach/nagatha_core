"""
Tracing and correlation ID utilities.

Provides correlation ID generation, storage, and context management
for distributed tracing across the framework.
"""

import uuid
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Generator, Optional


# Context variable for correlation ID
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.
    
    Returns:
        UUID string suitable for correlation tracking
        
    Example:
        >>> from nagatha_core.observability import generate_correlation_id
        >>> corr_id = generate_correlation_id()
        >>> print(corr_id)
        '550e8400-e29b-41d4-a716-446655440000'
    """
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID from context.
    
    Returns:
        Current correlation ID or None if not set
        
    Example:
        >>> from nagatha_core.observability import get_correlation_id, set_correlation_id
        >>> set_correlation_id("test-123")
        >>> get_correlation_id()
        'test-123'
    """
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID in current context.
    
    Args:
        correlation_id: Correlation ID to set
        
    Example:
        >>> from nagatha_core.observability import set_correlation_id, get_correlation_id
        >>> set_correlation_id("my-correlation-id")
        >>> assert get_correlation_id() == "my-correlation-id"
    """
    _correlation_id.set(correlation_id)


def clear_correlation_id() -> None:
    """
    Clear the correlation ID from current context.
    
    Example:
        >>> from nagatha_core.observability import set_correlation_id, clear_correlation_id, get_correlation_id
        >>> set_correlation_id("test")
        >>> clear_correlation_id()
        >>> assert get_correlation_id() is None
    """
    _correlation_id.set(None)


@contextmanager
def correlation_context(correlation_id: Optional[str] = None) -> Generator[str, None, None]:
    """
    Context manager for correlation ID.
    
    Automatically sets and clears correlation ID for a code block.
    Generates a new ID if none provided.
    
    Args:
        correlation_id: Optional correlation ID (generates new if None)
        
    Yields:
        The correlation ID being used
        
    Example:
        >>> from nagatha_core.observability import correlation_context, get_correlation_id
        >>> with correlation_context() as corr_id:
        ...     print(f"Using: {corr_id}")
        ...     print(f"Context has: {get_correlation_id()}")
        Using: 550e8400-...
        Context has: 550e8400-...
        >>> # After context, it's cleared
        >>> assert get_correlation_id() is None
    """
    # Generate if not provided
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    # Save previous value
    previous = _correlation_id.get()
    
    try:
        # Set new value
        _correlation_id.set(correlation_id)
        yield correlation_id
    finally:
        # Restore previous value
        _correlation_id.set(previous)


def extract_correlation_id_from_headers(headers: dict) -> Optional[str]:
    """
    Extract correlation ID from HTTP headers.
    
    Looks for common header names:
    - X-Correlation-ID
    - X-Request-ID
    - X-Trace-ID
    
    Args:
        headers: HTTP headers dictionary
        
    Returns:
        Correlation ID if found, None otherwise
        
    Example:
        >>> headers = {"X-Correlation-ID": "abc-123"}
        >>> extract_correlation_id_from_headers(headers)
        'abc-123'
    """
    # Common header names (case-insensitive)
    header_names = [
        "x-correlation-id",
        "x-request-id",
        "x-trace-id",
    ]
    
    # Normalize headers to lowercase
    normalized = {k.lower(): v for k, v in headers.items()}
    
    for name in header_names:
        if name in normalized:
            return normalized[name]
    
    return None


def inject_correlation_id_into_headers(
    headers: dict,
    correlation_id: Optional[str] = None,
) -> dict:
    """
    Inject correlation ID into HTTP headers.
    
    Args:
        headers: Existing headers dictionary
        correlation_id: Correlation ID to inject (uses current context if None)
        
    Returns:
        Updated headers dictionary
        
    Example:
        >>> from nagatha_core.observability import inject_correlation_id_into_headers, set_correlation_id
        >>> set_correlation_id("test-123")
        >>> headers = inject_correlation_id_into_headers({})
        >>> headers["X-Correlation-ID"]
        'test-123'
    """
    if correlation_id is None:
        correlation_id = get_correlation_id()
    
    if correlation_id:
        headers = headers.copy()
        headers["X-Correlation-ID"] = correlation_id
    
    return headers
