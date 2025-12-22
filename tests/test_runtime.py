"""
Tests for nagatha_core.runtime package.

Tests settings, Celery factory, and Redis factory.
"""

import pytest
import os
from nagatha_core.runtime import Settings, get_settings, create_celery_app, create_redis_client


class TestSettings:
    """Test Settings class."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.rabbitmq_url == "amqp://guest:guest@localhost:5672//"
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.log_level == "INFO"
        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 8000
        assert settings.env == "development"
    
    def test_custom_settings(self):
        """Test creating settings with custom values."""
        settings = Settings(
            rabbitmq_url="amqp://custom:password@localhost:5672//",
            redis_url="redis://localhost:6379/1",
            log_level="DEBUG",
            api_port=9000,
        )
        
        assert settings.rabbitmq_url == "amqp://custom:password@localhost:5672//"
        assert settings.redis_url == "redis://localhost:6379/1"
        assert settings.log_level == "DEBUG"
        assert settings.api_port == 9000
    
    def test_get_celery_config(self):
        """Test getting Celery configuration."""
        settings = Settings()
        config = settings.get_celery_config()
        
        assert config["broker_url"] == settings.rabbitmq_url
        assert config["result_backend"] == settings.redis_url
        assert config["task_serializer"] == "json"
        assert config["timezone"] == "UTC"
    
    def test_settings_from_env(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("NAGATHA_RABBITMQ_URL", "amqp://test:test@localhost:5672//")
        monkeypatch.setenv("NAGATHA_REDIS_URL", "redis://localhost:6379/2")
        monkeypatch.setenv("NAGATHA_LOG_LEVEL", "WARNING")
        
        settings = Settings()
        
        assert settings.rabbitmq_url == "amqp://test:test@localhost:5672//"
        assert settings.redis_url == "redis://localhost:6379/2"
        assert settings.log_level == "WARNING"


class TestCeleryFactory:
    """Test Celery app factory."""
    
    def test_create_celery_app(self):
        """Test creating Celery app."""
        settings = Settings()
        app = create_celery_app(settings)
        
        assert app is not None
        assert app.conf.broker_url == settings.rabbitmq_url
        assert app.conf.result_backend == settings.redis_url
    
    def test_create_celery_app_custom_name(self):
        """Test creating Celery app with custom name."""
        app = create_celery_app(app_name="test_app")
        assert app.main == "test_app"
    
    def test_celery_app_configuration(self):
        """Test Celery app has correct configuration."""
        settings = Settings(
            celery_task_serializer="json",
            celery_timezone="UTC",
        )
        app = create_celery_app(settings)
        
        assert app.conf.task_serializer == "json"
        assert app.conf.timezone == "UTC"
        assert app.conf.enable_utc is True


class TestRedisFactory:
    """Test Redis client factory."""
    
    @pytest.mark.skipif(
        not os.getenv("REDIS_AVAILABLE"),
        reason="Redis server not available"
    )
    def test_create_redis_client(self):
        """Test creating Redis client (requires Redis server)."""
        settings = Settings()
        client = create_redis_client(settings)
        
        assert client is not None
        # Note: This will fail if Redis is not running
        # client.ping()
    
    def test_create_redis_client_custom_url(self):
        """Test creating Redis client with custom URL."""
        settings = Settings(redis_url="redis://localhost:6379/3")
        client = create_redis_client(settings)
        
        assert client is not None
