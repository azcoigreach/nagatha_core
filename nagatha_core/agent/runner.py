"""
Agent runner for executing agents with event bus integration.

Provides infrastructure for running agents with logging,
correlation tracking, and timing measurements.
"""

import time
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from .base import BaseAgent
from ..events.envelope import EventEnvelope
from ..contracts.protocols import EventBus as EventBusProtocol


class AgentRunner:
    """
    Runner for executing agents with full observability.
    
    Integrates agents with event buses, logging, and optional storage.
    Tracks correlation IDs, timing, and provides structured execution.
    
    Example:
        >>> from nagatha_core.agent import BaseAgent, AgentRunner
        >>> from nagatha_core.events import InMemoryEventBus
        ...
        >>> class MyAgent(BaseAgent):
        ...     def handle_event(self, event):
        ...         return []
        ...
        >>> agent = MyAgent(name="my_agent")
        >>> bus = InMemoryEventBus()
        >>> runner = AgentRunner(agent=agent, event_bus=bus)
        ...
        >>> event = EventEnvelope(source="test", type="test.event", payload={})
        >>> results = runner.run_once(event)
    """
    
    def __init__(
        self,
        agent: BaseAgent,
        event_bus: Optional[Any] = None,
        short_term_store: Optional[Any] = None,
        long_term_store: Optional[Any] = None,
        logger: Optional[Any] = None,
    ):
        """
        Initialize the agent runner.
        
        Args:
            agent: Agent instance to run
            event_bus: Optional event bus for publishing results
            short_term_store: Optional short-term storage (e.g., Redis)
            long_term_store: Optional long-term storage (e.g., database)
            logger: Optional logger instance
        """
        self.agent = agent
        self.event_bus = event_bus
        self.short_term_store = short_term_store
        self.long_term_store = long_term_store
        self.logger = logger or self._default_logger
    
    def run_once(self, event: EventEnvelope) -> Dict[str, Any]:
        """
        Execute the agent once with the given event.
        
        Handles event processing, timing, correlation tracking,
        and result publishing.
        
        Args:
            event: Event to process
            
        Returns:
            Execution result with timing and output events
        """
        start_time = time.time()
        correlation_id = event.correlation_id
        
        self.logger(f"[{self.agent.name}] Processing event: {event.type} "
                   f"(correlation: {correlation_id[:8]}...)")
        
        try:
            # Execute agent
            result_events = self.agent.handle_event(event)
            
            # Publish results to event bus if available
            if self.event_bus and result_events:
                for result_event in result_events:
                    self.event_bus.publish(
                        topic=result_event.type,
                        event=result_event,
                    )
            
            # Calculate timing
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger(f"[{self.agent.name}] Completed in {duration_ms:.2f}ms, "
                       f"emitted {len(result_events)} events")
            
            return {
                "status": "success",
                "correlation_id": correlation_id,
                "duration_ms": duration_ms,
                "input_event": event.to_dict(),
                "output_events": [e.to_dict() for e in result_events],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger(f"[{self.agent.name}] Failed after {duration_ms:.2f}ms: {e}")
            
            return {
                "status": "error",
                "correlation_id": correlation_id,
                "duration_ms": duration_ms,
                "input_event": event.to_dict(),
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
    
    def run_step(self) -> Optional[Dict[str, Any]]:
        """
        Execute one step of the agent's autonomous loop.
        
        For agents that initiate actions proactively.
        
        Returns:
            Optional execution result
        """
        start_time = time.time()
        
        try:
            result_event = self.agent.run_step()
            
            if result_event:
                # Publish to event bus if available
                if self.event_bus:
                    self.event_bus.publish(
                        topic=result_event.type,
                        event=result_event,
                    )
                
                duration_ms = (time.time() - start_time) * 1000
                
                self.logger(f"[{self.agent.name}] Step completed in {duration_ms:.2f}ms")
                
                return {
                    "status": "success",
                    "duration_ms": duration_ms,
                    "output_event": result_event.to_dict(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            
            return None
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger(f"[{self.agent.name}] Step failed after {duration_ms:.2f}ms: {e}")
            
            return {
                "status": "error",
                "duration_ms": duration_ms,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
    
    def get_agent_state(self) -> Dict[str, Any]:
        """
        Get current agent state.
        
        Returns:
            Agent state dictionary
        """
        return self.agent.get_state()
    
    @staticmethod
    def _default_logger(message: str) -> None:
        """Default logger implementation."""
        print(f"[AgentRunner] {message}")
