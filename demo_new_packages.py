#!/usr/bin/env python3
"""
Demo script showcasing the new nagatha_core packages.

This script demonstrates:
1. Event envelopes and event bus
2. Correlation ID tracking
3. Agent scaffolding
4. Integration of all new packages
"""

from nagatha_core.events import EventEnvelope, InMemoryEventBus
from nagatha_core.agent import BaseAgent, AgentRunner
from nagatha_core.observability import get_logger, correlation_context

logger = get_logger(__name__)


class GreetingAgent(BaseAgent):
    """Example agent that processes greeting events."""
    
    def handle_event(self, event: EventEnvelope):
        """Process greeting event and return response."""
        if event.type == "greeting.request":
            name = event.payload.get("name", "World")
            logger.info(f"Processing greeting for: {name}")
            
            return [EventEnvelope(
                source=self.name,
                type="greeting.response",
                payload={"message": f"Hello, {name}!"},
                correlation_id=event.correlation_id,
            )]
        return []


def main():
    """Run the demo."""
    print("=" * 60)
    print("Nagatha Core - New Packages Demo")
    print("=" * 60)
    
    # 1. Setup event bus
    print("\n1. Creating event bus...")
    bus = InMemoryEventBus()
    
    # Subscribe to responses
    responses = []
    bus.subscribe("greeting.response", lambda e: responses.append(e))
    print("   ✓ Event bus created and subscribed")
    
    # 2. Create agent
    print("\n2. Creating greeting agent...")
    agent = GreetingAgent(name="greeter_bot")
    runner = AgentRunner(agent=agent, event_bus=bus)
    print("   ✓ Agent and runner created")
    
    # 3. Process events with correlation tracking
    print("\n3. Processing events with correlation tracking...")
    
    with correlation_context("demo-session-123") as corr_id:
        print(f"   Correlation ID: {corr_id[:16]}...")
        
        # Create and process event
        event = EventEnvelope(
            source="demo_script",
            type="greeting.request",
            payload={"name": "Nagatha"},
            correlation_id=corr_id,
        )
        
        print(f"   Sending: {event.type} from {event.source}")
        result = runner.run_once(event)
        
        print(f"   ✓ Status: {result['status']}")
        print(f"   ✓ Duration: {result['duration_ms']:.2f}ms")
        print(f"   ✓ Output events: {len(result['output_events'])}")
    
    # 4. Check results
    print("\n4. Results:")
    if responses:
        response = responses[0]
        print(f"   Message: {response['payload']['message']}")
        print(f"   Correlation: {response['correlation_id'][:16]}...")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    # 5. Show package structure
    print("\n5. Package Structure:")
    print("   contracts/   - Types and protocols")
    print("   runtime/     - Settings and factories")
    print("   events/      - Event messaging")
    print("   agent/       - Agent scaffolding")
    print("   observability/ - Logging and tracing")
    
    print("\nAll new packages working together! 🎉")


if __name__ == "__main__":
    main()
