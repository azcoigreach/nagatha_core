"""
Base agent implementation.

Provides abstract base class for building autonomous agents
that handle events and execute decision loops.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..contracts.protocols import Agent as AgentProtocol
from ..events.envelope import EventEnvelope


class BaseAgent(ABC):
    """
    Abstract base class for agent implementations.
    
    Agents are autonomous decision-makers that:
    - Process incoming events
    - Execute decision loops
    - Emit actions/events
    - Maintain internal state
    
    Subclasses must implement handle_event() at minimum.
    
    Example:
        >>> class EchoAgent(BaseAgent):
        ...     def handle_event(self, event: EventEnvelope) -> List[EventEnvelope]:
        ...         # Echo back the event
        ...         return [EventEnvelope(
        ...             source=self.name,
        ...             type="echo.response",
        ...             payload=event.payload,
        ...             correlation_id=event.correlation_id,
        ...         )]
        ...
        >>> agent = EchoAgent(name="echo_bot")
        >>> event = EventEnvelope(source="user", type="echo.request", payload={"msg": "hi"})
        >>> responses = agent.handle_event(event)
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent.
        
        Args:
            name: Agent name/identifier
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self._state: Dict[str, Any] = {}
    
    @abstractmethod
    def handle_event(self, event: EventEnvelope) -> List[EventEnvelope]:
        """
        Handle an incoming event.
        
        Process the event and optionally return a list of response events
        or actions to take.
        
        Args:
            event: Event envelope to process
            
        Returns:
            List of resulting events to emit (may be empty)
        """
        pass
    
    def run_step(self) -> Optional[EventEnvelope]:
        """
        Execute one step of the agent's decision loop.
        
        Override this to implement proactive behavior (agents that
        initiate actions without incoming events).
        
        Returns:
            Optional event to emit
        """
        return None
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current agent state.
        
        Returns:
            Copy of internal state dictionary
        """
        return self._state.copy()
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Update agent state.
        
        Args:
            updates: State updates to apply
        """
        self._state.update(updates)
    
    def reset_state(self) -> None:
        """Reset agent state to empty."""
        self._state.clear()
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name={self.name})"
