"""
Agent package - Base agent classes and runner infrastructure.

Provides scaffolding for building autonomous agents that process
events and make decisions.
"""

from .base import BaseAgent
from .runner import AgentRunner

__all__ = [
    "BaseAgent",
    "AgentRunner",
]
