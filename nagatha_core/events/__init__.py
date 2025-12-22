"""
Events package - Event envelopes and event bus implementations.

Provides event-driven communication primitives for nagatha_core.
Includes event envelope data structures and pub/sub event bus implementations.
"""

from .envelope import EventEnvelope
from .bus import InMemoryEventBus, RedisEventBus

__all__ = [
    "EventEnvelope",
    "InMemoryEventBus",
    "RedisEventBus",
]
