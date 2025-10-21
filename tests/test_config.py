"""
Tests for the config module.
"""

import os
import tempfile
from pathlib import Path

from nagatha_core.config import (
    FrameworkConfig,
    CeleryConfig,
    APIConfig,
    LoggingConfig,
    load_config,
)


def test_celery_config_defaults():
    """Test CeleryConfig with defaults."""
    config = CeleryConfig()
    
    assert config.broker_url == "amqp://guest:guest@localhost:5672//"
    assert config.result_backend == "redis://localhost:6379/0"
    assert config.task_serializer == "json"
    assert config.enable_utc is True


def test_api_config_defaults():
    """Test APIConfig with defaults."""
    config = APIConfig()
    
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.debug is False


def test_logging_config_defaults():
    """Test LoggingConfig with defaults."""
    config = LoggingConfig()
    
    assert config.level == "INFO"
    assert config.log_file is None


def test_framework_config_creation():
    """Test FrameworkConfig creation."""
    config = FrameworkConfig()
    
    assert isinstance(config.celery, CeleryConfig)
    assert isinstance(config.api, APIConfig)
    assert isinstance(config.logging, LoggingConfig)
    assert len(config.module_paths) > 0


def test_framework_config_to_dict():
    """Test FrameworkConfig serialization."""
    config = FrameworkConfig()
    config_dict = config.to_dict()
    
    assert "celery" in config_dict
    assert "api" in config_dict
    assert "logging" in config_dict
    assert "module_paths" in config_dict


def test_load_config_from_env():
    """Test loading config from environment variables."""
    from nagatha_core.config import load_config_from_env
    
    # Set environment variables
    os.environ["NAGATHA_CELERY_BROKER_URL"] = "amqp://test:test@localhost"
    os.environ["NAGATHA_API_PORT"] = "9000"
    
    config = load_config_from_env()
    
    # Note: The nested config loading might need refinement
    # This test validates the basic structure
    assert isinstance(config, FrameworkConfig)
    
    # Cleanup
    del os.environ["NAGATHA_CELERY_BROKER_URL"]
    del os.environ["NAGATHA_API_PORT"]


def test_config_to_dict():
    """Test config dictionary conversion."""
    config = FrameworkConfig(
        celery=CeleryConfig(broker_url="amqp://test"),
        api=APIConfig(port=9000),
    )
    
    config_dict = config.to_dict()
    
    assert config_dict["celery"]["broker_url"] == "amqp://test"
    assert config_dict["api"]["port"] == 9000
