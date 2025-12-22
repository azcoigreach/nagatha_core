"""
Protocol and ABC definitions for nagatha_core.

Defines interfaces that all implementations must follow for
proper integration with the framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from datetime import datetime


class EventBus(Protocol):
    """
    Protocol for event bus implementations.
    
    Event buses handle publish/subscribe patterns for event-driven communication.
    """
    
    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Publish an event to a topic.
        
        Args:
            topic: Topic name to publish to
            event: Event data to publish
        """
        ...
    
    def subscribe(self, topic: str, handler: Any) -> None:
        """
        Subscribe to a topic with a handler.
        
        Args:
            topic: Topic name to subscribe to
            handler: Callback function to handle events
        """
        ...


class ShortTermStore(Protocol):
    """
    Protocol for short-term (in-memory/cache) storage.
    
    Typically backed by Redis or similar key-value stores.
    Good for session data, temporary results, caching.
    """
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None
        """
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value with optional TTL.
        
        Args:
            key: Storage key
            value: Value to store
            ttl: Time-to-live in seconds (None = no expiry)
        """
        ...
    
    def delete(self, key: str) -> bool:
        """
        Delete a key.
        
        Args:
            key: Storage key
            
        Returns:
            True if key existed and was deleted
        """
        ...


class LongTermStore(Protocol):
    """
    Protocol for long-term (persistent) storage.
    
    Typically backed by databases (SQL/NoSQL).
    Good for permanent records, configuration, historical data.
    """
    
    def save(self, collection: str, document: Dict[str, Any]) -> str:
        """
        Save a document to a collection.
        
        Args:
            collection: Collection/table name
            document: Document to save
            
        Returns:
            Document ID
        """
        ...
    
    def find(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find documents matching a query.
        
        Args:
            collection: Collection/table name
            query: Query criteria
            
        Returns:
            List of matching documents
        """
        ...
    
    def update(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a document.
        
        Args:
            collection: Collection/table name
            doc_id: Document ID
            updates: Fields to update
            
        Returns:
            True if document was updated
        """
        ...
    
    def delete(self, collection: str, doc_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            collection: Collection/table name
            doc_id: Document ID
            
        Returns:
            True if document was deleted
        """
        ...


class EventStore(Protocol):
    """
    Protocol for event sourcing storage.
    
    Append-only storage for events. Used for event sourcing patterns,
    audit logs, and event replay capabilities.
    """
    
    def append(self, stream: str, event: Dict[str, Any]) -> str:
        """
        Append an event to a stream.
        
        Args:
            stream: Event stream name
            event: Event data
            
        Returns:
            Event ID
        """
        ...
    
    def read(
        self,
        stream: str,
        from_position: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read events from a stream.
        
        Args:
            stream: Event stream name
            from_position: Starting position (0-based)
            limit: Maximum number of events to read
            
        Returns:
            List of events
        """
        ...


class ModulePlugin(ABC):
    """
    Abstract base class for module/plugin implementations.
    
    Subminds should implement this interface to integrate with nagatha_core.
    """
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get module metadata.
        
        Returns:
            Dictionary with name, version, description, capabilities
        """
        pass
    
    @abstractmethod
    def register_tasks(self, registry: Any) -> None:
        """
        Register tasks with the framework.
        
        Args:
            registry: Task registry instance
        """
        pass
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Health check endpoint.
        
        Returns:
            Health status information
        """
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this module provides.
        
        Returns:
            List of capability names
        """
        return []


class Agent(ABC):
    """
    Abstract base class for agent implementations.
    
    Agents process events and make decisions autonomously.
    """
    
    @abstractmethod
    def handle_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle an incoming event.
        
        Args:
            event: Event data to process
            
        Returns:
            List of resulting events/actions to emit
        """
        pass
    
    def run_step(self) -> Optional[Dict[str, Any]]:
        """
        Execute one step of the agent's decision loop.
        
        Returns:
            Optional action to take
        """
        return None
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current agent state.
        
        Returns:
            State dictionary
        """
        return {}
