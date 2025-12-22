"""
Event bus implementations.

Provides in-memory and Redis-backed event bus implementations
for publish/subscribe messaging patterns.
"""

import json
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict
import threading

from redis import Redis

from ..contracts.protocols import EventBus as EventBusProtocol
from .envelope import EventEnvelope


class InMemoryEventBus:
    """
    In-memory event bus for testing and development.
    
    Simple pub/sub implementation using Python data structures.
    Not suitable for production or multi-process scenarios.
    
    Example:
        >>> bus = InMemoryEventBus()
        >>> def handler(event):
        ...     print(f"Received: {event['type']}")
        >>> bus.subscribe("tasks", handler)
        >>> bus.publish("tasks", {"type": "task.started", "id": "123"})
        Received: task.started
    """
    
    def __init__(self):
        """Initialize the in-memory event bus."""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Publish an event to a topic.
        
        Args:
            topic: Topic name
            event: Event data (dict or EventEnvelope)
        """
        # Convert EventEnvelope to dict if needed
        if isinstance(event, EventEnvelope):
            event = event.to_dict()
        
        with self._lock:
            handlers = self._subscribers.get(topic, [])
        
        # Call all handlers for this topic
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't break other handlers
                print(f"Error in handler for topic '{topic}': {e}")
    
    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to a topic with a handler.
        
        Args:
            topic: Topic name to subscribe to
            handler: Callback function to handle events
        """
        with self._lock:
            if handler not in self._subscribers[topic]:
                self._subscribers[topic].append(handler)
    
    def unsubscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unsubscribe a handler from a topic.
        
        Args:
            topic: Topic name
            handler: Handler to remove
        """
        with self._lock:
            if handler in self._subscribers[topic]:
                self._subscribers[topic].remove(handler)
    
    def clear(self) -> None:
        """Clear all subscriptions."""
        with self._lock:
            self._subscribers.clear()
    
    def get_subscriber_count(self, topic: str) -> int:
        """
        Get the number of subscribers for a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Number of subscribers
        """
        return len(self._subscribers.get(topic, []))


class RedisEventBus:
    """
    Redis-backed event bus for production use.
    
    Uses Redis pub/sub for distributed event broadcasting.
    Suitable for multi-process and multi-server scenarios.
    
    Example:
        >>> from nagatha_core.runtime import get_redis_instance
        >>> redis_client = get_redis_instance()
        >>> bus = RedisEventBus(redis_client)
        >>> bus.publish("tasks", {"type": "task.started", "id": "123"})
    """
    
    def __init__(self, redis_client: Redis):
        """
        Initialize the Redis event bus.
        
        Args:
            redis_client: Redis client instance
        """
        self._redis = redis_client
        self._pubsub = redis_client.pubsub()
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False
    
    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Publish an event to a topic via Redis.
        
        Args:
            topic: Topic name (will be prefixed with 'nagatha:events:')
            event: Event data (dict or EventEnvelope)
        """
        # Convert EventEnvelope to dict if needed
        if isinstance(event, EventEnvelope):
            event = event.to_dict()
        
        # Publish to Redis
        channel = f"nagatha:events:{topic}"
        message = json.dumps(event)
        self._redis.publish(channel, message)
    
    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to a topic with a handler.
        
        Note: Subscription handling requires calling start_listening()
        to begin processing messages.
        
        Args:
            topic: Topic name
            handler: Callback function
        """
        channel = f"nagatha:events:{topic}"
        
        # Add handler to local registry
        if handler not in self._subscribers[topic]:
            self._subscribers[topic].append(handler)
        
        # Subscribe to Redis channel
        self._pubsub.subscribe(channel)
    
    def start_listening(self) -> None:
        """
        Start listening for published events.
        
        Spawns a background thread to process messages from Redis.
        """
        if self._running:
            return
        
        self._running = True
        self._listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
        )
        self._listener_thread.start()
    
    def stop_listening(self) -> None:
        """Stop listening for events."""
        self._running = False
        if self._listener_thread:
            self._listener_thread.join(timeout=2.0)
    
    def _listen_loop(self) -> None:
        """Background loop to process Redis pub/sub messages."""
        while self._running:
            try:
                message = self._pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    self._handle_message(message)
            except Exception as e:
                print(f"Error in Redis event listener: {e}")
    
    def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a received Redis message.
        
        Args:
            message: Redis message dict
        """
        try:
            # Extract topic from channel name
            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode("utf-8")
            
            topic = channel.replace("nagatha:events:", "")
            
            # Parse event data
            data = message["data"]
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            event = json.loads(data)
            
            # Call all handlers for this topic
            handlers = self._subscribers.get(topic, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in handler for topic '{topic}': {e}")
        
        except Exception as e:
            print(f"Error handling Redis message: {e}")
    
    def close(self) -> None:
        """Close the event bus and cleanup resources."""
        self.stop_listening()
        self._pubsub.close()
