"""
Event envelope data structure.

Provides a standardized container for events with metadata
for correlation, tracing, and routing.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class EventEnvelope:
    """
    Standard envelope for events in nagatha_core.
    
    Wraps event payloads with metadata for routing, correlation,
    and observability.
    
    Attributes:
        id: Unique event identifier (UUID)
        ts: Timestamp when event was created (UTC)
        source: Source system/module that created the event
        type: Event type/name (e.g., "task.started", "agent.action")
        correlation_id: ID to correlate related events
        payload: Event-specific data
        meta: Additional metadata (tags, priority, etc.)
        
    Example:
        >>> envelope = EventEnvelope(
        ...     source="echo_bot",
        ...     type="task.completed",
        ...     payload={"result": "Hello, World!"},
        ... )
        >>> envelope.id
        '...'  # Auto-generated UUID
        >>> envelope.correlation_id
        '...'  # Auto-generated if not provided
    """
    
    source: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert envelope to dictionary for serialization.
        
        Returns:
            Dictionary representation of the envelope
        """
        return {
            "id": self.id,
            "ts": self.ts.isoformat(),
            "source": self.source,
            "type": self.type,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
            "meta": self.meta,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventEnvelope":
        """
        Create envelope from dictionary.
        
        Args:
            data: Dictionary with envelope fields
            
        Returns:
            EventEnvelope instance
        """
        # Parse timestamp if it's a string
        ts = data.get("ts")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            ts=ts,
            source=data["source"],
            type=data["type"],
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            payload=data.get("payload", {}),
            meta=data.get("meta", {}),
        )
    
    def with_correlation(self, correlation_id: str) -> "EventEnvelope":
        """
        Create a new envelope with a specific correlation ID.
        
        Useful for creating related events that share the same correlation.
        
        Args:
            correlation_id: Correlation ID to use
            
        Returns:
            New EventEnvelope with updated correlation_id
        """
        return EventEnvelope(
            source=self.source,
            type=self.type,
            payload=self.payload,
            correlation_id=correlation_id,
            meta=self.meta.copy(),
        )
    
    def __repr__(self) -> str:
        """String representation of the envelope."""
        return (
            f"EventEnvelope(id={self.id[:8]}..., "
            f"type={self.type}, source={self.source}, "
            f"correlation_id={self.correlation_id[:8]}...)"
        )
