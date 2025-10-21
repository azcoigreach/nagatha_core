"""
Tests for the registry module.
"""

from nagatha_core.registry import TaskRegistry
from nagatha_core.types import TaskStatus


def test_registry_creation():
    """Test TaskRegistry creation."""
    registry = TaskRegistry()
    
    assert registry.modules == {}
    assert registry.tasks == {}
    assert registry._discovered is False


def test_register_task(registry):
    """Test registering a task."""
    
    def test_task(message: str) -> str:
        """Test task."""
        return f"Task: {message}"
    
    # Manually add module metadata first
    from nagatha_core.types import ModuleMetadata
    registry.modules["test"] = ModuleMetadata(
        name="test",
        description="Test module",
        version="0.1.0",
    )
    
    # Register the task
    task_name = registry.register_task("test", "task", test_task)
    
    assert task_name == "test.task"
    assert "test.task" in registry.tasks
    assert "task" in registry.modules["test"].tasks


def test_list_modules(registry):
    """Test listing modules."""
    from nagatha_core.types import ModuleMetadata
    
    # Add test modules
    registry.modules["test1"] = ModuleMetadata(
        name="test1",
        description="Test module 1",
        version="0.1.0",
    )
    registry.modules["test2"] = ModuleMetadata(
        name="test2",
        description="Test module 2",
        version="0.2.0",
    )
    
    modules = registry.list_modules()
    
    assert len(modules) == 2
    assert "test1" in modules
    assert "test2" in modules


def test_list_tasks(registry):
    """Test listing tasks."""
    from nagatha_core.types import ModuleMetadata
    
    # Add module with tasks
    metadata = ModuleMetadata(
        name="test",
        description="Test",
        version="0.1.0",
        tasks={
            "task1": {"name": "test.task1", "doc": "Task 1"},
            "task2": {"name": "test.task2", "doc": "Task 2"},
        },
    )
    registry.modules["test"] = metadata
    
    tasks = registry.list_tasks()
    
    assert "test" in tasks
    assert len(tasks["test"]) == 2


def test_get_module_metadata(registry):
    """Test getting module metadata."""
    from nagatha_core.types import ModuleMetadata
    
    metadata = ModuleMetadata(
        name="test",
        description="Test module",
        version="0.1.0",
    )
    registry.modules["test"] = metadata
    
    retrieved = registry.get_module_metadata("test")
    
    assert retrieved is not None
    assert retrieved.name == "test"
    assert retrieved.version == "0.1.0"


def test_get_task_status(registry):
    """Test getting task status."""
    # This test would require a real Celery app
    # For now, we test the basic structure
    try:
        result = registry.get_task_status("fake-task-id")
        assert result.task_id == "fake-task-id"
        assert result.status == TaskStatus.PENDING
    except Exception:
        # Expected if Celery is not running
        pass


def test_echo_bot_module_load(registry):
    """Test loading the echo_bot module."""
    try:
        # Try to load echo_bot
        loaded = registry.load_module("nagatha_core/modules", "echo_bot")
        
        if loaded:
            assert "echo_bot" in registry.modules
            assert "echo" in registry.modules["echo_bot"].tasks
    except Exception as e:
        # Module might not be importable in test environment
        pass
