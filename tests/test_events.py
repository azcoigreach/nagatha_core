"""
Tests for nagatha_core.events package.

Tests event envelopes and event bus implementations.
"""

import pytest
import time
from datetime import datetime
from nagatha_core.events import EventEnvelope, InMemoryEventBus


class TestEventEnvelope:
    """Test EventEnvelope functionality."""
    
    def test_create_envelope(self):
        """Test creating an event envelope."""
        envelope = EventEnvelope(
            source="test_module",
            type="test.event",
            payload={"message": "Hello, World!"},
        )
        
        assert envelope.source == "test_module"
        assert envelope.type == "test.event"
        assert envelope.payload == {"message": "Hello, World!"}
        assert envelope.id is not None
        assert envelope.correlation_id is not None
        assert isinstance(envelope.ts, datetime)
    
    def test_envelope_to_dict(self):
        """Test converting envelope to dictionary."""
        envelope = EventEnvelope(
            source="test",
            type="test.event",
            payload={"data": "test"},
        )
        
        data = envelope.to_dict()
        
        assert data["source"] == "test"
        assert data["type"] == "test.event"
        assert data["payload"] == {"data": "test"}
        assert "id" in data
        assert "ts" in data
        assert "correlation_id" in data
    
    def test_envelope_from_dict(self):
        """Test creating envelope from dictionary."""
        data = {
            "id": "test-id",
            "ts": "2025-01-01T00:00:00+00:00",
            "source": "test",
            "type": "test.event",
            "correlation_id": "corr-123",
            "payload": {"key": "value"},
            "meta": {"tag": "important"},
        }
        
        envelope = EventEnvelope.from_dict(data)
        
        assert envelope.id == "test-id"
        assert envelope.source == "test"
        assert envelope.type == "test.event"
        assert envelope.correlation_id == "corr-123"
        assert envelope.payload == {"key": "value"}
        assert envelope.meta == {"tag": "important"}
    
    def test_with_correlation(self):
        """Test creating envelope with specific correlation ID."""
        original = EventEnvelope(
            source="test",
            type="test.event",
            payload={"data": 1},
        )
        
        related = original.with_correlation("shared-correlation")
        
        assert related.correlation_id == "shared-correlation"
        assert related.source == original.source
        assert related.type == original.type
        assert related.payload == original.payload


class TestInMemoryEventBus:
    """Test InMemoryEventBus functionality."""
    
    def test_publish_subscribe(self):
        """Test basic publish/subscribe."""
        bus = InMemoryEventBus()
        received = []
        
        def handler(event):
            received.append(event)
        
        bus.subscribe("test.topic", handler)
        bus.publish("test.topic", {"type": "test", "data": "hello"})
        
        assert len(received) == 1
        assert received[0]["type"] == "test"
        assert received[0]["data"] == "hello"
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same topic."""
        bus = InMemoryEventBus()
        received1 = []
        received2 = []
        
        bus.subscribe("topic", lambda e: received1.append(e))
        bus.subscribe("topic", lambda e: received2.append(e))
        
        bus.publish("topic", {"msg": "broadcast"})
        
        assert len(received1) == 1
        assert len(received2) == 1
    
    def test_unsubscribe(self):
        """Test unsubscribing from topic."""
        bus = InMemoryEventBus()
        received = []
        
        def handler(event):
            received.append(event)
        
        bus.subscribe("topic", handler)
        bus.publish("topic", {"count": 1})
        
        bus.unsubscribe("topic", handler)
        bus.publish("topic", {"count": 2})
        
        assert len(received) == 1
        assert received[0]["count"] == 1
    
    def test_publish_envelope(self):
        """Test publishing EventEnvelope."""
        bus = InMemoryEventBus()
        received = []
        
        bus.subscribe("test", lambda e: received.append(e))
        
        envelope = EventEnvelope(
            source="test",
            type="test.event",
            payload={"data": "test"},
        )
        
        bus.publish("test", envelope)
        
        assert len(received) == 1
        assert received[0]["type"] == "test.event"
    
    def test_clear(self):
        """Test clearing all subscriptions."""
        bus = InMemoryEventBus()
        bus.subscribe("topic1", lambda e: None)
        bus.subscribe("topic2", lambda e: None)
        
        assert bus.get_subscriber_count("topic1") == 1
        assert bus.get_subscriber_count("topic2") == 1
        
        bus.clear()
        
        assert bus.get_subscriber_count("topic1") == 0
        assert bus.get_subscriber_count("topic2") == 0
