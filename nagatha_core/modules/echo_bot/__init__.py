"""
echo_bot - A simple test module that echoes messages.

This is an example sub-module demonstrating the module interface
and task registration pattern for nagatha_core.
"""

__version__ = "0.1.0"

from pydantic import BaseModel, Field


class EchoKwargs(BaseModel):
    """Schema for echo task kwargs."""

    message: str = Field(..., description="Message to echo.")

def echo(message: str) -> str:
    """
    Echo a message back.
    
    Args:
        message: The message to echo
        
    Returns:
        The echoed message
    """
    return f"Echo: {message}"


def heartbeat() -> dict:
    """
    Health check for the module.
    
    Returns:
        Status dictionary
    """
    return {
        "status": "healthy",
        "module": "echo_bot",
        "version": __version__,
    }


def register_tasks(registry):
    """
    Register tasks with the nagatha_core registry.
    
    This function is called automatically during module discovery.
    
    Args:
        registry: The TaskRegistry instance
    """
    registry.register_task("echo_bot", "echo", echo, kwargs_model=EchoKwargs)
