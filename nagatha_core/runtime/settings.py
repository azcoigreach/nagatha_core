"""
Runtime settings using pydantic-settings.

Centralizes all configuration with environment variable support
and sensible defaults.
"""

from typing import Any, Dict, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Environment variables are prefixed with NAGATHA_ by default.
    Example: NAGATHA_RABBITMQ_URL, NAGATHA_REDIS_URL, etc.
    """
    
    # RabbitMQ Configuration
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@localhost:5672//",
        description="RabbitMQ broker URL",
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis server URL for result backend and caching",
    )
    
    # Celery Configuration
    celery_task_serializer: str = Field(default="json")
    celery_accept_content: List[str] = Field(default=["json"])
    celery_result_serializer: str = Field(default="json")
    celery_timezone: str = Field(default="UTC")
    celery_enable_utc: bool = Field(default=True)
    celery_task_track_started: bool = Field(default=True)
    celery_task_acks_late: bool = Field(default=True)
    celery_worker_prefetch_multiplier: int = Field(default=4)
    celery_worker_max_tasks_per_child: int = Field(default=1000)
    
    # API Configuration
    api_host: str = Field(default="127.0.0.1", description="FastAPI host")
    api_port: int = Field(default=8000, description="FastAPI port")
    api_reload: bool = Field(default=True, description="Enable auto-reload in dev")
    api_workers: int = Field(default=1, description="Number of API workers")
    api_debug: bool = Field(default=False, description="Enable debug mode")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )
    log_file: Optional[str] = Field(default=None, description="Optional log file path")
    
    # Module Discovery
    module_paths: List[str] = Field(
        default=["nagatha_core/modules"],
        description="Paths to search for modules",
    )
    
    # Environment
    env: str = Field(default="development", description="Environment name")
    
    # AI Configuration (extensible)
    ai_config: Dict[str, Any] = Field(default_factory=dict, description="AI module config")
    
    model_config = SettingsConfigDict(
        env_prefix="NAGATHA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )
    
    def get_celery_config(self) -> Dict[str, Any]:
        """
        Get Celery configuration dictionary.
        
        Returns:
            Dictionary of Celery settings
        """
        return {
            "broker_url": self.rabbitmq_url,
            "result_backend": self.redis_url,
            "task_serializer": self.celery_task_serializer,
            "accept_content": self.celery_accept_content,
            "result_serializer": self.celery_result_serializer,
            "timezone": self.celery_timezone,
            "enable_utc": self.celery_enable_utc,
            "task_track_started": self.celery_task_track_started,
            "task_acks_late": self.celery_task_acks_late,
            "worker_prefetch_multiplier": self.celery_worker_prefetch_multiplier,
            "worker_max_tasks_per_child": self.celery_worker_max_tasks_per_child,
        }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
