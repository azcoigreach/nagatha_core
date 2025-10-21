"""
Tests for the echo_bot module.
"""

from nagatha_core.modules.echo_bot import echo, heartbeat


def test_echo_function():
    """Test the echo function."""
    result = echo("Hello")
    
    assert result == "Echo: Hello"


def test_echo_empty_string():
    """Test echo with empty string."""
    result = echo("")
    
    assert result == "Echo: "


def test_echo_special_characters():
    """Test echo with special characters."""
    result = echo("Hello @#$%")
    
    assert result == "Echo: Hello @#$%"


def test_heartbeat_function():
    """Test the heartbeat function."""
    status = heartbeat()
    
    assert isinstance(status, dict)
    assert status["status"] == "healthy"
    assert status["module"] == "echo_bot"
    assert "version" in status


def test_heartbeat_version():
    """Test heartbeat includes version."""
    status = heartbeat()
    
    assert status["version"] == "0.1.0"
