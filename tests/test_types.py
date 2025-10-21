"""
Tests for the types module.
"""

from datetime import datetime
from nagatha_core.types import (
    TaskStatus,
    TaskResult,
    ModuleMetadata,
    TaskRequest,
)


def test_task_status_enum():
    """Test TaskStatus enum values."""
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.SUCCESS.value == "success"
    assert TaskStatus.FAILURE.value == "failure"


def test_task_result_creation():
    """Test TaskResult creation."""
    result = TaskResult(
        task_id="test-123",
        status=TaskStatus.SUCCESS,
        result={"data": "test"},
    )
    
    assert result.task_id == "test-123"
    assert result.status == TaskStatus.SUCCESS
    assert result.result == {"data": "test"}
    assert result.error is None


def test_task_result_to_dict():
    """Test TaskResult serialization."""
    result = TaskResult(
        task_id="test-123",
        status=TaskStatus.SUCCESS,
        result="test result",
    )
    
    result_dict = result.to_dict()
    
    assert result_dict["task_id"] == "test-123"
    assert result_dict["status"] == "success"
    assert result_dict["result"] == "test result"


def test_module_metadata_creation():
    """Test ModuleMetadata creation."""
    metadata = ModuleMetadata(
        name="test_module",
        description="A test module",
        version="0.1.0",
    )
    
    assert metadata.name == "test_module"
    assert metadata.description == "A test module"
    assert metadata.version == "0.1.0"
    assert metadata.has_heartbeat is False


def test_module_metadata_to_dict():
    """Test ModuleMetadata serialization."""
    metadata = ModuleMetadata(
        name="test_module",
        description="A test module",
        version="0.1.0",
        tasks={"task1": {"name": "test_module.task1"}},
        has_heartbeat=True,
    )
    
    meta_dict = metadata.to_dict()
    
    assert meta_dict["name"] == "test_module"
    assert meta_dict["version"] == "0.1.0"
    assert meta_dict["has_heartbeat"] is True


def test_task_request_creation():
    """Test TaskRequest creation."""
    request = TaskRequest(
        task_name="echo_bot.echo",
        kwargs={"message": "hello"},
        priority=5,
    )
    
    assert request.task_name == "echo_bot.echo"
    assert request.kwargs == {"message": "hello"}
    assert request.priority == 5
    assert request.retry is True


def test_task_request_validation():
    """Test TaskRequest validation."""
    valid_request = TaskRequest(
        task_name="echo_bot.echo",
        kwargs={},
    )
    
    assert valid_request.validate() is True
    
    invalid_request = TaskRequest(
        task_name="",
        kwargs={},
    )
    
    assert invalid_request.validate() is False
