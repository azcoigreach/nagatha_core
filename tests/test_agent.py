"""
Tests for nagatha_core.agent package.

Tests agent base classes and runner infrastructure.
"""

import pytest
from nagatha_core.agent import BaseAgent, AgentRunner
from nagatha_core.events import EventEnvelope, InMemoryEventBus


class EchoAgent(BaseAgent):
    """Simple test agent that echoes events."""
    
    def handle_event(self, event: EventEnvelope):
        """Echo back the event."""
        return [EventEnvelope(
            source=self.name,
            type="echo.response",
            payload=event.payload,
            correlation_id=event.correlation_id,
        )]


class CounterAgent(BaseAgent):
    """Agent that counts events."""
    
    def __init__(self, name: str, config=None):
        super().__init__(name, config)
        self._state["count"] = 0
    
    def handle_event(self, event: EventEnvelope):
        """Increment counter and return count."""
        self._state["count"] += 1
        return [EventEnvelope(
            source=self.name,
            type="counter.updated",
            payload={"count": self._state["count"]},
            correlation_id=event.correlation_id,
        )]


class TestBaseAgent:
    """Test BaseAgent functionality."""
    
    def test_create_agent(self):
        """Test creating an agent."""
        agent = EchoAgent(name="test_agent")
        assert agent.name == "test_agent"
        assert agent.config == {}
        assert agent.get_state() == {}
    
    def test_agent_with_config(self):
        """Test creating agent with config."""
        config = {"setting": "value"}
        agent = EchoAgent(name="test", config=config)
        assert agent.config == config
    
    def test_handle_event(self):
        """Test handling events."""
        agent = EchoAgent(name="echo")
        
        event = EventEnvelope(
            source="test",
            type="test.event",
            payload={"message": "hello"},
        )
        
        results = agent.handle_event(event)
        
        assert len(results) == 1
        assert results[0].type == "echo.response"
        assert results[0].payload == {"message": "hello"}
        assert results[0].correlation_id == event.correlation_id
    
    def test_agent_state(self):
        """Test agent state management."""
        agent = CounterAgent(name="counter")
        
        # Initial state
        assert agent.get_state() == {"count": 0}
        
        # Handle event
        event = EventEnvelope(source="test", type="test", payload={})
        agent.handle_event(event)
        
        # State updated
        assert agent.get_state() == {"count": 1}
        
        # Update state
        agent.update_state({"extra": "data"})
        assert agent.get_state() == {"count": 1, "extra": "data"}
        
        # Reset state
        agent.reset_state()
        assert agent.get_state() == {}


class TestAgentRunner:
    """Test AgentRunner functionality."""
    
    def test_create_runner(self):
        """Test creating an agent runner."""
        agent = EchoAgent(name="test")
        runner = AgentRunner(agent=agent)
        
        assert runner.agent == agent
    
    def test_run_once(self):
        """Test running agent once."""
        agent = EchoAgent(name="echo")
        bus = InMemoryEventBus()
        runner = AgentRunner(agent=agent, event_bus=bus)
        
        event = EventEnvelope(
            source="test",
            type="test.event",
            payload={"data": "test"},
        )
        
        result = runner.run_once(event)
        
        assert result["status"] == "success"
        assert "duration_ms" in result
        assert "correlation_id" in result
        assert len(result["output_events"]) == 1
    
    def test_run_once_with_event_bus(self):
        """Test runner publishes to event bus."""
        agent = EchoAgent(name="echo")
        bus = InMemoryEventBus()
        received = []
        
        bus.subscribe("echo.response", lambda e: received.append(e))
        
        runner = AgentRunner(agent=agent, event_bus=bus)
        
        event = EventEnvelope(
            source="test",
            type="test.event",
            payload={"msg": "hello"},
        )
        
        runner.run_once(event)
        
        # Event should be published to bus
        assert len(received) == 1
        assert received[0]["type"] == "echo.response"
    
    def test_run_once_error_handling(self):
        """Test error handling in runner."""
        class FailingAgent(BaseAgent):
            def handle_event(self, event):
                raise ValueError("Test error")
        
        agent = FailingAgent(name="failing")
        runner = AgentRunner(agent=agent)
        
        event = EventEnvelope(source="test", type="test", payload={})
        result = runner.run_once(event)
        
        assert result["status"] == "error"
        assert "error" in result
        assert "Test error" in result["error"]
    
    def test_get_agent_state(self):
        """Test getting agent state via runner."""
        agent = CounterAgent(name="counter")
        runner = AgentRunner(agent=agent)
        
        state = runner.get_agent_state()
        assert state == {"count": 0}
        
        # Handle event to update state
        event = EventEnvelope(source="test", type="test", payload={})
        runner.run_once(event)
        
        state = runner.get_agent_state()
        assert state == {"count": 1}
