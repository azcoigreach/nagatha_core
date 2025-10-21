"""
Test configuration and fixtures for nagatha_core tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def config():
    """Get test configuration."""
    from nagatha_core.config import FrameworkConfig, CeleryConfig, APIConfig, LoggingConfig
    
    return FrameworkConfig(
        celery=CeleryConfig(
            broker_url="memory://",
            result_backend="cache+memory://",
        ),
        api=APIConfig(
            host="127.0.0.1",
            port=8000,
            debug=True,
        ),
        logging=LoggingConfig(
            level="DEBUG",
        ),
        module_paths=["nagatha_core/modules"],
    )


@pytest.fixture
def registry():
    """Get a fresh registry instance for testing."""
    from nagatha_core.registry import TaskRegistry
    
    return TaskRegistry()


@pytest.fixture
def celery_app():
    """Get the Celery app."""
    from nagatha_core.broker import get_celery_app
    
    return get_celery_app()
